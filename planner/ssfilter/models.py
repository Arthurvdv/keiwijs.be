"""Persistent feed configuration record and its JSON/table representations."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from .rules import FilterConfig, clean_keywords
from .tags import (
    Tag,
    TagValidationError,
    default_tags,
    next_rollover_utc,
    tags_from_json,
    tags_to_json,
    validate_month_day,
    validate_tags,
)

SCHEMA_VERSION = 1
DEFAULT_ROLLOVER = "07-01"


def row_key_for(normalised_url: str) -> str:
    return hashlib.sha256(normalised_url.encode("utf-8")).hexdigest()


def partition_for(normalised_url: str) -> str:
    return (urlsplit(normalised_url).hostname or "unknown").lower()


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class FeedConfig:
    row_key: str
    partition_key: str
    source_url: str
    tags: list[Tag]
    include_untagged: bool = True
    include_keywords: tuple[str, ...] = ()
    exclude_keywords: tuple[str, ...] = ()
    use_organisator: bool = False
    strip_participants: bool = True
    rollover_month_day: str = DEFAULT_ROLLOVER
    next_rollover_utc: datetime = field(default_factory=utcnow)
    last_rollover_utc: datetime | None = None
    created_utc: datetime = field(default_factory=utcnow)
    updated_utc: datetime = field(default_factory=utcnow)
    last_rendered_utc: datetime | None = None
    last_changed_utc: datetime | None = None
    content_hash: str = ""
    last_error: str | None = None
    last_error_utc: datetime | None = None
    consecutive_errors: int = 0
    schema_version: int = SCHEMA_VERSION

    # ------------------------------------------------------------------ factories
    @classmethod
    def new(cls, normalised_url: str, now: datetime | None = None) -> FeedConfig:
        now = now or utcnow()
        return cls(
            row_key=row_key_for(normalised_url),
            partition_key=partition_for(normalised_url),
            source_url=normalised_url,
            tags=default_tags(),
            next_rollover_utc=next_rollover_utc(DEFAULT_ROLLOVER, now),
            created_utc=now,
            updated_utc=now,
        )

    def filter_config(self) -> FilterConfig:
        return FilterConfig(
            tags=tuple(self.tags),
            include_untagged=self.include_untagged,
            include_keywords=self.include_keywords,
            exclude_keywords=self.exclude_keywords,
            use_organisator=self.use_organisator,
            strip_participants=self.strip_participants,
        )

    # ------------------------------------------------------------------ settings DTO (API)
    def settings_dto(self) -> dict[str, Any]:
        return {
            "tags": tags_to_json(self.tags),
            "includeUntagged": self.include_untagged,
            "includeKeywords": list(self.include_keywords),
            "excludeKeywords": list(self.exclude_keywords),
            "useOrganisator": self.use_organisator,
            "stripParticipants": self.strip_participants,
            "rolloverMonthDay": self.rollover_month_day,
            "nextRolloverUtc": self.next_rollover_utc.isoformat(),
            "lastRolloverUtc": self.last_rollover_utc.isoformat()
            if self.last_rollover_utc
            else None,
        }

    def with_settings(self, dto: Mapping[str, Any], now: datetime | None = None) -> FeedConfig:
        """Return a copy with user-editable settings replaced and validated."""
        now = now or utcnow()
        tags = validate_tags(tags_from_json(_as_list(dto.get("tags"), "tags")))
        month_day = validate_month_day(str(dto.get("rolloverMonthDay", self.rollover_month_day)))
        try:
            include = clean_keywords(
                [str(x) for x in _as_list(dto.get("includeKeywords", []), "includeKeywords")]
            )
            exclude = clean_keywords(
                [str(x) for x in _as_list(dto.get("excludeKeywords", []), "excludeKeywords")]
            )
        except ValueError as exc:
            raise TagValidationError(str(exc)) from exc
        return replace(
            self,
            tags=tags,
            include_untagged=bool(dto.get("includeUntagged", True)),
            include_keywords=include,
            exclude_keywords=exclude,
            use_organisator=bool(dto.get("useOrganisator", False)),
            strip_participants=bool(dto.get("stripParticipants", True)),
            rollover_month_day=month_day,
            next_rollover_utc=next_rollover_utc(month_day, now),
            updated_utc=now,
        )

    # ------------------------------------------------------------------ table entity
    def to_entity(self) -> dict[str, Any]:
        return {
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "SourceUrl": self.source_url,
            "Tags": json.dumps(tags_to_json(self.tags), ensure_ascii=False),
            "IncludeUntagged": self.include_untagged,
            "IncludeKeywords": json.dumps(list(self.include_keywords), ensure_ascii=False),
            "ExcludeKeywords": json.dumps(list(self.exclude_keywords), ensure_ascii=False),
            "UseOrganisator": self.use_organisator,
            "StripParticipants": self.strip_participants,
            "RolloverMonthDay": self.rollover_month_day,
            "NextRolloverUtc": self.next_rollover_utc,
            "LastRolloverUtc": self.last_rollover_utc,
            "CreatedUtc": self.created_utc,
            "UpdatedUtc": self.updated_utc,
            "LastRenderedUtc": self.last_rendered_utc,
            "LastChangedUtc": self.last_changed_utc,
            "ContentHash": self.content_hash,
            "LastError": self.last_error,
            "LastErrorUtc": self.last_error_utc,
            "ConsecutiveErrors": self.consecutive_errors,
            "SchemaVersion": self.schema_version,
        }

    @classmethod
    def from_entity(cls, e: Mapping[str, Any]) -> FeedConfig:
        return cls(
            row_key=str(e["RowKey"]),
            partition_key=str(e["PartitionKey"]),
            source_url=str(e["SourceUrl"]),
            tags=tags_from_json(json.loads(e.get("Tags") or "[]")),
            include_untagged=bool(e.get("IncludeUntagged", True)),
            include_keywords=tuple(json.loads(e.get("IncludeKeywords") or "[]")),
            exclude_keywords=tuple(json.loads(e.get("ExcludeKeywords") or "[]")),
            use_organisator=bool(e.get("UseOrganisator", False)),
            strip_participants=bool(e.get("StripParticipants", True)),
            rollover_month_day=str(e.get("RolloverMonthDay") or DEFAULT_ROLLOVER),
            next_rollover_utc=_dt(e.get("NextRolloverUtc")) or utcnow(),
            last_rollover_utc=_dt(e.get("LastRolloverUtc")),
            created_utc=_dt(e.get("CreatedUtc")) or utcnow(),
            updated_utc=_dt(e.get("UpdatedUtc")) or utcnow(),
            last_rendered_utc=_dt(e.get("LastRenderedUtc")),
            last_changed_utc=_dt(e.get("LastChangedUtc")),
            content_hash=str(e.get("ContentHash") or ""),
            last_error=e.get("LastError") or None,
            last_error_utc=_dt(e.get("LastErrorUtc")),
            consecutive_errors=int(e.get("ConsecutiveErrors") or 0),
            schema_version=int(e.get("SchemaVersion") or SCHEMA_VERSION),
        )


@dataclass(frozen=True)
class RolloverLogEntry:
    row_key: str
    at: datetime
    trigger: str
    before: list[Tag]
    after: list[Tag]
    summary: str

    def to_entity(self) -> dict[str, Any]:
        return {
            "PartitionKey": str(self.at.year),
            "RowKey": f"{self.row_key}-{self.at.strftime('%Y%m%dT%H%M%S')}",
            "FeedRowKey": self.row_key,
            "At": self.at,
            "Trigger": self.trigger,
            "Before": json.dumps(tags_to_json(self.before), ensure_ascii=False),
            "After": json.dumps(tags_to_json(self.after), ensure_ascii=False),
            "Summary": self.summary,
        }


def _dt(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    # azure-data-tables may hand back TablesEntityDatetime (a datetime subclass) -> handled above
    raise TypeError(f"unsupported datetime value: {type(value)!r}")


def _as_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise TagValidationError(f"{name} must be a list")
    return value
