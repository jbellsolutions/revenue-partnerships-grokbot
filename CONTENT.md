# Content and channel growth plays: YouTube, X, LinkedIn (round 2, 2026-11-12)

Justin, 2026-11-12: "what are the best setups for creating good viral content and specifically growing channels, specifically on YouTube, X, and LinkedIn? Those are our main focuses."

This extends `PLAYS.md` sections 4 and 5 (C1 to C3, G1 to G3). In a pack, `PLAYS.md`, `sources/` and `refresh/` refer to the private plays research, not this folder. The research is in `sources/9-content-youtube.md`, `10-content-x.md` and `11-content-linkedin.md`, using the brief in `sources/CONTENT-BRIEF.md`. Every setup below is **draft-only**: the bot researches and writes, and Justin posts.

## Read this first

- **No source shows a GrokBot growing a channel with audited numbers.** The best Grok cases are self-reported:
  - Postiz: 69.8M impressions across three X accounts, no follower data.
  - Elisa: 500+ YouTube subscribers and 1.5M Instagram views in 30 days.

  The large datasets are about formats and hooks, not bots: AuthoredUp (309,614 LinkedIn posts), Metricool (600K), Buffer (52M), and X's own open-sourced ranker.
- **Two ban findings change how the pack works today:**
  1. **X:** a GrokBot that posted and replied through the browser got its account **permanently restricted to read-only** on 2026-09-25 ([forum report](https://forum.cursor.com/t/grok-bots-x-assistant-ran-browser-automated-posting-and-replies-without-warning-about-xs-automation-rules-and-the-account-was-frozen/172989)). X's developer rules allow only the official API for automation and ban browser automation. xAI's own page lists the GrokBot X connector as read-only: search, timeline, mentions, trends and bookmarks. The pack's `x-channel` skill planned to post through Justin's signed-in browser, and this round turns that off.
  2. **LinkedIn:** GrokBot's cloud computer runs on a data-centre IP. Signing it into a LinkedIn account caused "unusual activity" warnings and a CAPTCHA (AI Data House, 2026-08-16). LinkedIn's User Agreement 8.2 bans bots that post, comment, like or message. In 2026 LinkedIn named AI comment tools as a target, cut reach on generic AI posts, and added a "Seems like AI slop" flag (2026-07-30).
- **So the safe lane on all three platforms is the same.** The bot researches, drafts, scores and reads analytics. Justin publishes from his own device:
  - On X and LinkedIn, he posts and replies himself.
  - On YouTube, uploads stay private until he makes them public.

  Marking a type `auto` never switches on browser posting on X or LinkedIn.
- **Generic AI text now costs reach on X and LinkedIn.** Every draft has to carry one first-hand detail only Justin has (a client build described without the name, a number from his own work). If the bot has no such detail, it asks Justin for one instead of drafting.

## How plays are scored

Same rule as `PLAYS.md`: score = evidence + fit + safety, each from 1 to 3.

**Evidence:**
- 3: data or a table is shown on a large sample.
- 2: a creator states specific numbers, or a platform's own page or code says so.
- 1: a claim or a template.

**Re-score from round 1.** Postiz's write-up shows charts and Stripe figures that the round 1 source (stealwhatworks, a claim) didn't, so X1 takes evidence 2 where C1 had 1. It is still vendor-hosted and doesn't isolate the bot's contribution, so it isn't a 3.

## Top setups per platform

Ranked by score, then by the PLAYS.md tie-break: higher evidence, then higher safety, then the more recent source. E1, the content engine, isn't in the ranking: it is built from the setups below, and scoring it too would count their evidence twice. It is the recommended build (next section).

| Rank | Setup | Platform | Score | Why |
|---|---|---|---|---|
| 1 | **L2 Hook lab** | LinkedIn (and X) | 9 | The strongest data in the round, from 309,614 posts. Story openers do best (2.60% median), question openers worst (2.16%), and short hooks of 40 characters or fewer beat long ones. |
| 2 | **X1 Outlier research, angle brief, draft queue** | X | 8 | The best Grok-specific case (Postiz, 69.8M impressions). The bot only researches and drafts. |
| 3 | **X2 Write to the open-source ranker** | X | 8 | Primary source: `xai-org/x-algorithm`. Shares, replies and quotes count far more than likes. Reports and mutes count strongly against a post. Posts read to the end are rewarded (Oct 2026). |
| 4 | **Y1 Outlier, title and thumbnail loop, with YouTube's own A/B test** | YouTube | 8 | YouTube picks the winner by watch time. The bot drafts the options. |
| 5 | **Y2 Shorts from Justin's own long videos** | YouTube | 8 | Shorts bring discovery. Long-form carries the watch hours and the revenue (Shorts RPM is roughly 3 to 14% of long-form). |
| 6 | **L1 Voice-profile ghostwriter with a first-hand detail** | LinkedIn | 8 | The one way left to use AI drafts on LinkedIn without losing reach. |
| 7 | **X3 and L5 Reply desks:** the bot briefs, Justin types | X, LinkedIn | 8 | A human-typed reply list on X: about 6K impressions a day rising to a best day of 555K (ShipGuild). On LinkedIn, replies within 60 to 90 minutes of posting. |
| 8 | **L3 Newsjacking queue:** scan X and news, take for LinkedIn | LinkedIn | 8 | LinkedIn trails X by a couple of days (Distinct Idea: 208K impressions on one client post). Elisa runs this as a GrokBot chief of staff. |
| 9 | **L6 and X4 One recording into a carousel, a thread, singles and an Article** | LinkedIn, X | 8 | Carousels win on interactions (Metricool, 600K posts) while images win on reach (TheShieldIndex), so alternate the formats. Posts people read to the end are rewarded on X. |
| 10 | **X5 Weekly format test** (the X part of W1) | X | 8 | Accounts that post daily grow, and accounts that post in bursts stall (InnMind, Buffer). The same loop on YouTube (Y4) and LinkedIn (L8) scores 7, since it has evidence 1 there. |

Per platform:
- **YouTube:** Y1, Y2, then Y3 (upload prep), Y4 (retention and CTR read), Y5 (comment desk), Y6 (cadence: 1 long video a week plus 2 to 3 Shorts cut from it).
- **X:** X1, X2, X3, X4 (one recording into a thread, 3 single posts and an Article), X5 (weekly format test), X6 (trend scout), X7 (Original Content Rewards watch).
- **LinkedIn:** L2, L1, L3, L5, L6 (document carousel), then L4 (comment queue), L7 (newsletter recap), L8 (weekly read), L9 (niche check).

## E1. The content engine: the recommended build (one idea or recording, three channels)

**In:** an idea Justin types ("post idea: ..."), a voice memo, or a recording dropped in `requests/channels/` or `requests/content-seo/`. A recording can be his own YouTube video, a podcast guest spot, or a client call recorded with consent.

**Out:** one file, `requests/justin/content-<date>-<slug>.md`, with one section per channel. Each piece also goes to its owner's queue.
- **YouTube:**
  - Long video: a brief with 3 titles, 3 thumbnail concepts, a hook and an outline. For a finished video, the upload prep: title, description, chapters, and the AI-use setting where it applies.
  - Shorts: 3 to 5 cut points of 20 to 45 seconds from Justin's own footage, each with a hook line and on-screen words. Cut with Studio's "Edit into a Short" so each Short links back to the long video.
- **X:**
  - 1 thread.
  - 3 single posts, each with a different hook from the same source.
  - 1 Article of 1,000+ words when the source is long.
  - Each one scored with the X2 weights check.
  - No link in the body. Test link posts in the weekly read.
- **LinkedIn:**
  - 2 posts. Each has 3 first lines from the hook lab and one first-hand detail.
  - 1 document carousel outline, 8 to 12 slides, rendered as a PDF from Justin's brand file.
  - The weekly newsletter section.
  - Links go in the first comment, not the body.
- **Calendar:** a proposed slot for each piece, spaced so no platform gets two from Justin within a few hours (X discounts a second post from the same author in one feed). Start at 1 long video and 2 to 3 Shorts a week, 1 to 3 X posts a day, and 3 LinkedIn posts a week. The weekly read moves these numbers.

**Gates:**
- Each piece's type is ask-first: `youtube_publish`, `x_post`, `linkedin_post`.
- The first post on each channel waits for Justin.
- Justin publishes X and LinkedIn by hand from his own device. YouTube uploads stay private until he makes them public.
- Clients are described, never named. Podcast clips need the host's OK when the host owns the recording.

**Evidence:**
- **Round 1 G1:** botdirectory's repurposer template, with approval per channel.
- **X4:** a one-recording-to-thread workflow.
- **L6:**
  - Metricool, 600K posts: carousels get 17x the interactions of images.
  - TheShieldIndex, 50K posts: images beat carousels on reach.
  - The two disagree, so alternate and compare.
- **Y2:** a small creator's real numbers, where long-form drove the watch hours.

**Score:** not ranked (it combines the setups above). The parts it uses score 8 or 9.

**Replaces:** `repurpose-one-recording` (G1). The engine is that skill's upgrade, on the same Daily content routine, so the two never compete.

## YouTube

**Y1. Outlier, title and thumbnail loop.**
- **What it does:**
  - Twice a week the bot lists niche videos whose views are far above their channel's size.
  - It drafts 2 briefs, each with 3 titles, 3 thumbnail concepts (a frozen moment, four or five words), a hook and an outline.
  - Once a video is live, Justin loads 3 titles and 3 thumbnails into YouTube's own A/B test, which picks the winner by watch time ([help](https://support.google.com/youtube/answer/16391400)).
  - Judge in batches of 10 videos, since one hit pays for the misses.
- **Proof:** [YP8D2_j3_Hc](https://youtu.be/YP8D2_j3_Hc) (2026-11-11, sponsored) and [083D6rEc-3Q](https://youtu.be/083D6rEc-3Q) (older).
- **Score:** 2 + 3 + 3 = 8.

**Y2. Shorts from Justin's own long videos.**
- **What it does:** turns each long video into 3 to 5 cut points from its transcript. Justin or an editor makes the cuts in Studio.
- **Proof:**
  - [G5qyAopGLOA](https://youtu.be/G5qyAopGLOA) (2026-10-24): 33K views, 282 watch hours and 35 subscribers in 2 months, with long videos driving most of the watch hours.
  - [m3bIdi7ZPKE](https://youtu.be/m3bIdi7ZPKE) (2026-11-04): Shorts alone didn't compound.
- **Score:** 2 + 3 + 3 = 8.

**Y3. Upload prep.**
- **What it does:** from the transcript, drafts the title options, description, chapters and tags.
- **Proof:** [oEzK7W6r1Dk](https://youtu.be/oEzK7W6r1Dk), a GrokBot "media manager" (2026-09-18), demonstrated on screen.
- **Note:** uploads through an unverified API project are locked private, which matches the rule that uploads go up private.
- **Score:** 2 + 3 + 2 = 7.

**Y4. Weekly retention and CTR read.**
- **What it reads:** click rate on impressions, the share of viewers still watching at 30 seconds, spikes and dips, and traffic source.
- **What it writes:** 3 lines that feed Y1.
- **Limit:** below a few hundred views a video, this read is noise.
- **Score:** 1 + 3 + 3 = 7.

**Y5. Comment desk.**
- **What it does:**
  - Drafts replies to comments on Justin's own videos. YouTube Studio's own reply suggestions are an option too.
  - Questions become video ideas.
  - Buyers go to sales-crm.
- **Gate:** Justin sends every reply. No auto-heart, and no comments on other channels.
- **Score:** 1 + 3 + 3 = 7.

**Y6. Cadence.** Start with 1 long video a week and 2 to 3 Shorts cut from it. Nothing in the evidence says more is better at Justin's size. **Score:** 2 + 2 + 3 = 7.

**YouTube ban triggers** ([inauthentic and reused content](https://support.google.com/youtube/answer/1311392), [spam](https://support.google.com/youtube/answer/2801973), [AI disclosure](https://support.google.com/youtube/answer/14328491)):
- mass-produced or templated AI videos
- reposting other people's footage
- automated or repetitive comments
- sub-for-sub or bought engagement
- AI personas giving business or finance advice as experts
- realistic synthetic content that isn't disclosed

## X

**X1. Outlier research, angle brief and draft queue.**
- **What it does:**
  - Daily, uses Grok's native X search over Justin's niche, with a like floor of 500 that rises if the niche is noisy.
  - For each outlier: why a stranger stops scrolling, 5 hook options, the format, and the claims to check.
  - Drafts 1 to 3 posts from Justin's own material. Never copies wording.
- **Proof:** [Postiz](https://postiz.com/blog/grok-bot-3-x-accounts-69m-impressions-content-system) (2026-09-24, vendor) and [2nryhGE4MXw](https://youtu.be/2nryhGE4MXw) (2026-10-27, a claim).
- **Score:** 2 + 3 + 3 = 8.

**X2. Write to the open-source ranker.**
- **What the code says** ([xai-org/x-algorithm](https://github.com/xai-org/x-algorithm), read 2026-11-12):
  - The For You score adds up each action's predicted chance times its weight.
  - Shares (above all copy-link shares), replies, quotes, DM shares and follows count far more than likes.
  - Reports, mutes, "not interested" and blocks count strongly against a post.
  - There is no bookmark action in the code.
  - A second post from the same author in one feed is discounted.
  - Posts older than 48 hours drop out.
  - October 2026 updates reward posts people read to the end.
- **What the bot does:** rewrites each draft for replies and shares: one idea per post, a specific claim worth answering, no bait that invites reports.
- **Score:** 2 + 3 + 3 = 8. The weights are primary evidence; that writing to them causes growth is our inference.

**X3. Reply desk, where the bot briefs and Justin types.**
- **What it does:**
  - Every evening the bot lists 5 to 15 posts under an hour old from accounts 2 to 20 times Justin's size.
  - For each it writes a one-line brief: what the post claims, and the data point or counter-case Justin actually has.
  - **The bot writes a brief, not the reply.** Justin types each reply in his own words.
- **Proof:**
  - [ShipGuild](https://web3bytes.beehiiv.com/p/how-i-got-monetized-on-x-in-6-weeks-with-replies): about 6K impressions a day rising to a best day of 555K, with hand-typed replies.
  - Risk: X removed about 42,000 AI-reply accounts in 2026. One creator's human-edited but polished replies stopped being counted.
- **Score:** 2 + 3 + 3 = 8.

**X4. One recording into a thread, 3 single posts and an Article.** Part of E1. **Score:** 2 + 3 + 3 = 8.

**X5. Weekly format test.**
- **What it does:** logs every post (hook, format, time, impressions, replies, profile clicks, follows), runs one format for a week, and keeps the winners.
- **Score:** 2 + 3 + 3 = 8.

**X6. Trend scout.**
- **What it does:** within an hour or two of niche news, drafts Justin's take. No unrelated trending hashtags.
- **Score:** 2 + 3 + 2 = 7.

**X7. Original Content Rewards watch.**
- **Thresholds:** 500 verified followers and 500K verified impressions in 90 days. Replies don't count.
- **What it does:** reports Justin's distance from the thresholds weekly.
- **Note:** the thresholds come from a vendor summary because X's own page returned 403. Confirm on help.x.com.
- **Score:** 2 + 2 + 3 = 7.

**X ban triggers:**
- browser-driven posting, which has a documented read-only lockout
- AI reply bots without X's written approval
- auto-likes, follows and DMs, and keyword replies
- the same text posted across accounts
- engagement pods
- asking for engagement 3 or more times, which can cost Rewards eligibility

X's terms effective 2026-10-09 are reported to make the account owner responsible for what an agent does.

## LinkedIn

**L2. Hook lab.**
- **What it does:** for every draft, writes 3 first lines (story, contrarian, results with a reason) and flags any opener over 200 characters. Justin picks.
- **Proof:** [AuthoredUp](https://authoredup.com/blog/linkedin-hook-examples), 309,614 posts, Dec 2025 to May 2026. The gaps between styles are small, so this sharpens a draft rather than making one.
- **Score:** 3 + 3 + 3 = 9.

**L1. Voice-profile ghostwriter.**
- **What it does:**
  - Builds a voice profile from Justin's last 20 to 30 posts and his transcripts.
  - Turns a voice memo or bullets into 2 to 3 drafts.
  - Every draft carries one first-hand detail; if there is none, it asks Justin for one.
- **Score:** 2 + 3 + 3 = 8.

**L3. Newsjacking queue.**
- **What it does:** each morning, flags X and news items that beat their source's usual reach and drafts 5 to 10 small-business takes for LinkedIn. It reads X and news only; it never scrapes LinkedIn.
- **Proof:**
  - Elisa (2026-10-28, GrokBot chief of staff, $200 a month, self-reported).
  - Distinct Idea, "This AI Agent Gets Me LinkedIn Content Before I Wake Up" (YouTube, 2026-03-27): 208K impressions on one client post.
- **Score:** 2 + 3 + 3 = 8.

**L5. Reply desk for the first 90 minutes.**
- **What it does:**
  - When Justin says "posted", the bot reads the comment notification emails and drafts a reply to each.
  - Justin sends them, ideally within 15 minutes and within 90 at most.
  - He may ask 5 to 8 real contacts to look at the post. A standing comment-trading group is a pod, so not that.
- **Score:** 2 + 3 + 3 = 8.

**L6. Document carousel.** An 8 to 12 slide PDF built from a recording. Part of E1. **Score:** 2 + 3 + 3 = 8.

**L4. Comment queue.**
- **What it does:**
  - From a list of 30 to 50 people Justin wants to be seen by, the bot drafts an angle for each of their new posts.
  - The input is Justin's notification digest. The bot never reads the feed in a browser.
  - Justin writes a few substantive comments a day himself.
- **Score:** 1 + 3 + 3 = 7.

**L7. Newsletter recap.** Weekly: the best posts, the video and the podcast in one edition, with a "share with a named colleague" ask. Justin publishes it. **Score:** 2 + 2 + 3 = 7.

**L8 and L9. Weekly read and niche check.**
- **L8:** from the analytics CSV Justin downloads, ranks posts by impressions per follower and comments per 1,000 impressions, tags each one by hook, format and topic, and tests 3 versus 5 posts a week.
- **L9:** flags posts someone outside his niche could have written.
- **Score:** 1 + 3 + 3 = 7.

**LinkedIn ban triggers** ([User Agreement 8.2](https://www.linkedin.com/legal/user-agreement), [prohibited software](https://www.linkedin.com/help/linkedin/answer/a1341387), [Fortune 2026-07-31](https://fortune.com/2026/07/31/linkedin-seems-like-ai-slop-button-billions-automated-comments-attempts/)):
- any bot that posts, comments, likes, shares or messages
- scraping profiles or feeds
- using another person's session or copying cookies
- engagement pods
- AI comment tools
- signing a data-centre browser into the account

Generic AI posts aren't removed, but their reach drops to first-degree connections.

## W1. Weekly channel read (all three platforms, one routine)

**When:** Fridays.

**What it reads:**
- **YouTube:** Studio, read-only, Y4 above.
- **X:** analytics as screenshots or numbers Justin pastes, X5 above, plus the X7 distance check.
- **LinkedIn:** the analytics CSV Justin downloads, L8 and L9 above.

**What it writes:** `daily/<date>/channel-read.md`, with this for each platform:
- what to repeat
- what to stop
- next week's one format test
- whether cadence moves up or down

E1 and the platform skills read this file before they draft.

**Score:** 8 for X5 (2 + 3 + 3). The same loop on YouTube (Y4) and LinkedIn (L8) scores 7 (1 + 3 + 3).

## Seen and rejected

- Any bot posting, replying, liking or following through a browser on X or LinkedIn, even with approval.
- AI reply bots that send replies.
- Auto-comment extensions.
- Engagement pods.
- Clipping other people's videos.
- Bulk faceless AI channels and "100 Shorts at once".
- Buying aged channels.
- Sub-for-sub.
- Chasing X Rewards with high-volume AI posts.
- Scraping LinkedIn profiles or feeds.
- Reading Reddit or X through workarounds when they block (this research didn't, and the bot shouldn't).

## Gaps (the weekly refresh closes these)

- Captions for about 15 in-window videos weren't read because YouTube returned 429. They are in `refresh/watchlist.json` under `content_videos`.
- No Reddit thread was read; old.reddit.com returned 403 everywhere.
- X's and LinkedIn's help pages were read second-hand only (403 and 404).
- Not tested yet:
  - whether GrokBot can read X analytics or YouTube Studio
  - the menu path and limits of Studio's "Edit into a Short"
- No follower growth caused by a Grok agent was verified on any platform.
