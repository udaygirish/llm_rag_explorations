# storage_helpers.py

import os
import boto3
from google.cloud import storage as gcs_storage
from azure.storage.blob import BlobServiceClient
from ftplib import FTP, FTP_TLS
from urllib.parse import urlparse

# Storage Helpers to Support Different Storage Systems

# Currently Not in USe but according to Architecture 

class AWS_S3_Helper:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    
    def upload_file(self, file_name, bucket, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)
        self.s3.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to S3 bucket {bucket} as {object_name}.")

    def download_file(self, bucket, object_name, file_name=None):
        if file_name is None:
            file_name = os.path.basename(object_name)
        self.s3.download_file(bucket, object_name, file_name)
        print(f"File {object_name} downloaded from S3 bucket {bucket} to {file_name}.")


class GCS_Helper:
    def __init__(self, credentials_path=None):
        if credentials_path:
            self.storage_client = gcs_storage.Client.from_service_account_json(credentials_path)
        else:
            self.storage_client = gcs_storage.Client()

    def upload_file(self, bucket_name, file_name, object_name=None):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name if object_name else os.path.basename(file_name))
        blob.upload_from_filename(file_name)
        print(f"File {file_name} uploaded to GCS bucket {bucket_name} as {object_name}.")

    def download_file(self, bucket_name, object_name, file_name=None):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        file_name = file_name if file_name else os.path.basename(object_name)
        blob.download_to_filename(file_name)
        print(f"File {object_name} downloaded from GCS bucket {bucket_name} to {file_name}.")


class AzureBlob_Helper:
    def __init__(self, connection_string):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def upload_file(self, container_name, file_name, blob_name=None):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name or os.path.basename(file_name))
        with open(file_name, "rb") as data:
            blob_client.upload_blob(data)
        print(f"File {file_name} uploaded to Azure Blob container {container_name} as {blob_name}.")

    def download_file(self, container_name, blob_name, file_name=None):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        file_name = file_name if file_name else os.path.basename(blob_name)
        with open(file_name, "wb") as data:
            data.write(blob_client.download_blob().readall())
        print(f"File {blob_name} downloaded from Azure Blob container {container_name} to {file_name}.")


class FTP_Helper:
    def __init__(self, server, username=None, password=None, secure=False):
        if secure:
            self.ftp = FTP_TLS(server)
            self.ftp.login(user=username, passwd=password)
            self.ftp.prot_p()  # Secure data connection
        else:
            self.ftp = FTP(server)
            self.ftp.login(user=username, passwd=password)
    
    def upload_file(self, file_name, remote_path):
        with open(file_name, 'rb') as file:
            self.ftp.storbinary(f"STOR {remote_path}", file)
        print(f"File {file_name} uploaded to FTP server as {remote_path}.")

    def download_file(self, remote_path, file_name=None):
        if file_name is None:
            file_name = os.path.basename(remote_path)
        with open(file_name, 'wb') as file:
            self.ftp.retrbinary(f"RETR {remote_path}", file.write)
        print(f"File {remote_path} downloaded from FTP server to {file_name}.")


def get_storage_helper(url, credentials=None):
    parsed_url = urlparse(url)
    if parsed_url.scheme == 's3':
        return AWS_S3_Helper(**credentials)
    elif parsed_url.scheme == 'gs':
        return GCS_Helper(credentials.get('credentials_path'))
    elif parsed_url.scheme == 'az':
        return AzureBlob_Helper(credentials.get('connection_string'))
    elif parsed_url.scheme.startswith('ftp'):
        return FTP_Helper(parsed_url.hostname, parsed_url.username, parsed_url.password, parsed_url.scheme == 'ftps')
    else:
        raise ValueError(f"Unsupported storage type for URL: {url}")

