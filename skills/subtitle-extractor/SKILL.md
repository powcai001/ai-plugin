---
name: subtitle-extractor
description: Extract or generate SRT/VTT/TXT subtitles from YouTube, Bilibili, X/Twitter, and local video/audio files; distinguish embedded subtitle tracks from speech transcription while avoiding danmaku.
---

# Subtitle Extractor

## Workflow

1. Identify the source and the requested output format. Default to `.srt`; use `.vtt`, `.md`, or `.txt` only when requested.
2. Route by source:
   - YouTube: use the bundled Jim Liu transcript implementation under `scripts/youtube/`.
   - Bilibili: use the bundled OpenCLI converter first; if no subtitle track exists, download audio only and transcribe speech locally.
   - X/Twitter: use the bundled transcriber; it first checks for a platform subtitle track, then downloads progressive MP4 audio/video and runs faster-whisper with VAD.
   - Local video: inspect embedded text subtitle tracks first and extract the selected track; if none exists, transcribe speech.
   - Local audio: transcribe speech directly.
3. Report the mode shown by the script: `subtitle_track` means a platform subtitle was downloaded, `embedded_subtitle_track` means a local text subtitle stream was extracted, and `speech_transcription` means audio was transcribed.
4. Save user-facing deliverables under the current task's `outputs/` directory unless the user specifies another path. Do not put temporary media in `outputs/`.
5. Verify the result: the file exists, is non-empty, has the expected extension, and spot-checks contain timestamp/text pairs for SRT or VTT.

The normal entry point is:

```bash
python3 {baseDir}/scripts/extract_subtitle.py 'URL' --output outputs/subtitle.srt
```

Common options are `--lang`, `--page`, `--model`, `--format`, `--cookies-from-browser`, `--subtitle-track`, and `--transcribe`. Run the script with `--help` before adding platform-specific flags.

For commands, platform limits, dependencies, and fallbacks, read [references/platforms.md](references/platforms.md). When validating this skill or diagnosing a regression, read [references/testing.md](references/testing.md).

## Constraints

- Danmaku is not a subtitle. Never present danmaku output as the requested subtitle.
- A missing platform caption does not mean speech is absent. Transcription requires audio; OCR is required for subtitles burned into the picture.
- Platform login, cookies, age restrictions, region locks, and anti-bot checks can block extraction. Preserve the exact blocker and use the smallest appropriate fallback rather than repeatedly retrying.
- Do not send private local media to a third-party web downloader. Prefer local tools.
- Local processing is offline: FFmpeg is used only to inspect/extract an embedded subtitle stream, and transcription runs locally through faster-whisper. Burned-in or image-based subtitles require OCR, which is not implemented.

See [references/credits.md](references/credits.md) for the MIT-licensed YouTube implementation included in this skill.
