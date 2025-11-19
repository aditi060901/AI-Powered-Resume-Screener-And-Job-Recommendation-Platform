import boto3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

s3 = boto3.client("s3")
BUCKET = os.getenv("AWS_BUCKET_NAME")

def upload_bytes_to_s3(file_bytes, key):
    s3.put_object(Bucket=BUCKET, Key=key, Body=file_bytes)
    return f"s3://{BUCKET}/{key}"

def read_s3_file_bytes(s3_url):
    bucket, key = s3_url.replace("s3://", "").split("/", 1)
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()
