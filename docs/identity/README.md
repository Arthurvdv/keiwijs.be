# Identity guide — for AI agents and humans

A platform-agnostic description of the visual and verbal identity of a **school /
parent community** website or tool. Written so that an AI agent can apply it without
further briefing; today it targets a Hugo site, tomorrow it can drive an app, an e-mail
template or a slide deck.

Audience of the product: parents (first), teachers and pupils (second) of a Flemish
primary school community. Language of the product: Dutch (nl-BE), with English as a
secondary language. Language of this guide: English, with Dutch example copy.

## Files

| File | What it decides | Read when |
|---|---|---|
| [colors.md](colors.md) | All colour tokens (light + derived dark), status colours, audience blocks, hue scales, shadows, contrast rules. **Source of truth for every hex value.** | always |
| [typography.md](typography.md) | Typeface (Open Sans), weights, two type scales (website / compact app), casing and emphasis rules. | always |
| [components.md](components.md) | Spacing & shape tokens, buttons, forms, navigation, containers, lists, badges, empty states, iconography, illustration, accessibility baseline. | building any UI |
| [tone-of-voice.md](tone-of-voice.md) | Register (je/jij), the two modes (landing vs product), label grammar, action vocabulary, error/empty-state patterns, number & date formats, Dutch micro-examples. | writing or reviewing any copy |
| [planner-item-types.md](planner-item-types.md) | The taxonomy of school-planner item types, their names, icon descriptions, colours and open-licensed icon equivalents, plus a data-file layout. | anything that lists, filters or legends calendar items |
| [hugo-implementation.md](hugo-implementation.md) | Maps the above onto a Hugo project: `tokens.css` (verbatim), font hosting, base styles, partials to touch, content pass, verification checklist. | implementing on Hugo |

## The identity in one paragraph

White, light and practical. Open Sans with **big light-grey titles** and dark regular
text; one **warm orange-red accent** (`--color-accent`) for the word that matters, the
active tab and the hero; a **calm blue** (`--color-action`) for everything clickable;
green / yellow / red strictly for meaning. Controls have small radii (4–8 px) and a
visible blue focus ring; marketing cards are the one place for big 24 px corners and a
soft navy-tinted shadow. Colour lives in flat, filled, multi-colour **icons and friendly
illustrations**, not in the chrome. The voice talks to parents as **je**, in short
plain Flemish sentences, with nouns for menus, object-plus-verb for buttons, one period
per sentence and no exclamation marks in the interface.

## Non-negotiables (check these first in any review)

1. Hex values only from `colors.md`; no new blues, no pure black, no UI gradients.
2. `--color-accent` and `--color-text-muted` never on text smaller than 24 px (19 px
   bold); every text/background pair meets WCAG AA.
3. Open Sans only, weights 300/400/600/700, self-hosted, sentence case everywhere.
4. One primary action per view; links blue, never bold-by-default; focus ring on every
   control.
5. Dutch copy in **je/jij**; buttons = object + infinitive; labels without period,
   sentences with; no exclamation marks or emoji in UI chrome.
6. Empty and error states: illustration (where room) + one plain sentence + the next
   step.
7. Icons: 24 px, flat and filled for objects, outline monochrome for UI glyphs; never
   recolour a multi-colour icon; never copy a third-party icon set — use the described
   open equivalents.

## How to use this guide as an agent

1. Load `README.md`, `colors.md`, `typography.md`, `tone-of-voice.md`; load
   `components.md` for UI work, `planner-item-types.md` for calendar/planner features,
   and the platform file (`hugo-implementation.md`) last.
2. Refer to tokens by name in code and in explanations (`--color-action`), never by hex.
3. When something is not covered, derive it from the nearest rule and the "character"
   paragraphs at the top of each file, and leave a short comment marking it as derived.
4. Example copy in these files is illustrative. Write new copy that follows the
   patterns; do not paste the examples into a product unchanged.
5. Finish with the verification checklist of the platform file (or, without one, the
   non-negotiables above).

## Provenance and scope

The tokens were measured from a live, in-use school-communication environment and its
public site, then consolidated: duplicates were merged, legacy values dropped in favour
of the current design-token layer, a dark theme was derived, and all pairs were
contrast-checked. The guide is intentionally free of references to that source so it can
stand on its own; nothing in it is a copy of its text, icons or logo.

Version: 1.0 · October 2026 · Maintainer: Arthur van de Vondervoort.
