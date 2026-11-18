# PlusVibe campaigns: settings end to end

Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. MINE = my recommendation. Plans for campaign features are mostly not stated; exceptions noted.

## 1. Lifecycle and endpoints

- Create: POST /campaign/add/campaign (workspace_id, camp_name) returns id. A new campaign is a draft (D create-a-new-campaign-38494475e0). Configure with PATCH /campaign/update/campaign.
- Duplicate: POST /campaign/duplicate (campaign_id, camp_name; duplicate_subsequences default yes). Copies sequences, schedule, settings and sender accounts as a new draft; leads and stats not copied (D duplicate-campaign-42358299e0).
- Activate: POST /campaign/launch (campaign_id; optional activate_subsequences yes/no default no; resume_paused_leads yes/no default no). Also accepts a subsequence ID, whose parent must be started first (D activate-campaign-38494486e0).
- Pause: POST /campaign/pause. Delete or archive: DELETE /campaign/delete with is_archive yes/no and is_save_lead_data yes/no ("cannot be undone") (D delete-or-archive-a-campaign-38494489e0).
- Status values: ACTIVE, PAUSED, COMPLETED, ARCHIVED (list filter) (D list-all-campaigns-38494478e0); update accepts ACTIVE, PAUSED, INACTIVE (D update-campaign-38494488e0). List can filter campaign_type all, parent or subseq and parent_camp_id.
- Bulk tags on campaigns, bulk activate/pause, bulk edit schedule and settings exist in UI (H 14312123, H 14312129) and tags by API (D bulk-assignremove-tags-from-campaigns-43462388e0).

## 2. What must be in place before launch

Documented requirements (not one consolidated checklist; assembled from several pages):
- Sender accounts attached, a schedule, and sequence steps. The only explicit statement: subsequences are activated by activate_subsequences only when "sender accounts, schedule and sequence all set" (D activate-campaign-38494486e0). Apply the same to parents (my inference).
- Step 1 variation needs a subject; later steps may leave it empty to chain on the previous thread (D update-campaign: "subject ... Required for step 1"; H 10388713 "Leave Subject Line empty to chain emails with previous step").
- Start date: "You should always specify the Campaign Start Date" (H 9952660 for subsequences, same fields as campaigns H 8844133). End date optional; without it the campaign runs until all leads complete.
- Leads must exist in the campaign (add after configuration). Lead add through the API: POST /lead/add (D add-leads-to-a-campaign-38494490e0).
- Reliable sending also depends on accounts: SPF, DKIM, DMARC green and warmup done (see warmup.md, deliverability.md).
- The Lead Gen Jay package refuses to launch and to add leads until its own audit gate is ported (package SKILL.md, third party). Not a PlusVibe rule.

## 3. Every field update-campaign accepts

PATCH /campaign/update/campaign, partial update; omitted fields unchanged (D update-campaign-38494488e0). Required: workspace_id, campaign_id (24 hex).

General
- camp_name; status (ACTIVE, PAUSED, INACTIVE); opportunity_val (number); template_id (24 hex); unlink_template yes/no.
- email_accounts: array of account IDs or tag IDs (24 hex). Not accepted for subsequences (400); they use the parent's accounts.

Schedule (`schedules`; required keys inside when sent: daily_limit, days, timezone, timing)
- daily_limit (>= 0, max total sends per day); daily_limit_new_lead (>= 0, max new leads per day).
- start_date YYYY-MM-DD; end_date YYYY-MM-DD or empty string.
- days: object, '1' Monday to '7' Sunday.
- timezone: IANA, pattern ^[A-Za-z]+(?:/[A-Za-z_]+){1,2}$. timing.from and timing.to HH:MM 24h.
- Sending is only on schedule days: a 3-day wait that lands on a non-sending day goes out on the next active day (H 8689166).

Advanced schedule
- use_adv_schedule true requires adv_schedule (the normal schedule is kept but unused); false returns to `schedules`.
- adv_schedule: timezone, windows (keys Monday to Sunday, each a list of {from, to} HH:MM; omit a day to skip it), daily_limit (required), daily_limit_new_lead (required, null for no separate cap). UI presets Business Hours, Light Mon and Fri, Skip Lunch, per-day copy (H 15433192).
- Skip Holidays (UI): pause sending on public holidays by country calendar or custom calendar; no API field found in the update docs (H 15450823).

Sequences
- sequences[] each with step (>= 1), wait_time (>= 0, "Day to wait AFTER this step"), variations[] (variation letter such as A or B, subject, preheader max 100 chars and dropped for plain text, name, body HTML).
- first_wait_time (>= 0) and first_wait_time_unit (days or minutes): subsequences only, required whenever sequences are sent for a subsequence (include current value to keep it).
- var_sel_type: R_ROBIN or INIT_STEP_VAR (follow-up variation selection mode).
- disable_variations: {step, variation (A to Z or two letters starting A, B, C), is_active yes/no}. The doc's own example uses a different key naming than the field list; check read-back (package SKILL.md also flags it).
- Sequence replacement via update overwrites steps; verify with a read.
- Variation stats: GET variation stats endpoint (D get-campaign-variation-stats-38494483e0).

Sending behaviour
- send_priority 0 to 1 (0 new leads only, 1 follow-ups only, 0.5 balanced default).
- ignore_mailbox_limit 0 or 1 (subsequences only).
- is_esp_match yes/no; other_email_acc yes/no (Fallback Sending).
- is_rampup yes/no with rampup_start_daily (>= 1) and rampup_daily_inc (>= 1); starting amount plus increase cannot exceed the campaign daily limit. Counts sending days only (D; H 16915358). UI: Campaign, Edit, Schedule, scroll to "Campaign Ramp-Up".
- is_max_lead_domain_per_day yes/no and max_lead_domain_per_day (>= 1).

Stop rules and reply handling
- stop_on_lead_replied yes/no.
- is_acc_based_sending yes/no: "Stop sending to same Domain on reply".
- exclude_ooo yes/no: continue sending for out-of-office replies. ooo_nr_opt AI or MAN (next reply timing). ooo_nr_ai_d (fixed days if AI cannot read the return date) and ooo_nr_d (fixed days when MAN). H 10388653, H 12023504 (extra days for OOO, not read in full).
- Auto-pause on bounce: is_pause_on_bouncerate yes/no, bounce_rate_limit.

Safety and content
- is_emailopened_tracking yes/no; is_unsubscribed_link yes/no; send_as_txt yes/no; unsub_blocklist yes/no.
- send_risky_email yes/no; send_seg_email yes/no (default yes); seg_block_list (SEG codes; see deliverability.md).
- pause_on_empty_var yes/no: "On for campaigns created after Nov 2026; campaigns created earlier are off until enabled". Before each send every variable in subject and body is checked; a lead with an empty variable (no value and no fallback) is paused with pause_reason naming the variable. When the count paused since last activation reaches empty_var_pause_limit (1 to 30, default 5), the campaign auto-pauses (is_paused_at_empty_var 1) and the owner is notified. The owner is notified by email, notification center, push and the CAMPAIGN_AUTO_PAUSED system-alert webhook (reason EMPTY_VARIABLES). Also applied to the campaign's subsequences.
- resume_paused_leads yes/no (default no) with status ACTIVE: also resumes paused leads (user paused or empty-variable safety) of the campaign and its ACTIVE subsequences.

## 4. Lead handling

- Statuses (fetch leads filter): SKIPPED, COMPLETED, NOT_CONTACTED, CONTACTED, BOUNCED, REPLIED, UNSUBSCRIBED, PAUSED (D fetch-workspace-leads-38494495e0). Paused is a flag (is_paused 1), not a status (D get-lead-counts-by-status).
- POST /lead/update/status: new_status COMPLETED, PAUSED (only NOT_CONTACTED or CONTACTED leads), UNPAUSED (resumes from current step), REACTIVATED (SKIPPED lead back into the sequence; leads skipped by label change, invalid format or failed verification cannot be reactivated; MX-skipped leads are re-checked). Pause applies to the lead and its subsequence copies (D update-the-status-of-a-lead-38494496e0, H 16954797). AI Reply Agent and Auto Follow-up keep running on paused leads (H 16954797).
- POST /lead/add fields: email, first_name, last_name, notes, address_line, city, country, country_code, phone_number, company_name, company_website, linkedin_person_url, linkedin_company_url, custom_variables (object); flags skip_if_in_workspace, skip_lead_in_active_pause_camp, skip_lead_for_active_only_camp, resume_camp_if_completed, hubspot_sync, is_overwrite, verify_lead (default false; consumes verification credits; response returns verification_task_id). Response counters: leads_uploaded, duplicate_email_count, already_in_campaign, invalid_email_count, skipped, remaining_in_plan, overflowed_lead_count (D add-leads-to-a-campaign-38494490e0).
- Custom variables: a lead's `custom_variables.first_line` is stored as `custom_first_line`, and a template fills it only as `{{custom_first_line}}`. `{{first_line}}` shows in the preview as written. Checked in the campaign preview, 2026-11-07. `plusvibe.py load-copy` maps our `{{first_line}}` on the way in.
- Lead limits: 30,000 campaign leads (Personal), 100,000 (Business); list leads 300,000 and 1,000,000; counts include completed and paused campaigns (H 10005524, P).
- Upload methods in UI: CSV, existing list, manual, CRM (H 8624790).

## 5. Subsequences

- Create by API: POST /campaign/add/subsequence with workspace_id, name, parent_camp_id, events[]. Event names: LEAD_LABEL_UPDATED (val array of labels, each must start LEAD_MARKED_AS_), LEAD_REPLY_CONTENT (include_text required, exclude_text optional), LEAD_REPLY_ALL, LEAD_REPLY_ALL_EXCEPT_OOO_AUTOMATIC_REPLY (D create-a-new-subsequence-38494476e0).
- Only one condition at a time in the UI. Subsequences have their own schedule (days, time, timezone, start and end date, subsequence daily limit) (H 9953583, H 9914807, H 9952660).
- "Bypass Email Accounts' Daily Sending Limits" checkbox, API ignore_mailbox_limit (H 9914807).
- Leads with an active subsequence do not get Unibox auto follow-ups (H 14004398).
- Move leads from parent: POST /lead/add-lead-in-subseq (subseq_id, parent_lead_ids) (D add-leads-to-a-subsequence-campaign-38494491e0).

## 6. Webhooks and events tied to campaigns

See webhooks.md. CAMPAIGN_AUTO_PAUSED alert covers bounce-rate pauses.

## 7. MINE: recommended pre-launch checklist

1. Accounts attached by tag, DNS green, warmup past 2 to 4 weeks. 2. Step 1 subject set, spintax previewed with Preview and Test Email. 3. Schedule with start date, advanced windows matching target hours, daily_limit sized to mailboxes times per-mailbox cap. 4. send_as_txt yes, open tracking no, unsubscribe yes, bounce pause on, fallback and ESP match on, empty-variable pause on. 5. Campaign ramp-up on. 6. Add leads (verify_lead true), re-read the campaign, then launch.
