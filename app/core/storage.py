import tempfile
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from app import schemas
from app.core.config import settings
from app.schemas import FileUpload


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
        raise Exception(f'Error happen on uploading object: {exc}')


def get_object_url(object_name, bucket_name):
    try:
        client = create_client()
        if object_name in ['', None]:
            return ''
        url = client.get_presigned_url('GET', bucket_name, object_name, expires=timedelta(days=1))

        return url
    # except S3Error as exc:
    #     raise Exception(f'Error happen on getting object: {exc}')
    except Exception:
        return ""


def create_client():
    try:
        client = Minio(settings.S3_HOST, settings.S3_ROOT_USER, settings.S3_ROOT_PASSWORD,
                       secure=False  # Todo
                       )
        return client
    except S3Error as exc:
        raise Exception(f'Error happen on connection: {exc}')


def get_image(filename, bucket):
    if not filename:
        return None
    object_url = get_object_url(filename, bucket)
    return schemas.Image(filename=filename, url=object_url)


def get_file(filename, bucket):
    if not filename:
        return None
    object_url = get_object_url(filename, bucket)
    return FileUpload(file_name=filename, url=object_url)


def remove_file_from_s3(filename, bucket):
    if not filename:
        return None
    try:
        client = create_client()
        client.remove_object(bucket_name=bucket, object_name=filename)

    except S3Error:
        pass


def download_file_from_minio(bucket_name: str, object_name: str):
    try:
        client = create_client()
        res = client.get_object(bucket_name, object_name)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(res.data)
            temp_file.flush()
            return temp_file.name

    except Exception as exc:
        raise Exception(f"Error downloading file from MinIO: {exc}")
