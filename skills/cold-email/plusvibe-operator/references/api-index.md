# PlusVibe API endpoint index

Base URL: https://api.plusvibe.ai/api/v1 (source: package client.js DEFAULT_BASE_URL; Email Infra Provider partner endpoints use https://api.plusvibe.ai/v1, source https://developer.plusvibe.ai/email-infra-provider-guide-2268692m0.md). Auth: header `x-api-key`. Every endpoint needs `workspace_id`. Rate limit 5 requests per second (https://developer.plusvibe.ai/getting-started-2268178m0.md). API key needs the Business plan.

Each line: METHOD path | summary | first sentence of the documented description | source page id (page URL is https://developer.plusvibe.ai/<id>.md).



## Analytics

- GET /campaign/stats/all | Get all campaigns statistics | Retrieves aggregated statistics across all campaigns within a workspace for a given date range. | get-all-campaigns-statistics-38494514e0
- GET /analytics/campaign/stats | Get campaign stats | Retrieve detailed statistics for a specific campaign or all campaigns within a workspace. | get-campaign-stats-38494513e0
- GET /analytics/campaign/summary | Get campaign summary | Get campaign summary | get-campaign-summary-38494511e0
- GET /analytics/workspaces/performance | Get workspaces performance | Get per-workspace sending and reply performance for your organization, with optional workspace status, campaign status and date range filters. | get-workspaces-performance-42549931e0
- GET /analytics/workspaces/summary | Get workspaces summary | Get aggregate campaign and lead totals for your organization. | get-workspaces-summary-42549930e0

## Blocklist

- POST /blocklist/add/entries | Adds entries to the blocklist | Adds email addresses or domains to the blocklist | adds-entries-to-the-blocklist-38494526e0
- POST /blocklist/delete/entries | Delete entries in the blocklist | Delete entries in the blocklist | delete-entries-in-the-blocklist-38494527e0
- GET /blocklist/list | Get entries in the blocklist | Retrieve a list of blocklisted values for the specified workspace, newest first. | get-entries-in-the-blocklist-38494525e0

## Campaign

- POST /campaign/launch | Activate campaign | This endpoint will activate a campaign. | activate-campaign-38494486e0
- PUT /campaign/bulk-assign-tags | Bulk Assign/Remove Tags from Campaigns | This endpoint allows you to assign or remove a tag on multiple campaigns simultaneously. | bulk-assignremove-tags-from-campaigns-43462388e0
- POST /campaign/add/campaign | Create a new campaign | Creates a new campaign under a specified workspace. | create-a-new-campaign-38494475e0
- POST /campaign/add/subsequence | Create a new subsequence | Creates a new subsequence under a specified parent campaign. | create-a-new-subsequence-38494476e0
- DELETE /campaign/delete | Delete or archive a campaign | Deletes or archives a campaign based on the provided parameters. | delete-or-archive-a-campaign-38494489e0
- POST /campaign/duplicate | Duplicate campaign | Creates a copy of an existing campaign as a new draft campaign, carrying over its sequences, schedule, settings and sender accounts. | duplicate-campaign-42358299e0
- GET /campaign/get/accounts | Get campaign email accounts | Get a list of email accounts associated to the campaign. | get-campaign-email-accounts-38494481e0
- GET /unibox/campaign-emails | Get campaign emails | Fetch campaign emails sent to a specific lead within a workspace. | get-campaign-emails-38494482e0
- GET /campaign/get/name | Get campaign name | Get campaign name | get-campaign-name-38494479e0
- GET /campaign/get/status | Get campaign status | Get campaign status | get-campaign-status-38494480e0
- GET /campaign/get/variation-stats | Get campaign variation stats | Returns variation-level performance statistics for each campaign step. | get-campaign-variation-stats-38494483e0
- GET /campaign/list-all | List all campaigns | Retrieve a list of campaigns for a specific workspace with optional filtering capabilities. | list-all-campaigns-38494478e0
- POST /campaign/pause | Pause campaign | Pause campaign | pause-campaign-38494487e0
- POST /campaign/set/name | Set campaign name | This section allows users to set a new name for their campaign. | set-campaign-name-38494484e0
- PATCH /campaign/update/campaign | Update Campaign | This is a PATCH endpoint to update an existing campaign. | update-campaign-38494488e0

## Client Access

- POST /client | Create client | Create a client and assign them to one or more workspaces. | create-client-38494535e0
- DELETE /client | Delete client | Permanently remove a client from the workspace. | delete-client-38494538e0
- PUT /client | Edit client | Update client info and workspace permissions. | edit-client-38494536e0
- GET /client | List clients | Fetch all clients in a workspace. | list-clients-38494539e0
- PATCH /client | Update client status | Activate or deactivate a client. | update-client-status-38494537e0

## DFY

- POST /dfy/cancel-subscription | Cancel a DFY Subscription | Cancels a DFY subscription of the workspace. | cancel-a-dfy-subscription-40879060e0
- POST /dfy/generate-sender-identities | Generate Sender Identities (MS Enterprise) | Builds the 99 mailbox names an **MS_ENTERPRISE** order needs, out of a few real sender identities. | generate-sender-identities-ms-enterprise-40881753e0
- GET /dfy/subscriptions | List DFY Subscriptions | Lists the workspace's DFY subscriptions (email account and domain orders), newest first. | list-dfy-subscriptions-40879058e0
- POST /dfy/place-order | Place a DFY Order | Places a DFY order: purchases the domains and creates ready-to-send email accounts on them, in a single order. | place-a-dfy-order-40879059e0
- GET /dfy/domain-search | Search Domain Availability | Checks whether domains are available for purchase through DFY. | search-domain-availability-40879057e0

## Email Account

- POST /account/bulk-add-regular-accounts | Bulk Add SMTP Accounts | Bulk add multiple SMTP (non-Google / non-Microsoft) email accounts via API. | bulk-add-smtp-accounts-38494505e0
- PUT /account/bulk-assign-tags | Bulk Assign/Remove Tags from Email Accounts | This endpoint allows you to assign or remove tags from multiple email accounts simultaneously. | bulk-assignremove-tags-from-email-accounts-38494508e0
- POST /account/bulk-delete | Bulk Delete Email Accounts | Delete up to 1,000 email accounts in one request, by email address (`emails`), by email account ID (`ids`), or both. | bulk-delete-email-accounts-46324626e0
- POST /account/bulk-reconnect | Bulk reconnect email accounts | Reconnecting only works if account credentials haven't changed (e.g., a temporary error or bounce). | bulk-reconnect-email-accounts-38494509e0
- PATCH /account/bulk-update-warmup | Bulk Update Email Account Warmup Status | This endpoint allows you to modify the warmup status for multiple email accounts simultaneously. | bulk-update-email-account-warmup-status-38494507e0
- PUT /account/bulk-update | Bulk Update Email Accounts | This endpoint allows you to modify various settings for multiple email accounts simultaneously, including basic information, daily limits, signatures, warmup settings, rampup configurations, Randomize Daily Limit and Rest Cycles. | bulk-update-email-accounts-38494506e0
- POST /account/test/vitals | Check account vitals | This endpoint allows you to quickly check if the SPF, DKIM, and DMARC records have been properly set for a list of domains. | check-account-vitals-38494500e0
- POST /account/warmup/enable | Enable Email account warmup | Enable Email account warmup | enable-email-account-warmup-38494501e0
- GET /account/email-stats/bulk | Get email account stats for a date range (per mailbox) | Returns statistics for the given date range **for every sending mailbox individually**, 100 mailboxes per page. | get-email-account-stats-for-a-date-range-per-mailbox-43054283e0
- GET /account/status | Get email account status | Get Email account status and warmup status for the passed email account | get-email-account-status-38494499e0
- GET /account/warmup-stats/bulk | Get Warmup Stats (Per Mailbox) | Returns warmup results (inbox, spam, promotion) for the given date range **for every mailbox individually**, 100 mailboxes per page. | get-warmup-stats-per-mailbox-43864836e0
- GET /account/warmup-stats/overall | Get Warmup Stats (Workspace-Level) | Returns warmup results (inbox, spam, promotion) for the **whole workspace** over the given date range: totals, inbox rates per recipient provider and a per-day `chart_data` array. | get-warmup-stats-workspace-level-43871189e0
- GET /account/email-stats | Get workspace email stats for a date range | Returns aggregated email statistics for the **whole workspace** over the given date range, broken down per day in the `chart` array and summed up in the `header` object. | get-workspace-email-stats-for-a-date-range-38494510e0
- GET /account/list | List all email accounts in the workspace | List all email accounts in the workspace. | list-all-email-accounts-in-the-workspace-38494498e0
- POST /account/move-workspace | Move Email Accounts to Another Workspace | Moves email accounts from the source workspace (`workspace_id`) to another workspace of the same organization (`to_workspace_id`). | move-email-accounts-to-another-workspace-40817914e0
- POST /account/warmup/pause | Pause Email account warmup | Pause Email account warmup | pause-email-account-warmup-38494502e0

## Email Account Automation

- POST /ea-automation-rules/ | Create automation rule | Creates an automation rule. | create-automation-rule-41015401e0
- DELETE /ea-automation-rules/ | Delete automation rule | Deletes a rule. | delete-automation-rule-41015403e0
- POST /ea-automation-rules/duplicate | Duplicate automation rule | Creates a copy of a rule named "<name> (Copy)", active, at the lowest priority. | duplicate-automation-rule-41015406e0
- PATCH /ea-automation-rules/patch | Enable / disable automation rule | Sets a rule's status without touching the rest of its configuration. | enable-disable-automation-rule-41015405e0
- POST /account/recovery | Get account recovery details | Returns, for up to 100 email accounts, whether an email-account automation rule is holding the account in recovery and, if so, which rule, why it fired, the throttled limits in force, when the recovery period ends (`recovery_ends_ | get-account-recovery-details-45795651e0
- GET /ea-automation-rules/detail | Get automation rule | Returns a rule's full configuration. | get-automation-rule-41015404e0
- GET /ea-automation-rules/ | List automation rules | Returns the workspace's automation rules ordered by priority (1 = evaluated first). | list-automation-rules-41015400e0
- PUT /ea-automation-rules/ | Update automation rule | Replaces a rule's configuration. | update-automation-rule-41015402e0

## Email Placement Test

- GET /email-placement/get/recipient-providers | Get recipient providers | Retrieve list of available recipient email providers for testing. | get-recipient-providers-38494546e0

## Email Placement Test > Child (Test Run) Test

- GET /email-placement/get/test-detail | Get child test details | Retrieve detailed information about a specific child test run. | get-child-test-details-38494554e0
- GET /email-placement/list/tests | List child (Test Run) tests | Retrieve all child test runs under a specific parent test. | list-child-test-run-tests-38494553e0

## Email Placement Test > Parent Test (Recurring & One-off)

- POST /email-placement/create/parent-test | Create a new parent test | Creates a new email placement test. | create-a-new-parent-test-38494547e0
- DELETE /email-placement/delete/parent-test | Delete parent test(s) | Delete one or more parent tests in a workspace. | delete-parent-tests-38494551e0
- POST /email-placement/duplicate/parent-test | Duplicate a parent test | Create a copy of an existing parent test with a new name. | duplicate-a-parent-test-38494552e0
- GET /email-placement/get/parent-test-detail | Get parent test details | Retrieve detailed information about a specific parent test. | get-parent-test-details-38494550e0
- GET /email-placement/list/parent-tests | List all parent tests | Retrieve a paginated list of parent tests with optional filtering and sorting. | list-all-parent-tests-38494549e0
- PATCH /email-placement/update/parent-test | Update a parent test | Update test configuration including settings, scheduling, recipients, senders, and content. | update-a-parent-test-38494548e0

## Email Placement Test > Results & Analytics

- GET /email-placement/get/test-stats | Get detailed test statistics | Retrieve detailed statistics for a specific child test run including sender-level breakdown. | get-detailed-test-statistics-38494556e0
- GET /email-placement/get/test-automatic-result | Get test result for a sender account | Retrieve detailed test result for a specific sender account. | get-test-result-for-a-sender-account-38494557e0
- GET /email-placement/get/test-summary | Get test summary | Retrieve aggregated summary statistics for a parent test with optional filtering by recipient type and sender provider. | get-test-summary-38494555e0

## Email Verification

- GET /verify/emails | Get email list verification results | Returns the progress and per-address results of a task queued with *Verify a list of emails*. | get-email-list-verification-results-45795650e0
- GET /verify/credits | Get email verification credits | Returns the verification credit balance available to this workspace and the price of one verification. | get-email-verification-credits-45793860e0
- GET /verify/get | Get email verification task | Returns the progress of a verification task queued with *Queue email verification*. | get-email-verification-task-45792649e0
- GET /verify/tasks | List email verification tasks | Lists the workspace's email verification tasks, newest first: campaign verifications (including ones started by `verify_lead` on upload) and list verifications. | list-email-verification-tasks-45795957e0
- POST /verify/queue | Queue email verification | Verifies the email addresses of a campaign's leads and stores the result on each lead as `is_email_verified` (`VALID`, `INVALID`, `RISKY`, `NOT_CHECKED`). | queue-email-verification-45792648e0
- POST /verify/stop | Stop email verification task | Stops a `QUEUED` or `RUNNING` verification task. | stop-email-verification-task-45792650e0
- POST /verify/emails | Verify a list of emails | Verifies up to 100 email addresses that are not leads. | verify-a-list-of-emails-45795649e0

## Lead

- POST /lead/add | Add leads to a campaign | Send a list of lead objects to add to a campaign. | add-leads-to-a-campaign-38494490e0
- POST /lead/add-lead-in-subseq | Add leads to a subsequence campaign | Add existing leads from a parent campaign to a subsequence campaign. | add-leads-to-a-subsequence-campaign-38494491e0
- POST /lead/delete | Delete leads from a campaign | Users can remove leads by providing the campaign ID and other optional parameters, such as deleting leads with matching domains. | delete-leads-from-a-campaign-38494493e0
- GET /lead/workspace-leads | Fetch workspace leads | Retrieve a list of leads based on specified filters like status, campaign, and more. | fetch-workspace-leads-38494495e0
- GET /lead/count/lead-status | Get lead counts by status | Retrieve the number of leads for each status in a workspace. | get-lead-counts-by-status-38494497e0
- GET /lead/get | Get or search for lead | This endpoint can also be used to search for a lead, if campaign\_id is left blank, all leads matching email will be returned. | get-or-search-for-lead-38494492e0
- POST /lead/data/update | Lead Variable/Label Update or Add | When using this endpoint, existing variables/label in the lead's data will be updated, and new variables provided in the `variables` property will be added to the lead's data. | lead-variablelabel-update-or-add-38494494e0
- POST /lead/update/status | Update the status of a lead | Updates the status of a lead in the specified campaign and workspace. | update-the-status-of-a-lead-38494496e0

## Partner/other

- POST /webhook/partner-upload-regular-accounts | Bulk Add SMTP Accounts (via Username and Password) | Bulk add multiple SMTP (non-Google / non-Microsoft) email accounts via API, by providing PlusVibe Username and Password. | bulk-add-smtp-accounts-via-username-and-password-40641118e0
- GET /webhook/partner-check-email-account | Check if an email exists in another workspace | Validates an email account before connection and returns: Whether the email account is already connected in another workspace (existed_in_other_ws) The current number of connected email accounts (current) The maximum number of ema | check-if-an-email-exists-in-another-workspace-40641115e0
- POST /webhook/partner-google-oauth-url | Initiate Google OAuth login flow | These endpoints allow email infrastructure provider partners to programmatically initiate the Google/Microsoft OAuth login flow to add an account to PlusVibe. | initiate-google-oauth-login-flow-40641116e0
- POST /webhook/partner-microsoft-oauth-url | Initiate Microsoft OAuth login flow | These endpoints allow email infrastructure provider partners to programmatically initiate the Google/Microsoft OAuth login flow to add an account to PlusVibe. | initiate-microsoft-oauth-login-flow-40641117e0
- GET /webhook/partner-list-email-accounts | List all email accounts in the workspace | List all email accounts in the workspace. | list-all-email-accounts-in-the-workspace-40641114e0
- POST /webhook/partner-list-workspace | List workspaces | These endpoints allow email infrastructure provider partners to programmatically initiate the Google/Microsoft OAuth login flow to add an account to PlusVibe. | list-workspaces-40641113e0

## Tags

- POST /tags/create | Create a New Tag | Creates a new tag in the specified workspace. | create-a-new-tag-38494532e0
- DELETE /tags/delete | Delete Multiple Tags | Deletes one or more tags from the workspace. | delete-multiple-tags-38494534e0
- GET /tags/list | List Tags | Retrieves a list of tags associated with a workspace. | list-tags-38494531e0
- PUT /tags/update | Update an Existing Tag | Updates an existing tag's properties including name, color, and description. | update-an-existing-tag-38494533e0

## Unibox

- POST /unibox/emails/cancel-scheduled | Cancel a scheduled reply | Cancels a reply that was scheduled with `POST /unibox/emails/reply` + `scheduled_at`, so it is never sent. | cancel-a-scheduled-reply-46323191e0
- POST /unibox/emails/compose | Compose New Email | This endpoint allows you to compose a new email to any lead. | compose-new-email-38494520e0
- DELETE /unibox/emails/delete | Delete a Single Email Message | Deletes a single email message within an existing Unibox thread. | delete-a-single-email-message-38494524e0
- DELETE /unibox/threads/delete | Delete an Entire Email Thread | Deletes an entire Unibox email thread, including all messages within the thread. | delete-an-entire-email-thread-38494523e0
- POST /unibox/emails/forward | Forward an existing email | Forwards an email to a new recipient. | forward-an-existing-email-38494519e0
- GET /unibox/emails/count/unread | Get count of unread emails | Returns the count of unread emails for a given workspace | get-count-of-unread-emails-38494517e0
- GET /unibox/threads | Get email threads (conversations) | Your inbox as conversations, one item per thread with its state (latest_message_type, is_unread, is_starred, is_archived, has_draft) and a preview of the latest message. | get-email-threads-conversations-41824471e0
- GET /unibox/emails | Get emails | Individual email messages with full bodies and attachments. | get-emails-38494515e0
- GET /unibox/other-emails | Get emails in Others folder | This folder shows replies not related to campaigns and leads. | get-emails-in-others-folder-38494516e0
- POST /unibox/threads/{thread_id}/mark-as-read | Mark Email Read | Mark all unread emails as read, in the thread | mark-email-read-38494521e0
- POST /unibox/emails/reply | Reply to an email | Sends a reply to an existing email. | reply-to-an-email-38494518e0
- POST /unibox/emails/save-as-draft | Save Email as Draft | Saves an email message as a draft in the Unibox for the specified workspace. | save-email-as-draft-38494522e0
- POST /unibox/emails/send | Send to any address | Sends a one-off email to any address, no lead or campaign required. | send-to-any-address-40707674e0

## Webhook

- POST /hook/add | Add a new webhook | Add a webhook to PlusVibe.ai for specified events, campaigns, and conditions. | add-a-new-webhook-38494528e0
- DELETE /hook/del | Delete webhook(s) | Deletes one or more webhooks by their IDs, within the specified workspace. | delete-webhooks-38494530e0
- GET /hook/list | List webhooks | Retrieves a list of all webhooks for the specified workspace. | list-webhooks-38494529e0

## Workspace

- POST /workspaces/add | Add a new workspace | Adds a new workspace to PlusVibe.ai using an existing workspace ID for reference. | add-a-new-workspace-38494473e0
- POST /workspaces/copy | Copy workspace settings | Duplicates selected settings and configurations from a source workspace to a destination workspace. | copy-workspace-settings-38494474e0
- GET /authenticate | Get workspaces | Test the provided API key and returns the list of accessible workspaces. | get-workspaces-38494472e0
- POST /workspaces/invite | Invite a user to a workspace | Invites a user, by email address, to join a workspace with the given role. | invite-a-user-to-a-workspace-40695617e0

## Workspace Additional Fields

- POST /workspaces/additional-fields | Create Additional Field | Creates a new additional field on the workspace. | create-additional-field-40806201e0
- DELETE /workspaces/additional-fields | Delete Additional Field | Deletes an additional field from the workspace. | delete-additional-field-40806203e0
- GET /workspaces/additional-fields | List Additional Fields | Retrieves all additional fields defined on the workspace. | list-additional-fields-40806200e0
- PUT /workspaces/additional-fields | Update Additional Field Default Value | Updates the default value of an existing additional field. | update-additional-field-default-value-40806202e0

## Workspace Settings

- POST /workspace-settings/lead-labels/add | Add Custom Lead Label | Creates a custom lead label. | add-custom-lead-label-41824284e0
- DELETE /workspace-settings/lead-labels/delete | Delete Custom Lead Labels | Deletes custom lead labels by id (get ids from GET /workspace-settings/lead-labels; max 100 per request). | delete-custom-lead-labels-41824285e0
- GET /workspace-settings/ | Get Workspace Settings | Returns the workspace-level settings in four groups: `blocklist` (where the blocklist is enforced + optional Google Sheet sync), `domain_daily_cap` (workspace-wide per-domain daily lead cap), `ai_lead_labeling` (labels the AI may  | get-workspace-settings-41824281e0
- GET /workspace-settings/lead-labels | List Lead Labels | Lists every lead label available in the workspace: the built-in system labels (Interested, Not Interested, Out Of Office, …) and the workspace's custom labels. | list-lead-labels-41824283e0
- PATCH /workspace-settings/update | Update Workspace Settings | Partial update: send only the groups (and only the keys inside a group) you want to change; everything else keeps its value. | update-workspace-settings-41824282e0

Total endpoints listed: 124