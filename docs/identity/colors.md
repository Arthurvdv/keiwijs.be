# Colors

Part of the identity guide — see [README.md](README.md) for how the files fit together.
This file is the **single source of truth for colour tokens**. Other files reference
tokens by name (`--color-accent`), never by raw hex, so that a palette change only
happens here.

## 1. Character of the palette

The palette is **light, friendly and functional**. White surfaces carry the content;
a single warm **orange-red accent** gives the brand its energy; a **calm blue** does the
interactive work (buttons, links, focus); and a small set of **saturated signal
colours** (green / yellow / red) is reserved for meaning. Greys are slightly cool
(navy-tinted), which keeps large white areas from looking flat. Colour is used
sparingly in chrome and generously in icons and illustrations.

Rules of thumb for an agent applying this:

- One accent per screen. Orange marks *what matters* (emphasised words in a title, the
  active tab, a key number). It is not a background for large areas except the hero.
- Blue means *you can click this*. Primary buttons, links, focus rings and selection
  states are blue; nothing decorative is blue.
- Green / yellow / red only ever mean success / caution / danger. Never use them to
  decorate.
- Greys do the structure: borders, dividers, muted text, secondary panels.
- Pastel "audience blocks" (green / yellow / blue / orange) are the only large colour
  fields, and each has its own fixed dark text colour.

## 2. Core tokens (light theme)

All values uppercase hex. "Use" tells the agent where the token is allowed.

### Brand & accent

| Token | Hex | Use |
|---|---|---|
| `--color-accent` | `#FF520E` | Brand accent: emphasised words in headings, active tab text + underline, hero background, key stats. Large text (≥ 24 px, or ≥ 19 px bold) and non-text UI only — contrast on white is 3.25:1, so **never body text**. |
| `--color-accent-strong` | `#D03808` | Darker accent for 1 px borders/underlines on accent surfaces, pressed state. |
| `--color-accent-soft` | `#FF7337` | Accent hover (e.g. nav underline on hover). |
| `--gradient-brand` | `linear-gradient(180deg, #FF750E 0%, #F40700 100%)` | Logo-mark style square, favicon, app icon. Not for UI surfaces. |

### Interactive (blue family)

| Token | Hex | Use |
|---|---|---|
| `--color-action` | `#3A70E6` | Primary button background (white text, 4.53:1). |
| `--color-action-hover` | `#2564CF` | Primary button hover / pressed. |
| `--color-link` | `#0033CC` | Inline text links in running text (8.95:1). No underline at rest, underline on hover. |
| `--color-link-button` | `#278DD7` | Icon-plus-label "link buttons" (e.g. "+ Profiel toevoegen"), skip-links. Also the **focus ring** colour. Large/bold text or icons only (3.57:1). |
| `--color-info` | `#1B96F1` | Informational icons (ⓘ), info banners' icon, "blue" module icons. |
| `--color-selected` | `#DCEBFA` | Selected row / selected list item background. |
| `--color-unread` | `#DCEDFF` | Unread / new row background. |

### Status

| Token | Hex | Hover (`--color-<name>-hover`) | Text on it | Use |
|---|---|---|---|---|
| `--color-success` | `#57D31A` | `#2EB42F` | `#262626` (7.74:1) | Success button/badge, "add" icons, positive state. |
| `--color-warning` | `#FFCC00` | `#D2B224` | `#262626` (10.01:1) | Caution badge/button, warning icon. |
| `--color-danger` | `#E30000` | `#D20000` | `#FFFFFF` (4.92:1) | Destructive button, error text (`--color-text-error`), unread indicator bar. |
| `--color-neutral-action` | `#D8E0E8` | `#91A6C1` | `#262626` | Neutral/tertiary button background. |

Soft surfaces for alerts and badges. Each soft token has two companions:
`--color-<name>-soft-border` and `--color-<name>-soft-text`.

| Token | Hex | `-soft-border` | `-soft-text` |
|---|---|---|---|
| `--color-info-soft` | `#E6F5FF` | `#B0DEFF` | `#022E4D` |
| `--color-success-soft` | `#EAFCEA` | `#BCF6BC` | `#0D450E` |
| `--color-warning-soft` | `#FFFCE8` | `#FFF4B7` | `#4D4409` |
| `--color-danger-soft` | `#FFE6E6` | `#FFACAC` | `#4D0000` |

### Text

| Token | Hex | Use |
|---|---|---|
| `--color-text` | `#262626` | Body text, labels, default headings (15.1:1). |
| `--color-text-secondary` | `#757575` | Secondary text, helper lines, meta that must stay readable (4.61:1 — AA for normal text). |
| `--color-text-muted` | `#868686` | Large light page titles (24 px weight 300), captions, timestamps, inactive tabs (3.64:1 → large text only). |
| `--color-text-disabled` | `#CCCCCC` | Disabled labels, placeholders only. Never for information. |
| `--color-text-error` | `#E30000` | Validation messages. |
| `--color-text-inverse` | `#FFFFFF` | Text on accent, action, danger and dark footer surfaces. |

### Surfaces & borders

| Token | Hex | Use |
|---|---|---|
| `--color-bg` | `#FFFFFF` | Page and card background. |
| `--color-bg-canvas` | `#EEEEEE` | App-style canvas behind white panels (dashboards, admin-like pages). |
| `--color-bg-alt` | `#F4F6F7` | Alternating light section on content pages, widget headers' lighter variant. |
| `--color-bg-sidebar` | `#F3F4F7` | Sidebar / navigation rail background. |
| `--color-bg-panel` | `#F1F1F1` | Secondary panels (tree views), search input background, **row hover**. |
| `--color-bg-hover` | `#F5F5F5` | Outline-button hover. |
| `--color-bg-flyout` | `#FEFEFE` | Dropdown / flyout menus. |
| `--color-bg-widget-header` | `#DBE0E6` | Header bar of boxed widgets. |
| `--color-border` | `#CCCCCC` | Default 1 px border for inputs, buttons, dividers, tab baselines. |
| `--color-border-strong` | `#868686` | Flyout outline, emphasised dividers. |
| `--color-border-subtle` | `#E1E1E1` | Section dividers on marketing-style pages. |
| `--color-divider-menu` | `#808080` | Dividers inside flyout menus. |
| `--color-footer-bg` | `#333333` | Footer background. |
| `--color-footer-bg-deep` | `#222222` | Footer form controls, second footer tier. |
| `--color-footer-text` | `#AAAAAA` | Footer text and links (5.44:1 on `#333333`); link hover `#FFFFFF`. |
| `--color-footer-border` | `#555555` | Footer dividers. |
| `--color-footer-heading` | `#919191` | Footer column titles (uppercase, 1 px letter-spacing). |
| `--color-socket-bg` | `#111111` | Bottom legal strip. |
| `--color-socket-text` | `#EEEEEE` | Text in the legal strip. |

### Shadows

Shadows are **navy-tinted** (`#002A58`), never pure black, which is what makes elevated
white cards look soft rather than dirty.

| Token | Value | Use |
|---|---|---|
| `--shadow-1` | `0 0 1px rgba(0,42,88,.08), 0 1px 2px rgba(0,42,88,.08)` | Subtle lift (inputs, chips). |
| `--shadow-2` | `0 0 2px rgba(0,42,88,.08), 0 1px 4px rgba(0,42,88,.08), 0 2px 8px rgba(0,42,88,.08)` | Cards in app-style layouts, active sidebar item (inset). |
| `--shadow-card` | `0 0 24px rgba(0,42,88,.30)` | Large rounded marketing cards (24 px radius). |
| `--shadow-flyout` | `0 4px 16px rgba(0,0,0,.50)` | Dropdown menus. |
| `--shadow-focus` | `0 0 5px #278DD7` | Together with a 1 px `#278DD7` border = focus ring. |

## 3. Audience / section blocks

Large full-width colour blocks used on landing pages to separate audiences or themes.
Each block has a **fixed dark text colour of the same hue**; do not put white or
`--color-text` on them (except on orange).

| Block | Background | Text / headings | Contrast |
|---|---|---|---|
| Green | `#98CC2C` | `#0D450E` | 5.87:1 |
| Yellow | `#F7C447` | `#4D4409` | 6.03:1 |
| Blue | `#76BFF7` | `#022E4D` | 7.04:1 |
| Orange | `#FF520E` | `#FFFFFF` | 3.25:1 → headings ≥ 24 px and short lead text ≥ 19 px bold only |
| Deep green (alt) | `#65BD0B` | `#0D450E` | — |
| Cyan (hero alt) | `#00B8FC` | `#FFFFFF` | large text only |

Buttons on a coloured block are **inverse**: white background, text in the blue
`#39A6EF` (marketing secondary) or in the block's dark text colour.

## 4. Extended hue scales

Use these when a token above does not cover the need (charts, illustrations, labels,
calendar categories). Step 500 is the base; 100 is the lightest tint, 900 the darkest
shade. Pair *100 background with *900 text, or *500 background with white/`#262626`
text depending on lightness.

| Hue | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 |
|---|---|---|---|---|---|---|---|---|---|
| Blue | `#E6F5FF` | `#B0DEFF` | `#7CC6FD` | `#4AAEF8` | `#1B96F1` | `#127CCB` | `#0B63A4` | `#054879` | `#022E4D` |
| Jeans (action blue) | `#E9F1FF` | `#B8D3FF` | — | — | `#327BF6` | `#2564CF` | `#1A4EA6` | — | `#09234D` |
| Green | `#EAFCEA` | `#BCF6BC` | `#8FED90` | — | `#3BD63D` | `#2EB42F` | `#219023` | — | `#0D450E` |
| Yellow | `#FFFCE8` | `#FFF4B7` | `#FFEB88` | — | `#FFD531` | `#D2B224` | `#A68E19` | — | `#4D4409` |
| Red | `#FFE6E6` | `#FFACAC` | `#FF7373` | — | `#FF0000` | `#D20000` | `#A60000` | — | `#4D0000` |
| Steel (cool grey) | `#F4F6F7` | `#DBE0E6` | `#C2CBD4` | `#A9B5C2` | `#91A0AF` | `#798C9E` | `#677A8D` | `#52606F` | `#343F49` |
| Silver (neutral grey) | `#F8F8F8` | `#F4F4F4` | `#ECECEC` | `#E5E5E5` | `#DDDDDD` | `#C9C9C9` | `#B7B7B7` | `#9D9D9D` | `#7C7C7C` |
| Dolphin (lavender grey) | `#F3F4F7` | `#D9DBE5` | `#BFC3D2` | — | `#8C92AC` | — | `#5A5E71` | — | `#292B35` |
| Black | `#E9E9E9` | `#B9B9B9` | `#888888` | `#585858` | `#272727` | — | — | — | `#141414` |

Additional base (500) hues available for categorical colour (calendar categories,
tags, chart series). Pick in this order for up to eight series so neighbours stay
distinguishable: `#1B96F1` blue · `#FF7112` orange · `#3BD63D` green · `#9559CD`
purple · `#FFD531` yellow · `#FF2E97` pink · `#00B4E2` aqua · `#B26714` brown.

Full list of base hues: aqua `#00B4E2`, blue `#1B96F1`, brown `#B26714`, grass
`#B2EB31`, green `#3BD63D`, lavender `#D956E0`, mint `#58E09E`, olive `#2B8114`, orange
`#FF7112`, pink `#FF2E97`, purple `#9559CD`, red `#FF0000`, tangerine `#FF9301`, violet
`#6046FF`, yellow `#FFD531`, lemon `#FFF36D`, emerald `#009B77`, sage `#9CAF88`, ocean
`#68CBCF`, jeans `#327BF6`, jazz `#7B50E6`, candy `#EC42BC`, dynamite `#D9340A`,
watermelon `#FF174C`, salmon `#FF8674`, hazelnut `#D5A372`, heaven `#B1C9E8`, night
`#8186BD`.

## 5. Illustration palette

Flat vector illustrations and multi-colour icons draw from the hue scales above plus a
skin/hair set. Typical combinations seen in the icon set:

- Objects: yellow `#FFD531` with shade `#D2B224` / `#A68E19`; blue `#1B96F1` with shade
  `#0D6FE0`; green `#57D31A` / `#3BD63D` with shade `#2EB42F`; red `#FF0000` with shade
  `#A60000`; orange `#FF9301` with shade `#A66100`.
- Neutral objects (paper, houses, frames): steel `#ECF0F4` / `#D8E0E8` / `#91A0AF` /
  `#798C9E` / `#52606F`.
- People: skin `#FBBB69` / `#F2B566` / `#A06C23`, hair `#7B4F12` / `#52606F` /
  `#D25D00`, clothing blue `#0D6FE0` / `#1A96F1`, green `#57D31A`.
- Brand mascot / playful accents: orange `#DD8523`, green `#759D28`, cream `#FCF9DD`.
- Fixed single-colour action icons: add / reply / back / favourite in `--color-success`,
  settings gear in violet `--color-icon-settings` = `#7A71BB`, info in `--color-info`.

Icon- and illustration-internal colours (shades inside one icon) are **descriptive, not
tokens**: they may appear in SVG files but never in CSS.

## 6. Dark theme (derived)

The source material is light-only; this dark theme is **derived** so the identity can be
applied where a dark mode is expected. It keeps the same hue logic: cool dark greys
(from the steel/black scales), the same orange accent, lighter tints of the blue family
for links, and *300-step tints for status text. All pairs below meet WCAG AA.

| Token | Dark value | Notes |
|---|---|---|
| `--color-bg` | `#1E2227` | Surface (cards, panels). |
| `--color-bg-canvas` | `#15181C` | Page canvas. |
| `--color-bg-alt` | `#232830` | Alternating section. |
| `--color-bg-sidebar` | `#1A1E23` | |
| `--color-bg-panel` / hover | `#272C33` | Row hover, trees. |
| `--color-bg-flyout` | `#272C33` | Flyouts, with `--shadow-flyout`. |
| `--color-border` | `#3A4149` | |
| `--color-border-strong` | `#52606F` | |
| `--color-border-subtle` | `#2E343B` | |
| `--color-text` | `#F4F6F7` | 14.8:1 on surface. |
| `--color-text-secondary` | `#A9B5C2` | 7.7:1 |
| `--color-text-muted` | `#91A0AF` | 6.0:1 |
| `--color-text-disabled` | `#52606F` | |
| `--color-accent` | `#FF520E` | 4.9:1 on surface → fine for titles/tabs; for inline emphasised words use `#FF7112` (5.8:1). |
| `--color-action` / hover | `#3A70E6` / `#2564CF` | Unchanged from light; white text stays 4.5:1+ (a lighter hover would drop below AA). |
| `--color-link` | `#7CC6FD` | 8.6:1 |
| `--color-link-button` / focus | `#4AAEF8` | 6.6:1 |
| `--color-selected` | `#0B3A66` | Selected row (derived from blue-800). |
| `--color-success` text / fill | `#8FED90` / `#3BD63D` | Fill keeps `#262626` text. |
| `--color-warning` text / fill | `#FFEB88` / `#FFCC00` | |
| `--color-danger` text / fill | `#FF7373` / `#E30000` | |
| Soft surfaces (bg / border / text) | info `#0B2A44` / `#0B63A4` / `#B0DEFF` · success `#0D2E12` / `#219023` / `#BCF6BC` · warning `#332D0A` / `#A68E19` / `#FFF4B7` · danger `#3A0F0F` / `#A60000` / `#FFACAC` | Alerts and badges; text ≥ 7:1 on its surface. |
| `--color-footer-bg` / `-deep` | `#0F1114` / `#0A0B0D` | Footer becomes the darkest band. |
| `--color-socket-bg` | `#050607` | |
| Shadows | same values, opacity ×2 | Shadows read weaker on dark; `--shadow-card` becomes `0 0 24px rgba(0,0,0,.6)`. |

Audience blocks keep their light-theme values in dark mode (they are brand surfaces,
not UI surfaces); surround them with the dark canvas.

## 7. Do / don't

- Do keep ≥ 90 % of any screen white/grey; the palette works by restraint.
- Do use the status soft surfaces for alerts, with the matching dark text.
- Don't tint text orange for emphasis in paragraphs — use bold (`600`) in `--color-text`;
  orange emphasis is a heading device.
- Don't introduce new blues; every blue in this file has a job.
- Don't use pure black `#000000` for text or borders.
- Don't add gradients to UI; the only gradient is the brand mark.
