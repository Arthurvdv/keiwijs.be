# Website (Hugo)

Static site for Smartschool Planner Filter. Hugo extended, no theme, no npm. Dutch is the default language, English lives under `/en/`.

## Local development

1. Start the API: `func start` in the repo root (listens on http://localhost:7071; CORS is handled by the API).
2. Start the site: `cd site && hugo server -D` and open http://localhost:1313.

The development API base is `params.apiBase` in `hugo.toml` (`http://localhost:7071`).

## Production build

```
cd site
hugo --minify --gc
```

The production environment (default for `hugo`) merges `config/production/hugo.toml`, which sets `apiBase` to the deployed API. Override per build with an environment variable:

```
HUGO_PARAMS_APIBASE=https://my-func.azurewebsites.net hugo --minify --gc --baseURL https://www.example.org/
```

Output goes to `site/public/` (deploy as the Static Web Apps app artifact; `staticwebapp.config.json` in the repo root holds headers and routes). Remember to put the same API host (and the feed/blob host used by "Test mijn link") in the `connect-src` of the CSP in `staticwebapp.config.json`.

## Placeholders to replace

Search for `REPLACE-ME`: API host (`config/production/hugo.toml`, `staticwebapp.config.json`), GitHub URL (`hugo.toml`, privacy pages), privacy e-mail (privacy pages).

## Translations

UI strings live in `i18n/nl.toml` and `i18n/en.toml`. Keys starting with `js_` are exported to `assets/js/app.js` as a JSON block; when you add one, also add it to the list in `layouts/partials/i18n-json.html`.
