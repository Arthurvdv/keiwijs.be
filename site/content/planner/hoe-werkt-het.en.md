---
title: "How it works"
linkTitle: "How it works"
description: "Where to find the Smartschool link, how classes are detected and how the yearly rollover works."
slug: "how-it-works"
---

## Where do I find my Smartschool link? {#link-vinden}

1. Open the **Planner** in Smartschool.
2. Click the gear icon on the left (**Manage**, Beheer) and choose **Share planner (ICS export)** (Planner delen (ICS-export)).
3. Click **Add profile** (Profiel toevoegen), give it a name and choose what to share. Smartschool also explains this under *Lees alle informatie in de handleiding* (read all information in the manual). If you already have a profile, skip this step.
4. **Copy the URL** of your profile from the list. It starts with `https://` and contains `.smartschool.be/planner/sync/ics/`.
5. Paste the link in the [planner]({{< relref "/planner" >}}) and click 'Check'.

## How are classes detected?

The tool reads the title of every activity and looks for class codes such as K1 to K3 and L1 to L6. Some examples:

| Title | Who sees it? |
|---|---|
| `L3: Bib` | only L3 |
| `L4 + L6 bib` | L4 and L6 |
| `Uitstap kleuters` | K1, K2 and K3 |
| `Schoolfeest lagere school` | L1 up to L6 |
| `Zwemmen iedereen (behalve L1)` | everyone except L1 |

If the title has no class, you can optionally use the class of the organising teacher (under Advanced).

## What does "without a class" mean?

Activities for the whole school, such as swimming, study days and holidays, usually have no class in the title. By default they stay in your calendar. Switch the toggle off if you prefer not to see them.

## How does the yearly rollover work?

Every year on the date you choose (1 July by default) the selected classes move up one place in the list. The order of the list therefore decides where your child goes next.

**Example:** you have two children, one in K2 and one in L4. On 1 July they become K3 and L5. If a child was in L6, that class drops off: the child leaves primary school and the class is no longer followed.

If a class should not move along, for instance because your child repeats a year, untick "move up next school year".

## Limitations

- Titles in Smartschool are free text. If a teacher writes a class differently, an activity may not be recognised. The preview always shows what happens.
- "Behalve" (except) is understood on a best-effort basis and is not watertight.
- The calendar is rebuilt every hour. Google Calendar itself can take up to 24 hours to pick up changes.
