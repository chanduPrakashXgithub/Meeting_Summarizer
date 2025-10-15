
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', '')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def upload_file_to_s3(file_path: str, key: str) -> str:
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)
    try:
        s3.upload_file(file_path, AWS_S3_BUCKET, key)
        url = f'https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}'
        return url
    except (BotoCoreError, ClientError) as e:
        raise
