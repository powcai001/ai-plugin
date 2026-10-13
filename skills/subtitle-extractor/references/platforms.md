# Platform Guide

## YouTube

The unified router calls the bundled Jim Liu TypeScript implementation:

```bash
python3 {baseDir}/scripts/extract_subtitle.py \
  'https://www.youtube.com/watch?v=VIDEO_ID' --lang en --output outputs/video.srt

# Direct access when debugging:
npx -y bun {baseDir}/scripts/youtube/main.ts 'URL' --list
```

The script supports text/SRT output, language priority, translated transcripts, cache refresh, and `yt-dlp` fallback. If the bundled implementation cannot run, use `yt-dlp` directly:

```bash
yt-dlp --list-subs 'URL'
yt-dlp --skip-download --write-subs --sub-langs 'LANGS' \
  --sub-format 'srt/best' --convert-subs srt -o '%(title).80s.%(ext)s' 'URL'
```

Use `--write-auto-subs` only when no manual caption exists or the user explicitly wants automatic captions.

## Bilibili

The preferred path in this environment is OpenCLI because the browser session can provide Bilibili login. The script first requests only the subtitle track:

```bash
python3 {baseDir}/scripts/extract_subtitle.py 'URL' --output outputs/video.srt

# Direct access:
python3 {baseDir}/scripts/bilibili_srt.py 'URL' --lang zh-CN --page 1 \
  --output outputs/video.srt
```

OpenCLI returns external or AI subtitle cues and the converter changes `0.48s` style times into SRT timestamps. If the browser session is not logged in, run `opencli bilibili login` first. `EMPTY_RESULT` means the video has no external or AI subtitle; it is not a danmaku result.

When no subtitle track exists, the default behavior is to download the best audio-only Bilibili format, run `whisper-ctranslate2` with VAD and repetition suppression, and write the requested SRT/VTT/TXT file. Use `--no-transcribe` when the user explicitly wants to fail rather than accept generated speech subtitles. The script prints `mode=subtitle_track` or `mode=speech_transcription`.

Fallback for environments where OpenCLI is unavailable: use maintained `yutto 'URL' --subtitle-only --no-danmaku --no-cover`. This requires Bilibili authentication and FFmpeg.

## X/Twitter

Most X videos have no separate subtitle track. The bundled script checks metadata first; if no track exists, it selects an HTTP progressive MP4 with embedded audio and transcribes locally:

```bash
python3 {baseDir}/scripts/extract_subtitle.py 'X_URL' \
  --model base --language English --output outputs/video.srt
```

The script uses `--vad_filter True`, `--condition_on_previous_text False`, and `--no_repeat_ngram_size 4` to suppress trailing silence hallucinations. Add `--cookies-from-browser BROWSER` through the router when login state is required. If captions are visibly burned into the picture, the correct route is OCR, which is not implemented yet.

## Local Video

For a local video, the script inspects subtitle streams with FFmpeg. If a text stream exists, `--subtitle-track N` selects the one-based track and FFmpeg converts it to SRT, VTT, or TXT:

```bash
python3 {baseDir}/scripts/extract_subtitle.py INPUT.mkv \
  --subtitle-track 1 --format srt --output outputs/local/video.srt
```

If the video has no text subtitle stream, the script downloads nothing and transcribes the media's speech locally:

```bash
python3 {baseDir}/scripts/extract_subtitle.py INPUT.mp4 \
  --model base --lang zh --output outputs/local/video.srt
```

Add `--transcribe` to skip an embedded track and force speech transcription.

## Local Audio

Audio has no subtitle stream, so the router transcribes it directly:

```bash
python3 {baseDir}/scripts/extract_subtitle.py INPUT.m4a \
  --model base --lang en --format srt --output outputs/local/audio.srt
```

FFmpeg is located from `PATH`, or from the `imageio-ffmpeg` package through `uv` when system FFmpeg is absent. Image-based subtitle formats such as PGS/VobSub and subtitles burned into pixels require OCR; that path is not implemented and must not be represented as extracted text subtitles.

## Tool Notes

- `yt-dlp` supports YouTube, Bilibili, and Twitter/X media extraction. Keep it current because platform extractors change often.
- OpenCLI provides the authenticated Bilibili subtitle API used by the converter.
- `faster-whisper`/`whisper-ctranslate2` transcribe speech and can output SRT/VTT/TXT; they do not OCR burned-in captions.
- FFmpeg extracts local embedded text subtitle streams. The router's Whisper path can decode media directly, so FFmpeg is not required when only transcription is needed.
