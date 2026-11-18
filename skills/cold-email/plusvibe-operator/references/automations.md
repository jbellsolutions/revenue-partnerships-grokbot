# PlusVibe email account automations (account health rules and recovery)

Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. MINE = my recommendation. Plan: not stated for automations. The pricing page lists "Advanced+ Automations" under Agency only (https://plusvibe.ai/plans), and does not say whether basic automations need Business. API use needs Business (D getting-started-2268178m0).

## 1. Concept

Rules watch account health (or a placement test's inbox rate) and, when a threshold is crossed, throttle the matched accounts for a recovery period, then restore or replace their settings (H 16167766, D create-automation-rule-41015401e0). When a rule fires: the account owner is notified and the `EMAIL_AUTOMATION_RULE_TRIGGERED` webhook fires (D create-automation-rule-41015401e0; this event name is not in the webhook overview list, see webhooks.md and gaps.md).

Each rule has four parts: selection, trigger conditions, recovery actions, post-recovery behaviour (H 16167766). Location: Email Accounts dashboard, Automation (H 16167766).

## 2. Rule types (API `type`)

- NORMAL (default): own-account health metrics. Created active, at lowest priority.
- EMAIL_PLACEMENT: attached to one recurring placement test (type AUTOMATIC only; one-off or manual tests are rejected with 400). One rule per test. Creating again for the same ptest_id replaces that rule's config, like update. Addressed by ptest_id, not id. Cannot be deleted or duplicated through the API; disable with the status endpoint (D create-automation-rule, delete-automation-rule-41015403e0, duplicate-automation-rule-41015406e0).

## 3. Selection (who the rule applies to)

UI scopes: All Accounts, By Provider, By Tags, Specific Accounts (H 16167766).
API selection.type: ALL_ACCOUNTS, PROVIDER (selection.providers: GOOGLE_WORKSPACE, MICROSOFT365, REGULAR_ACCOUNT; required), TAG (tag_ids required), IDS (ids required). Placement rules only: PT_EMAIL_ACCOUNT (the tested senders; with inbox_r_account only those whose own rate met the condition) and PT_ALL_ACCOUNT_OF_DOMAIN (every workspace account on the tested senders' domains). ALL_ACCOUNTS and IDS are not allowed for placement rules (D update-automation-rule-41015402e0).
Custom SMTP inboxes are REGULAR_ACCOUNT provider.

## 4. Triggers (conditions[].field)

NORMAL rules (D create-automation-rule-41015401e0, update-automation-rule-41015402e0, H 16167766):

| field | Meaning |
|---|---|
| 3d_recipient_bounce_rate | Bounces caused by the recipient address, past 3 days, percent. From 14 Sep 2026 |
| 3d_sender_bounce_rate | Bounces from your mailbox or domain being rejected, past 3 days, percent. From 14 Sep 2026. Existing rules on the older combined 3-day bounce rate keep working |
| 7d_overall_warmup_health | Overall warmup health, 7 days, percent (only evaluated for accounts with warmup running) |
| 7d_google_warmup_health, 7d_microsoft_warmup_health | Same, for Google or Microsoft recipients |
| 7d_ooo_replyrate, 14d_ooo_replyrate, 30d_ooo_replyrate | Reply rate including out-of-office replies over 7, 14, 30 days |

- Accounts without enough recent activity for a metric are never matched by it. A rate is -1 when 10 or fewer emails were sent in the bounce window (D list accounts).
- min_contacted (integer >= 0) applies to the reply-rate fields only; minimum unique leads contacted in the window. Omit or 0 means none. Recommended 30 for 7d, 60 for 14d, 100 for 30d (UI defaults the same). Sending it on any other metric returns 400 (D).
- operator: equals, not_equals, greater_than, less_than, greater_than_or_equal, less_than_or_equal, between (value then is a two-number array [low, high]). value may be a number or numeric string. value_type PERCENT or NUMBER (display only).
- conditions.logic AND or OR; each metric may appear at most once; at least 1 condition. With one condition send "AND".

Placement rules (inbox rate, percent): inbox_r_1 (whole test, last run), inbox_r_2 (average of last 2 runs), inbox_r_3 (average of last 3), inbox_r_account (each tested sender's own rate in latest run; must be the only condition; needs a PT_ selector). Whole-test fields may be combined with logic (D create-automation-rule). UI: "Last 2 tests" recommended for most users, "last 3" most stable; evaluation mode "as a whole" (default) or "each tested account individually" (H 15359387). Rules are evaluated once per completed run, changes apply from the next run, and an account already in recovery is skipped, so throttles never stack (D).

## 5. Actions (recovery phase)

API `actions` (D update-automation-rule-41015402e0):

| Field | Range |
|---|---|
| daily_limit (required) | integer >= 0 campaign limit while throttled. 0 pauses campaign sending |
| is_warmup_max_daily_limit (required) | 0 or 1 |
| warmup_max_daily_limit | integer >= 1, required when the flag is 1 |
| is_warmup_reply_rate (required) | 0 or 1 |
| warmup_reply_rate | integer 1 to 100 (percent). Different unit from account settings, which use 0 to 1 |
| recovery_in (required) | integer >= 1, days the throttle lasts |
| recovery_unit | DAYS only |

Warmup continues while campaigns are throttled or paused (H 16167766).

## 6. After recovery (`after_recovery`)

- restore_type ORIGINAL: put back the settings the account had just before the rule fired (campaign daily limit, warmup limit, warmup reply rate) (D, H 15359387).
- restore_type CUSTOMIZED: apply new values. Fields: camp_limit FIXED or RAMPUP; daily_limit (>= 1; the ramp cap when RAMPUP); rampup_daily_limit (start) and rampup_daily_inc when RAMPUP; is_warmup_max_daily_limit and warmup_max_daily_limit; is_warmup_reply_rate and warmup_reply_rate (1 to 100) (D).
- Example from help: campaign limit 0, warmup limit 7, reply rate 55%, duration 1 day, then revert (H 15359387). For new domains: campaign 0/day, warmup 5 to 10/day, recovery 1 to 3 days. For established domains: reduce rather than pause, shorter recovery (H 15359387).

## 7. Priority, exemption and recovery state

- Only one rule applies to an account at a time; the highest in the list wins. Drag to reorder in UI. 1 is evaluated first in the API list (H 16167766, D list-automation-rules-41015400e0).
- Exemption: after a rule triggers, the same rule is not evaluated again until the metric window has passed plus 1 day. For a 14-day reply-rate window that is at least 15 days (H 16167766).
- A reply-rate metric with zero campaign sends in the window is "no data", not 0%, so the rule is skipped. Warmup does not count toward reply-rate stats (H 16167766).
- Deleting or disabling a rule does not release accounts already in recovery; they finish on schedule (H 16167766, D delete and enable-disable endpoints).
- GET /account/list returns in_recovery (boolean, from 14 Sep 2026). POST /account/recovery (up to 100 emails, available from 23 Oct 2026) returns rule {id, name, priority}, why_triggered {reason, triggered_at}, sending_plan {before_recovery, recovery_period {current_day, total_days, recovery_ends_at, daily_limit, warmup_max_daily_limit, warmup_reply_rate}, after_recovery {restore_type, camp_limit, daily_limit, warmup_max_daily_limit, warmup_reply_rate, ramp_up {start, inc, target}}} and not_found (D get-account-recovery-details-45795651e0).
- Rest Cycles are frozen (no day counting, no new rest) while in_recovery is true (D list accounts).
- Forced exit: bulk update the sending limit in UI and confirm the force-exit prompt (H 16167766). API: PUT /account/bulk-update touching daily_limit, ramp-up or warmup-limit fields exits recovery by default (force_exit_recovery 1); pass 0 to keep recovery. In the first case "the rule's saved settings are NOT restored" (D bulk-update-email-accounts-38494506e0).
- Editing the rule's recovery days or restoring manually changes or ends recovery early (D get-account-recovery-details).

## 8. Endpoints

- GET /ea-automation-rules/ (NORMAL only, ordered by priority; l_triggered_at is last trigger or empty)
- GET /ea-automation-rules/detail (id, or type=EMAIL_PLACEMENT plus ptest_id)
- POST /ea-automation-rules/ (create)
- PUT /ea-automation-rules/ (replace full body; needs type and id or ptest_id; optional status)
- PATCH /ea-automation-rules/patch (status ACTIVE or INACTIVE; type required)
- DELETE /ea-automation-rules/ (body id; NORMAL only)
- POST /ea-automation-rules/duplicate (body id; copy named "<name> (Copy)", active, lowest priority)
- POST /account/recovery

## 9. MINE: a starting rule set for 200 SMTP inboxes

These are my suggestions built from the documented fields, not PlusVibe defaults.
- Rule 1, selection PROVIDER REGULAR_ACCOUNT, conditions OR of 3d_sender_bounce_rate greater_than a low single digit percent and 7d_overall_warmup_health less_than 80, actions daily_limit 0, warmup cap 7, warmup reply rate 55, recovery_in 2, after_recovery CUSTOMIZED RAMPUP.
- Rule 2, 14d_ooo_replyrate less_than a threshold with min_contacted 60, actions reduce limit rather than 0.
- Set force_exit_recovery 0 on any scheduled bulk-update job so it does not cancel recoveries.
