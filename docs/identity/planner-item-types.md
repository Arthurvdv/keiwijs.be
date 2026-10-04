# Planner item types & their icons

Part of the identity guide — see [README.md](README.md). This file captures the
**taxonomy of items in a school planner/calendar feed** and how each type is
represented visually, so that any surface (website, calendar legend, filter UI,
e-mail digest) shows the same type with the same name, icon and colour.

Icons are **described, not supplied**: the originals are a proprietary icon set. Each
row names an open-licensed equivalent (Lucide glyph or Unicode emoji rendered with
Twemoji / Noto Color Emoji) that reads the same at a glance. Where you draw your own,
follow the style in components.md §10–11 (flat, filled, 2-tone, no outlines, 24 px
grid).

> **Feed reality.** The parent-facing Smartschool iCal export (what the Keiwijs planner
> reads) carries **no item-type field**. In practice it only contains school-free days
> (description `Deelnemers: Iedereen`) and appointments on the school calendar
> (`Kalender: …`). The published feed therefore picks title icons from user-editable
> keyword rules (`planner/ssfilter/icons.py`), not from this taxonomy, and uses emoji
> because calendar apps cannot show images in titles.

## 1. Structure

The planner exposes items in a **three-level tree**. A "share / filter" UI shows it as
a checkbox tree with a *Select all* row at the top (see components.md §4 "Tree").

```
Select all
├─ Open slots (still to be planned)
├─ Activities
├─ Routines
├─ Lesson series
├─ Lesson sheets
├─ Assignments
├─ Own to-dos
├─ School-free days
├─ School events
├─ Appointments                      ← group (no icon)
│   ├─ Personal calendar
│   └─ <School calendar>             ← one per school the user belongs to
│       └─ <Course or group calendar> ← one per course/group, coloured dot
└─ Generic slot types                ← group (no icon), school-configurable list
    ├─ Newcomers' language class
    ├─ Individually adapted curriculum class
    ├─ Support hour
    ├─ Childcare during meetings
    ├─ Meeting
    ├─ Study hall
    ├─ Supervision
    └─ Waiting hour
```

Rules for the agent:

- Levels 1 items are **fixed**; the *Appointments* children depend on the user's
  memberships; the *Generic slot types* list is **defined by the school** and may differ
  per school — treat it as data, not as code.
- Group rows (*Appointments*, *Generic slot types*) have **no icon**, are rendered in
  `--color-link-button` at weight 400 and toggle all their children.
- Every leaf has exactly one 24 px icon, left of its label, 8 px gap.
- Order is meaningful; keep the order above in menus, legends and settings.

## 2. Type catalogue

Columns: Dutch label (the user-facing name, nl-BE) · suggested machine key · meaning ·
icon description · dominant hex · category colour token for dots/badges · open
equivalent. The "Hex" column describes the icon artwork (for redrawing or matching);
these are **not CSS tokens** — only the category colours are, and they all come from
`colors.md` §4.

### 2.1 Fixed types

| Dutch label | Key | Meaning | Icon (description) | Hex | Category colour | Open equivalent |
|---|---|---|---|---|---|---|
| Lege momenten (nog in te plannen) | `open-slot` | Placeholder slots in a timetable that have not been filled yet. | A square "viewfinder" frame: four thick rounded corner brackets in grey with a small dot in the centre; monochrome. | `#798C9E` | steel-500 `#91A0AF` | Lucide `scan` (add a centre dot) · emoji ⬚ not recommended |
| Activiteiten | `activity` | A planned lesson activity / timetable block. | A bright green sheet of paper with a folded top-right corner in a lighter green; no lines. | `#3BD63D`, fold `#8FED90` | green-500 `#3BD63D` | Lucide `file` filled green · emoji 📄 (recolour not possible → prefer Lucide) |
| Routines | `routine` | Recurring routine blocks (the same thing every day/week). | A pyramid/triangle made of five horizontal rainbow bands, top to bottom: red, orange, yellow, green, blue. Flat, no shading. | `#FF0000`, `#FF7000`, `#FFCC00`, `#57D31A`, `#1A96F1` | neutral; use multi-colour icon only | Lucide `triangle` with CSS bands, or a custom 5-band SVG · emoji 🔺 (single colour, weaker) |
| Lessenreeksen | `lesson-series` | A series of linked lessons (a learning path). | A blue S-shaped route: a thick rounded path with three hollow circles (start, middle, end) along it; monochrome blue. | `#1B96F1` | blue-500 `#1B96F1` | Lucide `route` or `waypoints` · emoji 🧭 (loosely) |
| Lesfiches | `lesson-sheet` | Lesson sheets / lesson preparation documents. | A light grey document with a folded corner carrying a checklist: three bullets (red, green, yellow) each with a grey line. | paper `#D8E0E8`, lines `#91A0AF`, fold `#717F8F`; dots `#FF0000` `#57D31A` `#FAD00A` | steel-300 `#C2CBD4` | Lucide `clipboard-list` / `list-checks` · emoji 📋 |
| Opdrachten | `assignment` | Assignments, homework and tasks set by a teacher. | Two flags on one pole area: a large red flag in front on a dark-red pole and a smaller yellow flag behind it on an olive pole. | red `#FF0000` / `#A60000`, yellow `#FFD531` / `#A68E19` / `#796A10` | red-500 `#FF0000` | Two Lucide `flag` glyphs offset, red + yellow · emoji 🚩 + 🏳️ (approximate) |
| Eigen to-do's | `todo` | The user's personal to-dos. | A single orange flag on a brown pole, waving to the right. | `#FF9301`, pole `#A66100` | tangerine-500 `#FF9301` | Lucide `flag` filled orange · emoji 🚩 recoloured orange |
| Lesvrije dagen | `school-free-day` | Days without lessons: holidays, pedagogical study days, optional leave days. | A sun: a yellow disc with a ring of pointed orange rays. | rays `#FF7100`, disc `#FAD00A` | yellow-500 `#FFD531` | Lucide `sun` filled · emoji ☀️ / 🌞 |
| Schoolactiviteiten | `school-event` | School-wide events (school party, trips, open days). | Two theatre masks overlapping: a red smiling mask in front-left, a blue sad mask behind-right. | red `#E52121`, blue `#1A96F1` / `#0D6FE0` | red-500 `#FF0000` or blue-500 — pick one per product and keep it | Lucide `drama` · emoji 🎭 |

### 2.2 Appointments (group `appointments`)

| Dutch label | Key | Meaning | Icon (description) | Hex | Category colour | Open equivalent |
|---|---|---|---|---|---|---|
| Persoonlijke kalender | `personal-calendar` | The user's own appointments. | Two adult figures from the chest up: a woman with orange-red hair in a dark blue top in front, a man with brown hair, white shirt and blue tie behind; flat with soft shading. | skin `#FBBB69` / `#F2B566` / `#A06C23`, hair `#D25D00` / `#7B4F12`, clothes `#0A5DBC` / `#1A96F1` / `#52606F`, shirt `#ECF0F4` | jeans-500 `#327BF6` | Lucide `users` · emoji 👥 / 🧑‍💼 |
| *(School name)* | `school-calendar` | The school's shared calendar; label = the school's name. | A house with a steep red roof, pale grey-lavender walls and a red door; flat. | roof/door `#FF0000`, walls `#DDDDEA` | red-500 `#FF0000` | Lucide `house` with red roof fill · emoji 🏫 / 🏠 |
| *(Course or group name)* | `group-calendar` | Sub-calendar of one course/class/group; label = the group's name. | A plain filled circle in the group's own colour (`currentColor`), e.g. yellow-green for a parents' newsletter group. | example `#B2EB31` (grass-500) | the group's colour | CSS circle; emoji 🟢 / 🟡 / 🔵 by colour |

Group colours come from the hue scales in colors.md §4 (step 500). Assign in the
categorical order given there so neighbouring groups differ.

### 2.3 Generic slot types (group `generic-types`, school-configurable)

These are timetable slot kinds a school defines itself. The icons below are the ones
used by this school's configuration; other schools may add or remove entries. Most are
standard emoji, so **render them with an emoji font (Twemoji/Noto) at 24 px** instead of
drawing them.

| Dutch label | Key | Meaning | Icon (description) | Hex | Open equivalent |
|---|---|---|---|---|---|
| Anderstalige nieuwkomers | `newcomer-class` | Reception/language class for pupils who are new to Dutch. | A handshake between two hands of different skin tones, each with a blue sleeve cuff. | skin `#FBBB69` / `#EC923A` / `#9F5F22` / `#8E531A`, cuffs `#0D6FE0`, cuff edge `#D8E0E8` | emoji 🤝 (U+1F91D) |
| IAC klas | `adapted-curriculum-class` | Class with an individually adapted curriculum. | A single jigsaw puzzle piece, teal, flat. | `#68CBCF` (ocean-500) | emoji 🧩 (U+1F9E9) recoloured teal, or Lucide `puzzle` filled |
| Ondersteuningsuur | `support-hour` | Extra support / remedial hour. | Two open hands, palms up, yellow with darker outlines. | `#FFD531`, `#DB9020` | emoji 👐 (U+1F450) |
| Opvang voor overleg | `childcare-during-meeting` | Childcare offered while meetings take place. | A hugging smiley: yellow face with closed happy eyes and two hands reaching forward. | `#FFD531`, `#FF9301`, `#A66100`, `#806601` | emoji 🤗 (U+1F917) |
| Overleg | `meeting` | Meeting / consultation (teacher–parent, team). | An adult woman in a blue top with a child in green beside her, both smiling. | `#0D6FE0`, `#57D31A`, skin `#FBBB69` / `#F2B566`, hair `#B26714` / `#663600` | emoji 🧑‍🤝‍🧑 or 👩‍👧; Lucide `users` |
| Studie | `study-hall` | Supervised study period. | A shushing smiley: yellow face, raised eyebrows, finger over the lips. | `#FFD531`, `#FF9301`, `#806601` | emoji 🤫 (U+1F92B) |
| Toezicht | `supervision` | Playground / lunch supervision. | A playground slide: yellow tower with a round blue window, red pointed roof, blue slide curving down, red ladder. | `#FFD531`, `#FF0000`, `#278DD7` | emoji 🛝 (U+1F6DD) |
| Wachtuur | `waiting-hour` | Free period between lessons ("waiting hour"). | A melting smiley: yellow face drooping into a puddle, calm smile. | `#FFD531`, `#806601` | emoji 🫠 (U+1FAE0) |

## 3. Visual rules for the types

- **Size & placement**: 24 px icon, vertically centred, 8 px before the label; in dense
  tables 16 px is allowed for the fixed types but not for emoji (they lose detail).
- **Never recolour** a multi-colour type icon to match the theme or the dark mode;
  place it on a neutral chip (`--color-bg-panel`, radius `--radius-sm`) if contrast on
  a coloured surface is poor.
- **Category colour** (last columns above) is for 8–12 px dots in a month view, left
  borders on event cards and legend swatches — **not** for recolouring the icon.
- **Checkbox tree** representation: checkbox (16 px) · icon (24 px) · label (13–14 px),
  row 32 px; group rows show label only, in `--color-link-button`.
- **Legend**: one line per type in catalogue order: icon · label · (optional) count in
  `--color-text-muted`.
- **Event card**: 4 px left border in the category colour, icon + title on line 1, time
  and location in `--ui-small` on line 2.

## 4. Copy rules for the types

- Use the Dutch labels exactly as given (sentence case, apostrophe in *to-do’s*,
  bracketed clarification kept for *Lege momenten (nog in te plannen)*).
- English keys (`school-free-day`, …) are for code, URLs and data files only; never show
  them to users.
- When a user selects what to include, the question is *Wat deel je?* or *Wat wil je
  zien?*; the toggle for all is *Alles selecteren*.
- Plural labels stay plural in filters (*Opdrachten*), singular in event titles
  (*Opdracht: boekbespreking*).

## 5. Data representation (reference)

A suggested data file an agent can generate from this catalogue (YAML; keys and order
as above). Emoji are stored as code points so fonts can be swapped.

```yaml
# data/planner_types.yaml
- key: open-slot
  label_nl: "Lege momenten (nog in te plannen)"
  group: null
  icon: { kind: glyph, name: scan, color: "#798C9E" }
  category_color: "#91A0AF"
- key: activity
  label_nl: "Activiteiten"
  group: null
  icon: { kind: glyph, name: file, color: "#3BD63D" }
  category_color: "#3BD63D"
- key: routine
  label_nl: "Routines"
  group: null
  icon: { kind: custom, name: rainbow-pyramid }
  category_color: "#91A0AF"
- key: lesson-series
  label_nl: "Lessenreeksen"
  group: null
  icon: { kind: glyph, name: route, color: "#1B96F1" }
  category_color: "#1B96F1"
- key: lesson-sheet
  label_nl: "Lesfiches"
  group: null
  icon: { kind: glyph, name: clipboard-list, color: "#91A0AF" }
  category_color: "#C2CBD4"
- key: assignment
  label_nl: "Opdrachten"
  group: null
  icon: { kind: custom, name: two-flags }
  category_color: "#FF0000"
- key: todo
  label_nl: "Eigen to-do’s"
  group: null
  icon: { kind: glyph, name: flag, color: "#FF9301" }
  category_color: "#FF9301"
- key: school-free-day
  label_nl: "Lesvrije dagen"
  group: null
  icon: { kind: emoji, codepoint: "U+2600" }
  category_color: "#FFD531"
- key: school-event
  label_nl: "Schoolactiviteiten"
  group: null
  icon: { kind: emoji, codepoint: "U+1F3AD" }
  category_color: "#FF0000"
- key: personal-calendar
  label_nl: "Persoonlijke kalender"
  group: appointments
  icon: { kind: glyph, name: users, color: "#327BF6" }
  category_color: "#327BF6"
- key: school-calendar
  label_nl: null            # the school's name
  group: appointments
  icon: { kind: glyph, name: house, color: "#FF0000" }
  category_color: "#FF0000"
  children: group-calendar  # one per course/group, icon = coloured circle
- key: newcomer-class
  label_nl: "Anderstalige nieuwkomers"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F91D" }
- key: adapted-curriculum-class
  label_nl: "IAC klas"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F9E9", color: "#68CBCF" }
- key: support-hour
  label_nl: "Ondersteuningsuur"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F450" }
- key: childcare-during-meeting
  label_nl: "Opvang voor overleg"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F917" }
- key: meeting
  label_nl: "Overleg"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F9D1 U+200D U+1F91D U+200D U+1F9D1" }
- key: study-hall
  label_nl: "Studie"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F92B" }
- key: supervision
  label_nl: "Toezicht"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1F6DD" }
- key: waiting-hour
  label_nl: "Wachtuur"
  group: generic-types
  icon: { kind: emoji, codepoint: "U+1FAE0" }
```

Group labels: `appointments` → *Afspraken*, `generic-types` → *Generieke types*.
