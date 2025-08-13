import asyncio
import logging
import os
import time
from pathlib import Path
from typing import List, Union, Optional
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from azure.storage.blob.aio import BlobServiceClient, ContainerClient, BlobClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from tqdm import tqdm

from .exceptions import DirectoryNotFoundException
from .transfer_path import StorageTransferPath

logger = logging.getLogger(__name__)


async def upload_single_blob_async(
    container_client: ContainerClient, 
    blob_name: str, 
    data: bytes,
    overwrite: bool = True
) -> None:
    """
    Upload a single blob asynchronously.
    
    :param container_client: Azure container client
    :param blob_name: Name of the blob in the container
    :param data: Data to upload
    :param overwrite: Whether to overwrite existing blob
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        await blob_client.upload_blob(data, overwrite=overwrite)
        logger.debug(f"Successfully uploaded blob: {blob_name}")
    except Exception as e:
        logger.error(f"Failed to upload blob {blob_name}: {e}")
        raise


async def download_single_blob_async(
    container_client: ContainerClient,
    blob_name: str,
    local_path: str
) -> None:
    """
    Download a single blob asynchronously.
    
    :param container_client: Azure container client
    :param blob_name: Name of the blob in the container
    :param local_path: Local path to save the file
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, "wb") as file:
            download_stream = await blob_client.download_blob()
            file.write(await download_stream.readall())
        
        logger.debug(f"Successfully downloaded blob: {blob_name} to {local_path}")
    except Exception as e:
        logger.error(f"Failed to download blob {blob_name}: {e}")
        raise


class BulkAzureBlob:
    """
    Azure Blob Storage client for bulk operations using async/await.
    """
    
    def __init__(
        self,
        connection_string: str,
        max_concurrent_operations: int = 50,
        verbose: bool = False,
    ) -> None:
        """
        Initialize Azure Blob Storage client.
        
        :param connection_string: Azure Storage connection string
        :param max_concurrent_operations: Maximum number of concurrent operations
        :param verbose: Show upload progress bar
        """
        self.connection_string = connection_string
        self.max_concurrent_operations = max_concurrent_operations
        self.verbose = verbose
        self._semaphore = asyncio.Semaphore(max_concurrent_operations)
        
    def _get_blob_service_client(self) -> BlobServiceClient:
        """
        Get Azure Blob Service Client.
        
        :return: BlobServiceClient instance
        """
        return BlobServiceClient.from_connection_string(self.connection_string)
    
    async def create_container(self, container_name: str) -> None:
        """
        Create a new container if it doesn't exist.
        
        :param container_name: Name of the container
        """
        try:
            async with self._get_blob_service_client() as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                await container_client.create_container()
                logger.info(f"Successfully created container: '{container_name}'.")
        except ResourceExistsError:
            logger.info(f"Container '{container_name}' already exists.")
        except Exception as e:
            logger.warning(f"Cannot create container: '{container_name}'. {e}")
    
    async def delete_container(self, container_name: str) -> None:
        """
        Delete a container and all its blobs.
        
        :param container_name: Name of the container
        """
        try:
            async with self._get_blob_service_client() as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                await container_client.delete_container()
                logger.info(f"Successfully deleted container: '{container_name}'.")
        except ResourceNotFoundError:
            logger.info(f"Container '{container_name}' does not exist.")
        except Exception as e:
            logger.warning(f"Cannot delete container: '{container_name}'. {e}")
    
    async def empty_container(self, container_name: str) -> None:
        """
        Delete all blobs in a container.
        
        :param container_name: Name of the container
        """
        try:
            async with self._get_blob_service_client() as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                
                # List all blobs and delete them
                async for blob in container_client.list_blobs():
                    blob_client = container_client.get_blob_client(blob.name)
                    await blob_client.delete_blob()
                
                logger.info(f"Successfully emptied container: '{container_name}'.")
        except Exception as e:
            logger.warning(f"Cannot empty container: '{container_name}'. {e}")
    
    async def upload_files(
        self,
        container_name: str,
        upload_paths: Union[StorageTransferPath, List[StorageTransferPath]],
    ) -> None:
        """
        Upload files to Azure Blob Storage asynchronously.
        
        :param container_name: Name of the container
        :param upload_paths: Single path or list of paths to upload
        """
        if isinstance(upload_paths, StorageTransferPath):
            upload_paths = [upload_paths]
        
        if not upload_paths:
            logger.warning("No files to upload.")
            return
        
        start_time = time.time()
        total_size = 0
        
        # Calculate total size and validate files
        for path in upload_paths:
            if not os.path.exists(path.local_path):
                raise FileNotFoundError(f"File not found: {path.local_path}")
            total_size += os.path.getsize(path.local_path)
        
        logger.info(f"Starting upload of {len(upload_paths)} files ({total_size / (1024*1024):.2f} MB)")
        
        async with self._get_blob_service_client() as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            
            # Create container if it doesn't exist
            try:
                await container_client.create_container()
            except ResourceExistsError:
                pass
            
            # Create progress bar if verbose
            pbar = None
            if self.verbose:
                pbar = tqdm(total=len(upload_paths), desc="Uploading files")
            
            # Upload files with semaphore for concurrency control
            async def upload_with_semaphore(path: StorageTransferPath):
                async with self._semaphore:
                    try:
                        with open(path.local_path, "rb") as data:
                            await upload_single_blob_async(
                                container_client, 
                                path.storage_path, 
                                data.read()
                            )
                        if pbar:
                            pbar.update(1)
                    except Exception as e:
                        logger.error(f"Failed to upload {path.local_path}: {e}")
                        raise
            
            # Execute all uploads concurrently
            tasks = [upload_with_semaphore(path) for path in upload_paths]
            await asyncio.gather(*tasks)
            
            if pbar:
                pbar.close()
        
        elapsed_time = time.time() - start_time
        speed = total_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0
        logger.info(f"Upload completed in {elapsed_time:.2f}s ({speed:.2f} MB/s)")
    
    async def upload_directory(
        self,
        container_name: str,
        local_dir: str,
        storage_dir: str = "",
        n_threads: int = 50,
    ) -> None:
        """
        Upload an entire directory to Azure Blob Storage.
        
        :param container_name: Name of the container
        :param local_dir: Local directory path
        :param storage_dir: Storage directory path (prefix for blobs)
        :param n_threads: Number of concurrent threads (not used in async version)
        """
        if not os.path.exists(local_dir):
            raise DirectoryNotFoundException(f"Directory not found: {local_dir}")
        
        if not os.path.isdir(local_dir):
            raise DirectoryNotFoundException(f"Path is not a directory: {local_dir}")
        
        upload_paths = []
        local_path = Path(local_dir)
        
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                # Calculate relative path from local_dir
                relative_path = file_path.relative_to(local_path)
                storage_path = str(relative_path).replace(os.sep, "/")
                
                if storage_dir:
                    storage_path = f"{storage_dir.rstrip('/')}/{storage_path}"
                
                upload_paths.append(
                    StorageTransferPath(
                        local_path=str(file_path),
                        storage_path=storage_path
                    )
                )
        
        await self.upload_files(container_name, upload_paths)
    
    async def download_files(
        self,
        container_name: str,
        download_paths: Union[StorageTransferPath, List[StorageTransferPath]],
    ) -> None:
        """
        Download files from Azure Blob Storage asynchronously.
        
        :param container_name: Name of the container
        :param download_paths: Single path or list of paths to download
        """
        if isinstance(download_paths, StorageTransferPath):
            download_paths = [download_paths]
        
        if not download_paths:
            logger.warning("No files to download.")
            return
        
        start_time = time.time()
        logger.info(f"Starting download of {len(download_paths)} files")
        
        async with self._get_blob_service_client() as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            
            # Create progress bar if verbose
            pbar = None
            if self.verbose:
                pbar = tqdm(total=len(download_paths), desc="Downloading files")
            
            # Download files with semaphore for concurrency control
            async def download_with_semaphore(path: StorageTransferPath):
                async with self._semaphore:
                    try:
                        await download_single_blob_async(
                            container_client,
                            path.storage_path,
                            path.local_path
                        )
                        if pbar:
                            pbar.update(1)
                    except Exception as e:
                        logger.error(f"Failed to download {path.storage_path}: {e}")
                        raise
            
            # Execute all downloads concurrently
            tasks = [download_with_semaphore(path) for path in download_paths]
            await asyncio.gather(*tasks)
            
            if pbar:
                pbar.close()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Download completed in {elapsed_time:.2f}s")
    
    async def download_directory(
        self,
        container_name: str,
        storage_dir: str,
        local_dir: str,
        n_threads: int = 50,
    ) -> None:
        """
        Download an entire directory from Azure Blob Storage.
        
        :param container_name: Name of the container
        :param storage_dir: Storage directory path (prefix for blobs)
        :param local_dir: Local directory path
        :param n_threads: Number of concurrent threads (not used in async version)
        """
        # Create local directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)
        
        async with self._get_blob_service_client() as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            
            download_paths = []
            
            # List all blobs in the storage directory
            async for blob in container_client.list_blobs(name_starts_with=storage_dir):
                # Calculate local path
                relative_path = blob.name[len(storage_dir):].lstrip("/")
                local_path = os.path.join(local_dir, relative_path)
                
                download_paths.append(
                    StorageTransferPath(
                        local_path=local_path,
                        storage_path=blob.name
                    )
                )
            
            await self.download_files(container_name, download_paths)
    
    async def list_blobs(
        self,
        container_name: str,
        storage_dir: str = "",
    ) -> List[str]:
        """
        List all blobs in a container or directory.
        
        :param container_name: Name of the container
        :param storage_dir: Storage directory path (prefix for blobs)
        :return: List of blob names
        """
        blob_names = []
        
        async with self._get_blob_service_client() as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            
            async for blob in container_client.list_blobs(name_starts_with=storage_dir):
                blob_names.append(blob.name)
        
        return blob_names
    
    async def check_blob_exists(
        self,
        container_name: str,
        blob_name: str,
    ) -> bool:
        """
        Check if a blob exists in the container.
        
        :param container_name: Name of the container
        :param blob_name: Name of the blob
        :return: True if blob exists, False otherwise
        """
        try:
            async with self._get_blob_service_client() as blob_service_client:
                blob_client = blob_service_client.get_blob_client(container_name, blob_name)
                await blob_client.get_blob_properties()
                return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking blob existence: {e}")
            return False


# Convenience functions for backward compatibility
async def bulk_upload_blobs(
    connection_string: str, 
    container_name: str, 
    files_to_upload: List[str],
    max_concurrent: int = 50,
    verbose: bool = False
) -> None:
    """
    Bulk upload files to Azure Blob Storage.
    
    :param connection_string: Azure Storage connection string
    :param container_name: Name of the container
    :param files_to_upload: List of file paths to upload
    :param max_concurrent: Maximum number of concurrent uploads
    :param verbose: Show progress bar
    """
    client = BulkAzureBlob(connection_string, max_concurrent, verbose)
    
    # Convert file paths to StorageTransferPath objects
    upload_paths = [
        StorageTransferPath(
            local_path=file_path,
            storage_path=os.path.basename(file_path)
        )
        for file_path in files_to_upload
    ]
    
    await client.upload_files(container_name, upload_paths)


async def bulk_download_blobs(
    connection_string: str,
    container_name: str,
    blob_names: List[str],
    local_dir: str,
    max_concurrent: int = 50,
    verbose: bool = False
) -> None:
    """
    Bulk download blobs from Azure Blob Storage.
    
    :param connection_string: Azure Storage connection string
    :param container_name: Name of the container
    :param blob_names: List of blob names to download
    :param local_dir: Local directory to save files
    :param max_concurrent: Maximum number of concurrent downloads
    :param verbose: Show progress bar
    """
    client = BulkAzureBlob(connection_string, max_concurrent, verbose)
    
    # Convert blob names to StorageTransferPath objects
    download_paths = [
        StorageTransferPath(
            local_path=os.path.join(local_dir, blob_name),
            storage_path=blob_name
        )
        for blob_name in blob_names
    ]
    
    await client.download_files(container_name, download_paths)
