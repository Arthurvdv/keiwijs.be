# Applying the identity to a Hugo site

Part of the identity guide — see [README.md](README.md). This is the only
platform-specific file. It maps the generic rules in the other files onto a Hugo
project: where tokens live, how fonts are loaded, which partials to touch, and how to
verify. Everything here assumes Hugo ≥ 0.120 with Hugo Pipes (`resources.Get`).

## 1. Plan of work for the agent

1. Read `colors.md`, `typography.md`, `components.md`, `tone-of-voice.md` (and
   `planner-item-types.md` if the site shows calendar/planner data).
2. Add the token stylesheet (§2) to `assets/css/tokens.css` and import it first from the
   site's main stylesheet. If the site already defines its own short custom properties,
   keep them working by aliasing them to the new tokens (§3) instead of rewriting every
   rule at once.
3. Self-host Open Sans (§4) and set the font stack.
4. Restyle the base elements and the shared partials (header, footer, buttons, forms,
   alerts) per §5.
5. Review all Dutch copy in `content/`, `i18n/*.toml` and `layouts/` against
   `tone-of-voice.md` (§6) — this is a content pass, not only CSS.
6. Run the verification checklist (§8).

Do not change information architecture or URLs as part of an identity pass.

## 2. Token stylesheet — `assets/css/tokens.css`

Copy verbatim. Values come from `colors.md`, `typography.md` and `components.md`; if a
value must change, change it there first.

```css
/* ---------- identity tokens: light ---------- */
:root {
  /* brand & accent */
  --color-accent: #FF520E;
  --color-accent-strong: #D03808;
  --color-accent-soft: #FF7337;
  --gradient-brand: linear-gradient(180deg, #FF750E 0%, #F40700 100%);

  /* interactive */
  --color-action: #3A70E6;
  --color-action-hover: #2564CF;
  --color-link: #0033CC;
  --color-link-button: #278DD7;
  --color-info: #1B96F1;
  --color-selected: #DCEBFA;
  --color-unread: #DCEDFF;

  /* status */
  --color-success: #57D31A;        --color-success-hover: #2EB42F;
  --color-warning: #FFCC00;        --color-warning-hover: #D2B224;
  --color-danger: #E30000;         --color-danger-hover: #D20000;
  --color-neutral-action: #D8E0E8; --color-neutral-action-hover: #91A6C1;
  --color-info-soft: #E6F5FF;    --color-info-soft-border: #B0DEFF;    --color-info-soft-text: #022E4D;
  --color-success-soft: #EAFCEA; --color-success-soft-border: #BCF6BC; --color-success-soft-text: #0D450E;
  --color-warning-soft: #FFFCE8; --color-warning-soft-border: #FFF4B7; --color-warning-soft-text: #4D4409;
  --color-danger-soft: #FFE6E6;  --color-danger-soft-border: #FFACAC;  --color-danger-soft-text: #4D0000;

  /* text */
  --color-text: #262626;
  --color-text-secondary: #757575;
  --color-text-muted: #868686;
  --color-text-disabled: #CCCCCC;
  --color-text-error: #E30000;
  --color-text-inverse: #FFFFFF;

  /* surfaces & borders */
  --color-bg: #FFFFFF;
  --color-bg-canvas: #EEEEEE;
  --color-bg-alt: #F4F6F7;
  --color-bg-sidebar: #F3F4F7;
  --color-bg-panel: #F1F1F1;
  --color-bg-hover: #F5F5F5;
  --color-bg-flyout: #FEFEFE;
  --color-bg-widget-header: #DBE0E6;
  --color-border: #CCCCCC;
  --color-border-strong: #868686;
  --color-border-subtle: #E1E1E1;
  --color-divider-menu: #808080;
  --color-icon-settings: #7A71BB;
  --color-footer-bg: #333333;
  --color-footer-bg-deep: #222222;
  --color-footer-text: #AAAAAA;
  --color-footer-border: #555555;
  --color-footer-heading: #919191;
  --color-socket-bg: #111111;
  --color-socket-text: #EEEEEE;

  /* audience blocks */
  --block-green: #98CC2C;  --block-green-text: #0D450E;
  --block-yellow: #F7C447; --block-yellow-text: #4D4409;
  --block-blue: #76BFF7;   --block-blue-text: #022E4D;
  --block-orange: #FF520E; --block-orange-text: #FFFFFF;

  /* shadows */
  --shadow-1: 0 0 1px rgba(0,42,88,.08), 0 1px 2px rgba(0,42,88,.08);
  --shadow-2: 0 0 2px rgba(0,42,88,.08), 0 1px 4px rgba(0,42,88,.08), 0 2px 8px rgba(0,42,88,.08);
  --shadow-card: 0 0 24px rgba(0,42,88,.30);
  --shadow-flyout: 0 4px 16px rgba(0,0,0,.50);
  --shadow-focus: 0 0 5px #278DD7;

  /* typography */
  --font-sans: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
  --text-display: 3rem;   --text-h1: 2.5rem;  --text-h2: 1.75rem; --text-h3: 1.125rem; --text-h4: 1rem;
  --text-lead: 1.25rem;   --text-body: 1rem;  --text-small: .875rem; --text-meta: .75rem;
  --text-button: .875rem; --text-nav: .8125rem; --text-overline: .8125rem;

  /* spacing & shape */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-5: 24px;
  --space-6: 32px; --space-7: 48px; --space-8: 64px; --space-9: 96px;
  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px; --radius-xl: 12px;
  --radius-card: 24px; --radius-pill: 999px; --radius-round: 50%;
  --motion-fast: 150ms; --motion-slow: 250ms; --opacity-disabled: .45;
  --container: 1130px; --content: 800px;

  color-scheme: light;
}

/* ---------- identity tokens: dark (derived) ---------- */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --_dark: 1; }
}
:root[data-theme="dark"] { --_dark: 1; }

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --color-bg: #1E2227; --color-bg-canvas: #15181C; --color-bg-alt: #232830;
    --color-bg-sidebar: #1A1E23; --color-bg-panel: #272C33; --color-bg-hover: #272C33;
    --color-bg-flyout: #272C33; --color-bg-widget-header: #272C33;
    --color-border: #3A4149; --color-border-strong: #52606F; --color-border-subtle: #2E343B;
    --color-text: #F4F6F7; --color-text-secondary: #A9B5C2; --color-text-muted: #91A0AF;
    --color-text-disabled: #52606F; --color-text-error: #FF7373;
    --color-link: #7CC6FD; --color-link-button: #4AAEF8;
    --color-selected: #0B3A66; --color-unread: #0B3A66;
    --color-info-soft: #0B2A44; --color-info-soft-border: #0B63A4; --color-info-soft-text: #B0DEFF;
    --color-success-soft: #0D2E12; --color-success-soft-border: #219023; --color-success-soft-text: #BCF6BC;
    --color-warning-soft: #332D0A; --color-warning-soft-border: #A68E19; --color-warning-soft-text: #FFF4B7;
    --color-danger-soft: #3A0F0F; --color-danger-soft-border: #A60000; --color-danger-soft-text: #FFACAC;
    --color-footer-bg: #0F1114; --color-footer-bg-deep: #0A0B0D; --color-socket-bg: #050607;
    --shadow-card: 0 0 24px rgba(0,0,0,.60); --shadow-focus: 0 0 5px #4AAEF8;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --color-bg: #1E2227; --color-bg-canvas: #15181C; --color-bg-alt: #232830;
  --color-bg-sidebar: #1A1E23; --color-bg-panel: #272C33; --color-bg-hover: #272C33;
  --color-bg-flyout: #272C33; --color-bg-widget-header: #272C33;
  --color-border: #3A4149; --color-border-strong: #52606F; --color-border-subtle: #2E343B;
  --color-text: #F4F6F7; --color-text-secondary: #A9B5C2; --color-text-muted: #91A0AF;
  --color-text-disabled: #52606F; --color-text-error: #FF7373;
  --color-link: #7CC6FD; --color-link-button: #4AAEF8;
  --color-selected: #0B3A66; --color-unread: #0B3A66;
  --color-info-soft: #0B2A44; --color-info-soft-border: #0B63A4; --color-info-soft-text: #B0DEFF;
  --color-success-soft: #0D2E12; --color-success-soft-border: #219023; --color-success-soft-text: #BCF6BC;
  --color-warning-soft: #332D0A; --color-warning-soft-border: #A68E19; --color-warning-soft-text: #FFF4B7;
  --color-danger-soft: #3A0F0F; --color-danger-soft-border: #A60000; --color-danger-soft-text: #FFACAC;
  --color-footer-bg: #0F1114; --color-footer-bg-deep: #0A0B0D; --color-socket-bg: #050607;
  --shadow-card: 0 0 24px rgba(0,0,0,.60); --shadow-focus: 0 0 5px #4AAEF8;
  color-scheme: dark;
}

@media (prefers-reduced-motion: reduce) {
  :root { --motion-fast: 0ms; --motion-slow: 0ms; }
}
```

Import order in `assets/css/main.css`:

```css
@import "tokens.css";
/* then base, components, utilities */
```

With Hugo Pipes in `baseof.html`:

```go-html-template
{{ $css := resources.Get "css/main.css" | resources.ExecuteAsTemplate "css/main.css" . | minify | fingerprint }}
<link rel="stylesheet" href="{{ $css.RelPermalink }}" integrity="{{ $css.Data.Integrity }}">
```

(`resources.ExecuteAsTemplate` lets `@import` of a sibling asset resolve; alternatively
concatenate with `resources.Concat`.)

## 3. Aliasing an existing short-name token set

Many small Hugo sites already have variables such as `--bg`, `--surface`, `--text`,
`--muted`, `--border`, `--accent`, `--accent-soft`, `--danger`, `--ok`, `--radius`,
`--font`. Keep them as **aliases** so existing rules switch over immediately, then
migrate rules to the long names when touched:

```css
:root {
  --bg: var(--color-bg-canvas);
  --surface: var(--color-bg);
  --text: var(--color-text);
  --muted: var(--color-text-secondary);
  --border: var(--color-border);
  --accent: var(--color-action);          /* interactive blue, NOT the orange */
  --accent-text: var(--color-text-inverse);
  --accent-soft: var(--color-selected);
  --danger: var(--color-danger);
  --danger-soft: var(--color-danger-soft);
  --ok: var(--color-success);
  --warn-soft: var(--color-warning-soft);
  --radius: var(--radius-lg);
  --font: var(--font-sans);
}
```

Remove any separate `@media (prefers-color-scheme: dark)` block that redefined the
short names — the dark values now flow through the aliases from `tokens.css`.

## 4. Fonts

Self-host Open Sans (OFL licence) as woff2 under `static/fonts/` — four files:
`OpenSans-Light.woff2` (300), `OpenSans-Regular.woff2` (400), `OpenSans-SemiBold.woff2`
(600), `OpenSans-Bold.woff2` (700). Variable-font builds are fine too (one file,
`font-weight: 300 800`).

```css
@font-face { font-family: "Open Sans"; font-style: normal; font-weight: 300; font-display: swap; src: url("/fonts/OpenSans-Light.woff2") format("woff2"); }
@font-face { font-family: "Open Sans"; font-style: normal; font-weight: 400; font-display: swap; src: url("/fonts/OpenSans-Regular.woff2") format("woff2"); }
@font-face { font-family: "Open Sans"; font-style: normal; font-weight: 600; font-display: swap; src: url("/fonts/OpenSans-SemiBold.woff2") format("woff2"); }
@font-face { font-family: "Open Sans"; font-style: normal; font-weight: 700; font-display: swap; src: url("/fonts/OpenSans-Bold.woff2") format("woff2"); }
```

Preload the 400 weight in `<head>`:
`<link rel="preload" href="/fonts/OpenSans-Regular.woff2" as="font" type="font/woff2" crossorigin>`.
No external font CDN (privacy page promises no third-party calls).

## 5. Base styles and partials

### Base (`assets/css/base.css`)

```css
*,*::before,*::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--color-bg-canvas); color: var(--color-text);
       font: var(--text-body)/1.6 var(--font-sans); -webkit-font-smoothing: antialiased; }
main { background: var(--color-bg); }
.container { max-width: var(--container); margin: 0 auto; padding: 0 var(--space-5); }
.prose    { max-width: 65ch; }
h1 { font-size: var(--text-h1); font-weight: 300; line-height: 1.2; color: var(--color-text-muted); margin: 0 0 .5em; }
h2 { font-size: var(--text-h2); font-weight: 300; line-height: 1.3; margin: 2em 0 .5em; }
h3 { font-size: var(--text-h3); font-weight: 700; line-height: 1.4; margin: 1.5em 0 .5em;
     display: flex; align-items: center; gap: var(--space-3); }
h3::after { content: ""; flex: 1; height: 1px; background: var(--color-border); }
h1 strong, h2 strong, .display strong { color: var(--color-accent); font-weight: 700; }
p strong { font-weight: 600; }
a { color: var(--color-link); text-decoration: none; }
a:hover, a:focus-visible { text-decoration: underline; }
small, .meta { font-size: var(--text-meta); color: var(--color-text-muted); }
:focus-visible { outline: none; border-color: var(--color-link-button); box-shadow: var(--shadow-focus); }
.skip-link { position: absolute; left: var(--space-4); top: -100px; background: var(--color-bg);
             color: var(--color-link-button); font: 600 .875rem var(--font-sans); padding: var(--space-3) var(--space-5);
             border-radius: 0 0 var(--radius-sm) var(--radius-sm); }
.skip-link:focus { top: 0; }
```

### Buttons (`assets/css/components.css`, excerpt)

```css
.btn { display: inline-flex; align-items: center; gap: var(--space-2); height: 40px; padding: 0 var(--space-4);
       border-radius: var(--radius-md); border: 1px solid transparent; font: 600 var(--text-button) var(--font-sans);
       cursor: pointer; transition: background var(--motion-fast) ease-in-out, opacity var(--motion-fast); }
.btn-primary { background: var(--color-action); color: var(--color-text-inverse); }
.btn-primary:hover { background: var(--color-action-hover); }
.btn-outline { background: var(--color-bg); color: var(--color-text); border-color: var(--color-border); }
.btn-outline:hover { background: var(--color-bg-hover); }
.btn-text { background: none; color: var(--color-text-secondary); }
.btn-link { background: none; color: var(--color-link-button); padding: 0; height: auto; }
.btn-accent { background: var(--color-accent); color: #fff; border-bottom-color: var(--color-accent-strong); height: 48px; padding: 0 30px; }
.btn-accent:hover { opacity: .9; }
.btn-danger { background: var(--color-danger); color: #fff; }
.btn[disabled] { opacity: var(--opacity-disabled); pointer-events: none; }
```

### Partials to touch

| Partial | Change |
|---|---|
| `layouts/_default/baseof.html` | add `<a class="skip-link" href="#main">Spring naar hoofdcontent</a>`, `<main id="main">`, `lang="nl-BE"` from `.Site.Language.Lang`, `<meta name="theme-color" content="#FF520E">`, preload font. |
| `layouts/partials/header.html` | white header 72 px, logo left, nav `--text-nav` 600 `#333333`, active item 2 px underline `--color-accent` (`{{ if .IsMenuCurrent }}` / `.HasMenuCurrent`), burger below 990 px. |
| `layouts/partials/footer.html` | `--color-footer-bg`, columns with `--text-overline` titles, links `--color-footer-text`; add a `--color-socket-bg` strip with the legal line. |
| `layouts/partials/lang-switch.html` | text toggle "NL · EN" in header right, `--text-nav`; current language 600. |
| `layouts/index.html` | hero: display title (one `<strong>` word), lead, one `.btn-accent` + one `.btn-outline`; below: 3-up `.card` grid (24 px radius, `--shadow-card`) or an audience block. |
| `layouts/_default/single.html` | `.prose` wrapper, h1 light grey, info banner shortcode available. |
| `layouts/shortcodes/alert.html` (new) | `{{< alert kind="info" >}}…{{< /alert >}}` → `.alert.alert-info` using the soft tokens. |
| `layouts/partials/planner-legend.html` (if applicable) | render `data/planner_types.yaml` (see `planner-item-types.md` §5): icon · label per row. |

### Theme toggle

`assets/js/theme.js` sets `data-theme="light|dark"` on `<html>` from `localStorage`
before CSS loads. It is an external, fingerprinted script loaded synchronously in
`<head>`, because the CSP (`script-src 'self'`) blocks inline scripts. The 3-state
control *Systeem / Licht / Donker* (`partials/theme-toggle.html`) sits in the header
next to the language switch. With "Systeem" (the default) `tokens.css` follows the OS
preference.

## 6. Content pass

- `i18n/nl.toml`: every button/label value → object + infinitive, sentence case, no
  period; helper/empty/error strings → full sentence with period; check the vocabulary
  table in `tone-of-voice.md` §5.
- `content/*.md` (nl): je/jij throughout; headings sentence case; one accented
  `<strong>` word max per h1/h2 (Markdown `**word**` renders as `<strong>` — the CSS
  colours it only inside headings).
- `content/privacy.md`: keep it plain-spoken; reassurance line pattern from
  `tone-of-voice.md` §4.
- English content follows the same structure; English register is friendly-direct,
  "you", sentence case.
- Front matter: `title` in sentence case; add `description` ≤ 155 characters in the
  same voice for `<meta name="description">`.

## 7. Hugo config touchpoints

```toml
[params]
  themeColor = "#FF520E"          # used in <meta name="theme-color">
  fontPreload = "/fonts/OpenSans-Regular.woff2"

[languages.nl]
  languageCode = "nl-BE"          # drives <html lang> and date formats
  [languages.nl.params]
    dateFormat = "2 January 2006" # render via time.Format with the nl translation table
```

Date rendering: `{{ .Date | time.Format ":date_long" }}` with `languageCode = "nl-BE"`
yields "9 januari 2026"; for list/table timestamps use `{{ .Date.Format "2006-01-02 15:04" }}`.

## 8. Verification checklist

1. `hugo --minify --gc` builds without warnings; `hugo server` renders both languages.
2. Grep the built site: `grep -rEo '#[0-9a-fA-F]{6}' public/**/*.css | sort -u` — every
   hex must exist in `colors.md` (allow the audience-block and hue-scale values).
3. Fonts: network tab shows only self-hosted woff2 files; computed `font-family` is
   "Open Sans" on body, headings and buttons; weights used ⊆ {300, 400, 600, 700}.
4. Contrast (axe / Lighthouse ≥ 95 accessibility): no normal-size text in
   `--color-text-muted` or `--color-accent`.
5. Keyboard: skip link appears on first Tab; every control shows the blue focus ring.
6. Dark mode: toggle OS preference — canvas `#15181C`, surface `#1E2227`, text
   `#F4F6F7`, links `#7CC6FD`; audience blocks unchanged.
7. Copy: no "u/uw", no exclamation marks in UI strings (`grep -n '!' i18n/nl.toml`),
   buttons ≤ 24 characters, labels without trailing periods.
8. Screenshots at 375 px, 768 px, 1280 px: header collapses below 990 px; no horizontal
   scroll; hero `<strong>` word is orange; cards have 24 px radius and the navy-tinted
   shadow.
9. Icons: 24 px, labelled or `aria-hidden`; planner legend (if present) follows
   `planner-item-types.md` order.
