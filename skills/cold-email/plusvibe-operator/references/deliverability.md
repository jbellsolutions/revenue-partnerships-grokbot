# PlusVibe deliverability: settings, DNS, limits, content, risk controls

Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. P = https://plusvibe.ai/plans. T = https://plusvibe.ai/terms-and-conditions. "MINE" marks my own recommendations. Values not documented are said so.

## 1. Workspace-level and account-level controls that exist

- No page called "Deliverability Settings" exists in the docs I could read (searched help centre, developer docs, plans page). What exists: account Delivery Settings (daily limit, interval, ramp-up, randomize, rest cycles), workspace Settings (Block List, Domain Daily Cap, AI labels, auto follow-up), campaign Safety Settings and Sending Preferences. See gaps.md.
- Workspace settings endpoint (PATCH /workspace-settings/update): blocklist.apply_on (AUTO_FOLLOW_UP, AI_REPLY_AGENT, MANUAL_REPLY, max 10), blocklist.gsheet_url, domain_daily_cap.is_enabled and max_leads_per_day (min 1; enabling requires max_leads_per_day), ai_lead_labeling.labels, auto_follow_up.* (D update-workspace-settings-41824282e0).
- "Deliverability Boost Engine" (test mode, no user action): IP optimisation, geo-smart routing, "Email Consistency Engine" that controls speed and delays. PlusVibe does not share details (H 10388363).
- Auto-rotation of sender emails is on every paid plan; "AI-algorithmic IPs Rotation" is listed for Agency (P). Business plan page text: "algorithmic IP rotation and advanced email provider matching" (P).

## 2. DNS: SPF, DKIM, DMARC, MX

- All four records needed: MX (to receive replies), SPF, DKIM, DMARC (H 8606099).
- Recommended DKIM selectors: Google "google", Office 365 "microsoft", other providers "default" (H 8606099).
- DMARC: configure SPF and DKIM first and let them authenticate for at least 48 hours before activating DMARC (H 8606099). Initial policy "None" with a report address, to monitor without affecting delivery (H 8994183).
- Test records before connecting accounts with MXToolbox, EasyDMARC or DMARCian (H 8606099).
- PlusVibe's check is not just DNS: it sends a test email and inspects the headers of the real message (H 8989315, H 9003168, H 9298690). Statuses: 3 greens means ready; any red or gray must be fixed before campaigns or warmup; "Pending" after connecting takes a few hours and if it never changes the test email was not received (contact support); "Error" means a problem sending through your SMTP server (H 8989315).
  - SPF: green pass, red fail, gray none/softfail/neutral or not checkable. DKIM: green pass, gray if not signed or From domain and signature domain do not match. DMARC: gray if SPF or DKIM passed but there is no policy or p=none (H 8989315). (H 8989315 words the SPF lines in terms of "DMARC authentication"; this looks like a copy error, see gaps.md.)
- API: POST /account/test/vitals with `accounts` (array of emails) returns success_list[].domain/allPass/spf/dkim/dmarc and failure_list (D check-account-vitals-38494500e0). Description says it checks "a list of domains".
- Alignment: H 8989315 says authentication is mandatory and Google blocks emails that fail; blog posts discuss DKIM alignment (https://plusvibe.ai/blog/dkim-alignment-deliverability-killer, not read in full).

## 3. Domains, TLDs, mailboxes per domain

- Do not use the primary business domain; use a secondary domain (trycompany.com style) (H 10836145, H 9298690).
- Use traditional TLDs (.com, .net, regional such as .co.uk). Non-traditional TLDs (.xyz, .online, .site) showed 3 to 5% lower deliverability to Google and Microsoft and up to 20% lower to other ESPs; some smaller ESPs add spam points that can exceed a 5.0 threshold based on domain alone (H 9298675).
- Mailboxes per domain, PlusVibe statements: max 3 (H 9399331); 3 to 5 (H 9298690); 5 to 10 domains per workspace/tenant, 3 mailboxes per domain, 30 to 50 messages per day per address (H 9447732). Azure special setups: up to 99 inboxes per domain, 5 campaign plus 5 warmup per inbox per day (H 13315859).
- Register domains early, domain age matters (H 9298690). Use Google Workspace or Microsoft 365 for best deliverability; be careful with resellers; a low-cost VPS cannot support 1000 mailboxes (H 9298690).
- Use official Microsoft licences, not cracked or shared inboxes (H 13315859).
- Forward new domains to the main domain (optional) (H 8606099).

## 4. Sending limits

PlusVibe statements (they differ by article):

| Item | Value | Source |
|---|---|---|
| Max cold emails per mailbox per day | 30 | H 9399331 |
| Messages per day per address | 30 to 50 | H 9447732 |
| Campaign limit for new accounts (regular Google/Microsoft) | start 3, +1/day, cap 20 to 25, interval 10 to 20 min | H 9447971 |
| Existing accounts migrating | start 20, +3/day, cap 20 to 25 | H 9447971 |
| Azure up to 99 per domain | 5 campaign + 5 warmup per inbox, 10 combined; post warmup 2 to 5 cold per day, gap 20 to 60 min | H 13315859 |
| Warmup per account | max 50 per day | H 9262943 |
| Minimum gap between emails | API min 2 minutes (interval_limit_in_min); bulk add also min 2 | D bulk-update-email-accounts-38494506e0 |
| Campaign daily limit | schedules.daily_limit (>= 0), daily_limit_new_lead (>= 0) | D update-campaign-38494488e0 |
| Per recipient domain per day | workspace cap and campaign cap, in UTC day; workspace cap wins; applies to business/custom domains only, not gmail.com, outlook.com, yahoo.com | H 14728585 |
| Per recipient domain, campaign API | is_max_lead_domain_per_day yes/no and max_lead_domain_per_day (>= 1), applies to campaign and subsequences | D update-campaign-38494488e0 |

- Per-domain sender limit (how many sends per sending domain across mailboxes): no PlusVibe setting found; only account-level limits and the recipient-domain caps above (see gaps.md).
- Randomize Daily Limit: 0 to 50 percent, recommended 40, reduces only, starts after ramp-up (D bulk-update; H 16915358).
- Rest Cycles example: send 5 days, rest 7 days (H 16915358). H says it is particularly important for Google accounts.
- Sending ramp-up counts sending days only; weekends, pauses, errors do not advance it (H 16915358).
- API ceiling quotes: no PlusVibe doc gives a per-mailbox maximum for daily_limit, only min 0.
- Third-party view in a PlusVibe blog: 10 inboxes at 30 each safer than 1 at 300 (https://plusvibe.ai/blog/inbox-rotation-math-stop-guessing-volume, marketing article).

## 5. Inbox rotation rules

- Multiple selected sender accounts send "evenly on rotation, based on the order they are added" (H 8805636).
- email_accounts in update-campaign accepts account IDs or tag IDs (D update-campaign-38494488e0). Tags assigned or removed later update campaigns' account lists automatically (D bulk-assignremove-tags-from-email-accounts-38494508e0).
- Sending Priority slider: 0 to 1, share of daily sends to follow-ups; default 0.5; target, not hard split (D update-campaign; H 8805208).
- Fallback sending: other_email_acc yes/no. Two UI options: for deleted/removed accounts and for errored accounts (disconnect, SMTP, auth errors, temporary provider restrictions) (H 15265029). The API exposes one field other_email_acc.
- Subsequences send from the parent campaign's accounts (D update-campaign-38494488e0). ignore_mailbox_limit (subsequences only) lets subsequence mail go even past a mailbox's daily limit or interval (D).
- Accounts in recovery from an automation rule are held at reduced limits (see automations.md).
- Uneven rotation can overload some inboxes (blog, marketing): https://plusvibe.ai/blog/inbox-rotation-math-stop-guessing-volume.

## 6. ESP matching

- Default ESP matching on all plans: Google to Google, Microsoft to Microsoft, others to any provider (H 10229396).
- Advanced ESP Matching (Business): choose which sender accounts serve which recipient ESP, and use tag-based selection (H 10229396). Located at Campaign, Settings, Sending Preferences (H 10388320).
- If nothing matches, the campaign sends from any account. If few matching senders exist, the campaign waits for them and limits can be affected (H 10229396).
- API: is_esp_match yes/no on update-campaign. The advanced rule fields (which sender maps to which recipient ESP) are not in the update-campaign doc (gap).
- ESP is auto-detected when leads are uploaded (H 10388320).

## 7. Secure Email Gateway (SEG) and risk controls

- SEG detection runs before each send. Campaign field send_seg_email (default yes): yes sends to SEG-protected leads; no skips them (leads stay in the campaign). seg_block_list is a list of SEG codes still skipped while send_seg_email is yes. Codes: APPRIVER, AREA1, AVG, BARRACUDA, CISCO, CLEARSWIFT, CYREN, DUOCIRCLE, FORCEPOINT, FORTINET, HEIMDAL, HORNETSECURITY, KASPERSKY, LIBRAESVA, MAILCHANNELS, MAILGATE, MAILINBLACK, MCAFEE, MESH, MIMECAST, NABLE, PROOFPOINT, RETARUS, SECURENCE, SONICWALL, SOPHOS, SPAMEXPERTS, SPAMHERO, SPAMTITAN, SYMANTEC, TOPSEC, TRELLIX, TRENDMICRO, TRUSTWAVE, VADESECURE, ZIX (D update-campaign-38494488e0; H 15912055).
- Risky emails: send_risky_email yes/no (D update-campaign). The doc does not define "risky"; verification statuses are in the verification endpoints (not covered here).
- Block List: always applied to campaign emails; optional on Unibox replies, AI Reply Agent, Auto follow-ups; Google Sheet sync takes the first 10,000 rows of column A, adds only, runs a few times a day (H 15999723). API: GET/POST/DELETE blocklist endpoints.
- unsub_blocklist yes/no: add unsubscribed leads to the workspace block list (D update-campaign).
- Pause lead on empty variable: pause_on_empty_var, empty_var_pause_limit 1 to 30 default 5 (D update-campaign). Described in campaigns.md.

## 8. Bounce protection

- Campaign: is_pause_on_bouncerate yes/no and bounce_rate_limit (number, "Pause campaign when higher than") (D update-campaign-38494488e0). Launch note example: halt at 3% after at least 100 emails sent (H 10388391). Webhook BOUNCED_EMAIL carries is_camp_paused and bounce_type SENDER or RECIPIENT; SYSTEM_ALERT CAMPAIGN_AUTO_PAUSED fires (D webhooks docs).
- Account level: automation rules on 3d recipient/sender bounce rate (see automations.md). Bounce rates return -1 when 10 or fewer were sent in 3 days (D list accounts).
- Verified leads: add leads with verify_lead true to verify in background; consumes credits (D add-leads-to-a-campaign-38494490e0).

## 9. Content rules

- Spintax: `{{random|Hello|Hey|Hi}}`, `{{fallback|{{first_name}}|Sir}}`; only one variable per spintax section; spaces are kept; `||` makes an empty option; keywords case-insensitive; use Preview Email and Test Email (H 8606174). AI spintax: Use AI, Add Spintax; options for variations per block, number of blocks, subject, creative temperature; do not use Rewrite after generating spintax (H 14730502). 1-click spintax listed on plans page (P).
- Spam word highlighter in previews: "Highlight potential spam and risky words" (H 8682030).
- Plain text: send_as_txt yes/no on update-campaign (D). PlusVibe recommends plain text with no tracking features for deliverability (H 9447879). Preheader (max 100 chars) is not included when sending plain text (D update-campaign).
- Open tracking: is_emailopened_tracking yes/no; "By default, this option is turned off" for the Disable setting per H 9447879 wording (confusing, see gaps.md). PlusVibe says tracking pixels can reduce deliverability "by up to 70%, even with a custom domain" and recommends turning open tracking off (H 9786540, H 10388431). Microsoft blocks images by default.
- Custom tracking domain: CNAME host px, value px.pipl.ai, enter px.yourdomain.com on the account; propagation up to 24 hours (H 9447891). PlusVibe notes a shared tracking domain can hurt deliverability. You can warm the tracking domain (warmup.md).
- Unsubscribe link: toggle in campaign Safety Settings, is_unsubscribed_link yes/no. No test email available for the link (H 8774352).
- Azure warmup guidance: avoid links, images, attachments, tracking pixels in warmup (H 13315859).
- Day variables, Liquid syntax: H 9735657, H 10748974 (not summarised here).

## 10. Placement and monitoring

See placement-tests.md. Placement tests are a health check, not a guarantee (H 13271457). Email health score on dashboard (H 10388508). Replies landing in spam are still detected (H 10388386).

## 11. MINE: practical settings for 200 custom SMTP inboxes

- Keep 3 or fewer mailboxes per domain (about 67 domains for 200 inboxes), traditional TLDs, secondary domains.
- Turn on campaign: send_as_txt yes, is_emailopened_tracking no, is_unsubscribed_link yes, is_pause_on_bouncerate yes with a limit, other_email_acc yes, is_esp_match yes.
- Account: warmup per warmup.md, randomize 40, rest cycles on, interval above 2 minutes; add the automation rule in automations.md.
- Confirm SPF, DKIM, DMARC with POST /account/test/vitals before enabling warmup.
