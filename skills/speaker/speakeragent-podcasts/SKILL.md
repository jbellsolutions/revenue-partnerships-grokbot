---
name: speakeragent-podcasts
description: Find and qualify podcast guest opportunities using SpeakerAgent's topic-first scoring, publication recency, guest-format review, host research and evidence-based personalized pitch process, with or without its SaaS API.
---

# Podcast research

Use the persona's exact topics and audience problems. Read [algorithm reference](../speakeragent/references/algorithms.md) for the 70/15/10/5 formula and confidence adjustment. Never substitute the conference weights.

1. Generate concise niche/category queries from talk subjects, industry and audience problems. Expand branded language into plain terms; preserve exact talk titles for scoring.
2. Search authorized catalogs if present, then PodcastIndex, Apple/iTunes, Listen Notes or ordinary search/RSS. The source uses Apify as a fallback below ten unique discoveries when configured. These providers are optional; browser research can perform the same decisions.
3. Normalize feed/show/provider IDs and URLs, merge complementary metadata and deduplicate. Do not use a shared hosting domain as a show identity. Distinguish the show from an individual episode and a network from a host.
4. Check current publishing activity, language, audience niche, actual guest appearances and editorial focus. Record episode dates and URLs. Do not infer audience size as a fact from episode count or Listen Score; retain it as an estimate.
5. Score topic alignment, recency, reach and guest format. Apply topic confidence adjustment. Scores below 20 are rejected in the source pipeline. GREEN/YELLOW/RED are ranking labels, not proof of current suitability.
6. Enrich in order: RSS owner/contact; official site and booking/contact pages; public professional host/producer evidence; optional authorized contact providers; explicit mailbox verification if available. Confirm the host is a person. Validate forms and check they are for guest applications, not general contact, streaming or login pages.
7. Build a worthwhile batch from the highest fitting shows with usable routes. The later source targets 20 outreach-ready records and keeps insufficient-contact records separately rather than letting them consume the ready target. Use the client's requested batch size instead of blindly generating 20.
8. Use [pitch preparation](../speakeragent-pitches/SKILL.md). Optional human-connection matching is justified by real speaker and host evidence. Review one actual episode detail for refinement; never imply the speaker listened unless supported.

Save unfinished enrichment and lower-priority discoveries for later. Do not spend on an inactive backfill just because the original SaaS does. Refresh current evidence before recommending an old stored record. Track `New`, `Contacted`, `Replied`, `Booked`, `Passed` only from actual client actions; a generated email remains a draft.
