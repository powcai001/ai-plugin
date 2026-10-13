# Validation

Use these cases when changing routing logic or commands. Keep generated test artifacts under `work/`, not `outputs/`.

## YouTube Success

Request English SRT through the unified router:

```bash
python3 {baseDir}/scripts/extract_subtitle.py \
  'https://www.youtube.com/watch?v=dQw4w9WgXcQ' \
  --lang en --output work/skill-test/youtube/routed.srt
```

Pass criteria: exit 0; a 4 KB-scale `.srt` exists; its first blocks contain numbered cues, `-->` timestamps, and text. A direct InnerTube empty response followed by `yt-dlp` fallback is acceptable. The transcript may legitimately include music markers such as `[♪♪♪]`.

## Bilibili Success

Use the logged-in OpenCLI browser session and the multi-part public test video from yt-dlp's extractor tests:

```bash
python3 {baseDir}/scripts/extract_subtitle.py \
  'https://www.bilibili.com/video/BV1bK411W797?p=1' \
  --output work/skill-test/bilibili/routed_p1.srt
```

Pass criteria: exit 0; the SRT starts near `00:00:00,480`; it contains Chinese cue text; no danmaku/XML/ASS file is created.

## Bilibili Speech-Transcription Fallback

Use `https://www.bilibili.com/video/BV16oM96GEhy`, a 36-second video that OpenCLI reports has no subtitle track:

```bash
python3 {baseDir}/scripts/extract_subtitle.py \
  'https://www.bilibili.com/video/BV16oM96GEhy' \
  --model base --lang zh --output work/skill-test/bilibili/BV16oM96GEhy.srt
```

Pass criteria: exit 0; `mode=speech_transcription`; a non-empty Chinese SRT is produced; no danmaku file is produced.

## Bilibili No-Transcribe Guard

Run the same URL with `--no-transcribe`. Pass criteria: exit 1 with `This Bilibili video has no external or AI subtitle track.`

## X/Twitter Success

Use the 30-second public test post from yt-dlp's extractor tests:

```bash
python3 {baseDir}/scripts/extract_subtitle.py \
  'https://x.com/TopHeroes_/status/2001950365332455490' \
  --model base --language English --output work/skill-test/x/routed.srt
```

Pass criteria: exit 0; seven English cues are generated; all cue ends are at or before the media duration around 30.33 seconds; no cue extends to 40 seconds. The last condition verifies that VAD suppressed trailing-silence hallucination.

## X/Twitter Subtitle-Track Probe

Run `uvx yt-dlp --list-subs 'https://x.com/TopHeroes_/status/2001950365332455490'`. Pass criteria: it reports no platform subtitles. This confirms the successful X test exercises transcription rather than caption download.

## Local Embedded Subtitle

Create a small Matroska file containing one SRT stream, or reuse the generated fixture, then call:

```bash
python3 {baseDir}/scripts/extract_subtitle.py work/test-local/embedded.mkv \
  --output work/skill-test/local/embedded.srt
```

Pass criteria: exit 0; `mode=embedded_subtitle_track`; the cue `Subtitle extractor local test` is preserved. Also verify TXT contains only the cue text and VTT starts with `WEBVTT`.

## Local Video Transcription

Use the downloaded X media fixture:

```bash
python3 {baseDir}/scripts/extract_subtitle.py work/x-test/video/2001841416071450628.mp4 \
  --model base --language en --transcribe \
  --output work/skill-test/local/video-transcript.srt
```

Pass criteria: exit 0; `mode=speech_transcription`; seven English cues are present.

## Local Audio Transcription

Extract or otherwise provide an M4A containing intelligible speech, then call:

```bash
python3 {baseDir}/scripts/extract_subtitle.py work/test-local/speech.m4a \
  --model base --language en --output work/skill-test/local/audio-transcript.srt
```

Pass criteria: exit 0; `mode=speech_transcription`; the result matches the local video transcription test in content and duration.

## YouTube No-Caption Path

Run `yt-dlp --list-subs 'https://www.youtube.com/watch?v=aqz-KE-bpKQ'`. Pass criteria: the command reports that no subtitles/automatic captions are available rather than producing an empty subtitle file.
