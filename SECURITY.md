# Security policy

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Use GitHub's
private vulnerability reporting on this repository ("Security" tab → "Report a
vulnerability"), or e-mail the maintainer address listed on the website's
privacy page. You should get a first reply within 7 days.

## Scope and threat model

* The service never holds Smartschool or Google credentials. The only secret per
  user is the Smartschool feed URL they paste, which is stored in plaintext in
  Azure Table Storage (Microsoft-managed encryption at rest). Holding that URL
  grants read access to the filtered feed and the ability to change or delete
  its settings. This is a documented design decision ("security through
  obscurity" at the user's request), not a bug.
* Published feeds live on a Blob Storage static website under an unguessable
  name derived from a SHA-256 of the source URL. The container is not listable.
* Upstream fetches are limited to `https://*.smartschool.be/planner/sync/ics/<uuid>/<uuid>`,
  resolved addresses must be public, redirects are re-validated, bodies are
  capped at 5 MiB and 15 s.
* Pupil names in `Extra deelnemers` are stripped from published feeds by default.

Reports about SSRF bypasses, feed-name enumeration, injection through calendar
content, or anything that would expose one user's data to another are very
welcome.
