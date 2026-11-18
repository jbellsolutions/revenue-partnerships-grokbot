# PlusVibe email placement tests

Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. P = https://plusvibe.ai/plans. MINE = my recommendation.

## 1. What it is

- Sends test emails from your sender accounts to PlusVibe-owned seed inboxes and records where each lands: Inbox, Promotions, Spam, or Missing (H 13273010, H 13271457).
- Seed inboxes are neutral: no opens, no replies, no spam-to-inbox moves, and no warmup on seed accounts, so results stay objective (H 13271457). Seed domains look like normal end-user domains (H 13271457).
- A perfect result "means your setup is capable of inboxing", not that campaigns will inbox at scale. Treat tests as a "health check, not a delivery guarantee" (H 13271457). Real campaigns differ by volume, burst speed, timing and recipient behaviour.

## 2. Test types (API `type` on create)

D create-a-new-parent-test-38494547e0 (POST /email-placement/create/parent-test, body workspace_id, name, type default AUTOMATIC):

| type | Meaning (verbatim sense) |
|---|---|
| AUTOMATIC | Recurring test that runs on the schedule you configure. Created in draft; configure with the update endpoint, then set status ACTIVE |
| ONE_OFF | Runs a single time as soon as you activate it. Created in draft |
| MANUAL | "test where you send the emails yourself" |

AUTOMATIC versus ONE_OFF details (D update-a-parent-test-38494548e0, PATCH /email-placement/update/parent-test):
- A one-off test uses SEQUENTIAL sending with your interval, MANUAL content (subject and body, subject max 200 chars) and an explicit list of sender account IDs. Scheduling fields do not apply; it runs immediately when set ACTIVE. It can only be set to ACTIVE while in draft, and "can no longer be edited after it has been activated".
- A recurring test: status ACTIVE turns it on; start_now yes starts a run immediately (needs ACTIVE, recurring only). Frequency enum shows only WEEKLY (description text says DAILY or WEEKLY), no_of_week 1 or 2, days_of_week array.
- Only recurring (AUTOMATIC) tests can have an automation rule attached; one-off and manual are rejected with 400 (D create-automation-rule-41015401e0).
- List endpoint filters: status DRAFT, ACTIVE, INACTIVE; type filter allows only AUTOMATIC; limit default 50, page default 1 (D list-all-parent-tests-38494549e0). So one-off tests may not appear in a type-filtered list (my reading; not stated).

## 3. Configuration fields (update endpoint)

| Field | Values |
|---|---|
| name | string |
| status | ACTIVE or INACTIVE |
| send_as_txt | yes/no |
| is_public | 0 or 1 (public results link) |
| start_now | yes/no |
| throttle (required) | AI or SEQUENTIAL. SEQUENTIAL requires min_intv (minutes, >= 1) |
| st_date, end_date | YYYY-MM-DD, optional |
| st_time, end_time | HH:MM. end_time only required if throttle is AI |
| tz (required) | IANA name |
| frequency, no_of_week, days_of_week | as above (marked required in the schema even though one-off does not use them) |
| recipient_config.rec_providers[] | recipient_type (from the recipient providers endpoint, examples GOOGLE, PERSONAL_GMAIL) and max_emails per recipient type |
| sender_config.senders[] | sender account IDs (24 hex) |
| content_config.type | CAMPAIGN or MANUAL. One-off must be MANUAL |
| content_config.random | 0 or 1 randomize campaign content each run |
| content_config.campaign_ids, step, variation | required for CAMPAIGN; step and variation required when random is off |
| content_config.subject, body | required for MANUAL |

UI equivalents (H 13273010): providers Google (Workspace), Microsoft (365 or Outlook), Personal Gmail; "Send up to 4 test emails per provider"; keep numbers low. Sending mode AI-Optimised (spread across the day, recommended) or Sequential (one email each interval). Start date empty means start immediately, end date empty means run indefinitely. Sender selection manual, or random by tags, provider, or domain. Content from an existing campaign (recommended, supports personalization; first lead's data fills variables) or written manually; "Randomise campaign content" option.

Other endpoints (D): GET /email-placement/get/recipient-providers; GET /email-placement/get/parent-test-detail; POST /email-placement/duplicate/parent-test (parent_test_id, name); DELETE /email-placement/delete/parent-test (ids array); GET /email-placement/list/tests (child runs); GET /email-placement/get/test-detail (child).

## 4. Cost, credits and plans

- Not included in the normal plan. "Automatic email placement testing is offered as an add-on subscription on top of your existing PlusVibe plan" (H 13271457).
- Credits: 1 sender account equals 1 credit per test run, regardless of how many recipient types or seed emails (H 13271457). Example: 5 sender accounts equals 5 credits per run.
- Tiers on the pricing page (P): Starter $19/month, 300 credits per month, recurring automatic tests, Inbox/Promotions/Spam/Missing detection, business recipient providers, test existing campaign content or manual emails, "Spam filter checks (coming soon)". Growth $39/month (marked Popular), 1000 credits, adds personal recipient inboxes, sender randomization by ESP, domain and tags, automatic content randomization, priority support. Scale $89/month, 5000 credits, adds high-volume, multi-sender multi-domain testing, advanced sender and infrastructure randomization, dedicated support.
- Name disagreement: help centre calls the tiers Starter, Pro and Scale (H 13271457, H 13271499); the pricing page names the middle tier Growth. Likely the same tier, not confirmed.
- Pro and Scale features (H 13271499): send to personal inboxes with a configurable number of test emails per recipient type; randomized campaign content; random sender selection by tags, provider, domain. Coming: blacklist monitoring, spam filter analysis, pre-send diagnostics.
- Public share link: results can be shared white-labelled and view-only, no login, no expiry unless revoked, "available on all plans" (H 14312152).
- One-off test cost: not documented. Package notes say creation cost "has not been measured" (Lead Gen Jay package README). Billing alert BILLING_PLACEMENT_SUBSCRIPTION_EXPIRED exists as a webhook alert (D add-a-new-webhook-38494528e0).
- Credit balance endpoint: none found in the placement endpoints (the verification endpoints have a separate credit endpoint). See gaps.md.

## 5. Reading results

- Statuses: Inbox, Promotions, Spam, Missing. Missing means the email was not found in any folder; if not detected within 1 hour of sending it is marked Missing. Often a strong deliverability warning (blocked by your sending server, dropped by the recipient server, filtered before mailbox, routing or reputation suppression) (H 13271457).
- Detection delay causes: SMTP throttling, provider queues, rate limits, reputation traffic shaping (H 13271457).
- GET /email-placement/get/test-summary (parent_test_id; filters rec_type e.g. GOOGLE or MICROSOFT, sender_provider GOOGLE_WORKSPACE, MICROSOFT365, REGULAR_ACCOUNT): inbox_rate, spam_rate, promotions_rate, total_emails, placement_breakdown {inbox, spam, promotions} (D get-test-summary-38494555e0).
- GET /email-placement/get/test-stats (child test_id): summary {inbox_rate, spam_rate, total_sent}, sender_breakdown[] {sender_email, inbox_count, spam_count, inbox_rate} (D get-detailed-test-statistics-38494556e0).
- GET /email-placement/get/test-automatic-result (child test_id, sender_acc_id): per rec_type inbox_count, spam_count, prom_count, miss_count, sent_count, and recs[] {rec_type, res, delivery_time} (D get-test-result-for-a-sender-account-38494557e0).
- Inbox rate in automation rules = share of a run's test emails that landed in the inbox, in percent (D create-automation-rule-41015401e0).
- Weakness for SMTP: the summary filter sender_provider uses REGULAR_ACCOUNT for SMTP/IMAP senders, so custom SMTP inboxes are reported under that provider group.

## 6. Good practice per PlusVibe

- Do not test every sender. Recommended sample 3 to 5% of inboxes; over-testing causes content fatigue and reputation issues (H 13273010, H 13271457).
- Test when something changes (domain, copy, infrastructure, volume), rotate content, match test timing to real campaign hours (H 13271457, H 13273010).
- Seed volume is small on purpose: sending many test emails affects sender reputation (H 13273010).

## 7. Recovery automation from placement tests

Recurring tests can drive an automation rule that pauses or throttles senders when the inbox rate falls. Full detail in automations.md, section "Placement-test rules" (H 15359387, D create-automation-rule-41015401e0).

## 8. MINE: using it at 200 inboxes

- 3 to 5% of 200 is 6 to 10 senders per run. At 1 credit per sender per run, a weekly run on 10 senders is about 40 to 45 credits a month, inside Starter's 300. Daily runs on 10 senders would be about 300 a month. These are my arithmetic from the stated credit rule, not PlusVibe figures.
- Use sender random selection by tag or domain (needs the higher tier per H 13271499) so the sample rotates.
