# Keiwijs Planner API

Python 3.13 Azure Functions app (v2 programming model) behind the planner at
https://www.keiwijs.be/planner/. The package root is this folder (`host.json`
lives here); `.funcignore` keeps tests, tools and docs out of the deployment.

## Local development

Prerequisites: Python 3.13 via [uv](https://docs.astral.sh/uv/), Azure Functions
Core Tools v4, Node (for Azurite).

```bash
cd planner
uv sync                                   # creates .venv with runtime + dev deps
npm i -g azurite
cp local.settings.json.example local.settings.json

# terminal 1: local storage emulator (blobs, queues, tables)
azurite --silent --location .azurite

# terminal 2: the API on http://localhost:7071
func start

# terminal 3: the site on http://localhost:1313/planner/ (reads params.apiBase)
cd ../site && hugo server
```

Tests, lint and types (from this folder):

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

See the [repository README](../README.md) for the architecture and the API, and
[docs/DEPLOY.md](../docs/DEPLOY.md) for deployment.
