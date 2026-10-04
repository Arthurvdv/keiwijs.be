# Typography

Part of the identity guide — see [README.md](README.md). Colour values are referenced
as tokens from [colors.md](colors.md).

## 1. Character

Humanist sans-serif, **light and airy at the top, compact and matter-of-fact below**.
The signature move is a **large, light-weight (300), grey page title** followed by
regular-weight dark body text — titles feel calm rather than loud. Emphasis is done
with weight (600/700) or with a single orange-accented word in a heading, never with
italics, uppercase or letter-spacing (the one exception: small uppercase footer column
titles). Everything is **sentence case**.

## 2. Typeface

| Role | Family | Weights | Notes |
|---|---|---|---|
| Everything (UI, body, headings) | **Open Sans** | 300, 400, 600, 700 | Self-host (woff2); Open Sans is open-licensed (OFL). Load only these four weights; no italics needed. |
| Fallback stack | `"Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif` | | |
| Optional display alternative | Proxima Nova (licensed) | 300, 400, 600, 700 | Only if a licence is available; metrics are close to Open Sans. Never mix the two on one page. |
| Monospace (code, URLs in docs) | `ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace` | 400 | Derived — the source has no code styling. |

CSS: `font-family: var(--font-sans); -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;`

## 3. Scale — website (default for Hugo and other content sites)

Root `16px`. Line-heights are unitless. Headings use `--color-text` unless noted.

| Token | Size | Line-height | Weight | Colour | Use |
|---|---|---|---|---|---|
| `--text-display` | 3rem (48 px) | 1.1 | 300 | `--color-text` or `--color-accent` | Hero / landing title. One per page. Can be wrapped in `<strong>` → 700 in accent colour for the "shouted" marketing variant. |
| `--text-h1` | 2.5rem (40 px) | 1.2 | **300** | `--color-text-muted` (`#868686`) | Page title. The light grey is intentional; it must be ≥ 24 px to pass contrast. Dark text is allowed when the title carries essential information on its own. |
| `--text-h2` | 1.75rem (28 px) | 1.3 | 300 | `--color-text` (accent allowed) | Section titles. |
| `--text-h3` | 1.125rem (18 px) | 1.4 | **700** | `--color-text` | Sub-section / card titles. Often followed by a 1 px `--color-border` rule that fills the remaining line (see components.md "Section title with rule"). |
| `--text-h4` | 1rem (16 px) | 1.4 | 600 | `--color-text` | Minor headings, list group titles. |
| `--text-lead` | 1.25rem (20 px) | 1.55 | 400 | `--color-text` | Intro paragraph under a display title (landing pages: up to 24 px / 1.5). |
| `--text-body` | 1rem (16 px) | 1.6 | 400 | `--color-text` | Running text. Max line length 70–75 characters (`max-width: 65ch`). |
| `--text-small` | 0.875rem (14 px) | 1.5 | 400 | `--color-text-secondary` | Helper text, table cells, form hints. |
| `--text-meta` | 0.75rem (12 px) | 1.4 | 400 | `--color-text-muted` | Timestamps, captions, footnotes, badges. |
| `--text-button` | 0.875rem (14 px) | 1 | 600 | — | Buttons and tabs. |
| `--text-nav` | 0.8125rem (13 px) | 1 | 600 | — | Top navigation items. |
| `--text-overline` | 0.8125rem (13 px) | 1.2 | 600, uppercase, `letter-spacing: 1px` | `--color-footer-heading` | Footer column titles only. |

Spacing after headings: `margin: 0 0 .5em`; before h2/h3 when following content:
`margin-top: 2em` / `1.5em`. Paragraph spacing `1em`.

## 4. Scale — compact application UI

For dashboards, admin pages, dense lists and anything that behaves like an app rather
than a document. Root stays 16px in CSS, but sizes are smaller and line-heights are
fixed in px to keep rows aligned.

| Token | Size | Line-height | Weight | Colour | Use |
|---|---|---|---|---|---|
| `--ui-title` | 24 px | 32 px | 300 | `--color-text-muted` | Screen title in a 53 px header row. |
| `--ui-title-accent` | 16 px | 22 px | 300 | `--color-accent` | Secondary screen title / section header in accent. |
| `--ui-section` | 13 px | 18 px | 700 | `--color-text` | Section label with trailing rule. |
| `--ui-body` | 13 px | 18 px | 400 | `--color-text` | List rows, labels, menus. |
| `--ui-body-lg` | 14 px | 18 px | 400 (600 when unread/selected) | `--color-text` | Row primary text (e.g. sender name, item title). |
| `--ui-small` | 12 px | 16 px | 400 | `--color-text-muted` | Row secondary text, descriptions. |
| `--ui-xs` | 11 px | 16 px | 400 | `--color-text-muted` | Chips, counters. Minimum size anywhere. |
| `--ui-button` | 13 px | 18 px | 600 (400 for flat primary) | — | Buttons 28 px tall. |
| `--ui-input` | 13–16 px | — | 400 | `--color-text` | Inputs; 16 px on touch-first forms to avoid mobile zoom. |

## 5. Rules

- **Weights carry hierarchy**: 300 for big titles, 400 for text, 600 for interactive
  labels and selected states, 700 for small structural headings and "unread/important"
  row text. Never use 500 or 800.
- **Sentence case everywhere**: headings, buttons, menu items, table headers. No Title
  Case; no ALL CAPS except `--text-overline`.
- **Emphasis in body text** = `<strong>` at 600 in `--color-text`. **Emphasis in
  headings** may be `<strong>` coloured `--color-accent` on one or two key words.
- No italics for emphasis (reserve `<em>` for titles of works, foreign words).
- No letter-spacing adjustments except the overline. No text-shadow.
- Numbers: tabular figures in tables (`font-variant-numeric: tabular-nums`).
- Links in running text: `--color-link`, no underline at rest, underline on hover and
  focus; links are never bold just because they are links.
- Labels (menu items, buttons, table headers) have **no trailing period**; full
  sentences (helper text, empty states, errors) **do**.
- Dutch typographic details: use the proper ellipsis character `…`, curly apostrophe
  `’` (e.g. *to-do’s*), accented emphasis is allowed in marketing copy (*hét*, *én*) but
  not in UI chrome; dates in prose as "9 januari 2026", in lists as `2026-01-09 18:00`
  (see tone-of-voice.md §6).
- Minimum body size on the website is 16 px; minimum anywhere is 11 px.

## 6. Example (Dutch, generated)

```html
<h1 class="page-title">Mijn kalender</h1>            <!-- 40px / 300 / #868686 -->
<p class="lead">Kies wat je wil zien en bewaar je selectie. Je kan ze later altijd aanpassen.</p>
<h2>Wat deel je?</h2>                                 <!-- 28px / 300 -->
<h3>Lesvrije dagen</h3>                               <!-- 18px / 700 + rule -->
<p>Vakanties en pedagogische studiedagen staan standaard aan. <strong>Zet ze uit</strong> als je ze al in een andere kalender hebt.</p>
<small>Laatst bijgewerkt op 9 januari 2026</small>    <!-- 12px / #868686 -->
```

Marketing variant of a display title with an accented word:

```html
<h1 class="display"><strong>Samen</strong> op de hoogte, zonder losse briefjes.</h1>
```
