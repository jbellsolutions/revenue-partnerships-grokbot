# Gaps and disagreements

Everything I looked for and could not find, and where sources disagree. Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. P = https://plusvibe.ai/plans. T = https://plusvibe.ai/terms-and-conditions.

## A. Could not find

1. A documented hard cap on connected inboxes for Business. Only the provisional threshold of 1,000 in T. No statement that price scales with inbox count (P).
2. What happens beyond the 150,000 monthly emails included in Business (P, H 10005524 silent).
3. A help page for the bulk account CSV. The dashboard has one and its sample file gives the columns, so see accounts.md section 3.
4. Any mention of Maildoso, or any provider-specific guidance for it, in help centre, developer docs or plans page. Custom SMTP is covered generically (H 8606065).
5. A maximum number of accounts per bulk-add call, and a maximum ids per bulk-update call. The Lead Gen Jay package enforces 1 to 100 for bulk-update ids (package accounts.js), but PlusVibe's page states none.
6. A page or setting called "Deliverability Settings" at workspace level. Closest: Delivery Settings per account (H 8844048), workspace Settings (D update-workspace-settings-41824282e0), campaign Safety Settings (H 9447879, H 8774352).
7. A per-sending-domain daily limit setting. Only per-account limits and per recipient domain caps (H 14728585).
8. Write API fields for: weekday only warmup, warmup custom tracking domain (warm_ctd is read only in the list response), read emulation, warmup Filter Tag, Skip Holidays, advanced ESP matching rules (which sender serves which recipient ESP), campaign sending preferences beyond is_esp_match.
9. Placement test one-off cost, a credit balance endpoint for placement credits, and how a one-off test is billed.
10. Payload for EMAIL_AUTOMATION_RULE_TRIGGERED (no page exists). The full list of sent_via values for UNIBOX_EMAIL_SENT was truncated in my extraction.
11. Verification credit price and bundle sizes.
12. Plan gating for rest cycles, campaign ramp-up, automations (basic), weekend-only mode, read emulation, business type, warmup schedule.
13. Pages I did not read in full or at all: help articles on the Tech setup guide (H 9447754, 35 KB, skimmed only), 100 cold email templates, cold email strategies, list building, subject lines, copy basics (marketing content, not operating rules), white label (H 12132526, H 13397195), HubSpot, GHL, Calendly, Google Sheets sync, MCP server pages (H 12443858, H 16550544), enrichment pages, Zapier. Developer docs: all 174 listed pages were downloaded, and all endpoint pages were converted to compact specs, but I read in detail only the pages named in these files. Schema stub pages (such as ScheduleV2) are empty or tiny.
14. Blog posts: I fetched but only skimmed https://plusvibe.ai/blog/cold-email-warm-up and https://plusvibe.ai/blog/inbox-rotation-math-stop-guessing-volume; also fetched, not read: dmarc-policy-setting-before-scaling-outbound, plain-text-formatting-avoids-spam-triggers, inbox-placement-testing, inbox-rotation. 642 blog URLs exist; I did not crawl them all. They are marketing copy and often generic (they cite non-PlusVibe sources).
15. Pages needing a browser or login: the app itself (https://app.plusvibe.ai), in-app settings screens, YouTube and Supademo walkthroughs, image-only instructions inside help articles (screenshots carry steps the text omits). Help collection index pages returned no article text.
16. Live behaviour: nothing was tested (no login, no API calls), so every statement is what the pages say.

## B. Sources disagree

1. Warmup ramp recommendations: H 9447952 (start 5, +5, 30% reply, 40/day and 70% after 2 weeks, max 50 at up to 60%), H 9399331 (20/day for 2 weeks), H 9447971 (initial 5, +3, max 20, randomize 20%, reply 35%), H 13315859 (Azure: 5/day, +1, reply 65 to 75%), H 12277791 (reply 35%). No single canonical profile.
2. Randomize range: "up to 40%" (H 12277791), "+/-10%" (H 10359788), example "+/-20%" (D bulk-update warmup_randomize_num, no max). H 12277791 describes only downward variation; D describes +/-.
3. Warmup duration: 2 weeks (H 9399331, H 9447971), 3 to 4 weeks new and 21 days old (H 8606081), about 3 weeks of improvement (H 9298690).
4. Mailboxes per domain: 3 (H 9399331, H 9447732), 3 to 5 (H 9298690), up to 99 for Azure (H 13315859).
5. Cold sends per mailbox per day: 30 (H 9399331), 30 to 50 (H 9447732), 20 to 25 cap (H 9447971), 5 plus 5 Azure (H 13315859).
6. Placement tier names: Starter, Pro, Scale (H 13271457, H 13271499) versus Starter, Growth, Scale (P). Also the help centre says automatic testing is an add-on subscription while public sharing is available "on all plans".
7. Business plan accounts: a search summary claimed pricing-v3 says unlimited; pricing-v3 redirects to https://plusvibe.ai/plans (checked with curl), whose text shows no unlimited accounts claim, so that claim is unverified; T gives 1,000 threshold (see plans-and-limits.md).
8. Webhook alert_type values: current "URGENT for every alert" (D add-a-new-webhook-38494528e0) versus NORMAL, ALERT or URGENT (D webhooks-payload-system-alert-2268661m0).
9. Placement update endpoint: frequency described as "DAILY or WEEKLY" but enum has only WEEKLY; scheduling fields marked required although one-off tests do not use them; list type filter only AUTOMATIC (D update-a-parent-test-38494548e0, D list-all-parent-tests-38494549e0).
10. Bulk-update examples contain fields not in its schema: `warmup_custom_domain` ("warmup_only" example), `disable_slow_rampup` and `disable_slow_warmup_rampup` ("disable_features" example) (D bulk-update-email-accounts-38494506e0). Do not rely on them without testing.
11a. The 50 per day warmup cap (H 9262943) versus the list endpoint example with warmup limit 75 and no schema maximum on warmup_max_daily_limit (D).
11b. warmup_randomize is described as "Randomize warmup email timing" in bulk-update but as randomizing daily volume in the list endpoint and help (D, H 12277791).
11. Unit mismatches: account warmup_reply_rate is 0 to 1 in the write API while list returns integer percent (40); automation reply rate is 1 to 100 (D).
12. Open tracking default: H 9447879 says the Disable Open Rate Tracking option "By default ... is turned off" (so tracking on) while P says "No open tracking by default"; H 9786540 recommends turning tracking off. Check each campaign's is_emailopened_tracking by read-back.
13. SPF status text in H 8989315 describes SPF colours as "passed DMARC authentication" (looks like a copy error).
14. EMAIL_AUTOMATION_RULE_TRIGGERED appears in the Create automation rule page but not in the webhook event list (D webhooks-overview-2268181m0).
15. Brand and domain: pages mix pipl.ai and plusvibe.ai (tracking CNAME target px.pipl.ai in H 9447891; app help links named pipl-ai). PlusVibe rebranded from pipl.ai (P banner).

## C. What the live API did (900 Maildoso inboxes, 2026-11-07)

Source: our own calls from `agents/gtm-box/cold/` (push_mailboxes.py, warmup.py). Trust these over the docs where they differ.

1. Bulk add (`/account/bulk-add-regular-accounts`) answers `{"status": "success"}` at once and processes after. 900 inboxes sent in 9 calls of 100 were all listed, and all ACTIVE, about five minutes later. No result email came for that run.
2. The account list (`/account/list`) gives each row's id as `id`. Workspaces come back with `_id`. Don't assume one key across endpoints.
3. Campaign update (`PATCH /campaign/update/campaign`), all three refused with 400 "Validation error" although the docs show otherwise:
   - `schedules` must be a list of schedule objects, not one object.
   - `schedules[0].start_date` (YYYY-MM-DD) is required. It doesn't launch the campaign.
   - `days` lists only sending days, each `true`. A `false` day is refused ("Day 6 must be true").
4. `PUT /account/bulk-update` set `first_name` but ignored an empty `last_name`: the old last name stayed. To change a sender's full name, send a real last name.
5. Account settings and `bulk-update-warmup` took 100 ids per call with no error.
6. Instantly's `POST /api/v2/accounts/warmup/disable` returned 409 Conflict on a batch that also named inboxes it didn't have, or had already paused. Naming only inboxes with `warmup_status` 1 went through, 100 a call, every time. warmup.py now does that and waits out a 409.
