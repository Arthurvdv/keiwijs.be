"""Runtime settings read from environment variables (Functions app settings)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

DEFAULT_HOST_PATTERN = r"^(?:[a-z0-9-]+\.)+smartschool\.be$"
DEFAULT_PATH_PATTERN = r"^/planner/sync/ics/[0-9a-f-]{36}/[0-9a-f-]{36}$"
WEB_CONTAINER = "$web"
FEEDS_PREFIX = "feeds"
TABLE_FEEDS = "FeedConfig"
TABLE_ROLLOVER_LOG = "RolloverLog"


@dataclass(frozen=True)
class Settings:
    storage_connection_string: str | None
    storage_account_url: str | None  # https://<account>.blob.core.windows.net (blob), table derived
    feed_base_url: str
    site_url: str
    allowed_origins: tuple[str, ...]
    host_pattern: re.Pattern[str]
    path_pattern: re.Pattern[str]
    user_agent: str

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        e = env if env is not None else dict(os.environ)
        site_url = e.get("SITE_URL", "http://localhost:1313").rstrip("/")
        origins = tuple(
            o.strip().rstrip("/")
            for o in e.get("ALLOWED_ORIGINS", site_url).split(",")
            if o.strip()
        )
        return cls(
            storage_connection_string=e.get("STORAGE_CONNECTION_STRING") or None,
            storage_account_url=e.get("STORAGE_ACCOUNT_BLOB_URL") or None,
            feed_base_url=e.get(
                "FEED_BASE_URL", "http://127.0.0.1:10000/devstoreaccount1/$web"
            ).rstrip("/"),
            site_url=site_url,
            allowed_origins=origins,
            host_pattern=re.compile(e.get("UPSTREAM_HOST_PATTERN", DEFAULT_HOST_PATTERN)),
            path_pattern=re.compile(e.get("UPSTREAM_PATH_PATTERN", DEFAULT_PATH_PATTERN)),
            user_agent=e.get(
                "UPSTREAM_USER_AGENT", f"SmartSchoolPlannerFilter/1.0 (+{site_url}/privacy/)"
            ),
        )

    @property
    def table_account_url(self) -> str | None:
        if not self.storage_account_url:
            return None
        return self.storage_account_url.replace(".blob.", ".table.", 1)
