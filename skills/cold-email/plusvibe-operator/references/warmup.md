# PlusVibe warmup: every setting, range, plan and ramp guidance

Sources are named beside each fact. H = help article https://help.plusvibe.ai/en/articles/<id>. D = developer docs page https://developer.plusvibe.ai/<page>.md. P = https://plusvibe.ai/plans. Anything marked "MINE" is my recommendation, not PlusVibe's. "Not documented" means I looked and found nothing.

## 1. What warmup is (as PlusVibe describes it)

- Warmup emulates conversations between PlusVibe users who also enabled warmup; recipients are "guaranteed to open" and many reply (H 8606071).
- Pool: P says "Private warm-up pool with 350k+ high-quality accounts", "Humanized Warm-Up behavior: email chains, mark as important, open, not-SPAM", "99.7% deliverability guarantee".
- Warmup moves warmup emails out of spam and promotions into the primary folder (H 10388705). It does not rely on the Google API (H 8606081).
- Warmup has no calendar end. Keep it on for as long as the account is used (H 8606081, H 9399331).
- Newly connected accounts start warmup as soon as it is enabled, and sending/receiving should begin "within couple hours" (H 8606073, H 8606081).

## 2. Plan requirements

| Capability | Plan | Source |
|---|---|---|
| Basic warmup (daily limit, increase per day, reply rate) | Personal and up. Free trial: "3 Inboxes Warm-Up Included" | P |
| "Advanced Warm-up settings: warmup custom tracking domain, email signatures, industry-specific content, volume randomization" | Business (comparison table lists Advanced Warm-up settings and Language Models under Business) | P |
| Randomized warmup limit | "Available now for Business plan users" | H 10359788 |
| Warmup ramp-up and campaign ramp-up | No plan stated. Announced for "Email Accounts > Settings > Delivery Settings/Warmup Limits" | H 10359788 |
| Weekend only mode, read emulation, business type, schedule | Not stated per plan. They sit under "Advanced Warmup Settings" (H 8606088, H 12277791) | H 8606088 |
| Rest Cycles, Randomize Daily Limit (campaign side) and Campaign Ramp-Up | No plan stated | H 16915358 |
| API access (needed to drive any of this by API) | Business ("You need to be on the Business Plan to be able to access the API key") | D getting-started-2268178m0 |

Conclusion for plan: Business is the plan that lists advanced warmup. See plans-and-limits.md.

## 3. Basic warmup settings

Where: Email Accounts and Warm-up tab, pick account, Warmup, Settings (H 8606073, H 12277791).

| UI setting | API field (PUT /account/bulk-update) | Range / unit | Notes |
|---|---|---|---|
| Filter Tag | not documented in API | n/a | Organises warmup emails into a folder in the inbox (H 8606073) |
| Daily limit (max warmup emails per day) | warmup_max_daily_limit | integer, min 1 | PlusVibe says it limits warmup emails to 50 per day per account (H 9262943). The API schema shows no maximum for warmup_max_daily_limit and a list example shows warmup limit 75, so the 50 is a stated policy, not a verified API validation. Daily limit is "more of a guideline"; the algorithm may send fewer (H 8606081) |
| Warmup Email Ramp-Up toggle ("slow rampup") | bulk_warmup_is_slow_rampup | yes or no | "Disabling Slow Warmup ... advisable only for older, already warmed-up email accounts" (H 8606088) |
| Initial Daily Email Limit | warmup_initial_daily_limit | integer, min 1 | Day 1 warmup volume when ramp-up is on (H 8606073) |
| Daily Increment In Emails | warmup_pace_increment | integer, min 1 | Added to the limit each day (H 8606073) |
| Reply rate % | warmup_reply_rate | number 0 to 1 (0.25 = 25%) | UI shows a percent. The list endpoint returns reply_rate as an integer such as 40 (D list-all-email-accounts-in-the-workspace-38494498e0). Automation rules use 1 to 100 instead (D create-automation-rule-41015401e0) |
| Custom words | warmup_custom_words | string | Custom warmup keywords, example "business, meeting, proposal" (D bulk-update-email-accounts-38494506e0) |

Constraint from bulk-update: "Rampup daily limit plus increment cannot exceed total daily limit" returns 400 (that example error is shown under campaign sending ramp-up; applies to the sending ramp-up fields bulk_rampup_daily_limit and bulk_rampup_daily_inc and daily_limit) (D bulk-update-email-accounts-38494506e0).

## 4. Advanced warmup options (all of them)

Source for the list: H 12277791 (Advanced Warmup Settings), H 8606088 (Overview), H 10388690 and H 10388713 (launch notes).

1. Randomized Warmup Limit
   - Percent, "up to 40%". System sends between (100% minus that %) and 100% of the daily limit. Daily limit 50 with 20% sends 40 to 50. Daily limit 3 with 20% sends 2 or 3 (H 12277791).
   - Tip from PlusVibe: 3% usually rounds up to the full limit; use 30 to 40% for visible variation (H 12277791).
   - API: warmup_randomize (yes/no) and warmup_randomize_num (integer, min 1, "20 means +/-20%", no maximum stated) (D bulk-update-email-accounts-38494506e0). Note the UI doc says it only reduces; the API description says +/-. See gaps.md.
2. Business Type
   - Warmup content uses industry keywords. Leave blank for generic (H 12277791). "Best practice here is to select a category that matches your target prospect category the most" (H 8606088).
   - API warmup_business_type enum (17 values): Artificial Intelligence and Machine Learning; Consulting Firms; Cryptocurrency and Blockchain; Digital Marketing Agencies; E-commerce Businesses; Education and Training Services; Financial Services; Healthcare and Wellness Providers; Hospitality Services; Human Resources and Recruiting; Legal Services; Manufacturing Companies; Non-profit Organizations; Pharmaceuticals and Biotech; Real Estate Agencies; Software and Technology Companies; Transportation and Logistics (D bulk-update-email-accounts-38494506e0).
3. Warmup Schedule
   - Outgoing warmup follows the schedule; incoming warmup replies can arrive any time (H 12277791). H 8606088 says to pick the time zone you send campaigns in "to avoid spikes".
   - API warmup_schedule object: tz (IANA name), from_time and to_time (HH:MM 24h, regex ^([01]\d|2[0-3]):([0-5]\d)$), days (array of full weekday names, minimum 5 entries). All four keys required (D bulk-update-email-accounts-38494506e0).
   - When no schedule is set the list endpoint returns warmup_schedule null, meaning warmup runs every day at any time (D list-all-email-accounts-in-the-workspace-38494498e0).
4. Warmup Custom Tracking Domain
   - Adds your custom tracking domain to warmup emails so the domain gains reputation (H 12277791, H 8606088). Read-only API field payload.warmup.advanced.warm_ctd (boolean). The bulk-update schema has no warm_ctd field, but its "warmup_only" example sends `warmup_custom_domain: 'yes'` (D bulk-update-email-accounts-38494506e0). Unresolved, see gaps.md.
5. Warmup Signature
   - Includes your real signature in warmup emails (H 12277791). API warmup_signature yes/no.
6. Warmup Reply Rate
   - "Recommended value: 35% (especially if deliverability drops)"; raise it when deliverability decreases (H 12277791).
7. Weekend Only Mode (name as written in H 8606088)
   - Accounts do not send on weekends but still receive warmup emails (H 8606088). Read-only API field payload.warmup.advanced.weekday_only. No write field found in bulk-update.
8. Read Emulation
   - Uses headless browsers to simulate reading warmup emails. "Disabled by default" because SMTP providers have their own tracking and enabling it "could potentially interfere with these analytics" (H 8606088). No API field found.
9. Monitoring blacklists: "You will be notified via email if your account gets blacklisted" (H 8606088).

## 5. Sending-side ramp-up, randomize and rest (not warmup but set in the same bulk-update call)

From D bulk-update-email-accounts-38494506e0 and H 16915358 (Randomize Daily Limit, Rest Cycles, Campaign Ramp-Up):

| Setting | API field | Range | Behaviour |
|---|---|---|---|
| Campaign daily limit per account | daily_limit | integer >= 0 | |
| Minimum interval between emails | interval_limit_in_min | integer >= 2 | Bulk add: values below 2 raised to 2 |
| Sending ramp-up on | bulk_is_slow_rampup | yes/no | |
| Start at | bulk_rampup_daily_limit | integer >= 1 | |
| Increase per sending day | bulk_rampup_daily_inc | integer >= 1 | Days with no sends do not advance the ramp; step rolls at 00:00 UTC (D list-all-email-accounts) |
| Randomize Daily Limit | bulk_limit_rand_pct | 0 to 50, 0 disables | Reduces the daily limit by a random amount up to that percent; starts after ramp-up completes; recommended 40 (D bulk-update, H 16915358) |
| Rest Cycles on | bulk_is_auto_pause | yes/no | When yes, both day fields required |
| Send for (days) | bulk_auto_pause_send_days | 1 to 365 | Only days with campaign sends count |
| Rest for (days) | bulk_auto_pause_days | 1 to 365 | Campaign sending 0 during rest; warmup continues. Changing the values restarts the cycle; resending the same values does not |
| Exit recovery behaviour | force_exit_recovery | 0 or 1, default 1 | 1 ends recovery for accounts the request touches (limit, ramp-up and warmup-limit fields). 0 keeps recovery and skips those fields for them |

Read side: payload.warmup_limit_today, payload.campaign_limit_today, payload.sending_rampup.current_step/current_limit, payload.rest_cycles.state/sending_day/resume_at, payload.warmup_rampup.* (D list-all-email-accounts-in-the-workspace-38494498e0).

## 6. How PlusVibe says to ramp (all variants, they differ)

1. H 9447952 (Email Warm-up): start at 5 warmup emails per day per account, increase by 5, aim for 30% reply rate. After two weeks, raise to 40 per day and a 70% reply rate (the article says "during outreach"). Maximum recommended 50 per day with a reply rate up to 60%.
2. H 9399331 (Cold Email Limits and Benchmarks): at most 3 accounts per domain; warm up at least 2 weeks; 20 warmup emails a day using default settings, ramping gradually; keep warmup on indefinitely; cold sending at most 30 per account per day.
3. H 9447971 (Optimal Email Limit Settings), for regular Google and Microsoft accounts. It states it does NOT apply to "50/100 inboxes per domain" Azure setups:

| | New accounts | Existing accounts migrating from other tools |
|---|---|---|
| Warmup time frame | 2 weeks | first 1 week |
| Total max warmup emails | 20 | 20 |
| Initial warmup limit | 5 | 15 |
| Daily ramp-up | 3 | 3 |
| Randomized warmup limit | 20% | 20% |
| Reply rate | 35% | 35% |
| Campaign time frame | about 1 month | first 1 week |
| Total max campaign emails | 20 to 25 | 20 to 25 |
| Initial campaign limit | 3 | 20 |
| Daily campaign ramp-up | 1 | 3 |
| Time interval | 10 to 20 minutes | 10 to 20 minutes |

   Also: keep warmup active when campaigns run at full capacity. If campaign reply rate drops, lower campaign volume or pause campaigns, run warmup only for 1 to 2 weeks and raise warmup reply rate to 70% or higher (H 9447971). Apply via Bulk Actions, Edit Settings, Warm-up or Account tabs.
4. H 8606081 (Warm-up FAQs): new domains/accounts warm at least 3 to 4 weeks; older ones at least 21 days before cold outreach.
5. H 13315859 (Azure inboxes, up to 99 inboxes per domain): days 1 to 14 send 5 warmup emails per day, ramp +1 per day, target reply rate 65 to 75%, interval at least 20 to 60 minutes, avoid links, images, attachments, tracking pixels. Day 15 onward: 2 to 5 cold emails a day plus 5 warmup a day. Safe limit stated: 5 campaign plus 5 warmup per inbox per day, 10 combined. Recommends consulting the infrastructure provider.
6. H 9298690: warmup normalises over about three weeks; disable spam filters on the account before enabling warmup so warmup mail is not blocked; some warmup mail landing in spam at first is normal.
7. Randomizer launch note says "varies your daily sending limit by +/-10%" (H 10359788), older than the 40% option in H 12277791.

Why the 50 cap exists: more than 50 warmup plus campaign mail risks the account being labelled a bulk sender (H 9262943).

Resetting warmup: remove the accounts for 2 days (UTC) or lower the sending limit for 2 to 3 days (H 8606081).

## 7. Warmup stats, health and endpoints

- Warmup health scores 7d overall, Google, Microsoft, other; 1d miss warmup rate; bounce rates (3d total, recipient, sender, -1 when 10 or fewer sent) (D list-all-email-accounts-in-the-workspace-38494498e0). Account health score is shown on dashboard and sortable (H 10388508).
- GET /account/warmup-stats/bulk: per mailbox, date range at most 14 days (stats kept 14 days), 100 mailboxes per page, include_chart, email_acc_ids up to 100 (D get-warmup-stats-per-mailbox-43864836e0).
- GET /account/warmup-stats/overall: workspace totals; filters provider, tags (NO_TAGS allowed), domain (domain cannot combine with provider or tags) (D get-warmup-stats-workspace-level-43871189e0).
- POST /account/warmup/enable and /account/warmup/pause (single, by email); PATCH /account/bulk-update-warmup (ids, warmup_status ACTIVE or INACTIVE) (D).
- Bulk update has no stated cap on ids in the PlusVibe doc. Lead Gen Jay's package enforces ids 1 to 100 (package accounts.js, not PlusVibe documentation).

## 8. Troubleshooting statements

- Warmup sent but not received: if third-party verifiers (Zerobounce, Emailable, MillionVerifier) cannot verify a newly connected account, PlusVibe pauses sending to prevent bounces (H 8606081).
- "Spam Box Not Found" ban message: warmup needs a spam folder it can read. Make sure a dedicated spam folder exists, move one email to spam, reconnect (H 8606081).
- Warmup bounced: ESP anti-spam too strict (DreamHost example); relax it (H 8782199).
- Large numbers of incoming warmup emails: pool detected a possible issue with the account, temporary (H 8606081).
- Warmup enabled but not sending: probably outside the account's warmup schedule (H 8606081).
- Changing only the sender name does not reset warmup; reconnecting keeps stats (H 8606081).
- Account in ERROR: warmup becomes INACTIVE until reconnected (H 8860007).

## 9. MINE: application to 200 custom SMTP inboxes (not PlusVibe statements)

- Plan: Business. Personal is described as "Basic Warm-Up".
- Set warmup per account by API using PUT /account/bulk-update with ids in batches (the doc states no batch cap; I would batch at 100 as the package does), then PATCH /account/bulk-update-warmup to ACTIVE.
- Custom SMTP accounts are regular accounts, so H 9447971 numbers (initial 5, +3 per day, max 20, randomize 20%, reply 35%) are the closest documented profile. H 9399331 and H 9298690 suggest max 3 mailboxes per domain and warmup of 2 to 4 weeks.
- Set warmup_schedule to the hours you will send campaigns; leave business type matching the target industry.
- Verify read-back with GET /account/list (warmup_rampup, warmup_limit_today, health scores) rather than trusting the 200 response.
