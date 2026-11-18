# Maildoso API reference (condensed)

Sources: OpenAPI at https://developers.maildoso.com/openapi.json (fetched read-only 2026-11-07, v0.1.0, title "maildoso_api"); https://intercom.help/maildoso/en/articles/16306972 ; https://blog.maildoso.ai/recommendations/automate-infrastructure-api-mcp . No call was made with a key.

## Auth and base
- Header: `Authorization: Bearer <PAT>`. Spec security scheme: http bearer, "JWT Bearer token or PAT from Logto". One Personal Access Token works for the REST API and the MCP server; it has full account access.
- Where to find the PAT: the spec and the blog say Settings > API Keys; the help centre says account email (top right) > Settings > General > API token (Copy / Regenerate) [h:16306972, h:18297265]. Sources differ; the help centre wording is newer.
- Base URL: not stated in the spec (servers is null). The blog's example is `https://api.maildoso.com/v1/user/me`; the help centre names backend api.maildoso.com. MCP endpoint: `https://mcp.maildoso.com/mcp` (help centre).
- Not documented: rate limits, pagination caps other than limit/offset, webhooks. No bounce/DSN feed exists via API (help centre h:16231432).

## Endpoints (method, path, purpose)
User
- GET /v1/user/me : current user (creates the user record on first call; good auth check).
- GET /v1/user/data ; POST /v1/user/data ; PATCH /v1/user/data : registrant data needed for ICANN-compliant domain registration.
- GET /v1/user/settings : user settings including the PAT.
- POST /v1/user/regenerate_auth_pat : delete the PAT and create a new one (old one stops working).
- GET /v1/user/stats : resource quotas (domains, maildoso_accounts, google_accounts, warmups, domains_compensation, renewed_domains_for_replacement_last_period, prewarmed_domains); available = total - in_use. No per-recipient or bounce data.
Domains
- GET /v1/user/domains : list domains; filters keyword, type, provider, IDs, date range, ordering; includes nameservers and domain_status (ACTIVE etc.).
- POST /v1/user/domains : buy domains. Body: domains[], redirect_to[]. TLDs not allowed: .ca .app .cloud .site .tech .xyz .eu .us .fr .nl. Unavailable names come back result "failure" with no id. Returns 202 with task_id (blog and help h:14166643). One domain per call with random 10-500 s gaps is Maildoso's advice for avoiding Spamhaus batch listing [h:14166643].
- POST /v1/user/domains/search : search availability with variations (same TLD exclusions).
- PUT /v1/user/domains : change a domain's settings. Body: id, redirect_to.
- PUT /v1/user/domains/tracking : turn Global Custom Domain Tracking on/off (default on).
- GET /v1/user/domains/provider-availability : whether domains can be used with Google Workspace or Maildoso SMTP.
- POST /v1/user/domains/external : connect your own domains. Body: domains[], redirect_to[], providers[]. Replaces DNS; set the two returned nameservers at the registrar within 24 h; Cloudflare Registrar unsupported. Error "Domain limit exceeded. Current: 0, Limit: 0" = no domain capacity attached to the plan [h:15431396].
- POST /v1/user/domains/restart-setup : restart setup for existing domains. Body: domain_ids[].
Email accounts (mailboxes)
- GET /v1/user/accounts-lookup : paginated mailbox lookup (the mailbox-lookup endpoint). Each item carries `imap` and `smtp` connection details for plugging into a sequencer; both null for Google accounts (use OAuth). Params: limit (omit = all), offset, created_at, order_by, keyword (substring of email), domains_ids, forwarding_accounts_ids, forwarding_accounts, redirect_urls, reputations, provider, status, is_admin, sequencer_status (failed|completed|none), short (only id and provider). Status values: active, inactive, pending, setup_awaiting, setup_processing, failed, deletion_scheduled, suspended_domain_expired, suspended_prewarmed_domain_paused, suspended_technical_issue.
- POST /v1/user/accounts : create mailboxes; body is an ARRAY of items with email_account, first_name, last_name, forwarding_account_id, password, provider, is_active, picture_url, skip_sequence, vendor_uuid. Only inside already-bought slots (API creation beyond slots makes the account Overlimit, h:17170897).
- DELETE /v1/user/accounts : body array of integer ids. SMTP deleted immediately; GW 409 while still setting up, else scheduled for the next renewal date; deletion removes all messages.
- PUT /v1/user/accounts/{account_id} : change forwarding_account_id, password, first_name, last_name, picture_url.
- GET /v1/user/accounts/{account_id}/totp : generate a TOTP code for a Google account (account must be ACTIVE).
Forwarding / Master Inbox
- GET /v1/user/accounts/forwarding : mailboxes and their forwarding accounts.
- PUT /v1/user/accounts/forwarding : set a mailbox's forwarding. Body: email_id, forward_id.
- GET /v1/user/forwarding-lookup : search/filter/paginate forwarding (Master Inbox) accounts.
- POST /v1/user/forwarding : create a forwarding address (example body: email on maildoso.email, first_name, last_name, assignment "MASTER").
- DELETE /v1/user/forwarding : bulk delete forwarding accounts (array of ids).
- POST /v1/user/forwarding/password : reset a forwarding account password.
Pre-warmed domains (beta; not in the old reseller API)
- GET /v1/user/prewarmed-domains/catalog : warmed domains free to activate.
- POST /v1/user/prewarmed-domains/activate : rent domains, all or nothing. Body: domain_ids[], redirect_url.
- GET /v1/user/prewarmed-domains : your rented domains.
- DELETE /v1/user/prewarmed-domains : delete domains (their mailboxes are deleted; subscription NOT reduced).
- GET /v1/user/prewarmed-domains/overdue-invoice : the invoice to pay first, or null.
- PATCH /v1/user/prewarmed-domains/redirect : one redirect URL for listed domains (null removes; effective within 15 min).
Warmup services
- GET /v1/user/services/warmups : list configured warm-up services.
- POST /v1/user/services/warmups : add a warm-up service config.
- PUT /v1/user/services/warmups : update configs by warmup_ids.
- DELETE /v1/user/services/warmups/{id} : remove one.
Billing
- GET /v1/billing/subscriptions : list subscriptions (optional status filter: incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, paused). Each has plan type, price, renewal_date, resources. Subscriptions cannot be bought or changed by API [h:15579323].
Sequencers
- GET /v1/sequencers : sequencer platforms with your connection status.
- POST /v1/sequencers : add a sequencer. Body: platform, sequencer_login, sequencer_password, sequencer_workspace, api_key (Instantly), app_url and client_id (EmailBison), smartlead_consent_url.
- PUT /v1/sequencers : update one (id, platform, login, password, api_key, workspace).
- POST /v1/sequencers/export : export mailboxes to a sequencer. Body: sequencer_id, account_ids[]. Supported providers: google ONLY. Status appears in the account's exported_to_sequencers field.

## Notes
- Sequencers: the export endpoint is for Google Workspace mailboxes only; SMTP mailboxes must be pulled from accounts-lookup (or the dashboard CSV) and added in the sequencer yourself. The blog claims export to Instantly, Smartlead and Saleshandy in one call; the spec and help centre limit export to Google accounts. Trust the spec. PlusVibe appears nowhere in the spec (zero mentions); Maildoso's GW sequencer tab lists Plusvibe, but the API platform enum is not published beyond examples ("instantly", "smartlead").
- Warmup services are NOT warmup execution. system_id values: trulyinbox, allegrow, supersend, instantly, smartlead, manyreach, nureply, mailivery, lemwarm, custom. warmup_meta.warmup_exclude = tags to keep out of forwarding; warmup_meta.api_key required for smartlead only. For PlusVibe use system_id custom with its warmup tag (my inference). Warmup volume itself is set inside the warmup tool (h:15435524). The "warmups" quota in stats is the legacy Premium warmup (closed to new buyers).
- Mailbox lookup for credentials: accounts-lookup returns imap/smtp blocks; known values are smtp.maildoso.com:587 STARTTLS, IMAP host per mailbox on port 993 [h:16431129].
- API-created mailboxes: wait for domain_status ACTIVE and 24 h after created_at on freshly bought domains [h:14166643].
