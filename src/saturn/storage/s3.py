"""S3-compatible storage backend."""

from saturn.storage.base import BlobDescriptor


class S3Storage:
    scheme = "s3"

    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        import boto3

        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def write_bytes(self, key: str, payload: bytes) -> BlobDescriptor:
        response = self.client.put_object(Bucket=self.bucket, Key=key, Body=payload)
        return BlobDescriptor(
            uri=f"s3://{self.bucket}/{key}",
            key=key,
            size_bytes=len(payload),
            etag=response.get("ETag"),
        )

    def read_bytes(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except self.client.exceptions.NoSuchKey:
            return False
        except Exception as exc:
            if getattr(exc, "response", {}).get("Error", {}).get("Code") in {"404", "NoSuchKey"}:
                return False
            raise
        return True

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
