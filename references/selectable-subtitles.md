# Selectable subtitles for compatible MP4 files

Use this workflow when the user asks for optional source-language subtitles, OCR, transcription, or translated subtitle tracks in compatible playback files.

## Scope and safety

- Modify only compatible playback copies. Do not alter archival MKVs or lossless disc mirrors.
- Inspect workspace documentation, actual streams, active processes, and existing subtitle artifacts before starting. Do not disrupt a healthy rip, encode, or verification process.
- Work from local files and do not access the optical drive unless the user separately authorizes disc access.
- Never overwrite a verified MP4. Create a separately named candidate, verify it, quarantine the superseded file reversibly, and only then promote the candidate to the canonical path.
- Copy existing video and audio streams during subtitle integration. Do not re-encode them merely to add subtitles.
- Do not upload media, audio, or subtitles to an external service without explicit authorization.

## Coordinator-led subtitle swarm

Use bounded swarm orchestration for all subtitle extraction, OCR, transcription, correction, translation, and verification work. If agents are unavailable, preserve the same coordinator, cluster ownership, serialization, and independent-review boundaries locally.

The coordinator exclusively owns:

- the episode dependency graph, cluster boundaries, shared glossary, and adjacent-context policy;
- unique working paths and final output reservations;
- concurrency decisions based on measured CPU, memory pressure, thermals when observable, storage, model throughput, and process health;
- cluster assembly, cue renumbering, duplicate and gap detection, final promotion, and all shared documentation updates.

Workers never edit shared workflow, status, manifest, or technical logs. They return structured results with their exact input cue range, context range, output path, cue count, source method, tool or model, warnings, checks, and unresolved uncertainty.

Split work at confirmed chapter or scene boundaries when possible. Each authored cue belongs to exactly one cluster. Supply a small read-only context window from the preceding and following cluster plus one shared glossary for names, ranks, locations, recurring phrases, and technical terms. Context cues must never be emitted twice. Do not split a dialogue exchange when a nearby safe boundary is available.

Start with no more than two simultaneous OCR, transcription, or translation model jobs. Increase concurrency only when aggregate completed cues per minute improves without harmful memory pressure, swapping, thermal constraint, storage pressure, stalled output, or interference with an existing media process. Reduce concurrency when those conditions deteriorate. Do not interrupt or restart a healthy process solely to convert it into clustered work; let it finish, verify its result, and apply clustering to remaining work.

Use separate responsibilities where work exists:

1. Source worker: extract original text or bitmap cues and preserve source timing and provenance.
2. OCR or transcription workers: reconstruct the source language in uniquely assigned clusters.
3. Source-review worker: correct OCR or transcript errors, names, punctuation, line breaks, and missing or duplicated cues against source evidence.
4. Translation workers: translate only reviewed source clusters using the shared glossary and inherited timing.
5. Language-quality worker: review meaning, naturalness, terminology, reading length, encoding, and special characters independently of the translating worker.
6. Timing worker: validate ordering, overlaps, negative or out-of-range timestamps, boundary continuity, numbering, and one-to-one cluster assembly.
7. Integration and playback worker: remux selectable tracks, prove video/audio stream preservation, and perform container and QuickTime checks.

The coordinator may combine lightweight roles when the workload is small, but the author of an OCR or translation cluster must not be its only quality reviewer. Merge only clusters that pass their assigned checks. Preserve failed or superseded cluster artifacts under clearly marked working or quarantine paths; never silently reuse them.

## Source-language subtitle hierarchy

Use the highest reliable source available, in this order:

1. Existing text subtitles in the MP4, archive MKV, local mirror, or verified sidecar.
2. Original bitmap DVD subtitles extracted from the archive MKV or local mirror and converted through reliable OCR.
3. Audio transcription only when no usable source subtitle exists.

Record whether each subtitle came from an original text track, bitmap OCR, or audio transcription. An OCR or transcript is not verified merely because a tool completed successfully.

For bitmap OCR, review names, punctuation, character substitutions, line breaks, overlaps, missing captions, timing, opening and closing credits, and chapter transitions. For transcription, use the known spoken language rather than automatic detection, retain usable timestamps, and prefer the most accurate locally practical model. Use an appropriate local transcription engine, such as a suitable Whisper implementation, only after verifying its installed capabilities and model requirements. Do not install or invoke a cloud service without authorization.

## Translated subtitles

Create a translated track only when the user requests it and the source-language subtitle has been reviewed first.

- Translate meaning and tone naturally while preserving names and established terminology.
- Reuse the verified source timing, then adjust line breaks and text length for readability without changing scene alignment.
- Label the track with the correct target-language code and title.
- Document it as a derived translation. Do not imply that the DVD contained a dub or original subtitle in that language.
- Do not invent an audio track, official localized title, or official translation.
- Translate reviewed clusters concurrently only within the coordinator's measured limit. Keep cue identifiers and source timestamps stable through translation so the coordinator can assemble results deterministically.
- Apply one coordinator-owned glossary across every cluster and future episode in the same series. Record glossary changes and recheck already translated clusters when a changed term affects them.

## Intermediate and container formats

Keep reviewed sidecars in a factual workspace location such as:

```text
Subtitles/Season_01/
  S01E01_Title_English.srt
  S01E01_Title_German.srt
```

Use MP4-compatible selectable text subtitles, normally `mov_text`/`tx3g`. Do not burn subtitles into the video. For an English source track and a user-requested German translation, use:

- English: language `eng`, title `English`, default according to the user's preference, forced false.
- German translation: language `deu`, title `German`, non-default unless requested otherwise, forced false, provenance recorded as translated from the reviewed English track.

Preserve video, audio, chapters, duration, frame rate, resolution, SAR/DAR, default audio selection, and relevant metadata. Build candidates with a temporary suffix such as `_Subtitles`; never target the canonical verified output directly.

## Pilot and verification gate

Process one episode as a pilot before a batch unless the user explicitly chooses another scope. Promote or batch only after the pilot passes.

For the pilot, measure completed cues per minute, peak memory pressure, model concurrency, correction rate, and merge defects. Use those measurements to choose concurrency for future episodes instead of assuming that more workers are faster. Do not begin the remaining episode batch until the assembled English and requested translated tracks pass the complete pilot gate.

For every candidate:

1. Confirm a readable, complete container and expected duration.
2. Confirm video and audio streams are byte-copied or otherwise unchanged as intended, with their codecs, languages, defaults, chapters, geometry, and frame rate preserved.
3. Confirm every subtitle track has the intended codec, language code, title, default flag, and forced flag.
4. Check caption counts, first and last timestamps, overlaps, invalid or out-of-range cues, and representative synchronization at the beginning, middle, end, chapters, and warning locations.
5. Review source-language accuracy and translated meaning, names, punctuation, encoding, umlauts, and line readability. Automated translation alone is not sufficient verification.
6. Verify cluster assembly: every expected cue appears exactly once, cluster boundaries contain no truncated dialogue, cue numbering is continuous, and shared context produced no duplicated text.
7. Fully decode video and audio and record the result.
8. Open the candidate in QuickTime Player. Play multiple positions and verify that each subtitle appears, can be switched independently, can be disabled, remains synchronized, and renders special characters correctly.
9. When practical, test another target television or Apple-compatible player. Record the test as unavailable rather than assuming compatibility when no device is accessible.

After verification, move the prior canonical MP4 to a clearly named quarantine inside the workspace, promote the verified candidate without re-encoding, and re-check the final path and hashes. Never permanently delete the quarantined predecessor without explicit confirmation.

## Persistent records

Update the workspace workflow, status, manifest, relevant disc log, and technical log after successful verification. Record per episode:

- final and quarantined paths, size, duration, and hash;
- source subtitle origin and language;
- OCR or transcription tool and version when used;
- review and correction status;
- translation source and provenance;
- cue counts and timing bounds;
- embedded codec, language tags, titles, default and forced flags;
- technical decode and QuickTime switching results;
- unavailable device tests and remaining uncertainties.
- cluster boundaries, worker ownership, glossary version, concurrency used, measured throughput, independent-review result, and merge gap/duplicate checks.

Do not mark a subtitle verified until its content, timing, metadata, selectability, disable behavior, and required playback checks have actually passed.
