import boto3
from botocore.exceptions import ClientError
from django.conf import settings

def create_minio_bucket():
    if not getattr(settings, "USE_MINIO", False):
        return

    s3 = boto3.resource(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        # 404 – bucket absent, 301 – wrong region
        if error_code in (404, 301):
            s3.create_bucket(Bucket=bucket)
        # 403/409 means “already exists / already owned” – safe to ignore
