"""Publishing rendered feeds: Blob Storage static website and an in-memory double."""

from __future__ import annotations

from typing import Protocol

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient, ContentSettings

from .config import FEEDS_PREFIX, WEB_CONTAINER, Settings

CONTENT_TYPE = "text/calendar; charset=utf-8"
CACHE_CONTROL = "public, max-age=900"


def blob_name(row_key: str) -> str:
    return f"{FEEDS_PREFIX}/{row_key}.ics"


class FeedPublisher(Protocol):
    def publish(self, row_key: str, body: bytes) -> None: ...

    def unpublish(self, row_key: str) -> None: ...

    def url_for(self, row_key: str) -> str: ...


class InMemoryFeedPublisher:
    def __init__(self, base_url: str = "http://feeds.test/$web"):
        self.base_url = base_url.rstrip("/")
        self.blobs: dict[str, bytes] = {}
        self.publish_calls = 0

    def publish(self, row_key: str, body: bytes) -> None:
        self.publish_calls += 1
        self.blobs[blob_name(row_key)] = body

    def unpublish(self, row_key: str) -> None:
        self.blobs.pop(blob_name(row_key), None)

    def url_for(self, row_key: str) -> str:
        return f"{self.base_url}/{blob_name(row_key)}"


class BlobFeedPublisher:
    def __init__(self, container: ContainerClient, base_url: str):
        self._container = container
        self.base_url = base_url.rstrip("/")

    @classmethod
    def from_settings(cls, settings: Settings) -> BlobFeedPublisher:
        if settings.storage_connection_string:
            service = BlobServiceClient.from_connection_string(settings.storage_connection_string)
        else:
            from azure.identity import DefaultAzureCredential

            if not settings.storage_account_url:
                raise RuntimeError("STORAGE_CONNECTION_STRING or STORAGE_ACCOUNT_BLOB_URL required")
            service = BlobServiceClient(
                settings.storage_account_url, credential=DefaultAzureCredential()
            )
        return cls(service.get_container_client(WEB_CONTAINER), settings.feed_base_url)

    def ensure_container(self) -> None:
        """Local development only: Azurite needs the $web container created explicitly."""
        if not self._container.exists():
            self._container.create_container(public_access="blob")

    def publish(self, row_key: str, body: bytes) -> None:
        self._container.upload_blob(
            name=blob_name(row_key),
            data=body,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=CONTENT_TYPE, cache_control=CACHE_CONTROL
            ),
        )

    def unpublish(self, row_key: str) -> None:
        try:
            self._container.delete_blob(blob_name(row_key))
        except ResourceNotFoundError:
            pass

    def url_for(self, row_key: str) -> str:
        return f"{self.base_url}/{blob_name(row_key)}"

    def ping(self) -> bool:
        try:
            return bool(self._container.exists())
        except Exception:  # noqa: BLE001 - health check must not raise
            return False
