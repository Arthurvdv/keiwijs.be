# Website (Hugo)

One Hugo site for the whole domain: the landing page at `/` (and `/en/`) and the Keiwijs Planner as a section under `/planner/` (and `/en/planner/`). Hugo extended, no theme, no npm. Dutch is the default language, English lives under `/en/`.

| URL | Source |
|---|---|
| `/`, `/en/` | `content/_index*.md` + `layouts/index.html` |
| `/planner/`, `/en/planner/` | `content/planner/_index*.md` + `layouts/planner/list.html` (the tool itself; loads `assets/js/app.js`) |
| `/planner/hoe-werkt-het/`, `/en/planner/how-it-works/` | `content/planner/hoe-werkt-het*.md` |
| `/planner/faq/`, `/planner/privacy/` (+ `/en/planner/...`) | `content/planner/*.md` |

Menus (top nav and the planner sub-nav) are defined per language in `hugo.toml`. Tool cards on the landing page come from `data/tools.yaml`.

## Local development

1. Start the API: `cd planner && func start` (listens on http://localhost:7071; CORS is handled by the API).
2. Start the site: `cd site && hugo server -D` and open http://localhost:1313/planner/.

The development API base is `params.apiBase` in `hugo.toml` (`http://localhost:7071`).

## Production build

```
cd site
hugo --minify --gc --baseURL https://www.keiwijs.be/
```

The production environment (default for `hugo`) merges `config/production/hugo.toml`, which sets `apiBase` to the deployed function app (`https://planner-keiwijs-be.azurewebsites.net`).

Output goes to `site/public/`. The deploy workflow copies `site/staticwebapp.config.json` (headers, 404 page, trailing-slash handling) into `site/public/` after substituting the feed host (`REPLACE-ME.web.core.windows.net`) in the CSP `connect-src`; the API host is already explicit there.

## Translations

UI strings live in `i18n/nl.toml` and `i18n/en.toml`. Keys starting with `js_` are exported to `assets/js/app.js` as a JSON block; when you add one, also add it to the list in `layouts/partials/i18n-json.html`. Landing-page marketing copy lives in the front matter of `content/_index*.md`, so the i18n files stay strict UI copy (no exclamation marks, see `docs/identity/tone-of-voice.md`).
