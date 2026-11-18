# PlusVibe email accounts: connecting, bulk SMTP import, tags, limits, reconnects, recovery

Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. T = https://plusvibe.ai/terms-and-conditions. P = https://plusvibe.ai/plans. MINE = my recommendation.

## 1. Provider types

API provider values seen: GOOGLE_WORKSPACE, MICROSOFT365, REGULAR_ACCOUNT (SMTP/IMAP) (D list accounts, D get-warmup-stats-workspace-level). A custom SMTP mailbox such as one from Maildoso is a REGULAR_ACCOUNT. Maildoso is not mentioned anywhere in the documentation I read (see gaps.md); treat it as a generic "Any Provider" IMAP/SMTP account.

Ways to connect in the UI (H 8606057, H 9399219): Google Workspace (OAuth app approval in the Google Admin Console), personal Gmail (IMAP enabled plus an App Password), Microsoft 365 (via API, no app passwords; admin consent may be needed; SMTP client auth must be enabled in the tenant) (H 10388690, H 8666007, H 8782184), and "Any Provider" with custom IMAP and SMTP.

## 2. Connecting a custom SMTP/IMAP account in the UI (H 8606065)

Email Accounts, Add New Account, choose "Any Provider", Continue. Form fields:
- Sender info: first name, last name, email.
- Incoming (IMAP): host, port (commonly 993 with SSL/TLS, 143 without), "Enable SSL/TLS" checkbox, IMAP username (usually the email address) and password.
- Outgoing (SMTP): host, port (commonly 465 with SSL/TLS, 587 without), "Enable SSL/TLS" checkbox, SMTP username and password. Checkbox "Use Same Login for SMTP Server" copies the IMAP login.
- Tips: wrong credentials are the first thing to check on an IMAP connection error; connectivity can be tested at Microsoft's connectivity test page (H 8606065).
- If a mailbox has 2FA enabled, an app password is needed (H 8606065 says if 2FA is not enabled "simply use your mailbox's password").
- Warmup reads the account's spam folder; make sure a spam folder exists (H 8606081).
- PlusVibe does not save sent mail in the Sent folder for ESPs that do not do it via SMTP, for example Amazon WorkMail; use PlusVibe's sent count (H 8842365).

## 3. Bulk add

**In the dashboard, by CSV.** The help pages don't cover it, but the screen exists (seen 2026-11-07): Email Accounts, Add New Account, Any provider, Bulk Upload, Continue. The sample file is `https://app.plusvibe.ai/v2/csv/account_bulk_upload_sample.csv` and its columns are: first_name, last_name, email, daily_limit, username, password, imap_host, imap_port, smtp_host, smtp_port, smtp_username, smtp_password, tags, min_interval, enable_camp_rampup, camp_rampup_start, camp_rampup_increment, enable_warmup, warmup_daily_limit, enable_warmup_rampup, warmup_rampup_start, warmup_rampup_increment. smtp_username and smtp_password are only needed if they differ from IMAP. tags must exist in the app first. min_interval below 2 is raised to 2.

This is the fallback for Justin's Maildoso mailboxes: `cold/mailbox_csv.py` builds the file on his Mac and he uploads it. The CSV holds passwords, so no agent builds, reads or uploads one.

**By API.** This is how Justin's Maildoso mailboxes go in. He runs `cold/push_mailboxes.py` on his Mac: it reads them from Maildoso's accounts-lookup and posts them here, 100 a call, with warmup off, and prints counts only. The body carries the passwords, so no agent runs the push. An agent may run `push_mailboxes.py check`, which keeps no password.

POST /account/bulk-add-regular-accounts (D bulk-add-smtp-accounts-38494505e0). "A successful response does not indicate that the email accounts were added successfully. It only means that the server has accepted the request. The results of the upload will be sent to PlusVibe account's email address."

Body: workspace_id, accounts[] (min 1). Each account:

| Key | Required | Type / rule |
|---|---|---|
| first_name | yes | string |
| last_name | yes | string |
| email | yes | email |
| daily_limit | yes | integer, campaign daily limit |
| username | yes | IMAP username |
| password | yes | IMAP password |
| imap_host | yes | string |
| imap_port | yes | integer |
| smtp_host | yes | string |
| smtp_username | yes | string |
| smtp_password | yes | string |
| smtp_port | yes | integer |
| min_interval | no | integer >= 2 minutes (values below 2 raised to 2) |
| enable_camp_rampup | no | yes or no |
| camp_rampup_start | no | integer initial campaign ramp-up |
| camp_rampup_increment | no | integer daily increment |
| enable_warmup | no | yes or no |
| warmup_daily_limit | no | integer |
| enable_warmup_rampup | no | yes or no |
| warmup_rampup_start | no | integer |
| warmup_rampup_increment | no | integer |

Not accepted at add time (so set afterwards with bulk-update): warmup reply rate, randomize, business type, schedule, rest cycles, tags, signature. Maximum accounts per request: not documented (gap). The delete endpoint allows 1,000 per call; the import endpoint states no cap.

Partner variant: POST /webhook/partner-upload-regular-accounts (D bulk-add-smtp-accounts-via-username-and-password-40641118e0) adds `provider_id` (required, 24 hex, assigned by PlusVibe to email infrastructure providers; request rejected if missing, unknown or disabled), optional `notification_email` for results, and either header x-api-key or `pipl_username` plus `pipl_password`. Partner base URL https://api.plusvibe.ai/v1 (D email-infra-provider-guide-2268692m0). Not for ordinary users; needs a provider ID from PlusVibe.

Exported CSV (read-only, from the UI): columns include ooo_rr (7-day reply rate including out-of-office), overall_hscore, google_hscore, microsoft_hscore, other_hscore (H 11469298). This is an export, not an import template.

Google and Microsoft OAuth initiation for providers: POST endpoints "Initiate Google OAuth login flow" and "Initiate Microsoft OAuth login flow", plus check-if-email-exists-in-another-workspace (D partner pages; see api-index.md).

## 4. Settings per account

Delivery settings: daily campaign limit, minimum interval in minutes, ramp-up; also warmup settings (see warmup.md). UI path: Email Accounts and Warmup, account, Analytics and Settings, Account, Settings, Delivery Settings (H 8844048). Bulk: select accounts, Bulk Actions, Edit Settings (popup tabs Warm-up and Account) (H 9447971).
Other fields: first_name, last_name, signature (HTML) with clear_signature yes/no, reply_to with clear_reply_to yes/no, custom_domain (custom tracking domain, CNAME px, see deliverability.md) (D bulk-update-email-accounts-38494506e0, list accounts).
Signature help: H 8617903.

## 5. Tags

- Create: POST /tags/create (name 1 to 100 chars, case-insensitive unique per workspace; color hex #RRGGBB or #RGB required; description max 500) returns tag_id (D create-a-new-tag-38494532e0). Also list, update and delete-multiple endpoints.
- Assign or remove: PUT /account/bulk-assign-tags with ids, tag_id and action ASSIGN or UNASSIGN. Campaigns using a tag update their account lists automatically (D bulk-assignremove-tags-from-email-accounts-38494508e0).
- List accounts filter: tags (comma separated tag IDs), email, skip, limit (D list accounts).
- Use tags for campaign sender pools, ESP matching rules, automation selection and placement test sampling.

## 6. Status, health and vitals

- GET /account/status (email) returns status, warmup_status, account (D get-email-account-status-38494499e0).
- Account statuses seen in docs: ACTIVE, ERROR (H 8860007), DISCONNECTED (webhook alert sample); warmup_status ACTIVE, PAUSED, INACTIVE (D warmup stats).
- Vitals: POST /account/test/vitals (see deliverability.md).
- Health analytics in list response: 7d warmup health scores, 1d miss warmup rate, 3d bounce rates, reply rates, counters email_sent_today, warmup_email_sent_today (D list accounts).
- Alerts by webhook: EMAIL_ACCOUNT_DISCONNECTED (see webhooks.md).

## 6b. Account counts and limits

- Free trial: "Connect up to 3 Email Accounts" (P). No connected-account limit is stated for Personal or Business on the pricing page. The terms set provisional thresholds: Personal 300, Business 1,000 connected email accounts, above which "manual approval" and possibly extra fees (T). Details in plans-and-limits.md.
- Inbox emails stored 9 months; "Other Replies" kept 7 days (H 10005524).

## 7. Errors, reconnects and recovery

- "Attention Required" email: if SMTP/IMAP connection fails repeatedly, account status becomes ERROR and warmup INACTIVE. Fix the server issue, reconnect, then check campaigns: campaigns set to ERROR need reactivating, ACTIVE ones need nothing (H 8860007).
- Server responses: invalid credentials or authentication failed means check credentials; "connect ECONNREFUSED" means the ESP probably blocked PlusVibe's IP and must whitelist it (contact PlusVibe support) (H 8860007).
- Microsoft: "535 5.7.139 SmtpClientAuthentication is disabled" means enable SMTP auth in the tenant (H 8782184). "5.7.708 traffic not accepted from this IP" on new Microsoft accounts: ask Microsoft support to unblock (H 8782236).
- Bulk reconnect: POST /account/bulk-reconnect (ids). "Reconnecting only works if account credentials haven't changed ... Google and Microsoft accounts: usually won't work ... Only try once" (D bulk-reconnect-email-accounts-38494509e0).
- Reconnect or re-adding the same address retains warmup and stats (H 8606081). Changing only the sender name does not reset warmup.
- Delete: POST /account/bulk-delete, up to 1,000 per request, by emails and/or ids. Accounts stop sending and warming immediately and leave every campaign; unknown or already deleted are reported, not errors; ids from another workspace reject the whole request (D bulk-delete-email-accounts-46324626e0).
- Move: POST /account/move-workspace (workspace_id, to_workspace_id, ids) within one organization; needs OWNER or WORKSPACE_ADMIN on the source and membership of the destination (D move-email-accounts-to-another-workspace-40817914e0).
- Automation recovery: see automations.md.

## 8. MINE: loading 200 Maildoso-style SMTP inboxes

- Collect per mailbox: first and last name, address, IMAP and SMTP host and port (typically 993 and 465 or 587 per H 8606065, but confirm against Maildoso's own settings), username and password.
- Build one JSON per batch (I would use 50 to 100 per request; no cap documented). Include enable_warmup yes and the warmup ramp values for the first pass; do not set campaign ramp yet.
- After the upload email arrives, GET /account/list (paged with skip and limit) to confirm all 200 are ACTIVE, then tag and bulk-update.
- Respect PlusVibe's own guidance of 3 or fewer mailboxes per domain (H 9399331).
