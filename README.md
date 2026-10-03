# Smartschool Planner Filter

A small, free, credential-free service that turns the Smartschool Planner feed
("Planner delen buiten Smartschool") into a calendar subscription that only
contains the events for **your child's class** plus school-wide events, and that
**moves the class selection forward every school year** on a date you pick.

Parents paste their Smartschool ICS link on the website, tick the class tags
(K1…K3, L1…L6 by default; the list is editable and the *order* is what matters),
preview what stays and what goes, and copy a new `webcal://` link into Google
Calendar, Apple Calendar or Outlook. Feeds are re-rendered every hour.

No Smartschool password, no Google login, no accounts. The pasted Smartschool
URL (it contains two random identifiers) is the only identity: pasting the same
URL again loads the saved settings. Anyone who knows that URL can read the
filtered feed or change its settings, so it should be treated like a password.
This trade-off is deliberate and documented on the privacy page.

## How it works

```
                 ┌──────────── Static Web App (Free) ────────────┐
   parent ─────► │ Hugo site: paste link, tag editor, preview    │
                 └──────┬────────────────────────────────────────┘
                        │ /api/inspect  /api/preview  /api/config
                 ┌──────▼────────── Azure Functions (Flex) ──────┐
                 │ ssfilter: fetch → tags → rules → transform    │
                 │ hourly timer: render every feed once          │
                 └──────┬───────────────────────────┬────────────┘
                        │ Table Storage              │ Blob $web
                        │ FeedConfig, RolloverLog    │ feeds/<hash>.ics
                        ▼                            ▼
                                            calendar apps poll the blob
```

* `ssfilter/ical.py` – byte-faithful RFC 5545 line parser/serializer (keeps UIDs
  and unknown properties intact).
* `ssfilter/tags.py` – tag model, Dutch class-name matching (`L3: Bib`,
  `L4 + L6`, `L1-L6`, `kleuters`, `lagere school`, `iedereen (behalve …)`), and
  the yearly rollover (sequence based: `K3 → L1`, last tag drops off).
* `ssfilter/rules.py` – keep/drop decision: exclude keyword → include keyword →
  untagged (school-wide) → tag match.
* `ssfilter/transform.py` – strips pupil names (`Extra deelnemers`), suffixes the
  calendar name, adds TTL hints, and fingerprints the output ignoring `DTSTAMP`
  (Smartschool regenerates it on every fetch).
* `ssfilter/fetcher.py` – SSRF-guarded upstream fetch (https, `*.smartschool.be`,
  `/planner/sync/ics/<uuid>/<uuid>` only, public IPs, size and time limits).
* `ssfilter/store.py`, `ssfilter/publisher.py` – Table Storage and Blob static
  website adapters plus in-memory doubles for tests.
* `ssfilter/renderer.py` – rollover-if-due → fetch → filter → finalize →
  publish-if-changed; on upstream failure the previous blob stays.
* `function_app.py` – HTTP API, admin routes (function key) and the hourly timer.
* `site/` – Hugo site (Dutch first, English toggle).
* `infra/` – Bicep for Flex Consumption + Storage + Static Web App + monitoring.

## API

All requests are JSON. CORS is restricted to the site origin(s).

| Method | Route | Body | Result |
|---|---|---|---|
| `POST` | `/api/inspect` | `{ "url" }` | calendar name, event list with detected tags and keep/drop decision under the saved (or default) settings, `existing`, `settings`, `feedUrl`, `tagHits` |
| `POST` | `/api/preview` | `{ "url", "settings" }` | same event list under the supplied settings; nothing is stored |
| `POST` | `/api/config` | `{ "url", "settings" }` | upsert + immediate render → `feedUrl`, `webcalUrl`, `render` result |
| `DELETE` | `/api/config` | `{ "url" }` | deletes the settings and the published feed |
| `GET` | `/healthz` | | `{ status, failingFeeds }` |
| `POST` | `/ops/render?rowKey=` | function key | render one feed or all |
| `POST` | `/ops/rollover?dryRun=1&rowKey=` | function key | show or apply due rollovers |

`settings` shape:

```json
{
  "tags": [{ "name": "K1", "selected": false, "moveNext": false }, { "name": "L3", "selected": true, "moveNext": true }],
  "includeUntagged": true,
  "includeKeywords": [],
  "excludeKeywords": [],
  "useOrganisator": false,
  "stripParticipants": true,
  "rolloverMonthDay": "07-01"
}
```

Errors are `{ "error": "<code>", "message": "<text>" }` with status 400
(`invalid_url`, `invalid_settings`, `bad_request`), 429 (`rate_limited`),
502 (`upstream_*`) or 500.

## Local development

Prerequisites: Python 3.13 via [uv](https://docs.astral.sh/uv/), Azure Functions
Core Tools v4, Node (for Azurite), Hugo extended.

```bash
uv sync                                   # creates .venv with runtime + dev deps
npm i -g azurite
cp local.settings.json.example local.settings.json

# terminal 1: local storage emulator (blobs, queues, tables)
azurite --silent --location .azurite

# terminal 2: the API on http://localhost:7071
func start

# terminal 3: the site on http://localhost:1313 (reads params.apiBase)
cd site && hugo server
```

Tests, lint and types:

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

The test fixture `tests/fixtures/calendar_anon.ics` is a real Smartschool
Planner export with teacher and pupil names replaced
(`tools/anonymise_ics.py`). `tests/golden/l3.ics` is the reviewed rendered
output for an L3 selection; regenerate it with `python tools/make_golden.py`
after an intentional output change.

## Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md). Everything is designed to stay inside the
Azure free grants: Functions Flex Consumption (250k executions + 100k GB-s per
month) for the API and the hourly renderer, Blob Storage static website for the
feeds (no execution metering), Static Web Apps Free for the site.

## Privacy and security

* Stored per feed: the Smartschool feed URL, the tag settings, timestamps and a
  hash of the last rendered content. Nothing else. No passwords, no accounts,
  no analytics.
* Pupil names in `Extra deelnemers` are removed from the published feed by
  default.
* The feed URL is a capability URL: do not share it. Delete everything with the
  button on the site (`DELETE /api/config`).
* Report security issues as described in [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE). Not affiliated with Smartschool / Smartbit bv.
