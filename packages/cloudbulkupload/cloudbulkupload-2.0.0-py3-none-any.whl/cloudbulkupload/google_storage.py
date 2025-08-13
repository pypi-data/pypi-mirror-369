import asyncio
import logging
import os
import time
from pathlib import Path
from typing import List, Union, Optional
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
from google.api_core.exceptions import NotFound, Conflict
from tqdm import tqdm

from .exceptions import DirectoryNotFoundException
from .transfer_path import StorageTransferPath

logger = logging.getLogger(__name__)


async def upload_single_blob_async(
    bucket: Bucket, 
    blob_name: str, 
    data: bytes,
    overwrite: bool = True
) -> None:
    """
    Upload a single blob asynchronously.
    
    :param bucket: Google Cloud Storage bucket
    :param blob_name: Name of the blob in the bucket
    :param data: Data to upload
    :param overwrite: Whether to overwrite existing blob
    """
    try:
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data)
        logger.debug(f"Successfully uploaded blob: {blob_name}")
    except Exception as e:
        logger.error(f"Failed to upload blob {blob_name}: {e}")
        raise


async def download_single_blob_async(
    bucket: Bucket,
    blob_name: str,
    local_path: str
) -> None:
    """
    Download a single blob asynchronously.
    
    :param bucket: Google Cloud Storage bucket
    :param blob_name: Name of the blob in the bucket
    :param local_path: Local path to save the file
    """
    try:
        blob = bucket.blob(blob_name)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download the blob
        blob.download_to_filename(local_path)
        
        logger.debug(f"Successfully downloaded blob: {blob_name} to {local_path}")
    except Exception as e:
        logger.error(f"Failed to download blob {blob_name}: {e}")
        raise


class BulkGoogleStorage:
    """
    Google Cloud Storage client for bulk operations using async/await.
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        credentials_json: Optional[str] = None,
        max_concurrent_operations: int = 50,
        verbose: bool = False,
    ) -> None:
        """
        Initialize Google Cloud Storage client.
        
        :param project_id: Google Cloud project ID
        :param credentials_path: Path to service account JSON file
        :param credentials_json: Service account JSON as string
        :param max_concurrent_operations: Maximum number of concurrent operations
        :param verbose: Show upload progress bar
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.credentials_json = credentials_json
        self.max_concurrent_operations = max_concurrent_operations
        self.verbose = verbose
        self._semaphore = asyncio.Semaphore(max_concurrent_operations)
        
        # Initialize the client
        if credentials_json:
            # Use credentials from JSON string
            import json
            from google.oauth2 import service_account
            
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self.client = storage.Client(credentials=credentials, project=project_id)
        elif credentials_path and os.path.exists(credentials_path):
            # Use credentials from file path
            self.client = storage.Client.from_service_account_json(
                credentials_path, project=project_id
            )
        else:
            # Use default credentials (Application Default Credentials)
            self.client = storage.Client(project=project_id)
    
    def _get_bucket(self, bucket_name: str) -> Bucket:
        """
        Get Google Cloud Storage bucket.
        
        :param bucket_name: Name of the bucket
        :return: Bucket instance
        """
        return self.client.bucket(bucket_name)
    
    async def create_bucket(self, bucket_name: str, location: str = "US") -> None:
        """
        Create a new bucket if it doesn't exist.
        
        :param bucket_name: Name of the bucket
        :param location: Location for the bucket (e.g., "US", "EU", "ASIA")
        """
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.create(location=location)
            logger.info(f"Successfully created bucket: '{bucket_name}'.")
        except Conflict:
            logger.info(f"Bucket '{bucket_name}' already exists.")
        except Exception as e:
            logger.warning(f"Cannot create bucket: '{bucket_name}'. {e}")
    
    async def delete_bucket(self, bucket_name: str) -> None:
        """
        Delete a bucket and all its blobs.
        
        :param bucket_name: Name of the bucket
        """
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.delete(force=True)  # force=True deletes all blobs
            logger.info(f"Successfully deleted bucket: '{bucket_name}'.")
        except NotFound:
            logger.info(f"Bucket '{bucket_name}' does not exist.")
        except Exception as e:
            logger.warning(f"Cannot delete bucket: '{bucket_name}'. {e}")
    
    async def empty_bucket(self, bucket_name: str) -> None:
        """
        Delete all blobs in a bucket.
        
        :param bucket_name: Name of the bucket
        """
        try:
            bucket = self.client.bucket(bucket_name)
            
            # List all blobs and delete them
            blobs = list(bucket.list_blobs())
            for blob in blobs:
                blob.delete()
            
            logger.info(f"Successfully emptied bucket: '{bucket_name}'.")
        except Exception as e:
            logger.warning(f"Cannot empty bucket: '{bucket_name}'. {e}")
    
    async def upload_files(
        self,
        bucket_name: str,
        upload_paths: Union[StorageTransferPath, List[StorageTransferPath]],
        use_transfer_manager: bool = False,
    ) -> None:
        """
        Upload files to Google Cloud Storage asynchronously.
        
        :param bucket_name: Name of the bucket
        :param upload_paths: Single path or list of paths to upload
        :param use_transfer_manager: Use Google's Transfer Manager for better performance
        """
        if isinstance(upload_paths, StorageTransferPath):
            upload_paths = [upload_paths]
        
        if not upload_paths:
            logger.warning("No files to upload.")
            return
        
        # Use Google's Transfer Manager for better performance if requested
        if use_transfer_manager:
            await self._upload_with_transfer_manager(bucket_name, upload_paths)
            return
        
        start_time = time.time()
        total_size = 0
        
        # Calculate total size and validate files
        for path in upload_paths:
            if not os.path.exists(path.local_path):
                raise FileNotFoundError(f"File not found: {path.local_path}")
            total_size += os.path.getsize(path.local_path)
        
        logger.info(f"Starting upload of {len(upload_paths)} files ({total_size / (1024*1024):.2f} MB)")
        
        bucket = self._get_bucket(bucket_name)
        
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
                            bucket, 
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
    
    async def _upload_with_transfer_manager(
        self,
        bucket_name: str,
        upload_paths: List[StorageTransferPath],
    ) -> None:
        """
        Upload files using Google's Transfer Manager for maximum performance.
        
        :param bucket_name: Name of the bucket
        :param upload_paths: List of paths to upload
        """
        try:
            from google.cloud.storage import transfer_manager
            
            start_time = time.time()
            total_size = 0
            
            # Calculate total size and validate files
            for path in upload_paths:
                if not os.path.exists(path.local_path):
                    raise FileNotFoundError(f"File not found: {path.local_path}")
                total_size += os.path.getsize(path.local_path)
            
            logger.info(f"Starting Transfer Manager upload of {len(upload_paths)} files ({total_size / (1024*1024):.2f} MB)")
            
            bucket = self._get_bucket(bucket_name)
            
            # Get filenames and source directory for transfer manager
            filenames = [os.path.basename(path.local_path) for path in upload_paths]
            source_directory = os.path.dirname(upload_paths[0].local_path)
            
            # Create progress bar if verbose
            pbar = None
            if self.verbose:
                pbar = tqdm(total=len(upload_paths), desc="Transfer Manager Upload")
            
            # Use transfer manager
            transfer_results = transfer_manager.upload_many_from_filenames(
                bucket, filenames, source_directory=source_directory, max_workers=50
            )
            
            # Check for errors
            errors = [r for r in transfer_results if isinstance(r, Exception)]
            if errors:
                raise Exception(f"Transfer manager errors: {errors}")
            
            if pbar:
                pbar.update(len(upload_paths))
                pbar.close()
            
            elapsed_time = time.time() - start_time
            speed = total_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0
            logger.info(f"Transfer Manager upload completed in {elapsed_time:.2f}s ({speed:.2f} MB/s)")
            
        except ImportError:
            logger.warning("Google Transfer Manager not available, falling back to standard upload")
            await self.upload_files(bucket_name, upload_paths, use_transfer_manager=False)
        except Exception as e:
            logger.error(f"Transfer Manager upload failed: {e}")
            raise
    
    async def upload_directory(
        self,
        bucket_name: str,
        local_dir: str,
        storage_dir: str = "",
        n_threads: int = 50,
    ) -> None:
        """
        Upload an entire directory to Google Cloud Storage.
        
        :param bucket_name: Name of the bucket
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
        
        await self.upload_files(bucket_name, upload_paths)
    
    async def download_files(
        self,
        bucket_name: str,
        download_paths: Union[StorageTransferPath, List[StorageTransferPath]],
    ) -> None:
        """
        Download files from Google Cloud Storage asynchronously.
        
        :param bucket_name: Name of the bucket
        :param download_paths: Single path or list of paths to download
        """
        if isinstance(download_paths, StorageTransferPath):
            download_paths = [download_paths]
        
        if not download_paths:
            logger.warning("No files to download.")
            return
        
        start_time = time.time()
        logger.info(f"Starting download of {len(download_paths)} files")
        
        bucket = self._get_bucket(bucket_name)
        
        # Create progress bar if verbose
        pbar = None
        if self.verbose:
            pbar = tqdm(total=len(download_paths), desc="Downloading files")
        
        # Download files with semaphore for concurrency control
        async def download_with_semaphore(path: StorageTransferPath):
            async with self._semaphore:
                try:
                    await download_single_blob_async(
                        bucket,
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
        bucket_name: str,
        storage_dir: str,
        local_dir: str,
        n_threads: int = 50,
    ) -> None:
        """
        Download an entire directory from Google Cloud Storage.
        
        :param bucket_name: Name of the bucket
        :param storage_dir: Storage directory path (prefix for blobs)
        :param local_dir: Local directory path
        :param n_threads: Number of concurrent threads (not used in async version)
        """
        # Create local directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)
        
        bucket = self._get_bucket(bucket_name)
        
        download_paths = []
        
        # List all blobs in the storage directory
        blobs = bucket.list_blobs(prefix=storage_dir)
        for blob in blobs:
            # Calculate local path
            relative_path = blob.name[len(storage_dir):].lstrip("/")
            local_path = os.path.join(local_dir, relative_path)
            
            download_paths.append(
                StorageTransferPath(
                    local_path=local_path,
                    storage_path=blob.name
                )
            )
        
        await self.download_files(bucket_name, download_paths)
    
    async def list_blobs(
        self,
        bucket_name: str,
        storage_dir: str = "",
    ) -> List[str]:
        """
        List all blobs in a bucket or directory.
        
        :param bucket_name: Name of the bucket
        :param storage_dir: Storage directory path (prefix for blobs)
        :return: List of blob names
        """
        bucket = self._get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=storage_dir)
        return [blob.name for blob in blobs]
    
    async def check_blob_exists(
        self,
        bucket_name: str,
        blob_name: str,
    ) -> bool:
        """
        Check if a blob exists in the bucket.
        
        :param bucket_name: Name of the bucket
        :param blob_name: Name of the blob
        :return: True if blob exists, False otherwise
        """
        try:
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking blob existence: {e}")
            return False


# Convenience functions for backward compatibility
async def bulk_upload_blobs(
    project_id: str, 
    bucket_name: str, 
    files_to_upload: List[str],
    credentials_path: Optional[str] = None,
    credentials_json: Optional[str] = None,
    max_concurrent: int = 50,
    verbose: bool = False,
    use_transfer_manager: bool = False
) -> None:
    """
    Bulk upload files to Google Cloud Storage.
    
    :param project_id: Google Cloud project ID
    :param bucket_name: Name of the bucket
    :param files_to_upload: List of file paths to upload
    :param credentials_path: Path to service account JSON file
    :param credentials_json: Service account JSON as string
    :param max_concurrent: Maximum number of concurrent uploads
    :param verbose: Show progress bar
    """
    client = BulkGoogleStorage(
        project_id=project_id, 
        credentials_path=credentials_path,
        credentials_json=credentials_json,
        max_concurrent_operations=max_concurrent, 
        verbose=verbose
    )
    
    # Convert file paths to StorageTransferPath objects
    upload_paths = [
        StorageTransferPath(
            local_path=file_path,
            storage_path=os.path.basename(file_path)
        )
        for file_path in files_to_upload
    ]
    
    await client.upload_files(bucket_name, upload_paths, use_transfer_manager=use_transfer_manager)


async def bulk_download_blobs(
    project_id: str,
    bucket_name: str,
    blob_names: List[str],
    local_dir: str,
    credentials_path: Optional[str] = None,
    credentials_json: Optional[str] = None,
    max_concurrent: int = 50,
    verbose: bool = False
) -> None:
    """
    Bulk download blobs from Google Cloud Storage.
    
    :param project_id: Google Cloud project ID
    :param bucket_name: Name of the bucket
    :param blob_names: List of blob names to download
    :param local_dir: Local directory to save files
    :param credentials_path: Path to service account JSON file
    :param credentials_json: Service account JSON as string
    :param max_concurrent: Maximum number of concurrent downloads
    :param verbose: Show progress bar
    """
    client = BulkGoogleStorage(
        project_id=project_id, 
        credentials_path=credentials_path,
        credentials_json=credentials_json,
        max_concurrent_operations=max_concurrent, 
        verbose=verbose
    )
    
    # Convert blob names to StorageTransferPath objects
    download_paths = [
        StorageTransferPath(
            local_path=os.path.join(local_dir, blob_name),
            storage_path=blob_name
        )
        for blob_name in blob_names
    ]
    
    await client.download_files(bucket_name, download_paths)
