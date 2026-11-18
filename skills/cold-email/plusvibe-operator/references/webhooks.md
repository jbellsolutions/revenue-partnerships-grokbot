# PlusVibe webhooks

Source key: D = https://developer.plusvibe.ai/<page>.md. H = https://help.plusvibe.ai/en/articles/<id>. Plan: webhooks are listed under Business ("Webhooks & Advanced Integrations") at https://plusvibe.ai/plans. Setup page in the app: https://app.plusvibe.ai/v2/settings/webhook/ (D webhooks-overview-2268181m0).

## 1. Event types (D webhooks-overview-2268181m0)

| webhook_event value | Fires when |
|---|---|
| FIRST_EMAIL_REPLIES | A lead replies for the first time, excluding Out of Office and automatic replies |
| ALL_EMAIL_REPLIES | Any lead reply, first and later |
| ALL_SUBSEQUENCE_REPLIES | A lead replies inside a subsequence. Same payload as all replies plus subseq_id and subsequence_name; camp_id and campaign_name are the parent campaign |
| ALL_POSITIVE_REPLIES | A reply detected as positive sentiment, first or later |
| EMAIL_SENT | A campaign email is sent ("Campaign Emails Sent"). Not the same as UNIBOX_EMAIL_SENT |
| BOUNCED_EMAIL | An email bounced |
| UNIBOX_EMAIL_SENT | An email sent from Unibox: manual reply or compose, scheduled messages at actual send time, AI-triggered replies, automated follow-ups. Forwards excluded |
| LEAD_MARKED_AS_{LABEL} | A label is applied to a lead by AI or manually. Label name in all uppercase, for example LEAD_MARKED_AS_INTERESTED, LEAD_MARKED_AS_NOT_INTERESTED. Custom labels work as LEAD_MARKED_AS_X |
| SYSTEM_ALERT | Workspace needs attention. You pick which alerts |
| EMAIL_AUTOMATION_RULE_TRIGGERED | Mentioned only in the Create automation rule page ("the EMAIL_AUTOMATION_RULE_TRIGGERED webhook fires"). Not in the webhook overview or add-webhook docs. Payload undocumented (gap) |

## 2. System alerts (D add-a-new-webhook-38494528e0, D webhooks-payload-system-alert-2268661m0)

When event_types includes SYSTEM_ALERT: `camp_ids` must be ["ALL"] and `alerts` is required (map alert name to {type}). Alert names:
EMAIL_ACCOUNT_DISCONNECTED (sending account went into error), EMAIL_ACCOUNT_FORWARDING_BOUNCED, INTEGRATION_DISCONNECTED, INTEGRATION_GSHEET_SYNC_FAILED, CAMPAIGN_AUTO_PAUSED (bounce-rate pause; also empty-variable pause with reason EMPTY_VARIABLES per D update-campaign), WEBHOOK_DISABLED (another webhook auto-disabled after repeated failed deliveries), BILLING_PAYMENT_FAILED, BILLING_SUBSCRIPTION_EXPIRED, BILLING_DFY_SUBSCRIPTION_EXPIRED, BILLING_DFY_DOMAIN_CANCELLED, BILLING_DFY_EMAIL_EXPIRED, BILLING_DFY_PAYMENT_FAILING, BILLING_PLACEMENT_SUBSCRIPTION_EXPIRED.
Payload: webhook_id, webhook_name, workspace_name, webhook_event SYSTEM_ALERT, alert, alert_type, data (alert specific; arrays capped at 10 items with a count field such as total_count). The EMAIL_ACCOUNT_DISCONNECTED sample data carries per account: email, provider, status DISCONNECTED, warmup_status, reason (for example invalid_grant), error_time. alert_type: the add-webhook page says currently URGENT for every alert; the payload page says NORMAL, ALERT or URGENT (disagreement, see gaps.md).

## 3. Create, list, delete

- POST /hook/add: workspace_id, url (required), name, camp_ids (required; campaign IDs or "ALL"), event_types (required array), alerts (SYSTEM_ALERT only), is_slack (1 or 0), secret (optional), ignore_ooo (1 ignores out-of-office; replies events only), ignore_automatic (1 ignores automatic replies). Returns _id.
- GET /hook/list (workspace_id) returns hooks[] with _id, url, name, secret, camp_ids, etc.
- DELETE /hook/del (workspace_id plus array of webhook IDs).
- Sample payload sending: from the webhook settings page in the app, for every subscribed event type, signed if a secret is set (D webhooks-overview).

## 4. Signature (optional)

If a secret is set, every delivery has a header `Signature` = hex(HMAC_SHA256(key = secret, message = raw JSON body)). Hash the raw body, not re-serialized JSON; compare in constant time. Test vector: secret `my_webhook_secret`, body `{"webhook_event":"SYSTEM_ALERT","alert":"EMAIL_ACCOUNT_DISCONNECTED"}` gives a927cde9781124cf8e28e8e5886e4dff6bf7c792877211fd2a3d6e9d0cc95097 (D webhooks-overview). Zapier and Make do not need a secret.

## 5. Payload fields

Replies (FIRST_EMAIL_REPLIES, ALL_EMAIL_REPLIES, ALL_SUBSEQUENCE_REPLIES, ALL_POSITIVE_REPLIES) (D webhooks-payload-email-replies-2268182m0): webhook_id, webhook_name, webhook_event, campaign_name, workspace_name, camp_id (legacy), campaign_id, subseq_id, subsequence_name, parent_lead_id, org_id, workspace_id, email_account_id, source_thread_id, source_message_id, thread_id, source_label_ids, subject, from, from_email (the lead), to, to_email (your connected account), lead_id, sub_camp_id, direction (IN or OUT), snippet, body (HTML), text_body, is_read, status, modified_at, created_at, actual_replied_from, last_email_id (use as reply_to_id for the Reply endpoint), message_id, references, reply_to, cc, label, is_email_verified (1, 0, -1), email_account_name, sender_first_name, sender_last_name, lead fields (email, first_name, last_name, address_line, city, state, country, country_code, phone_number, job_title, department, company_name, company_website, industry, linkedin_person_url, linkedin_company_url), sentiment (POSITIVE, NEUTRAL, NEGATIVE), step, variation.

Campaign emails sent, EMAIL_SENT (D webhooks-payload-campaign-emails-sent-2268184m0): webhook_id, webhook_name, webhook_event, campaign_name, workspace_name, camp_id (legacy), campaign_id, parent_lead_id, sent_email_id, email_account_name, email_account_id, lead_email, lead_id, _id (same as lead_id), organization_id, workspace_id, current_step, sent_on, variation, message_id, subject, body, is_text (1 plain text, 0 HTML), is_completed, created_at, modified_at, status (COMPLETED etc.), label, sender_first_name, sender_last_name, email (duplicate of lead_email), actual_replied_from, plus lead fields (first_name, last_name, address_line, city, state, country, country_code, phone_number, job_title, department, company_name, company_website, industry, linkedin_person_url, linkedin_company_url) and any further fields the page lists after these.

Bounced, BOUNCED_EMAIL (D webhooks-payload-bounced-email-2268659m0): webhook_id, webhook_name, webhook_event, campaign_name, workspace_name, camp_id, campaign_id, date, sender_email, lead_email, lead_mx, is_verified, sender_mx, msg (full bounce text), is_camp_paused (true when the campaign paused for high bounce), bounce_type SENDER or RECIPIENT (from 14 Sep 2026).

Lead marked as label, LEAD_MARKED_AS_* (D webhooks-payload-lead-marked-as-label-2268183m0): webhook_id, webhook_name, webhook_event, campaign_name, workspace_name, camp_id, parent_lead_id, _id and lead_id, organization_id, campaign_id, workspace_id, current_step, email_account_id, email_account_name, created_at, modified_at, status, label, sentiment, step and variation (at the time it was marked), last_lead_reply (HTML of the latest inbound reply), text_body, last_lead_reply_subject, last_email_id, last_thread_id, latest_message and latest_subject (latest message, inbound or outbound), is_email_verified, sender_first_name, sender_last_name, actual_replied_from, and lead fields (email, first_name, last_name, address_line, city, state, country, country_code, phone_number, job_title, department, company_name, company_website, industry, linkedin_person_url, linkedin_company_url).

Unibox email sent, UNIBOX_EMAIL_SENT (D webhooks-payload-unibox-email-sent-2268660m0): webhook_id, webhook_name, webhook_event, campaign_name, workspace_name, camp_id, parent_lead_id, org_id, organization_id, workspace_id, email_account_id, sent_via (how it was sent from Unibox, for example MANUAL_REPLY for a reply in an existing thread; the page lists further values I did not capture), is_forwarded (always 0), source_thread_id, source_message_id, thread_id, source INTERNAL, sub_camp_id, direction OUT, snippet, subject, from, from_email (your account), to (the lead), cc, message_id, references, reply_to (message being replied to), lead_id, campaign_id, body, text_body, is_read 1, status, label, sentiment, lead fields (email, first_name, last_name, company_name, company_website, job_title, phone_number, address_line, city, state, country, country_code, linkedin urls, actual_replied_from), email_account_name, sender_first_name, sender_last_name, step, variation, camp_tag_ids, is_completed, custom_* workspace fields, created_at, modified_at.

## 6. Using them (practical)

- Replies: route ALL_POSITIVE_REPLIES or LEAD_MARKED_AS_INTERESTED to CRM or Slack; use last_email_id as reply_to_id for POST /unibox/emails/reply.
- Health: subscribe to SYSTEM_ALERT with EMAIL_ACCOUNT_DISCONNECTED and CAMPAIGN_AUTO_PAUSED, and BOUNCED_EMAIL to track sender bounces (bounce_type SENDER).
- Pausing leads from a CRM event uses POST /lead/update/status, not a webhook (H 16954797).
- Integrations: Make (H 10359788), Zapier, Slack alerts (H 9418270), HubSpot, GoHighLevel, Calendly.
- Other help: H 9219846 "Understanding webhooks in PlusVibe" (not summarised).
