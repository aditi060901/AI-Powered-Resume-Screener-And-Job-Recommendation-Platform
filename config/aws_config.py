import boto3
import os
from botocore.client import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_BUCKET = os.getenv("AWS_BUCKET_NAME")

# Create global S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
    config=Config(signature_version='s3v4')
)

def upload_bytes_to_s3(file_bytes, file_name, content_type="application/octet-stream"):
    """
    Uploads a file (in bytes) directly to S3.
    """
    s3_client.put_object(
        Bucket=AWS_BUCKET,
        Key=file_name,
        Body=file_bytes,
        ContentType=content_type
    )
    return f"s3://{AWS_BUCKET}/{file_name}"


def download_file_from_s3(file_key):
    """
    Returns file bytes directly.
    """
    obj = s3_client.get_object(Bucket=AWS_BUCKET, Key=file_key)
    return obj["Body"].read()


def generate_presigned_url(file_key, expiry=3600):
    """
    Generate a temporary download URL (1 hour by default).
    """
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": AWS_BUCKET, "Key": file_key},
        ExpiresIn=expiry
    )

