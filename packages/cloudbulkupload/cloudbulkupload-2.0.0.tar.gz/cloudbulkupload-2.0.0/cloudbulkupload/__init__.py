from .bulkboto3 import BulkBoto3
from .azure_blob import BulkAzureBlob, bulk_upload_blobs, bulk_download_blobs
from .google_storage import BulkGoogleStorage, bulk_upload_blobs as google_bulk_upload_blobs, bulk_download_blobs as google_bulk_download_blobs
from .transfer_path import StorageTransferPath

__author__ = "Dynamic Deploy"
__version__ = "2.0.0"
