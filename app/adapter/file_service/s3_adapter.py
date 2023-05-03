import logging
from typing import ByteString, Optional
import boto3.session
from botocore.exceptions import ClientError

from app.adapter.file_service.constant import S3_BUCKET_NAME


class S3ClientAdapter:

    def __init__(self) -> None:
        self.client = boto3.client('s3')
        self.bucket_name = S3_BUCKET_NAME

    def get_file_content(self, file_name: str) -> bytes:
        file_contents = b""
        try:
            logging.info(f"bucket name {self.bucket_name}")
            # Use the S3 client to download the file
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_name)

            # Read the contents of the file
            file_contents = response['Body'].read()
        except ClientError as e:
            logging.info(e)
            if e.response['Error']['Code'] == "NoSuchKey":
                logging.info(f"no file {file_name} in s3 bucket")
            else:
                logging.error("An error occurred: ", e)
        return file_contents

    def upload_file(self, content: bytes, file_name: Optional[str]):
        self.client.put_object(Bucket=self.bucket_name, Key=file_name, Body=content)

    def get_list_file(self, prefix: str = None) -> list[str]:
        resp = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [resp_content["Key"] for resp_content in resp["Contents"]]
