# In-universe franchise watch order

Use when the user's discs include films and television episodes from one franchise, or when they request a continuous story-chronology viewing sequence. Digitize the films they actually supply as well as the episodes. This is local ingestion and USB playback preparation; do not upload media to a service without a separate request.

## Establish the sequence

1. Inventory the actual discs, selected cuts, episodes, films, specials, and their verified identities. Do not create a playback file for a film the user does not have.
2. Separate continuities, reboots, remakes, and alternate cuts before ordering. A shared franchise name does not prove one timeline. Preserve official episode numbering and one final file per episode. Technical source segments of one episode become one episode file; separately numbered `Part I`, `Part II`, and `Part III` episodes remain separate files. A movie split across discs becomes one movie only when its identity and part order are established.
3. Research **where the main story of each owned work belongs in-universe**. Prefer creators, studios, broadcasters, official episode guides, and on-disc evidence; use credible independent chronology guides to resolve gaps. Record URLs or supplied packaging, access date, exact edition/cut, placement relative to neighboring episodes, and confidence. Release date, production date, disc order, filename, flashback setting, and a character's age alone do not establish the viewing position.
4. For time travel, overlapping stories, or disputed placements, describe the ambiguity and choose a clear viewing rule with the user rather than silently inventing a single canonical timeline. Do not mix separate continuities to fill gaps.

Keep one `watch_order.json` in the franchise workspace as the order source of truth. Give each entry a stable content ID, continuity, kind (`episode`, `film`, or verified special), owned/missing status, official identity, story neighbors, placement evidence, confidence, and, for owned items, final file path and verification state. The ordered list is authoritative; four-digit filename ordinals are generated anew for each export. Insert newly acquired works at their researched position and rebuild the numbered view instead of treating old prefixes as permanent identities. Generate a plain `WATCH_ORDER.txt` from the same list; avoid competing hand-written orders.

For an owned box whose discs have not yet been mapped, `watch_order.json` may also have a `planned_sequence` of researched high-level story blocks and a `next_disc` prompt. Each planned item needs a unique `id` and `title`; record placement, provisional physical label, source URLs, uncertainty and progress. `build_watch_view.py` prints this plan in `WATCH_ORDER.txt` while keeping the playback folder limited to verified `entries`. A planned disc is neither a verified owned MP4 nor a missing franchise title. Replace planning blocks with stable per-episode/film entries as their exact on-disc identities and final files are established. Do not invent playable files or physical disc maps from the plan.

## Missing works and availability

Include missing entries only when they help bridge the user's owned viewing span or have been requested explicitly. Do not enumerate an entire large franchise by default. Record exactly what is missing, whether it is a whole film, season, or episode, and why it belongs between the neighboring owned works. Do not insert an alternate edit of content already present as though it were a new story installment.

For each requested missing entry, check current legal viewing offers in the user’s relevant country or countries. Confirm exact title, season, and edition with the provider when possible. Record service, country, subscription/free/rent/buy type, source URL and check date. Availability and account access change; say `No confirmed offer` when verification fails.

`WATCH_ORDER.txt` is a UTF-8 human guide beside the playback folder. List each owned or requested missing work in story order with dated availability evidence. Keep detailed per-title notes separately if useful. Do not assume a TV video browser opens `.txt` files; test that feature on the actual model before relying on it.

If the user wants missing-title reminders in the `Next` sequence and the player cannot open text, use clearly labelled short MP4 information cards. Consolidate a long missing span into one card rather than flooding the view. A card must say `NOT ON THIS USB`, name the missing work and its dated offer, and never masquerade as the film or episode. Replace it with a verified owned MP4 when acquired and regenerate ordinals.

## Make the USB sequence understandable

Create a single flat playback view per continuity with fixed-width numeric prefixes so filename sorting can interleave films and episodes:

```text
Franchise_Watch_Order/
  0001_S01E01_Episode_Title_Series_Name_Year.mp4
  0002_Film_Title_Year.mp4
  0003_S01E02_Next_Episode_Series_Name_Year.mp4
```

Names after the prefix retain each verified episode or film stem. The prefix is a playback-view order key, not an episode number. Use `scripts/build_watch_view.py` to preview and regenerate the numbered view and `WATCH_ORDER.txt` from the manifest; it hardlinks owned MP4s on one volume without duplicating bytes. Test the target player’s sort order and `Next` behavior separately.

Test the actual USB stick and player with a three-file episode, film or information card, episode transition when that sequence exists. Confirm numeric display order, `Next` behavior, sound and placement. If unavailable, record playback order as pending; a correctly numbered folder alone does not prove device behavior.

## Working SSD and TV USB stick

Treat the working media volume and playback USB device as separate locations. Identify the actual destination mount, volume and free space before an authorized export. Preview the selected numbered files and destination, preserve existing files, verify copy counts and hashes, then test the USB copy on the player. A working file is not delivered merely because it exists on the source volume.
