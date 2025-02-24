import boto3
from botocore.config import Config
from boto3_type_annotations.s3 import Client
from config import config

class S3Client:
    client: Client

    def prepare_s3(self, no_s3: bool = False) -> None:
        print("Preparing the S3 client.")

        if no_s3: 
            return

        self.client = boto3.client(
            service_name="s3",
            endpoint_url=config.S3_URL,
            aws_access_key_id=config.S3_ACCESS_KEY,
            aws_secret_access_key=config.S3_SECRET_KEY,
            config=Config(user_agent=config.S3_USER),
        )

        self.client.create_bucket(Bucke=config.S3_BUCKET)


    def cleanup_s3(self) -> None:
        print("Cleaning up the S3 client.")

        if self.client is None:
            return

        self.client.close()
        self.client = None


s3 = S3Client()

