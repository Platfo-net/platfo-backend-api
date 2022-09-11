
from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from datetime import timedelta


def add_file_to_s3(object_name, file_path, bucket_name):
    try:
        client = create_client()

        found = client.bucket_exists(bucket_name)
        if not found:
            client.make_bucket(bucket_name)
        client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )

        return object_name
    except S3Error as exc:
        raise Exception(f"Error happen on uploading object: {exc}")


def get_object_url(object_name, bucket_name):
    try:
        client = create_client()
        if object_name in ["", None]:
            return ""
        url = client.get_presigned_url(
            "GET",
            bucket_name,
            object_name,
            expires=timedelta(days=1)
        )
        return url
    except S3Error as exc:
        raise Exception(f"Error happen on getting object: {exc}")


def create_client():
    try:
        client = Minio(
            f"{settings.S3_HOST}:{settings.S3_PORT}",
            access_key=settings.S3_ROOT_USER,
            secret_key=settings.S3_ROOT_PASSWORD,
            secure=False
        )
        return client
    except S3Error as exc:
        raise Exception(f"Error happen on connection: {exc}")
