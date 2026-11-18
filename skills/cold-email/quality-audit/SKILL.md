---
name: quality-audit
version: 1.0.0
description: |
  Audit email quality across campaigns. Samples recent emails, checks
  personalization depth against the Cold Email Formula, scans for spam
  triggers and salesy language, verifies CAN-SPAM compliance, scores
  overall quality, and generates a detailed audit report. Read-only --
  never modifies sent emails or active campaigns.
  Use when: "quality audit", "audit emails", "check email quality",
  "spam check", "compliance check", "email audit", "quality review".
metadata:
  author: Justin Bell
  category: cold-email
  domain: quality-assurance
  updated: 2026-03-27
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Quality Audit

Audit email quality across campaigns for personalization, spam triggers, and compliance.

## Iron Law

**READ-ONLY. AUDIT ONLY, NEVER MODIFY SENT EMAILS.** This skill examines
emails that have already been sent or are queued for sending. It produces a
report with findings and recommendations. It never edits, deletes, or modifies
any email content. Changes to templates or quality rules must be implemented
separately after reviewing the audit report.

## Keywords

quality audit, audit emails, check email quality, spam check, compliance check,
email audit, quality review, email quality, personalization audit, CAN-SPAM audit

## Audit Dimensions

### 1. Personalization Depth

Check whether emails contain genuine, prospect-specific content:

| Score | Level | Criteria |
|:-----:|-------|----------|
| 5 | Exceptional | Dated reference, specific company detail, relevant pain point |
| 4 | Strong | Company-specific detail with relevant context |
| 3 | Adequate | Industry-relevant content, basic company reference |
| 2 | Weak | Generic industry language, no company specifics |
| 1 | Absent | Template-like content, could be sent to anyone |

**Target: 4+ average across sampled emails.**

### 2. Cold Email Formula Compliance

Verify each email follows the 4-part structure:

- [ ] Personalized line references real, dated information
- [ ] Problem is specific to the prospect's niche (not generic)
- [ ] Proof includes specific metrics/numbers
- [ ] CTA is a single yes/no question
- [ ] Total word count is under 80
- [ ] Subject line is 3-5 words, natural tone
- [ ] Signed: Justin

### 3. Spam Trigger Scan

Check for content that triggers spam filters:

**26-word blacklist:**
revolutionary, game-changing, amazing, incredible, skyrocket, explode,
crush it, unlock, supercharge, turbocharge, groundbreaking, unbelievable,
extraordinary, mind-blowing, best-in-class, world-class, cutting-edge,
next-level, guaranteed, limited time, act now, don't miss out,
once in a lifetime, exclusive offer, massive, huge

**Additional spam signals:**
- Exclamation points (any)
- Emojis (any)
- ALL CAPS words (except acronyms)
- Excessive links (more than 1)
- Image-heavy content
- Misleading subject lines
- Missing unsubscribe mechanism

### 4. CAN-SPAM Compliance

Verify legal compliance for commercial emails:

- [ ] Sender identity is clear (From name and address)
- [ ] Physical mailing address included (in SmartLead footer)
- [ ] Unsubscribe mechanism is functional
- [ ] Subject line is not deceptive
- [ ] Email is identified as an advertisement (if applicable)
- [ ] Opt-out requests are honored within 10 business days
- [ ] No harvested email addresses in recipient list

### 5. Pricing Leak Check

Verify no email mentions:
- Dollar amounts ($1,000, $300/mo, etc.)
- Tier names (Starter, Professional, Enterprise)
- Specific pricing language
- Investment amounts
- Mastermind fees

**PRICING IS NEVER IN EMAILS.** Price is revealed on sales calls only.

## Execution Phases

### Phase 1: Sample Selection

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
python3 -c "
from core.database import ColdEmailDB
db = ColdEmailDB()
# Count available emails for audit
sent = db.get_contacts_by_status('sent')
approved = db.get_contacts_by_status('approved')
print(f'Sent emails available for audit: {len(sent)}')
print(f'Approved (queued) emails: {len(approved)}')
print(f'Recommended sample size: {min(50, max(10, len(sent)//5))}')
"
```

Select a representative sample:
- Random selection across all variants
- Include emails from all 15 templates
- Include both primary emails and follow-ups
- Sample from different time periods if available

### Phase 2: Automated Checks

Run deterministic checks on all sampled emails:

```python
# Pseudocode for automated audit checks
for email in sample:
    results = {
        "word_count": count_words(email.body) <= 80,
        "subject_length": 3 <= count_words(email.subject) <= 5,
        "no_salesy_words": not any(w in email.body.lower() for w in SALESY_WORDS),
        "no_emojis": not has_emojis(email.body),
        "no_exclamation": "!" not in email.body,
        "no_pricing": not has_pricing(email.body),
        "has_yesno_cta": has_yes_no_question(email.body),
        "no_generic_opener": not has_generic_opener(email.body),
    }
```

### Phase 3: AI Quality Assessment

Use Claude Haiku for nuanced evaluation:
- Is the personalization genuine or fabricated?
- Does the email read like a human wrote it for one person?
- Is the proof credible and relevant?
- Would a busy executive spend 10 seconds on this?

### Phase 4: Compliance Verification

Check CAN-SPAM requirements against the SmartLead campaign configuration:
- Verify unsubscribe links are active
- Verify sender information is accurate
- Verify physical address is included
- Check opt-out processing time

### Phase 5: Generate Audit Report

```
=== EMAIL QUALITY AUDIT REPORT ===
Date: YYYY-MM-DD
Sample Size: X emails (out of Y total)
Audit Period: [date range]

OVERALL QUALITY SCORE: X/10

PERSONALIZATION DEPTH
  Average Score: X/5
  Exceptional (5): X%
  Strong (4): X%
  Adequate (3): X%
  Weak (2): X%
  Absent (1): X%

COLD EMAIL FORMULA COMPLIANCE
  Pass Rate: X%
  Common Violations:
    - [violation]: X occurrences
    - [violation]: X occurrences

SPAM TRIGGER SCAN
  Clean Emails: X%
  Flagged Emails: X%
  Triggers Found:
    - [trigger]: X occurrences
    - [trigger]: X occurrences

CAN-SPAM COMPLIANCE
  Status: [PASS/FAIL]
  Issues: [list any]

PRICING LEAK CHECK
  Status: [PASS/FAIL]
  Leaks Found: [count]

TEMPLATE QUALITY BREAKDOWN
  [template_name]: X/10 avg quality
  [template_name]: X/10 avg quality
  ...

RECOMMENDATIONS
  1. [specific actionable recommendation]
  2. [specific actionable recommendation]
  3. [specific actionable recommendation]
```

## Running the Audit

```bash
# Full audit of recent emails
python3 -c "
from agents.quality_checker import QualityCheckerAgent
from core.database import ColdEmailDB
# Initialize and run audit checks
db = ColdEmailDB()
print('Starting quality audit...')
"

# Quick spot-check via dashboard Chat tab
# "Audit the quality of the last 20 emails sent"
```

## Safety Rules

- READ-ONLY: never modify, delete, or edit any sent or queued emails
- Never expose individual prospect email addresses in audit reports
- Never auto-implement recommendations -- present for human review only
- Never access SmartLead sending controls from within this audit
- Flag critical compliance issues immediately (do not bury in report)
- If CAN-SPAM violations are found, recommend immediate pause pending review
