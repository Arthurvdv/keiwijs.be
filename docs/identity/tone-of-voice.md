# Tone of voice

Part of the identity guide — see [README.md](README.md). Instructions are in English;
all example copy is **Dutch (Flemish register, nl-BE)** and was written for this guide —
reuse the patterns, not the sentences.

## 1. Who is speaking, to whom

The voice is that of a **helpful organiser among parents**: someone who knows the school
year inside out, keeps things practical and never talks down. The reader is a parent
(or occasionally a teacher or pupil) who is busy, on a phone, and wants to get one
thing done. The voice is **warm but not chatty**: warmth comes from clarity, short
sentences and friendly illustrations, not from exclamation marks or jokes.

Audience words: *ouders*, *leerlingen*, *leerkrachten*, *de school*, *je kind* (or *je
zoon of dochter* when gender-neutral phrasing is not needed), *het oudercomité* /
*de ouderwerking*. The organisation speaks as **we/wij/ons**; the reader is always
**je/jij/jouw**.

## 2. Register

- **Informal "je/jij/jouw" everywhere.** Never *u/uw*, not even in legal or privacy
  text — keep those pages plain and friendly too.
- **Flemish, standard Dutch.** Prefer *je kan* over *je kunt*, *vakantie*, *lesvrije
  dag*, *oudercontact*, *schoolpoort*, *boekentas*. Avoid Netherlands-specific words
  (*ouderavond* → *oudercontact*; *juf/meester* are fine).
- **Plain words over system words.** *bewaren* not *persisteren*, *kalender* not
  *ICS-feed* (explain technical words once, in brackets, then use the plain word).
- **Sentence case** for everything: headings, buttons, menu items. Product and
  organisation names keep their own capitals.

## 3. Two modes

| | **Landing / marketing mode** | **Product / UI mode** |
|---|---|---|
| Goal | invite, reassure, explain the value | let the user act without thinking |
| Sentences | 8–18 words, one idea each; a question as a hook is fine | as short as possible; one full sentence for helper text |
| Headlines | short promise lines; one key word may be accented in orange | noun labels (*Berichten*, *Instellingen*) |
| Verbs | friendly imperatives (*Ontdek…*, *Bekijk…*, *Volg…*) | object-first infinitives for actions (*Kalender toevoegen*) |
| Energy | an occasional exclamation mark or typographic accent (*hét*, *én*) | no exclamation marks, no emoji |
| Recurring words | *eenvoudig, samen, overzichtelijk, veilig, vlot, altijd mee* | *toevoegen, bewaren, wissen, zoeken, kiezen* |

## 4. Headings & body (landing mode)

Patterns:

- Promise line: `Altijd mee met wat er op school gebeurt.`
- Question hook + answer: `Nog snel kijken of het morgen zwemmen is? Je kalender weet het al.`
- Escalation: `Een kalender. En een nieuwsbrief. En het menu. Allemaal op één plek.`
- Accented key word (in HTML `<strong>` → orange): `Alles van de school, <strong>samen</strong> in jouw agenda.`
- Reassurance line (privacy/safety recurs on every page): `Je gegevens blijven van jou en worden niet gedeeld.`
- Three-part value line: `eenvoudig, veilig en altijd actueel`

Body example:

> Je kiest één keer de klas van je kind. Vanaf dan zie je alleen wat voor jullie telt:
> uitstappen, lesvrije dagen en activiteiten van de ouderwerking. Verandert de klas na
> de zomer? Dan schuift je selectie gewoon mee.

## 5. UI copy (product mode)

### Labels

- **Menu items are nouns**: *Start*, *Kalender*, *Nieuws*, *Documenten*, *Instellingen*,
  *Help*. Compound nouns follow Dutch casing: *Mijn documenten*, *Postvak in*.
- **Buttons are object + infinitive**, 2–4 words, no period, no exclamation:
  *Profiel toevoegen*, *Selectie bewaren*, *Filters wissen*, *Link kopiëren*,
  *Bericht beantwoorden*, *Bestand uploaden*. Single verbs are fine when the object is
  obvious: *Zoeken*, *Annuleren*, *Sluiten*, *Doorgaan*, *Afdrukken*.
- **Destructive actions name the object**: *Profiel verwijderen* (never just
  *Verwijderen* in a dialog title).
- **Link buttons** read like a small invitation with a "+" icon: *+ Kalender toevoegen*.
- **Tabs and filters** are nouns or short noun phrases: *Per groep*, *Lijst*, *Invullen*,
  *Beheren*, *Prullenmand*.
- **Tooltips** are noun phrases describing the result: *Nieuw item aanmaken*, *Link naar
  klembord kopiëren*.

### Standard action vocabulary

| Meaning | Use | Avoid |
|---|---|---|
| create new | *aanmaken* (object + aanmaken) | *creëren*, *nieuw* alone |
| add to a list | *toevoegen* | *insert* |
| save | *bewaren* | *opslaan* (acceptable but not house style), *save* |
| delete | *verwijderen* | *wissen* for objects |
| clear filters/fields | *wissen* | *resetten* |
| edit | *wijzigen* / *bewerken* | *aanpassen* in buttons (fine in prose) |
| search | *zoeken* (placeholder: *Zoeken op naam of klas*) | *zoekopdracht* |
| copy | *kopiëren* | *copy* |
| send | *verzenden* | *versturen* in buttons (fine in prose) |
| sign in / out | *aanmelden* / *afmelden* | *inloggen* / *uitloggen* |
| back | an arrow icon with tooltip *Terug* | *Vorige* |
| settings / notifications | *instellingen* / *meldingen* | *configuratie*, *notificaties* |
| select all | *Alles selecteren* | *Alles aanvinken* |

### Helper text, placeholders, confirmations

- Helper text = **one full sentence, with a period**, telling what happens:
  *Je kan deze selectie later altijd aanpassen.*
- Placeholders are short instructions: *Zoeken op titel of datum*, *Geef een naam in*.
- Info banners explain the feature in two sentences and may end with a link:
  *Je kan je kalender meenemen naar je eigen agenda-app. Maak een profiel aan en kopieer
  de link die je dan krijgt. Lees hoe het werkt in de handleiding.*
- Confirmations are statements, not cheers: *Je selectie is bewaard.* (not *Gelukt!*)
- Questions in the UI are allowed as section labels when they genuinely ask the user
  to choose: *Wat deel je?*, *Welke klas?*

### Empty states and errors

- Empty list: *Er zijn nog geen profielen.* — add *(nog)* or *nog* when the user can
  create the item; drop it when they can't (*Er zijn geen berichten in deze map.*).
- Softened absence: *Er staat niets gepland voor deze week.*
- Error = **what happened + what to do next**, two sentences, no apology, no blame:
  *Je hebt geen toegang tot dit onderdeel. Kies een ander onderdeel via 'Ga naar' in de
  navigatiebalk.* UI references go in single quotes.
- Validation: *Je hebt dit veld niet ingevuld.* / *Deze link herkennen we niet. Kopieer
  hem opnieuw vanuit je kalender.*
- Never: *Oeps!*, *Er ging iets mis!*, *Fout 500*, *Ongeldige invoer*.

## 6. Mechanics

- **Punctuation**: no exclamation marks in UI chrome (allowed sparingly in landing
  copy); no emoji in UI (illustrations do that job); ellipsis `…` for truncation; single
  quotes for UI references; no trailing period on labels, always one on sentences.
- **Numbers & dates**: in prose *9 januari 2026*, *om 18 uur*, *van 8.30 tot 15.30 uur*;
  in lists and tables `2026-01-09 18:00` (24-hour clock); month names lowercase
  (*oktober 2026*); weekday abbreviations lowercase two letters *ma di wo do vr za zo*;
  weeks start on Monday; relative time only when precise (*gisteren*, *vandaag*, else a
  date).
- **School vocabulary**: *schooljaar 2026–2027*, *kleuterklas* K1–K3, *leerjaar* L1–L6,
  *lesvrije dag*, *pedagogische studiedag*, *facultatieve verlofdag*, *oudercontact*,
  *zwemmen*, *uitstap*, *schoolfeest*, *opvang*, *middagpauze*.
- **Capitalisation**: sentence case; *Google Agenda*, *Apple Agenda*, *Outlook* as
  product names; no caps for *ouderwerking*, *school*.
- **Length limits**: button ≤ 24 characters; menu item ≤ 18; page title ≤ 40; empty
  state ≤ 90; info banner ≤ 220.

## 7. Worked micro-examples (generated)

| Context | Write | Not |
|---|---|---|
| Hero title | *Alles van de school, samen in jouw agenda.* | *DE ULTIEME SCHOOLKALENDER!* |
| Hero subtitle | *Kies de klas van je kind en krijg alleen wat voor jullie telt.* | *Onze oplossing biedt gepersonaliseerde kalenderfiltering.* |
| Primary CTA | *Begin met je kalender* | *Klik hier* |
| Secondary CTA | *Lees hoe het werkt* | *Meer informatie over de werking* |
| Section title | *Wat deel je?* | *Deelinstellingen* |
| Toggle label | *Lesvrije dagen tonen* | *Toggle lesvrije dagen* |
| Success message | *Je kalender is bijgewerkt.* | *Succes! Kalender succesvol geüpdatet!* |
| Empty state | *Er zijn nog geen activiteiten voor deze maand.* | *Geen data gevonden.* |
| Privacy line | *Je link blijft bij jou. Wij bewaren geen wachtwoorden.* | *Wij hechten veel belang aan uw privacy.* |
| Footer legal | *Gemaakt door ouders, voor ouders. Vragen? Mail ons.* | *© Alle rechten voorbehouden. Disclaimer.* |
