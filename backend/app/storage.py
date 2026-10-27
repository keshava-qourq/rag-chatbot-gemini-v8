"""Document storage behind one seam: Amazon S3 when configured, MEDIA_ROOT otherwise.

Per the project's storage rule, code that needs to read or write an uploaded PDF
calls only the functions below -- never a boto3 client or a MEDIA_ROOT path
directly. That keeps the two backends interchangeable: set `S3_BUCKET` and
nothing else about the caller has to change. Objects are never made public;
`url()` returns a short-lived presigned link in the S3 case.
"""

from __future__ import annotations

import uuid

from app.config import AWS_REGION, MEDIA_ROOT, S3_BUCKET


def _client():
    import boto3

    # No keys, no endpoint: the AWS SDK's default credential chain already works
    # in every environment this runs in (see ENVIRONMENT.md).
    return boto3.client("s3", region_name=AWS_REGION)


def make_key(session_id: str, filename: str) -> str:
    """A storage key unique enough to never collide, but still traceable to its upload."""
    return f"sessions/{session_id}/{uuid.uuid4().hex}-{filename}"


def save(key: str, data: bytes, content_type: str = "application/pdf") -> None:
    """Write ``data`` under ``key``, to S3 when configured, else under MEDIA_ROOT."""
    if S3_BUCKET:
        _client().put_object(Bucket=S3_BUCKET, Key=key, Body=data, ContentType=content_type)
        return
    path = MEDIA_ROOT / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def load(key: str) -> bytes:
    """Read back what ``save`` wrote for ``key``."""
    if S3_BUCKET:
        response = _client().get_object(Bucket=S3_BUCKET, Key=key)
        return response["Body"].read()
    return (MEDIA_ROOT / key).read_bytes()


def delete(key: str) -> None:
    """Remove the object at ``key``, if it exists."""
    if S3_BUCKET:
        _client().delete_object(Bucket=S3_BUCKET, Key=key)
        return
    path = MEDIA_ROOT / key
    path.unlink(missing_ok=True)


def url(key: str, expires_in: int = 3600) -> str:
    """A short-lived link to the object: a presigned S3 URL, or a local media path.

    Citation source display (US-010) follows this link rather than the bucket's
    own URL, since the bucket never makes objects public.
    """
    if S3_BUCKET:
        return _client().generate_presigned_url(
            "get_object", Params={"Bucket": S3_BUCKET, "Key": key}, ExpiresIn=expires_in
        )
    return f"/media/{key}"
