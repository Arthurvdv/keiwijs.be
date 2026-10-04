"""Feed configuration persistence: Azure Table Storage and an in-memory double."""

from __future__ import annotations

import copy
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Protocol

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient, UpdateMode

from .config import TABLE_FEEDS, TABLE_ROLLOVER_LOG, Settings
from .models import FeedConfig, RolloverLogEntry, row_key_for, utcnow


class FeedRepository(Protocol):
    def get(self, row_key: str) -> FeedConfig | None: ...

    def get_by_url(self, normalised_url: str) -> FeedConfig | None: ...

    def upsert(self, cfg: FeedConfig) -> None: ...

    def delete(self, cfg: FeedConfig) -> None: ...

    def list_all(self) -> Iterable[FeedConfig]: ...

    def mark_rendered(
        self,
        cfg: FeedConfig,
        *,
        content_hash: str | None,
        changed: bool,
        error: str | None,
        now: datetime | None = None,
    ) -> None: ...

    def log_rollover(self, entry: RolloverLogEntry) -> None: ...

    def count_failing(self, threshold: int) -> int: ...


def _render_patch(
    cfg: FeedConfig, content_hash: str | None, changed: bool, error: str | None, now: datetime
) -> dict[str, Any]:
    patch: dict[str, Any] = {"PartitionKey": cfg.partition_key, "RowKey": cfg.row_key}
    if error is None:
        patch.update(
            LastRenderedUtc=now,
            ConsecutiveErrors=0,
            LastError="",
        )
        if content_hash is not None:
            patch["ContentHash"] = content_hash
        if changed:
            patch["LastChangedUtc"] = now
    else:
        patch.update(
            LastError=error[:500],
            LastErrorUtc=now,
            ConsecutiveErrors=cfg.consecutive_errors + 1,
        )
    return patch


def _apply_patch(cfg: FeedConfig, patch: dict[str, Any]) -> None:
    mapping = {
        "LastRenderedUtc": "last_rendered_utc",
        "ConsecutiveErrors": "consecutive_errors",
        "LastError": "last_error",
        "ContentHash": "content_hash",
        "LastChangedUtc": "last_changed_utc",
        "LastErrorUtc": "last_error_utc",
    }
    for key, attr in mapping.items():
        if key in patch:
            value = patch[key]
            setattr(cfg, attr, value if value != "" else None)


class InMemoryFeedRepository:
    def __init__(self) -> None:
        self.rows: dict[str, FeedConfig] = {}
        self.rollover_log: list[RolloverLogEntry] = []

    def get(self, row_key: str) -> FeedConfig | None:
        cfg = self.rows.get(row_key)
        return copy.deepcopy(cfg) if cfg else None

    def get_by_url(self, normalised_url: str) -> FeedConfig | None:
        return self.get(row_key_for(normalised_url))

    def upsert(self, cfg: FeedConfig) -> None:
        self.rows[cfg.row_key] = copy.deepcopy(cfg)

    def delete(self, cfg: FeedConfig) -> None:
        self.rows.pop(cfg.row_key, None)

    def list_all(self) -> Iterable[FeedConfig]:
        return [copy.deepcopy(c) for c in self.rows.values()]

    def mark_rendered(
        self,
        cfg: FeedConfig,
        *,
        content_hash: str | None,
        changed: bool,
        error: str | None,
        now: datetime | None = None,
    ) -> None:
        now = now or utcnow()
        patch = _render_patch(cfg, content_hash, changed, error, now)
        _apply_patch(cfg, patch)
        stored = self.rows.get(cfg.row_key)
        if stored is not None:
            _apply_patch(stored, patch)

    def log_rollover(self, entry: RolloverLogEntry) -> None:
        self.rollover_log.append(entry)

    def count_failing(self, threshold: int) -> int:
        return sum(1 for c in self.rows.values() if c.consecutive_errors >= threshold)


class TableFeedRepository:
    def __init__(self, service: TableServiceClient):
        self._service = service
        self._feeds: TableClient = service.get_table_client(TABLE_FEEDS)
        self._log: TableClient = service.get_table_client(TABLE_ROLLOVER_LOG)

    @classmethod
    def from_settings(cls, settings: Settings) -> TableFeedRepository:
        if settings.storage_connection_string:
            service = TableServiceClient.from_connection_string(settings.storage_connection_string)
        else:
            from azure.identity import DefaultAzureCredential

            if not settings.table_account_url:
                raise RuntimeError("STORAGE_CONNECTION_STRING or STORAGE_ACCOUNT_BLOB_URL required")
            service = TableServiceClient(
                settings.table_account_url, credential=DefaultAzureCredential()
            )
        return cls(service)

    def ensure_tables(self) -> None:
        for name in (TABLE_FEEDS, TABLE_ROLLOVER_LOG):
            try:
                self._service.create_table(name)
            except ResourceExistsError:
                pass

    def get(self, row_key: str) -> FeedConfig | None:
        # PartitionKey is the school host; we only know the RowKey, so query by RowKey.
        rows = list(self._feeds.query_entities(f"RowKey eq '{row_key}'", results_per_page=1))
        return FeedConfig.from_entity(rows[0]) if rows else None

    def get_by_url(self, normalised_url: str) -> FeedConfig | None:
        return self.get(row_key_for(normalised_url))

    def upsert(self, cfg: FeedConfig) -> None:
        self._feeds.upsert_entity(cfg.to_entity(), mode=UpdateMode.REPLACE)

    def delete(self, cfg: FeedConfig) -> None:
        try:
            self._feeds.delete_entity(cfg.partition_key, cfg.row_key)
        except ResourceNotFoundError:
            pass

    def list_all(self) -> Iterable[FeedConfig]:
        for entity in self._feeds.list_entities():
            yield FeedConfig.from_entity(entity)

    def mark_rendered(
        self,
        cfg: FeedConfig,
        *,
        content_hash: str | None,
        changed: bool,
        error: str | None,
        now: datetime | None = None,
    ) -> None:
        now = now or utcnow()
        patch = _render_patch(cfg, content_hash, changed, error, now)
        self._feeds.update_entity(patch, mode=UpdateMode.MERGE)
        _apply_patch(cfg, patch)

    def log_rollover(self, entry: RolloverLogEntry) -> None:
        self._log.upsert_entity(entry.to_entity(), mode=UpdateMode.REPLACE)

    def count_failing(self, threshold: int) -> int:
        rows = self._feeds.query_entities(f"ConsecutiveErrors ge {threshold}", select=["RowKey"])
        return sum(1 for _ in rows)
