# SpeakerAgent CLI and dashboard

## Version selection

The old `main` CLI is a six-command script using a shared deployment key and speaker ID. Its documentation says conferences were retired; that applies to the old `/api/leads` route, not all later Conference Alpha features.

The dashboard observed on November 5, 2026 recommends `codex/cli-security-updates`. The bundled CLI is the later `cli-agency-release` commit `714ef03` (full commit in the source manifest), which includes that hardened branch and agency-seat support. Its README still contains older contradictory sections; use executable help and the instructions below.

Use the shipped script without installing a package:

```sh
python3 integrations/speakeragent-cli/speakeragent.py --help
```

Or install the local vetted folder in a dedicated virtual environment and use `speakeragent`. The location above is relative to the distribution root, not the current skill directory. Do not replace a working customer version without reviewing the version difference.

## Authentication

Configure `SPEAKERAGENT_API_KEY` privately, never in chat or command arguments. Run `speakeragent auth check`. Personal keys derive the speaker from protected introspection. Agency keys require `speakeragent speakers list --json`, then the client-selected paid seat via `--speaker-id`. If the client already selected a seat, reuse it. Do not guess or override a personal key's account.

At the audited commit, both `sa_test_` and `sa_live_` prefixes route to the test API. The prefix does not prove production access. Verify destination and account with introspection; do not reroute a key to another host. A 401 requires a valid connection, a 403 requires the missing authorized scope/seat; neither is solved by bypassing checks.

## Commands and effects

| Command | Use / effect |
|---|---|
| `auth check` | Verify configured account and scope. |
| `speakers list --json` | Agency-owned active paid seats. |
| `podcasts --json` | List active podcast records; filters include status, triage, saved. |
| `show ID` | Inspect one record, sensitive fields redacted by default. |
| `email ID --reveal-sensitive` | Read an existing draft when the user requested its content; does not send. |
| `refresh ID` | Enrich and draft; may incur provider usage. Re-read until the intended change is observed. |
| `status ID Contacted` | Change recorded status only; not proof of a send. |
| `saved ID true` | Save/heart a record. |
| `profile show` / `profile edit --from FILE` | Read/update selected speaker profile. |
| `matches status` | Inspect podcast scout progress. |
| `matches generate --wait --yes` | Consume one scout run, only when that run is authorized. Optional selected `--persona-id`. |
| `billing show` | Inspect plan and remaining scout allowance, not a generic credit ledger. |
| `voice samples list` / `voice status` | Inspect writing samples or extraction state. |
| `voice samples set --from FILE --confirm-own-writing --yes` | Replace samples only with authorization and actual authorship attestation. |
| `voice preview` | Generate a synthetic voice preview; not audio cloning. |

`--reveal-sensitive` is for requested private contact/draft content, not general summaries. The hardened CLI omits the old Gmail compose URL. No CLI command sends email. Later web application code has managed-email features; this is a separate capability and authorization path.

Conference Alpha has no corresponding command in this CLI. Read source routes only for architecture understanding. Use the available dashboard and its normal account checks, or independent research; do not give customers an internal shared API key to reach conference endpoints.

## Dashboard runbook

1. Open the authorized dashboard and observe account and selected persona. Existing sign-in does not choose the right persona for you.
2. Persona: inspect identity, bio, distinctiveness, Big 3 Topics, scout preferences and materials. Load/change only the intended persona and verify the visible selection.
3. Dashboard: inspect Podcasts and Saved, score, match reason, host/contact source and hook. Open the cited show/site when reviewing evidence. A “Verified” badge may reflect legacy DNS checks; inspect actual provenance before treating it as mailbox verification.
4. Scout: inspect plan/run allowance and current progress. A rerun consumes usage; do not trigger one to demonstrate that a button exists. If authorized, run once, record persona/start state, poll status and inspect saved output.
5. Conference Alpha: inspect existing results, date/CFP badges, research outcome, missing evidence and Sources and alternative contacts. `Find the right contact` can start additional research. Prefer an existing case before spending again. Capture pending state before leaving.
6. Pipeline: distinguish imported opportunities, drafts and actual outreach outcomes. `Send Pitch` is an external action; do not click it during read-only review.
7. API / CLI: view installation and scope information. Key creation/revocation changes access and is a separate setup action. A displayed secret is one-time; store privately, not in an artifact.

Wait for page hydration before concluding there are no records. Reobserve after navigation or filter changes. If the UI date disagrees with its description, verify the official date and retain the discrepancy. Do not blindly trust stale counts or a result named “conference.”
