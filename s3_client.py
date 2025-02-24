import boto3
from botocore.config import Config
from boto3_type_annotations.s3 import Client
from config import config

s3: Client = None

def prepare_s3(no_s3: bool = False) -> None:
    print("Preparing the S3 client.")

    if no_s3: 
        return

    global s3
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=config.S3_URL,
        aws_access_key_id=config.S3_ACCESS_KEY,
        aws_secret_access_key=config.S3_SECRET_KEY,
        config=Config(user_agent=config.S3_USER),
    )
    s3.create_bucket(Bucket="katoda")


def cleanup_s3() -> None:
    print("Cleaning up the S3 client.")

    global s3

    if s3 is None:
        return

    s3.close()
    s3 = None
