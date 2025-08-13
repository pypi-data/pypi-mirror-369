<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/dynamicdeploy/cloudbulkupload">
    <img src="https://raw.githubusercontent.com/dynamicdeploy/cloudbulkupload/refs/heads/main/imgs/logo.png" alt="Logo">
  </a>
    
  <h3 align="center">Cloud Bulk Upload (cloudbulkupload)</h3>

  <p align="center">
    Python package for fast and parallel transferring a bulk of files to S3, Azure Blob Storage, and Google Cloud Storage!
    <br />
    <a href="https://pypi.org/project/cloudbulkupload/">See on PyPI</a>
    ·
    <a href="https://github.com/dynamicdeploy/cloudbulkupload/blob/main/examples.py">View Examples</a>
    ·
    <a href="https://github.com/dynamicdeploy/cloudbulkupload/issues">Report Bug/Request Feature</a>
    

![Python](https://img.shields.io/pypi/pyversions/cloudbulkupload.svg?style=flat)
![Version](https://img.shields.io/pypi/v/cloudbulkupload.svg?style=flat)
![License](https://img.shields.io/pypi/l/cloudbulkupload.svg?style=flat)
[![Downloads](https://img.shields.io/pypi/dm/cloudbulkupload.svg)](https://pypi.org/project/cloudbulkupload/)   

</p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-cloudbulkupload">About cloudbulkupload</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#quick-start">Quick Start</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage-by-provider">Usage by Provider</a>
      <ul>
        <li><a href="#aws-s3">AWS S3</a></li>
        <li><a href="#azure-blob-storage">Azure Blob Storage</a></li>
        <li><a href="#google-cloud-storage">Google Cloud Storage</a></li>
      </ul>
    </li>
    <li>
      <a href="#testing-and-performance">Testing and Performance</a>
      <ul>
        <li><a href="#running-tests">Running Tests</a></li>
        <li><a href="#performance-comparison">Performance Comparison</a></li>
        <li><a href="#test-results">Test Results</a></li>
      </ul>
    </li>
    <li>
      <a href="#documentation">Documentation</a>
    </li>
    <li>
      <a href="#contributing">Contributing</a>
    </li>
    <li>
      <a href="#contributors">Contributors</a>
    </li>
    <li>
      <a href="#license">License</a>
    </li>
  </ol>
</details>

## About cloudbulkupload

[Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) is the official Python SDK
for accessing and managing all AWS resources such as Amazon Simple Storage Service (S3).
Generally, it's pretty ok to transfer a small number of files using Boto3. However, transferring a large number of
small files impede performance. Although it only takes a few milliseconds per file to transfer,
it can take up to hours to transfer hundreds of thousands, or millions, of files if you do it sequentially.
Moreover, because Amazon S3 does not have folders/directories, managing the hierarchy of directories and files
manually can be a bit tedious especially if there are many files located in different folders.

The `cloudbulkupload` package solves these issues. It speeds up transferring of many small files to **Amazon AWS S3**, **Azure Blob Storage**, and **Google Cloud Storage** by
executing multiple download/upload operations in parallel by leveraging the Python multiprocessing module and async/await patterns.
Depending on the number of cores of your machine, Cloud Bulk Upload can make cloud storage transfers even **100X faster** than sequential
mode using traditional Boto3! Furthermore, Cloud Bulk Upload can keep the original folder structure of files and
directories when transferring them.

### 🚀 Main Functionalities

- **🔄 Multi-Cloud Support**: AWS S3, Azure Blob Storage, and Google Cloud Storage
- **⚡ High Performance**: Multi-thread and async operations for maximum speed
- **📁 Directory Operations**: Upload/download entire directories with structure preservation
- **🎯 Bulk Operations**: Efficient handling of thousands of files
- **📊 Progress Tracking**: Built-in progress bars for long-running operations
- **🧪 Comprehensive Testing**: Full test suite with performance comparisons
- **🔧 Configurable**: Customizable concurrency, timeouts, and error handling
- **📈 Performance Monitoring**: Built-in metrics and comparison tools

### 🏆 Performance Benefits

- **100X faster** than sequential uploads
- **Async operations** for Azure and Google Cloud
- **Multi-threading** for AWS S3
- **Configurable concurrency** for optimal performance
- **Memory efficient** for large file sets

## Getting Started

### Prerequisites

* [Python 3.11+](https://www.python.org/)
* [pip](https://pip.pypa.io/en/stable/)
* API credentials for your chosen cloud provider(s)

**Note**: You can deploy a free S3-compatible server using [MinIO](https://min.io/) 
on your local machine for testing. See our [documentation](docs/TESTING.md) for setup instructions.

### Installation

Use the package manager [pip](https://pypi.org/project/cloudbulkupload/) to install `cloudbulkupload`.

```bash
pip install cloudbulkupload
```

For development and testing:
```bash
pip install "cloudbulkupload[test]"
```

### Quick Start

```python
# AWS S3
from cloudbulkupload import BulkBoto3

aws_client = BulkBoto3(
    endpoint_url="your-endpoint",
    aws_access_key_id="your-key",
    aws_secret_access_key="your-secret",
    verbose=True
)

# Upload directory
aws_client.upload_dir_to_storage(
    bucket_name="my-bucket",
    local_dir="path/to/files",
    storage_dir="uploads",
    n_threads=50
)
```

```python
# Azure Blob Storage
import asyncio
from cloudbulkupload import BulkAzureBlob

async def azure_example():
    azure_client = BulkAzureBlob(
        connection_string="your-connection-string",
        verbose=True
    )
    
    await azure_client.upload_directory(
        container_name="my-container",
        local_dir="path/to/files",
        storage_dir="uploads"
    )

asyncio.run(azure_example())
```

```python
# Google Cloud Storage
import asyncio
from cloudbulkupload import BulkGoogleStorage

async def google_example():
    google_client = BulkGoogleStorage(
        project_id="your-project-id",
        verbose=True
    )
    
    await google_client.upload_directory(
        bucket_name="my-bucket",
        local_dir="path/to/files",
        storage_dir="uploads"
    )

asyncio.run(google_example())
```

## Usage by Provider

### AWS S3

AWS S3 support uses multi-threading for optimal performance on the AWS platform.

#### Basic Setup

```python
from cloudbulkupload import BulkBoto3

client = BulkBoto3(
    endpoint_url="https://s3.amazonaws.com",  # or your custom endpoint
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
    max_pool_connections=300,
    verbose=True
)
```

#### Directory Operations

```python
# Upload entire directory
client.upload_dir_to_storage(
    bucket_name="my-bucket",
    local_dir="path/to/local/directory",
    storage_dir="uploads/my-files",
    n_threads=50
)

# Download entire directory
client.download_dir_from_storage(
    bucket_name="my-bucket",
    storage_dir="uploads/my-files",
    local_dir="downloads",
    n_threads=50
)
```

#### Individual File Operations

```python
from cloudbulkupload import StorageTransferPath

# Upload specific files
upload_paths = [
    StorageTransferPath("file1.txt", "uploads/file1.txt"),
    StorageTransferPath("file2.txt", "uploads/file2.txt")
]

client.upload(bucket_name="my-bucket", upload_paths=upload_paths)

# Download specific files
download_paths = [
    StorageTransferPath("uploads/file1.txt", "local/file1.txt"),
    StorageTransferPath("uploads/file2.txt", "local/file2.txt")
]

client.download(bucket_name="my-bucket", download_paths=download_paths)
```

#### Bucket Management

```python
# Create bucket
client.create_new_bucket("new-bucket-name")

# List objects
objects = client.list_objects(bucket_name="my-bucket", storage_dir="uploads")

# Check if object exists
exists = client.check_object_exists(bucket_name="my-bucket", object_path="uploads/file.txt")

# Empty bucket
client.empty_bucket("my-bucket")
```

### Azure Blob Storage

Azure Blob Storage support uses async/await patterns for optimal performance.

#### Basic Setup

```python
import asyncio
from cloudbulkupload import BulkAzureBlob

async def main():
    client = BulkAzureBlob(
        connection_string="your-azure-connection-string",
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Your operations here
    await client.upload_directory(
        container_name="my-container",
        local_dir="path/to/files",
        storage_dir="uploads"
    )

asyncio.run(main())
```

#### Directory Operations

```python
# Upload directory
await client.upload_directory(
    container_name="my-container",
    local_dir="path/to/local/directory",
    storage_dir="uploads/my-files"
)

# Download directory
await client.download_directory(
    container_name="my-container",
    storage_dir="uploads/my-files",
    local_dir="downloads"
)
```

#### Individual File Operations

```python
from cloudbulkupload import StorageTransferPath

# Upload specific files
upload_paths = [
    StorageTransferPath("file1.txt", "uploads/file1.txt"),
    StorageTransferPath("file2.txt", "uploads/file2.txt")
]

await client.upload_files("my-container", upload_paths)

# Download specific files
download_paths = [
    StorageTransferPath("uploads/file1.txt", "local/file1.txt"),
    StorageTransferPath("uploads/file2.txt", "local/file2.txt")
]

await client.download_files("my-container", download_paths)
```

#### Container Management

```python
# Create container
await client.create_container("new-container")

# List blobs
blobs = await client.list_blobs("my-container", prefix="uploads/")

# Check if blob exists
exists = await client.check_blob_exists("my-container", "uploads/file.txt")

# Empty container
await client.empty_container("my-container")
```

#### Convenience Functions

```python
from cloudbulkupload import bulk_upload_blobs, bulk_download_blobs

# Bulk upload
files = ["file1.txt", "file2.txt", "file3.txt"]
await bulk_upload_blobs(
    connection_string="your-connection-string",
    container_name="my-container",
    files_to_upload=files,
    max_concurrent=50,
    verbose=True
)

# Bulk download
await bulk_download_blobs(
    connection_string="your-connection-string",
    container_name="my-container",
    files_to_download=files,
    local_dir="downloads",
    max_concurrent=50,
    verbose=True
)
```

### Google Cloud Storage

Google Cloud Storage support uses async/await patterns and includes a hybrid approach with Google's Transfer Manager for maximum performance.

#### Basic Setup

```python
import asyncio
from cloudbulkupload import BulkGoogleStorage

async def main():
    client = BulkGoogleStorage(
        project_id="your-project-id",
        credentials_path="/path/to/service-account.json",  # Optional
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Your operations here
    await client.upload_directory(
        bucket_name="my-bucket",
        local_dir="path/to/files",
        storage_dir="uploads"
    )

asyncio.run(main())
```

#### Authentication Options

```python
# Method 1: Service Account Key File
client = BulkGoogleStorage(
    project_id="your-project-id",
    credentials_path="/path/to/service-account.json"
)

# Method 2: Service Account JSON String (for cloud/container environments)
client = BulkGoogleStorage(
    project_id="your-project-id",
    credentials_json='{"type": "service_account", ...}'
)

# Method 3: Application Default Credentials
client = BulkGoogleStorage(project_id="your-project-id")
```

#### Directory Operations

```python
# Upload directory
await client.upload_directory(
    bucket_name="my-bucket",
    local_dir="path/to/local/directory",
    storage_dir="uploads/my-files"
)

# Download directory
await client.download_directory(
    bucket_name="my-bucket",
    storage_dir="uploads/my-files",
    local_dir="downloads"
)
```

#### Individual File Operations

```python
from cloudbulkupload import StorageTransferPath

# Upload specific files
upload_paths = [
    StorageTransferPath("file1.txt", "uploads/file1.txt"),
    StorageTransferPath("file2.txt", "uploads/file2.txt")
]

await client.upload_files("my-bucket", upload_paths)

# Download specific files
download_paths = [
    StorageTransferPath("uploads/file1.txt", "local/file1.txt"),
    StorageTransferPath("uploads/file2.txt", "local/file2.txt")
]

await client.download_files("my-bucket", download_paths)
```

#### Hybrid Approach: Standard vs Transfer Manager

```python
# Standard Mode (Consistent API across all providers)
await client.upload_files("my-bucket", upload_paths)

# Transfer Manager Mode (High Performance - Google Cloud only)
await client.upload_files("my-bucket", upload_paths, use_transfer_manager=True)
```

#### Bucket Management

```python
# Create bucket
await client.create_bucket("new-bucket-name")

# List blobs
blobs = await client.list_blobs("my-bucket", prefix="uploads/")

# Check if blob exists
exists = await client.check_blob_exists("my-bucket", "uploads/file.txt")

# Empty bucket
await client.empty_bucket("my-bucket")
```

#### Convenience Functions

```python
from cloudbulkupload import google_bulk_upload_blobs, google_bulk_download_blobs

# Bulk upload
files = ["file1.txt", "file2.txt", "file3.txt"]
await google_bulk_upload_blobs(
    project_id="your-project-id",
    bucket_name="my-bucket",
    files_to_upload=files,
    max_concurrent=50,
    verbose=True,
    use_transfer_manager=True  # Optional: Use Google's Transfer Manager
)

# Bulk download
await google_bulk_download_blobs(
    project_id="your-project-id",
    bucket_name="my-bucket",
    files_to_download=files,
    local_dir="downloads",
    max_concurrent=50,
    verbose=True
)
```

## Testing and Performance

### Running Tests

The package includes a comprehensive test suite for all providers and performance comparisons.

#### Install Test Dependencies

```bash
pip install "cloudbulkupload[test]"
```

#### Run Different Test Types

```bash
# Unit tests
python run_tests.py --type unit

# Performance tests
python run_tests.py --type performance

# AWS S3 tests
python run_tests.py --type aws

# Azure Blob Storage tests
python run_tests.py --type azure

# Google Cloud Storage tests
python run_tests.py --type google-cloud

# AWS vs Azure comparison
python run_tests.py --type azure-comparison

# Three-way comparison (AWS, Azure, Google)
python run_tests.py --type three-way-comparison

# All tests
python run_tests.py --type all
```

#### Individual Test Files

```bash
# Run specific test files
python tests/aws_s3_test.py
python tests/azure_blob_test.py
python tests/google_cloud_test.py
python tests/performance_comparison_three_way.py
```

### Performance Comparison

The package includes built-in performance comparison tools to test and compare different cloud providers.

#### Three-Way Performance Comparison

```bash
python tests/performance_comparison_three_way.py
```

This will:
- Test AWS S3, Azure Blob Storage, and Google Cloud Storage
- Compare upload/download speeds
- Generate performance reports
- Create CSV files with detailed metrics

#### Performance Metrics

The tests measure:
- **Upload Speed**: MB/s for different file sizes
- **Download Speed**: MB/s for different file sizes
- **Concurrency Impact**: Performance with different thread counts
- **File Size Impact**: Performance with different file sizes
- **Provider Comparison**: Direct comparison between AWS, Azure, and Google Cloud

#### Expected Performance

Based on our testing:
- **AWS S3**: 5-8 MB/s with multi-threading
- **Azure Blob Storage**: 6-9 MB/s with async operations
- **Google Cloud Storage**: 6-9 MB/s with async operations
- **Google Transfer Manager**: 8-12 MB/s for large files

### Test Results

Test results are automatically generated and saved to:
- `performance_comparison_results.csv` - AWS vs Azure comparison
- `performance_comparison_three_way_results.csv` - Three-way comparison
- `test_results.csv` - General test results
- `google_cloud_test_results.json` - Google Cloud specific results

For detailed test documentation, see [docs/TESTING.md](docs/TESTING.md).

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### 📚 Implementation Guides
- [docs/AZURE_GUIDE.md](docs/AZURE_GUIDE.md) - Complete Azure Blob Storage guide
- [docs/GOOGLE_CLOUD_GUIDE.md](docs/GOOGLE_CLOUD_GUIDE.md) - Complete Google Cloud Storage guide

### 📋 Implementation Summaries
- [docs/AZURE_IMPLEMENTATION_SUMMARY.md](docs/AZURE_IMPLEMENTATION_SUMMARY.md) - Azure implementation details
- [docs/GOOGLE_CLOUD_IMPLEMENTATION_SUMMARY.md](docs/GOOGLE_CLOUD_IMPLEMENTATION_SUMMARY.md) - Google Cloud implementation details

### 🧪 Testing Documentation
- [docs/TESTING.md](docs/TESTING.md) - Complete testing guide
- [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md) - Test results and analysis
- [docs/COMPREHENSIVE_TEST_SUMMARY.md](docs/COMPREHENSIVE_TEST_SUMMARY.md) - Comprehensive test summary

### 📦 PyPI Publishing
- [docs/PYPI_PUBLISHING_GUIDE.md](docs/PYPI_PUBLISHING_GUIDE.md) - How to publish to PyPI
- [docs/PYPI_QUICK_REFERENCE.md](docs/PYPI_QUICK_REFERENCE.md) - Quick PyPI reference

### 📖 Original Documentation
- [docs/ORIGINAL_README.md](docs/ORIGINAL_README.md) - Original README for reference

## Contributing

Any contributions you make are **greatly appreciated**. If you have a suggestion that would make this better, please fork the repo and create a pull request. 
You can also simply open an issue with the tag "enhancement". To contribute to `cloudbulkupload`, follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dynamicdeploy/cloudbulkupload.git
cd cloudbulkupload

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[test,dev]"

# Run tests
python run_tests.py --type all
```

## Contributors

Thanks to the following people who have contributed to this project:

* [Amir Masoud Sefidian](https://sefidian.com/) 📖 - Original creator of the bulk upload concept
* [Dynamic Deploy](https://github.com/dynamicdeploy) 🚀 - Multi-cloud expansion and maintenance

## License

Distributed under the [MIT](https://choosealicense.com/licenses/mit/) License. See `LICENSE` for more information.

---

## Credits

This project is based on the original work by **Amir Masoud Sefidian** who created the bulk upload concept and initial implementation. The original repository can be found at: [https://github.com/iamirmasoud/bulkboto3](https://github.com/iamirmasoud/bulkboto3)

The project has been significantly expanded to support multiple cloud providers (AWS S3, Azure Blob Storage, and Google Cloud Storage) while maintaining the core performance benefits of the original implementation.



