#!/usr/bin/env python3
"""Fetch Bilibili subtitles through OpenCLI and write an SRT file."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_seconds(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if not match:
        raise ValueError(f"Invalid timestamp: {value!r}")
    return float(match.group(0))


def format_timestamp(value: object) -> str:
    seconds = max(0.0, parse_seconds(value))
    whole = int(seconds)
    milliseconds = round((seconds - whole) * 1000)
    if milliseconds == 1000:
        whole += 1
        milliseconds = 0
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def default_stem(target: str, page: int | None) -> str:
    match = re.search(r"BV[0-9A-Za-z]+", target)
    stem = match.group(0) if match else re.sub(r"[^0-9A-Za-z_-]+", "_", target).strip("_")
    return f"{stem}_p{page}" if page else stem


class NoSubtitleError(RuntimeError):
    pass


def fetch_rows(target: str, language: str | None, page: int | None) -> list[dict[str, object]]:
    command = ["opencli", "bilibili", "subtitle", target, "-f", "json"]
    if language:
        command += ["--lang", language]
    if page is not None:
        command += ["--page", str(page)]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        if result.returncode == 66 and ("no data" in detail.lower() or "没有发现" in detail):
            raise NoSubtitleError("This Bilibili video has no external or AI subtitle track.")
        raise RuntimeError(f"OpenCLI could not fetch Bilibili subtitles (exit {result.returncode}): {detail}")
    rows = json.loads(result.stdout)
    if not isinstance(rows, list) or not rows:
        raise NoSubtitleError("This Bilibili video has no external or AI subtitle track.")
    return rows


def rows_to_srt(rows: list[dict[str, object]]) -> str:
    blocks: list[str] = []
    for index, row in enumerate(rows, 1):
        blocks.append(
            f"{index}\n"
            f"{format_timestamp(row['from'])} --> {format_timestamp(row['to'])}\n"
            f"{str(row.get('content', '')).strip()}\n"
        )
    return "\n".join(blocks)


def render_rows(rows: list[dict[str, object]], format_name: str) -> str:
    if format_name == "txt":
        return "\n".join(str(row.get("content", "")).strip() for row in rows if str(row.get("content", "")).strip()) + "\n"
    if format_name == "vtt":
        cues = rows_to_srt(rows).replace(",", ".")
        return f"WEBVTT\n\n{cues}"
    return rows_to_srt(rows)


def whisper_language(language: str | None) -> str | None:
    if not language:
        return None
    normalized = language.lower().split("-")[0]
    return {
        "zh": "Chinese",
        "en": "English",
        "ja": "Japanese",
        "ko": "Korean",
        "yue": "Cantonese",
    }.get(normalized)


def media_target(target: str, page: int | None) -> str:
    if not page:
        return target
    if re.fullmatch(r"BV[0-9A-Za-z]+", target):
        return f"https://www.bilibili.com/video/{target}?p={page}"
    if "bilibili.com/video/" in target and "p=" not in target:
        return target + ("&" if "?" in target else "?") + f"p={page}"
    return target


def transcribe_audio(
    target: str,
    page: int | None,
    output: Path,
    model: str,
    language: str | None,
    format_name: str,
) -> None:
    with tempfile.TemporaryDirectory(prefix="bilibili-subtitle-") as temporary:
        work_dir = Path(temporary)
        download = [
            "uvx", "yt-dlp", "--no-playlist", "-f", "ba/b",
            "-o", str(work_dir / "media.%(ext)s"), media_target(target, page),
        ]
        result = subprocess.run(download)
        if result.returncode != 0:
            raise RuntimeError("Could not download Bilibili audio for transcription.")
        media_files = list(work_dir.glob("media.*"))
        if not media_files:
            raise RuntimeError("Bilibili audio download finished without a media file.")
        generated = work_dir / "generated"
        generated.mkdir()
        command = [
            "uvx", "--from", "whisper-ctranslate2", "whisper-ctranslate2",
            str(media_files[0]), "--model", model, "--output_format", format_name,
            "--output_dir", str(generated), "--condition_on_previous_text", "False",
            "--vad_filter", "True", "--no_repeat_ngram_size", "4",
        ]
        speech_language = whisper_language(language)
        if speech_language:
            command += ["--language", speech_language]
        result = subprocess.run(command)
        if result.returncode != 0:
            raise RuntimeError("Speech transcription failed.")
        matches = list(generated.glob(f"*.{format_name}"))
        if not matches or matches[0].stat().st_size == 0:
            raise RuntimeError("No intelligible speech was detected in the Bilibili audio.")
        shutil.move(matches[0], output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Bilibili BV ID or video URL")
    parser.add_argument("--lang", help="Subtitle language, such as zh-CN or ai-zh")
    parser.add_argument("--page", type=int, help="Multi-part episode number, starting at 1")
    parser.add_argument("--output", "-o", type=Path, help="Output SRT path")
    parser.add_argument("--model", default="base", help="Whisper model for no-subtitle fallback")
    parser.add_argument("--format", choices=("srt", "vtt", "txt"), default="srt")
    parser.add_argument(
        "--no-transcribe",
        action="store_true",
        help="Fail when no subtitle track exists instead of transcribing speech",
    )
    args = parser.parse_args(argv)

    output = args.output or Path("outputs/bilibili") / f"{default_stem(args.target, args.page)}.{args.format}"
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        rows = fetch_rows(args.target, args.lang, args.page)
    except NoSubtitleError:
        if args.no_transcribe:
            raise
        transcribe_audio(args.target, args.page, output, args.model, args.lang, args.format)
        print(output)
        print("mode=speech_transcription")
        return 0

    output.write_text(render_rows(rows, args.format), encoding="utf-8")
    print(output)
    print("mode=subtitle_track")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
