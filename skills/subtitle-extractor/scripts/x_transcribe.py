#!/usr/bin/env python3
"""Download an X/Twitter video and transcribe its speech to a subtitle file."""

from __future__ import annotations

import argparse
import glob
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=capture)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip() if capture else ""
        raise RuntimeError(f"Command failed ({command[0]}): {detail}")
    return result


def metadata(url: str, cookies: str | None) -> dict[str, object]:
    command = ["uvx", "yt-dlp", "-J", url]
    if cookies:
        command += ["--cookies-from-browser", cookies]
    result = run(command, capture=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"yt-dlp did not return JSON: {result.stdout[:500]}") from error


def choose_progressive_format(formats: list[dict[str, object]]) -> str:
    candidates: list[tuple[int, float, int, str]] = []
    for item in formats:
        protocol = str(item.get("protocol", "")).lower()
        ext = str(item.get("ext", "")).lower()
        # X marks its progressive MP4 variants with null/unknown codecs; these contain both streams.
        vcodec = str(item.get("vcodec") or "unknown").lower()
        acodec = str(item.get("acodec") or "unknown").lower()
        if not protocol.startswith("http") or ext != "mp4" or vcodec == "none" or acodec == "none":
            continue
        candidates.append(
            (
                int(item.get("height") or 0),
                float(item.get("tbr") or 0),
                int(item.get("filesize") or 0),
                str(item["format_id"]),
            )
        )
    if not candidates:
        raise RuntimeError(
            "No progressive MP4 with embedded audio was available. Install FFmpeg, then use yt-dlp with bv*+ba/b."
        )
    return max(candidates)[-1]


def tweet_id(url: str) -> str:
    match = re.search(r"/status(?:es)/(\d+)", url)
    if not match:
        parsed = urlparse(url)
        return re.sub(r"[^0-9A-Za-z_-]+", "_", parsed.path).strip("_") or "x-video"
    return match.group(1)


def download_existing_subtitle(
    url: str, output: Path, language: str, cookies: str | None
) -> None:
    command = [
        "uvx", "yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
        "--sub-langs", language or "all,-live_chat", "--sub-format", "srt/best",
        "--convert-subs", "srt", url,
    ]
    if cookies:
        command += ["--cookies-from-browser", cookies]
    with tempfile.TemporaryDirectory(prefix="x-subtitle-") as temporary:
        work_dir = Path(temporary)
        run(command + ["-o", str(work_dir / "subtitle.%(ext)s")])
        matches = sorted(glob.glob(str(work_dir / "subtitle.*.srt")) + glob.glob(str(work_dir / "subtitle.srt")))
        if not matches:
            raise RuntimeError("X reported a subtitle track but yt-dlp did not write one.")
        shutil.move(matches[0], output)


def transcribe(
    url: str,
    output: Path,
    model: str,
    language: str | None,
    cookies: str | None,
    format_name: str,
) -> None:
    info = metadata(url, cookies)
    if info.get("subtitles"):
        download_existing_subtitle(url, output, language, cookies)
        return

    formats = info.get("formats") or []
    if not isinstance(formats, list):
        raise RuntimeError("yt-dlp returned no format list.")
    format_id = choose_progressive_format(formats)

    with tempfile.TemporaryDirectory(prefix="x-subtitle-") as temporary:
        work_dir = Path(temporary)
        media = work_dir / "media.mp4"
        command = ["uvx", "yt-dlp", "-f", format_id, "-o", str(media), url]
        if cookies:
            command += ["--cookies-from-browser", cookies]
        run(command)
        generated = work_dir / "generated"
        generated.mkdir()
        transcriber = [
            "uvx", "--from", "whisper-ctranslate2", "whisper-ctranslate2", str(media),
            "--model", model, "--output_format", format_name, "--output_dir", str(generated),
            "--condition_on_previous_text", "False", "--vad_filter", "True",
            "--no_repeat_ngram_size", "4",
        ]
        if language:
            transcriber += ["--language", language]
        run(transcriber)
        matches = list(generated.glob(f"*.{format_name}"))
        if not matches:
            raise RuntimeError("Transcription finished but no subtitle file was generated.")
        shutil.move(matches[0], output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="X/Twitter post URL")
    parser.add_argument("--output", "-o", type=Path, help="Output subtitle path")
    parser.add_argument("--model", default="base", help="Whisper model (default: base)")
    parser.add_argument("--language", help="Speech language; omit for detection")
    parser.add_argument("--format", choices=("srt", "vtt", "txt"), default="srt")
    parser.add_argument("--cookies-from-browser", dest="cookies", help="Browser profile for yt-dlp cookies")
    args = parser.parse_args(argv)

    output = args.output or Path("outputs/x") / f"{tweet_id(args.url)}.{args.format}"
    output.parent.mkdir(parents=True, exist_ok=True)
    transcribe(args.url, output, args.model, args.language, args.cookies, args.format)
    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
