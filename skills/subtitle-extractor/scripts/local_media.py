#!/usr/bin/env python3
"""Extract embedded text subtitles or transcribe local video/audio media."""

from __future__ import annotations

import argparse
import glob
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TEXT_SUBTITLE_CODECS = {
    "ass", "ssa", "microdvd", "mpl2", "mpsub", "pjs", "realtext", "sami",
    "srt", "subrip", "subviewer", "subviewer1", "text", "vplayer", "webvtt",
    "mov_text",
}


def find_ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    probe = subprocess.run(
        [
            "uv", "run", "--with", "imageio-ffmpeg", "python", "-c",
            "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())",
        ],
        text=True,
        capture_output=True,
    )
    if probe.returncode == 0:
        path = probe.stdout.strip().splitlines()[-1]
        if path and Path(path).exists():
            return path
    raise RuntimeError("FFmpeg was not found. Install FFmpeg or ensure uv and imageio-ffmpeg are available.")


def inspect_subtitle_streams(media: Path, ffmpeg: str) -> list[str]:
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(media)],
        text=True,
        capture_output=True,
    )
    diagnostic = result.stderr or ""
    if result.returncode not in (0, 1) or "No such file or directory" in diagnostic:
        raise RuntimeError(f"Could not inspect media with FFmpeg: {diagnostic.strip()[:800]}")
    pattern = re.compile(r"Stream #\d+:\d+.*?: Subtitle: ([\w-]+)", re.MULTILINE)
    return pattern.findall(diagnostic)


def srt_to_text(srt: str) -> str:
    blocks = re.split(r"\n\s*\n", srt.strip())
    lines: list[str] = []
    for block in blocks:
        rows = block.splitlines()
        if len(rows) >= 3 and "-->" in rows[1]:
            lines.extend(row.strip() for row in rows[2:] if row.strip())
    return "\n".join(lines) + ("\n" if lines else "")


def extract_embedded(
    media: Path,
    output: Path,
    ffmpeg: str,
    track: int,
    format_name: str,
) -> None:
    codecs = inspect_subtitle_streams(media, ffmpeg)
    text_codecs = [codec for codec in codecs if codec in TEXT_SUBTITLE_CODECS]
    if not text_codecs:
        image_codecs = [codec for codec in codecs if codec not in TEXT_SUBTITLE_CODECS]
        detail = f" Only image-based subtitle streams were found: {', '.join(image_codecs)}." if image_codecs else ""
        raise NoTextSubtitleError(
            f"No embedded text subtitle stream was found.{detail} OCR for burned-in or image subtitles is not implemented."
        )
    if track < 1 or track > len(text_codecs):
        raise RuntimeError(f"Subtitle track {track} is out of range; found {len(text_codecs)} text track(s).")

    with tempfile.TemporaryDirectory(prefix="local-subtitle-") as temporary:
        work_dir = Path(temporary)
        extracted = work_dir / "extracted.srt"
        result = subprocess.run(
            [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(media),
                "-map", f"0:s:{track - 1}", "-c:s", "srt", str(extracted),
            ],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0 or not extracted.exists() or extracted.stat().st_size == 0:
            raise RuntimeError(f"FFmpeg could not extract the subtitle stream: {result.stderr.strip()[:800]}")
        if format_name == "srt":
            shutil.copyfile(extracted, output)
        elif format_name == "vtt":
            converted = work_dir / "extracted.vtt"
            result = subprocess.run(
                [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(extracted), "-c:s", "webvtt", str(converted)],
                text=True,
                capture_output=True,
            )
            if result.returncode != 0 or not converted.exists():
                raise RuntimeError(f"FFmpeg could not convert SRT to VTT: {result.stderr.strip()[:800]}")
            shutil.copyfile(converted, output)
        else:
            output.write_text(srt_to_text(extracted.read_text(encoding="utf-8")), encoding="utf-8")


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


def transcribe(
    media: Path,
    output: Path,
    model: str,
    language: str | None,
    format_name: str,
) -> None:
    with tempfile.TemporaryDirectory(prefix="local-transcription-") as temporary:
        generated = Path(temporary) / "generated"
        generated.mkdir()
        command = [
            "uvx", "--from", "whisper-ctranslate2", "whisper-ctranslate2", str(media),
            "--model", model, "--output_format", format_name, "--output_dir", str(generated),
            "--condition_on_previous_text", "False", "--vad_filter", "True",
            "--no_repeat_ngram_size", "4",
        ]
        speech_language = whisper_language(language)
        if speech_language:
            command += ["--language", speech_language]
        result = subprocess.run(command)
        if result.returncode != 0:
            raise RuntimeError("Speech transcription failed.")
        matches = list(generated.glob(f"*.{format_name}"))
        if not matches or matches[0].stat().st_size == 0:
            raise RuntimeError("No intelligible speech was detected in the media.")
        shutil.move(matches[0], output)


class NoTextSubtitleError(RuntimeError):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="Local video or audio file")
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--model", default="base")
    parser.add_argument("--language")
    parser.add_argument("--format", choices=("srt", "vtt", "txt"), default="srt")
    parser.add_argument("--subtitle-track", type=int, default=1, help="One-based embedded text subtitle track")
    parser.add_argument(
        "--transcribe",
        action="store_true",
        help="Skip embedded subtitle extraction and transcribe speech",
    )
    args = parser.parse_args(argv)

    if not args.media.is_file():
        raise RuntimeError(f"Local media file does not exist: {args.media}")
    output = args.output or Path("outputs/local") / f"{args.media.stem}.{args.format}"
    output.parent.mkdir(parents=True, exist_ok=True)

    if not args.transcribe:
        try:
            extract_embedded(args.media, output, find_ffmpeg(), args.subtitle_track, args.format)
            print(output)
            print("mode=embedded_subtitle_track")
            return 0
        except NoTextSubtitleError:
            pass

    transcribe(args.media, output, args.model, args.language, args.format)
    print(output)
    print("mode=speech_transcription")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
