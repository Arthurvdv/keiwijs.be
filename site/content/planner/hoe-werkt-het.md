---
title: "Hoe werkt het?"
linkTitle: "Hoe werkt het?"
description: "Waar je de Smartschool-link vindt, hoe klassen worden herkend en hoe de jaarlijkse doorschuiving werkt."
slug: "hoe-werkt-het"
---

## Waar vind ik mijn Smartschool-link? {#link-vinden}

1. Open de **Planner** in Smartschool.
2. Klik links op het tandwiel (**Beheer**) en kies **Planner delen (ICS-export)**.
3. Klik op **Profiel toevoegen**, geef het een naam en kies wat je wil delen. Smartschool legt dit ook uit via *Lees alle informatie in de handleiding*. Heb je al een profiel, sla deze stap dan over.
4. **Kopieer de URL** van je profiel uit de lijst. Ze begint met `https://` en bevat `.smartschool.be/planner/sync/ics/`.
5. Plak de link in de [planner]({{< relref "/planner" >}}) en klik op 'Controleren'.

## Hoe worden klassen herkend?

De tool leest de titel van elke activiteit en zoekt er klascodes in, zoals K1 tot K3 en L1 tot L6. Een paar voorbeelden:

| Titel | Wie ziet dit? |
|---|---|
| `L3: Bib` | enkel L3 |
| `L4 + L6 bib` | L4 en L6 |
| `Uitstap kleuters` | K1, K2 en K3 |
| `Schoolfeest lagere school` | L1 tot en met L6 |
| `Zwemmen iedereen (behalve L1)` | iedereen behalve L1 |

Staat er geen klas in de titel, dan kan je optioneel de klas van de organiserende leerkracht gebruiken (onder Geavanceerd).

## Wat betekent "zonder klasvermelding"?

Activiteiten voor de hele school, zoals zwemmen, studiedagen en vakanties, hebben meestal geen klas in de titel. Standaard blijven die in jouw kalender. Zet de schakelaar uit als je ze liever niet ziet.

## Hoe werkt de jaarlijkse doorschuiving?

Elk jaar op de datum die je kiest (standaard 1 augustus) schuiven de geselecteerde klassen één plaats op in de lijst. De volgorde van de lijst bepaalt dus waar je kind naartoe gaat.

**Voorbeeld:** je hebt twee kinderen, het ene in K2 en het andere in L4. Op 1 augustus wordt dat K3 en L5. Zat een kind in L6, dan valt die klas weg: het kind verlaat de lagere school en die klas wordt niet meer gevolgd.

Wil je dat een klas niet meeschuift, bijvoorbeeld omdat je kind zit te blijven, haal dan het vinkje bij "Volgend schooljaar doorschuiven" (het afstudeerhoedje) weg.

## Pictogrammen

Bevat de titel van een activiteit een woord uit je lijst, dan komt het bijhorende pictogram ervoor, bijvoorbeeld ☀️ voor "vakantie" of 📚 voor "bib". De eerste regel die past, wint. Past er geen enkele regel, dan krijgt de activiteit het reservepictogram (standaard 📌); laat dat leeg als je dan liever geen pictogram ziet. Je kan regels toevoegen, verwijderen en van volgorde veranderen, of de pictogrammen in de titel helemaal uitzetten.

In de beschrijving krijgen de vaste velden van Smartschool altijd een pictogram: 🗓️ Kalender, 👤 Organisator, 👥 Deelnemers, 🔗 Weblink en 📝 Organisatie of verloop. Staan de pictogrammen in de titel aan, dan vervangt het pictogram de woorden Kalender, Organisator en Weblink: je ziet dan bijvoorbeeld "🗓️ Nieuwstrein voor ouders" in plaats van "🗓️ Kalender: Nieuwstrein voor ouders".

## Beperkingen

- De titels in Smartschool zijn vrije tekst. Een leerkracht die een klas anders schrijft, kan ervoor zorgen dat een activiteit niet herkend wordt. Het voorbeeld toont altijd wat er gebeurt.
- "Behalve" wordt zo goed mogelijk begrepen, maar is niet waterdicht.
- De kalender wordt elk uur opnieuw opgebouwd. Google Agenda zelf kan tot 24 uur nodig hebben om wijzigingen op te halen.
