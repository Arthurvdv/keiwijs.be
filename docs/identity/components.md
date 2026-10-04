# Components, layout & iconography

Part of the identity guide — see [README.md](README.md). Colours are tokens from
[colors.md](colors.md); type sizes from [typography.md](typography.md).

## 1. Overall feel

- **Flat, white, low-chrome.** Content sits directly on white; sections are separated by
  whitespace and thin `--color-border` rules, not by boxes. Cards with shadows are a
  marketing-page device, not an app device.
- **Compact and aligned.** App-style layouts use a 4 px grid (4 / 8 / 12 / 16 / 24 / 32
  / 48 / 64). Website layouts use the same scale ×1.5 for section spacing.
- **Small radii, one exception.** 4–8 px on controls; 24 px only for large marketing
  cards; full circles for avatars, pills and toggles.
- **Colour sits in icons, not in chrome.** Navigation, panels and buttons are grey/white
  with one blue and one orange; multi-colour appears in icons, illustrations and status
  dots.
- **Friendly empty states.** Every empty list or error screen gets a flat illustration
  and one plain sentence (see §9).

## 2. Spacing & shape tokens

| Token | Value |
|---|---|
| `--space-1` … `--space-9` | 4, 8, 12, 16, 24, 32, 48, 64, 96 px |
| `--radius-sm` | 4 px — inputs, small buttons, menu items, tabs (top corners), checkboxes 3 px |
| `--radius-md` | 6 px — default buttons and inputs on new screens |
| `--radius-lg` | 8 px — flyouts, sidebar nav buttons, website buttons |
| `--radius-xl` | 12 px — boxed frames / dialogs |
| `--radius-card` | 24 px — large marketing cards |
| `--radius-pill` | 999 px — pills, toggles, pagination circles |
| `--radius-round` | 50 % — avatars, radios, calendar day marker |
| `--motion-fast` / `--motion-slow` | 150 ms / 250 ms, `ease-in-out` |
| `--opacity-disabled` | 0.45 |
| `--container` | 1130 px max, 24 px side padding (50 px ≥ 1140 px) |
| `--content` | 800 px max for long-form text |
| Breakpoints | ≤ 767 phone · 768–989 tablet (collapse nav to burger) · ≥ 990 desktop · ≥ 1140 wide |

## 3. Buttons

All buttons: `--text-button` (14 px / 600) on the website, 13 px in app UI; height 28 px
(app) / 40 px (website) / 48 px (hero CTA); horizontal padding 16 px (website) or 8 px
(app); radius `--radius-md`; transition `--motion-fast`; `cursor: pointer`; disabled =
`--opacity-disabled` and no hover. Icon-left buttons use a 16 px icon with 8 px gap.
Labels: sentence case, verb included, no period (see tone-of-voice.md).

| Variant | Background | Text | Border | Hover | Use |
|---|---|---|---|---|---|
| **Primary** | `--color-action` | `--color-text-inverse` | none | `--color-action-hover` | One per view: the main action. |
| **Outline** (default secondary) | `--color-bg` | `--color-text` | 1 px `--color-border` | bg `--color-bg-hover` | Everything that is not the main action. |
| **Text / ghost** | transparent | `--color-text-secondary` | none | text `--color-text` | Cancel, "Filters wissen". |
| **Link button** | transparent | `--color-link-button`, 600 | none | underline | Inline add/create actions, always with a 16 px icon ("+" in `--color-success`, or a blue icon). |
| **Accent CTA** (marketing only) | `--color-accent` | white | 1 px bottom `--color-accent-strong` | `opacity: .9` | Hero and landing-page CTAs, max one per section, 15 px 30 px padding, may carry a right-arrow icon. |
| **Secondary CTA** (marketing) | `#39A6EF` | white | none | `opacity: .9` | Second CTA next to an accent CTA. |
| **Inverse** (on colour blocks) | white | block text colour or `#39A6EF` | none | `opacity: .9` | Buttons on audience blocks. |
| **Success / Warning / Danger** | `--color-success` / `--color-warning` / `--color-danger` | `#262626` / `#262626` / white | none | step-500 hover values | Confirm-type actions where the meaning is the point (danger for destructive confirm). |
| **Neutral** | `--color-neutral-action` | `--color-text` | none | `#91A6C1` | Tertiary in button groups. |
| **Icon button** | transparent | icon colour | none | bg `--color-bg-panel` | 24 px icon in a 32–48 px square hit area; always `aria-label`. |

Example (Dutch, generated):

```html
<button class="btn btn-primary">Selectie bewaren</button>
<button class="btn btn-outline">Annuleren</button>
<a class="btn btn-link"><svg class="icon icon-add"></svg>Kalender toevoegen</a>
```

## 4. Forms

- **Label** above the field, `--text-small` 600 in `--color-text`; required fields get
  a trailing ` *` in `--color-accent`. In dense app forms, label left (fixed 140 px) and
  value right.
- **Input / select / textarea**: height 40 px (website) / 28 px (app), 1 px
  `--color-border`, radius `--radius-md`, padding 8 px 12 px, white background, text
  `--color-text`, placeholder `--color-text-disabled`. Search inputs may use
  `--color-bg-panel` background with a magnifier icon on the left (or right for
  pill-shaped site search).
- **Focus ring** (all controls): `border-color: var(--color-link-button); box-shadow:
  var(--shadow-focus); outline: none` — shown for keyboard focus (`:focus-visible`).
  Checkbox/radio: 1 px ring + `0 0 5px 1px` glow around the box.
- **Checkbox**: 16 px, radius 3 px, 1 px `--color-border`; checked = filled
  `--color-success` with white tick (in app lists) or `--color-action` (on the website).
  **Radio**: 16 px circle. **Toggle**: 32 × 16 px track, radius pill, off = white with
  1 px border, on = `--color-action`.
- **Helper text** under the field: `--text-meta` in `--color-text-secondary`, full
  sentence with period.
- **Validation**: border and message in `--color-danger`; message `--text-small`, placed
  under the field, phrased as a plain statement (e.g. *Je hebt dit veld niet
  ingevuld.*). No icons, no exclamation marks.
- **Tree / checkbox tree** (e.g. "what do you want to share?"): indent 24 px per level,
  row height 32 px, a "select all" row at the top in `--color-link-button`, group rows
  in `--color-link-button` 400 weight, leaf rows with a 24 px icon + label.

## 5. Navigation

- **Top bar**: 48 px high, background in a brand colour (`--color-accent`, or the
  organisation's own colour), white 12–13 px text, items padded 0 12 px with 48 px
  line-height; hover/expanded item = `rgba(0,0,0,.24)` overlay; icon items 48 × 48 with
  24 px white outline icons; a 32 px round avatar + name at the left. No shadow.
- **Website header** (content sites): white, 72–91 px high, logo left, text menu 13 px
  600 `#333333`, active item marked by a 2 px underline in `--color-accent`, hover
  underline `--color-accent-soft`. Collapses to a burger ≤ 989 px.
- **Flyout / dropdown menu**: `--color-bg-flyout`, 1 px `--color-border-strong`, radius
  `--radius-lg`, `--shadow-flyout`, padding 16 px; items 40 px tall with 24 px icon,
  radius `--radius-sm`, hover `--color-bg-panel`; group headings 13 px 700; dividers
  1 px `--color-divider-menu`.
- **Sidebar / rail**: 200–300 px wide, background `--color-bg-sidebar` (or
  `--color-bg-panel` for tree views), items 48 px (nav) or 32 px (tree) tall, 8 px
  radius, selected = **bold label** (and an inset `--shadow-2`), not a filled block.
- **Tabs**: 13–14 px 600, padding 8 px 16 px, inactive `--color-text-muted`, active
  `--color-accent` text + 3 px `--color-accent` bottom border, tab list underlined by
  1 px `--color-border-strong`.
- **Breadcrumb / back**: a 24 px green left-arrow icon button at the top-left of a
  detail screen (app), or a text breadcrumb in `--text-small` on the website.
- **Skip link**: "Spring naar hoofdcontent", `--color-link-button` on white, 14 px 600,
  visible on focus at the top-left, radius 0 0 4 px 4 px.
- **Pagination**: 32 px circles, white, `--color-text-muted`, `--shadow-1`; current =
  `--color-action` with white number.

## 6. Containers

| Pattern | Spec | Use |
|---|---|---|
| **Section (default)** | no box; title + 1 px `--color-border` rule; 24–48 px vertical spacing | Almost everything. |
| **Section title with rule** | h3 as `display:flex; align-items:center; gap:12px` with `::after { flex:1; height:1px; background: var(--color-border) }` | Sub-sections in forms, settings, lists. |
| **Boxed widget** | white, radius `--radius-md`, `0 1px 3px rgba(0,0,0,.25)`, header bar `--color-bg-widget-header` 40 px with 13 px 600 title and 1 px `--color-border` bottom | Dashboard tiles, help portals. |
| **Marketing card** | white, radius `--radius-card`, padding 32 px, `--shadow-card`, no border; 2- or 3-up grid with 24–40 px gap; optional 96 px illustration top-left | Landing pages. |
| **Info banner** | `--color-info-soft` bg, 1 px `#B0DEFF`, radius `--radius-lg`, padding 16 px 24 px, 16 px ⓘ icon in `--color-info`, text `--text-small`/`--text-body` in `--color-text`; may end with a link | Explaining a feature before a form. |
| **Alert (success/warning/danger)** | same shape with the matching soft tokens; danger text `--color-text-error` for the first sentence | Feedback after an action. |
| **Dialog** | 650 px wide (550 px for confirms), white, radius `--radius-xl`, title `--ui-title-accent` or 18 px 700, actions right-aligned (primary last), close "×" icon top-right | Confirmations, short forms. |
| **Side panel** | slides in from the right, 560–600 px, white, title `--ui-title` 24 px 300 muted, close "×" top-right, form inside with left labels | Edit-in-context ("Profiel wijzigen"-type screens). |
| **Audience block** | full-bleed background from colors.md §3, centred 48 px title + 24 px paragraph in the block's text colour, product image or illustration, 64–96 px vertical padding | Landing pages only. |
| **Footer** | `--color-footer-bg`, 4–5 columns, `--text-overline` titles, 13 px `--color-footer-text` links; below it a `--color-socket-bg` strip with 11 px legal text | Every page of a website. |

## 7. Lists & tables

- **Table**: header row 13 px 700 `--color-text` on white with 1 px `--color-border`
  bottom; rows 40 px (website) / 32 px (app); cell padding 8 px 12 px; zebra striping is
  **not** used; row hover `--color-bg-panel`; selected row `--color-selected`; numbers
  right-aligned with tabular figures; long cells truncated with `…` and a `title`.
- **Rich list row** (messages, items with avatars): 64 px tall, 32 px round avatar,
  primary 14 px (600 when unread) + secondary 13 px in `--color-text-muted`, timestamp
  right; unread = 3 px `--color-danger` bar on the left edge + primary text in
  `--color-danger`; hover reveals 24 px action icons on the right.
- **Definition rows** (settings): 24 px icon, bold title, one-line description in
  `--ui-small`, arranged in a 2–3 column grid.
- **Calendar month**: 7 columns, day letters `ma di wo do vr za zo` lowercase, Monday
  first, today = `--color-action` circle with white number, days with items get a 6 px
  dot in the item's category colour.

## 8. Badges, chips, counters

- **Counter badge** (unread): pill, `--color-danger` bg, white 11 px 700, min 16 px,
  anchored top-right of an icon.
- **Status badge**: pill, soft token background with matching dark text, 11–12 px 600,
  padding 2 px 8 px. Neutral badge: `--color-neutral-action` / `--color-text`.
- **Filter chip**: outline, 28 px tall, radius pill, 1 px `--color-border`, selected =
  `--color-selected` bg + `--color-action` text; a "wissen" text button clears all.
- **Category dot**: 8–12 px circle in a hue-500 colour next to a label (calendars,
  tags).
- **Label flag**: 24 px flag icon in green / yellow / red / blue for user-assigned
  labels.

## 9. Empty states, errors, loading

- **Empty state**: centred, 128 px flat illustration of the missing object (folder,
  pencil cup, play bubble, tag), then one sentence in 14 px `--color-text`, then an
  optional link button with a green "+" icon. Sentence pattern: *Er zijn (nog) geen …*
  — soften with *(nog)* when the user can create items.
- **No-access / not-found page**: centred 360 × 232 px friendly character illustration
  (e.g. a sad dinosaur holding a lock) + 12–14 px 600 `--color-text-muted` text in two
  sentences: what happened, then what to do next.
- **Loading**: skeleton blocks `#ECECEC` with a `#F8F8F8` shimmer, radius
  `--radius-sm`; no spinners for lists.
- **Toast** (derived): bottom-centre, dark `#262626` bg, white 13 px text, radius
  `--radius-lg`, 4 s auto-dismiss; success/danger add a 16 px coloured icon.

## 10. Iconography

Three icon layers, each with a fixed job:

| Layer | Style | Size | Colour | Where |
|---|---|---|---|---|
| **UI glyphs** | monochrome, outline, 1.5–2 px stroke, rounded joins (Lucide and Heroicons fit) | 16 / 24 | white on top bar; `--color-text-muted` for chevrons; `--color-link-button` for actionable glyphs | top bar, chevrons, close, copy, search, bell, help, log-out |
| **Action icons** | flat filled, single colour | 16 / 24 | green `--color-success` for add / reply / back / favourite; violet `--color-icon-settings` for settings gear; blue `--color-info` for info | link buttons, toolbars, trees |
| **Object / module icons** | flat, filled, multi-colour, soft 2-tone shading, no outlines, rounded corners | 24 / 48 / 128 | own colours per object (see colors.md §5 and planner-item-types.md) | module tiles, list rows, trees, empty states |

Rules: icons always have an accessible name or are `aria-hidden` next to a text label;
never recolour an object icon to match a theme; never mix outline UI glyphs with filled
object icons in the same row at the same size unless the glyph is purely decorative;
icon-only buttons need a tooltip (`title`) in the form of a noun phrase (*Nieuw item
aanmaken*).

## 11. Illustration

Flat vector, filled shapes, soft 2-tone shading, no outlines, rounded corners;
subjects are everyday school-life objects and friendly characters (a small orange robot
mascot, a green dinosaur, children and parents in simple clothes). Backgrounds are
transparent or a very light tint. Photography is used only for real context (a hand
holding a phone, a team photo) and never as a decorative hero. App screenshots are shown
inside simple device frames on audience blocks.

## 12. Accessibility baseline

- WCAG 2.2 AA: 4.5:1 for text < 24 px (19 px bold), 3:1 for larger text and UI
  boundaries; see contrast notes in colors.md. `--color-text-muted` and
  `--color-accent` are therefore large-text/UI only.
- Visible focus for every interactive element (the blue ring).
- Hit areas ≥ 24 × 24 px (prefer 32–48).
- Skip link, landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page.
- `prefers-reduced-motion`: disable the 150/250 ms transitions.
- Provide a "larger text" mode hook (`html.text-lg` bumps body to 18 px) when building
  app-style screens.
