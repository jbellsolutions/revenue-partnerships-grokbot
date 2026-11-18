# PlusVibe Unibox, replies, labels and AI reply features

Source key: H = https://help.plusvibe.ai/en/articles/<id>. D = https://developer.plusvibe.ai/<page>.md. MINE = my note.

## 1. Unibox basics

- Unibox holds replies from campaigns plus "Others" for replies not tied to a campaign lead. Inbox emails are stored 9 months; Others emails 7 days (H 10005524).
- Replies landing in spam are detected and shown (H 10388386). Auto-replies (Out of Office, Automatic Reply) are labelled, marked Read, and excluded from reply stats (H 10388653). Missing replies cause list: H 8777479.
- API (D, see api-index.md): GET /unibox/threads (conversation list with latest_message_type, is_unread, is_starred, is_archived, has_draft), GET /unibox/emails (messages; email_type all, received, sent; label; one folder flag among is_starred, is_scheduled, is_archived, is_draft; page_trail pagination, reset page_trail when changing filters), GET /unibox/other-emails, GET /unibox/emails/count/unread, POST /unibox/emails/reply, /forward, /compose, /send (any address), /save-as-draft, /cancel-scheduled, POST /unibox/threads/{thread_id}/mark-as-read, DELETE thread and DELETE email.
- Reply body fields: reply_to_id (id from unibox/emails or other-emails), subject (use "Re: " to keep the thread), from, to, body, cc, bcc, scheduled_at (YYYY-MM-DDTHH:mm, at least 1 minute ahead, with schedule_tz Region/City), attachments[] {file_name, content base64}. Scheduled sends return scheduled_email_id (D reply-to-an-email-38494518e0). Replying to an Others email moves the conversation into the main list.
- "sent" email_type covers only replies sent from Unibox; campaign emails come from the campaign emails endpoint (D get-emails-38494515e0).
- Block list can be applied to Unibox outgoing replies (H 15999723).
- Thread assignment: manual Assign, or automatic round-robin per AI label; auto-assign works only when the label was applied by AI detection and is a Business feature (H 14303088). Replace lead and associate-to-lead in Others: H 14312087, H 14312163. Push notifications: H 14736357. Scheduled replies: H 10388451.

## 2. AI reply labels

- Default AI labels on a lead's first reply: Interested, Not Interested, Out of Office, Automatic Reply. More can be enabled or disabled. Custom labels need a name the AI can understand and a sentiment (Positive, Negative, Neutral). Avoid overlapping labels such as "Leads" and "Interested" (H 9581731).
- Where: Workspace Settings, AI Reply Labels (H 10388503). "AI Auto Categorization" checkbox per label.
- Extra AI prompt for categorization is Business plan (H 9581731). Positive-reply notification email to a chosen address.
- API: GET /workspace-settings/lead-labels returns id, key, name, sentiment, icon, is_system, is_ai_label. POST add custom lead label, DELETE custom lead labels. ai_lead_labeling.labels (keys, max 100, replaces the list) via PATCH /workspace-settings/update (D list-lead-labels-41824283e0, update-workspace-settings-41824282e0).
- Labels are used as webhook triggers (LEAD_MARKED_AS_*) and as subsequence conditions (labels prefixed LEAD_MARKED_AS_) (D create-a-new-subsequence).

## 3. AI Reply Agent (Business plan; H 13164721, H 14312099)

- Rules per label, campaign and sending account, optional CC. Response AI Reply or Manual Reply. Models listed: GPT-5, GPT-5 Mini, GPT-4o. Prompt plus Test box.
- Sending method: prepare as draft, reply immediately, or reply with delay (minutes or days). Confidence filter "If AI confidence is low, save as a draft". Optional label applied after auto reply.
- Subsequent Replies toggle lets the agent continue multi-turn threads (Business and above); PlusVibe warns of hallucination and suggests keeping high-intent labels for humans (H 14312099).
- Recognises clear rejections ("Not interested") and stops (H 13164721).
- Turn off per rule in Unibox, AI Automation.
- Block list can stop agent replies to blocked recipients. AI Reply Agent keeps running for paused leads (H 16954797).

## 4. Auto follow-up in Unibox (H 14004398, D update-workspace-settings)

- If a lead does not respond after an outgoing Unibox email, follow-ups go out. Configure labels, days, sequence. Enabled for all threads by default once configured. Restarts from step 1 for each outgoing Unibox email; any incoming reply stops it; leads in a subsequence are excluded. Understands "contact me in Q4" style deferrals.
- Workspace API: auto_follow_up.is_enabled, wait_days 1 to 90, skip_weekends (default yes), labels (keys, or "UNLABELLED"), steps (max 10, each body HTML up to 100,000 chars and wait_days 1 to 90). Enabling needs at least one step and one label.

## 5. Out of office

Campaign option exclude_ooo continues sending after OOO replies, with ooo_nr_opt AI or MAN and fixed day fallbacks (D update-campaign). UI: H 12023504 (not read in full).

## 6. Mobile and white label

Mobile app, white-label client app and client access endpoints exist (H 13397195, H 14312147, D Client Access endpoints). Not covered here.
