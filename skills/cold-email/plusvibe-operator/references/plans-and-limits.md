# PlusVibe plans, limits, rate limits and the 300-inbox question

Source key: P = https://plusvibe.ai/plans (page fetched 2026-11-06; same page as https://www.plusvibe.ai/pricing-v3). T = https://plusvibe.ai/terms-and-conditions. H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. MINE = my note.

## 1. Answer: do 300 inboxes fit the Business plan at $77 a month?

Short answer from the sources: yes on the documented numbers, with a caveat.
- No connected-inbox cap is stated for Personal or Business on the pricing page (P). The only account cap shown is the free trial: "Connect up to 3 Email Accounts" (P).
- The terms of service, under "Provisional Usage Thresholds", state: "Personal Plan: 300 connected email accounts; Business Plan: 1000 connected email accounts; Enterprise & Agency Plans: thresholds tailored to your specific needs, subject to per-case approval. Exceeding these thresholds requires manual approval and may be subject to additional fees." (T). So 300 is inside Business's 1,000 and sits exactly at Personal's 300.
- The same terms say fair-use limits apply even on "unlimited plans", name "Connecting an excessive number of email accounts without valid business needs" as unreasonable use, and allow warnings or action for breaches (T, Fair Use of the Service). They also say limits are based on infrastructure stability, bounce rates and compliance, with raises by request.
- The monthly send allowance is a separate limit: Business lists "150,000 Emails Included" per month and "Cold Emails Limit 150,000/month" (P). What happens beyond 150,000 is not stated (gap). Per MINE: 300 inboxes at 30 per day for 22 sending days is 198,000, so volume, not inbox count, would be the binding number if you send at that rate; at about 17 per inbox per day it is roughly 112,000. At 200 inboxes and 30 per day for 22 days it is 132,000.
- A user testimonial on the page mentions an early lifetime deal with "unlimited inbox with 250K monthly sending limits" (P). Anecdote, not a plan term.
- One search-engine summary I retrieved claimed the plans page says "Connect up to 3 Email Accounts" under Business. In the raw page text I fetched, that line belongs to the free trial card only. I did not find "Unlimited" connected accounts on the pricing page text I fetched (the summary claimed pricing-v3 does; pricing-v3 redirects to /plans, verified with curl). Treat that claim as unverified.
- Not found: any statement that the $77 price changes with inbox count. Pricing varies only by enrichment credit tier (see below). Confirm with PlusVibe support in writing before relying on it.

## 2. Plans (P)

Prices shown with the Monthly/Yearly toggle ("Get 2 Months Free" yearly). Monthly view / yearly view:

| Plan | Monthly view | Yearly view | Included |
|---|---|---|---|
| Free trial | $0 for 14 days | | 1,000 emails, 100 enrichment credits, 3 inbox warm-ups, connect up to 3 email accounts, basic warmup and deliverability monitoring |
| Personal | $37 (1K credits), $45 (3K, +$8), $52 (5K, +$15), $58 (7K, +$21) | $30.8, $37.5, $43.3, $48.3 | 25,000 emails/month; 30,000 active leads in campaigns; 300,000 leads in lists; basic warmup; basic ESP matching; unified inbox; AI reply sentiment detection; auto-rotation of senders; unlimited campaigns; AI sequence writer; basic integrations; basic support |
| Business (Popular) | $77 (3K credits), $92 (7K, +$15), $119 (15K, +$42), $165 (30K, +$88), $220 (50K, +$143) | $64.2, $76.7, $99.2, $137.5, $183.4 | Everything in Personal plus 150,000 emails/month; 100,000 active leads; 1,000,000 leads in lists; advanced warmup settings and language models; advanced ESP matching; AI Reply Agents; webhooks and advanced integrations; Zapier and Make triggers; API access; priority support |
| Agency | from $497 (monthly view), $415 (yearly view) | | 500,000+ emails/month; 1,000,000+ active leads; unlimited list leads; isolated sending server; dedicated connector IPs and rotation; dedicated client workspaces; in-depth sender reputation checks; specialised warmup recovery scheme; white labelling; unlimited users; "Advanced+ Automations"; AI-algorithmic IP rotation; advanced AI reply agents; custom integrations; dedicated support and private Slack |

Other rows in the comparison table (P): "Dedicated Workspaces" shows 1, 1, Custom and "Add Extra Workspaces" shows "starting at $29/mo" and "Included" (the column mapping did not extract, so I cannot say which plan gets which); Unlimited team members; Slack alerts, HubSpot, Go High Level, Zapier, Make, webhooks, own OpenAI key, API access and "Custom MCP Server" are listed. Which plan each tick belongs to did not extract (gap). Help article H 10388485 says unlimited team members and Slack alerts were opened to Personal.

Done-for-you email setup (P): Google Workspace $4 per inbox per month, Microsoft 365 $4.5 per inbox per month, Microsoft Azure $49 per domain per month, a custom Done-for-you Email Setup at $1,500 per month, and a managed growth offer (price not captured). Terms say DFY inbox licences cannot be reinstated once cancelled and are non-refundable (T).

Placement test add-on (separate subscription): Starter $19/month 300 credits, Growth $39 1,000, Scale $89 5,000 (P). Details in placement-tests.md.

## 3. Plan gates found in the docs

- API key: Business plan (D getting-started-2268178m0).
- AI Reply Agent: Business and above (H 13164721, H 14312099). Subsequent replies: Business and above.
- Advanced ESP matching: Business (H 10229396).
- Auto-assign Unibox threads: Business (H 14303088).
- Additional AI prompt for label categorization: Business (H 9581731).
- Randomized warmup limit: Business (H 10359788). Advanced warmup: Business (P).
- Webhooks: Business (P). H 9064596: only Workspace Admins generate API keys and edit webhooks.
- Public placement-test share link: all plans (H 14312152).

## 4. Usage limits (H 10005524 "Understanding System Limits and Restrictions")

- Campaign leads: Personal 30,000, Business 100,000 (all leads in any campaign counted, even completed or paused).
- List leads: Personal 300,000, Business 1,000,000.
- Inbox emails stored 9 months. "Other Replies" kept 7 days.
- Warmup emails per account per day: max 50 (H 9262943).

## 5. API limits (D getting-started-2268178m0)

- Rate limit: 5 requests per second; exceeding it temporarily blocks requests. Some database-heavy endpoints use request weighting and count more. Contact PlusVibe if you hit limits consistently.
- Auth header x-api-key; the key reaches all workspaces under the account; workspace_id required on every endpoint. API key page https://app.plusvibe.ai/v2/settings/api-access/. Package client retries GET on 429 and 5xx only (third party).
- Per endpoint caps: bulk delete accounts 1,000; recovery details 100 emails; warmup stats 100 mailboxes per page and 14 day window; list parent tests limit default 50; webhook alert arrays capped at 10; blocklist Google Sheet 10,000 rows.
- Bulk account update ids: no cap stated by PlusVibe.

## 6. Credits

- Enrichment credits: tier on the plan (1K to 7K Personal, 3K to 50K Business) (P). Free tools and 1,000 free enrichment and personalization credits: H 9399250.
- Email verification credits: GET /verify/credits returns credits_remaining (organization-wide) and credit_per_verification; emails with an error result are not charged (D get-email-verification-credits-45793860e0). Price per credit and bundle sizes: not found. `verify_lead true` on add leads consumes credits.
- Placement test credits: 1 per sender account per run (H 13271457).
- Verification of leads can use the built-in verifier or third parties inside warmup checks (H 8606081).

## 7. Workspaces and roles (H 9064596)

Roles: Workspace Admin (full control, invites, API key, webhooks) and Workspace User (campaigns and leads). Org roles include OWNER and WORKSPACE_ADMIN in the move-accounts doc (D). Agency plan gives client workspaces and white label (H 12132526, H 13397195).
