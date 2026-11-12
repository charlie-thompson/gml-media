# GML nightly social autopilot

Each night, schedule the NEXT day's Good Morning Liberty posts on Facebook, Instagram and TikTok through Metricool. Charlie wants this hands-off. Do not post to X or YouTube.

## Accounts and IDs
- Metricool brand (blogId): `6570605`, timezone `America/Chicago`.
- Content bank: Claude Sheet `08f13b1f-218a-4f0e-971c-7d1cb919b4ff` (https://claude.ai/artifact/273eNjPq432bjzHmsrhLHc), sheet "Content Bank", ranked best-first. Read and write it through the Claude Docs connector (load its `guide` with `topic.sheets` first). Columns: A Rank, B Score, C Hook quote, D Speaker, E Topics, F Formats, G Clip link (YouTube with ?t=), H Start, I End, J Caption, K Episode, L Aired, M Evergreen, N Punch, O Context risk, P Status (New / Approved / Scheduled / Posted / Skip).
- OpusClip: connector tools `opusclip_*`. Do NOT pass brandTemplateId; the account's default GML brand kit applies automatically.
- This repo (public): images go in `cards/`, served at `https://raw.githubusercontent.com/charlie-thompson/gml-media/main/<path>`.

## Daily mix (times America/Chicago, for tomorrow)
- Facebook (8): 07:00 clip (REEL), 09:00 quote card (POST), 11:00 text post, 13:00 clip, 15:00 card, 17:00 text, 19:00 clip, 21:00 card.
- Instagram (3): 09:30 card (POST), 12:00 clip (REEL), 18:00 clip (REEL).
- TikTok (3): 08:00 clip, 13:30 clip, 20:00 clip. TikTok requires `tiktokData.title` (short hook, under 90 chars) and `privacyOption: PUBLIC_TO_EVERYONE`.
- About 3 to 4 distinct clips per day, reused across the three networks. Never post the same clip on the same network twice within 30 days.

## Steps
1. Check Metricool `getScheduledPosts` for tomorrow. If tomorrow already has posts, only fill missing slots.
1b. Fresh episodes first. List OpusClip projects (`opusclip_list_projects`) and find any created since the last run that are new GML episodes (OpusClip Auto Import creates these from new YouTube uploads). For each new episode:
   - Use its best clips (score >= 85, host's own take, not replaying someone else's clip) for at least half of tomorrow's clip slots. Fresh content beats the archive.
   - Pull its transcript with `opusclip_get_transcript` and pick 2 to 3 sharp host one-liners for quote cards and text posts. Same rules as the bank: verbatim, under 25 words, makes sense with no context, no Context risk.
   - Append the new moments to the Content Bank sheet as new rows (Status "Scheduled" for the ones used, "New" for the rest), so later runs can use them.
   - Record the project id in `state/processed_episodes.txt`.
2. Clips, in this order of preference:
   a. Unused clips already in OpusClip with score >= 85 (`opusclip_list_projects`, `opusclip_list_clips`), skipping anything in `state/used_clips.txt` or `state/skip_clips.txt`. Skip clips that are mostly someone else's audio, about shootings, sexual assault, or unverified accusations against private people.
   b. Otherwise cut new ones from the content bank: take the top rows with Status "New", "video_clip" in Formats and an empty Context risk. Submit with `opusclip_submit_project` (videoUrl = the YouTube watch URL, rangeStart = start seconds minus 10, rangeEnd = end seconds plus 10, clipDurationsSec [[20,90]], removeFiller true, customPrompt "Make one clip of the host's complete take in this range. Start on the hook, end on a complete thought."). Poll `opusclip_list_clips` until COMPLETE and take the best clip whose title matches the moment.
   c. Get the HD URL with `opusclip_export_clip` (poll while "rendering"). Pass that URL straight into Metricool `media`; Metricool copies it to its own storage at scheduling time, so the signed URL expiring later is fine.
3. Quote cards: take the next "New" rows with "quote_card" in Formats, empty Context risk, no "..." in the quote and 24 words or fewer. Render with `python3 tools/card.py` (function `card(quote, speaker, out_path)`; speaker shows only for "Chuck", "Nate" or "Josh", never "unclear"). Save as `cards/card_<rank>.jpg`, commit and push to main, then confirm the raw URL returns 200 before scheduling.
4. Text posts: next "New" rows with "text_post" in Formats and empty Context risk. Text = the hook quote in quotation marks, a blank line, then one supporting sentence from the Caption.
5. Captions for clips and cards: the bank's Caption (or a one-line hook for existing OpusClip clips, written in GML's voice: sharp, sarcastic, free-market), then a blank line and "Full episodes every weekday: Good Morning Liberty". TikTok: caption plus 3 hashtags. No em dashes anywhere.
6. Schedule each post with Metricool `createScheduledPost`, `autoPublish: true`, `draft: false`. Facebook clips use `facebookData.type: "REEL"`, cards and text use "POST". Instagram cards `instagramData.type: "POST"`, clips "REEL".
7. Bookkeeping: set Status to "Scheduled" in the sheet for every bank row used. Append used clips to `state/used_clips.txt`. Commit and push.
8. When the bank runs low (fewer than 30 "New" rows with quote_card), say so in the run summary.

## Rules
- Never post anything with a Context risk note, anything where the hosts are replaying someone else's clip, or anything mentioning Seald or its investors.
- If a step fails (OpusClip down, Metricool error), schedule what you can, then report what was skipped. Do not retry a failed Metricool call more than once.
- End each run with a short summary: posts scheduled per network, any gaps, any errors.
