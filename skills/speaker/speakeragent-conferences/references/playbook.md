# Conference playbook

## Search sequence

The source generator takes up to eight keywords. For keyword `k`, it rotates two event terms and builds five searches: `k "call for speakers" event current-year`, the second event term with next year, `k event "call for proposals" current-year`, `k event "call for papers" current-year`, and `k event "speaker applications" open`. Append useful geography. The script reproduces this query pattern with an explicit date; it does not execute searches.

Read results in source-balanced batches so a high-volume source does not consume the candidate allowance. Start from relevant official association calendars, known event series and search results. Confs.tech is useful for supported technology subjects, not arbitrary industries. On the master branch there are additional GitHub-deadline and WikiCFP source adapters; alpha-v0.6.1 has three independent lanes and follows WikiCFP pages encountered in search. Do not assume all branches contain the same lanes.

For paid engagements, follow qualified event families to their organizer portfolios, speaker guidance, keynote policies and previous programs. Research the speaker-selection team for an unpublished keynote opportunity. Record this as a relationship prospect until there is evidence of a current available engagement. Do not turn an organizer's ability to buy sponsorship into evidence it pays speakers.

## Evidence extraction

Inspect event-specific structured data when available, then corroborate against visible text. Capture exact edition, event date and CFP deadline separately. Read timezone wording for deadlines; date-only values stay date-only. If the title is 2027 but the submission form still says 2026, retain the conflict and seek clarification rather than submitting.

Default source discovery window is 60–365 days out. The personalized agent uses the client's explicit dates instead. Keep near-term, too-far-out and expired candidates in their proper research/watch/rejection categories. A closed CFP can coexist with a valid upcoming event.

Compensation labels: `confirmed_paid`, `likely_paid`, `expenses_only`, `confirmed_unpaid`, `mixed_by_session_type`, `unknown`. Add `pay_to_speak` as a separately labeled agent extension when a sponsor or purchase is required. Record session-specific terms and currency. A complimentary ticket is not a fee; travel reimbursement is not a fee; a dollar amount next to “registration” is not compensation. Organization-based ranges from the legacy scorer are historical estimates and must never fill an evidence-backed fee field.

For paid-only work, only confirmed paid cases satisfying the client's minimum are accepted. If a fee is confirmed but amount unspecified, payment exists but minimum-fee eligibility remains unresolved. Do not assign a numeric fee to `likely_paid` or `unknown`.

## Qualification questions

- Is there an actual event and current edition, or just an evergreen product/training page?
- Does this audience routinely face the problem the speaker can credibly solve?
- Does the format accept this speaker type, including consultants/vendors?
- Is the proposed topic educational and consistent with promotional restrictions?
- Does the place, language, timing and travel expectation fit the client?
- Is the route open now, closed, invitation-only or unknown?
- Is compensation about speakers in this session type, or attendees/sponsors?
- Is there an organizer route, named speaking contact or application form supported by current evidence?

Record each failure independently. Reject clear non-events and disqualifying criteria; preserve unresolved important facts as research holds. A relevance model's confident rejection can remove a candidate from the shortlist, but its timeout cannot establish relevance.

## Client brief

For each recommended opportunity provide: event/edition and date; audience and specific fit; proposed exact talk title; compensation and evidence; deadline/application status; eligibility; best route and whether named or organizational; remaining uncertainty; proposed next action. Give source URLs beside important claims. Keep a separate watchlist and rejection log. Do not pad the accepted count with those categories.
