# Secure File Uploader

This Django project demonstrates a secure file upload system with server-side encryption and optional S3 storage.

## Features

- Secure file upload with server-side encryption
- Flexible storage options (Amazon S3 or local file system)
- Factory pattern for easy storage type switching
- Unique file naming to prevent conflicts
- Comprehensive error handling and logging
- Extensive test suite using both moto for AWS simulation and mocking

## Prerequisites

- Python3
- pip
- virtualenv (recommended)
- AWS account (for S3 storage option)

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/abdulsamadcs/secure-file-uploader.git
   cd secure-file-uploader
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   USE_S3=False  # Set to True if using S3
   AWS_ACCESS_KEY_ID=your_aws_access_key  # Required if USE_S3 is True
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key  # Required if USE_S3 is True
   AWS_STORAGE_BUCKET_NAME=your_bucket_name  # Required if USE_S3 is True
   AWS_S3_REGION_NAME=your_aws_region  # Required if USE_S3 is True
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

To upload a file using curl:

```bash
curl -X POST -F "file=@test_file.txt" http://localhost:8000/upload/
```

This command assumes you have a `test_file.txt` in your current directory. Adjust the file path as necessary.

## Running Tests

To run the test suite:

```bash
python manage.py test file_handler
```

