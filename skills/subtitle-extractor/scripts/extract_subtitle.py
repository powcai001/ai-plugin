#!/usr/bin/env python3
"""Route YouTube, Bilibili, X/Twitter, and local media subtitle extraction requests."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def host_is(url: str, *names: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == name or host.endswith("." + name) for name in names)


def youtube(argv: list[str]) -> int:
    base = Path(__file__).resolve().parent.parent
    cache = Path.home() / ".cache" / "subtitle-extractor" / "youtube-transcript"
    command = [
        "npx", "-y", "bun", str(base / "scripts/youtube/main.ts"),
        "--output-dir", str(cache),
    ]
    return subprocess.run(command + argv).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--lang", "--languages", dest="language")
    parser.add_argument("--page", type=int)
    parser.add_argument("--model", default="base")
    parser.add_argument("--format", choices=("srt", "vtt", "txt", "text"), default="srt")
    parser.add_argument("--cookies-from-browser", dest="cookies")
    parser.add_argument("--no-transcribe", action="store_true", help="Fail instead of transcribing a Bilibili video without subtitles")
    parser.add_argument("--subtitle-track", type=int, default=1, help="One-based local embedded text subtitle track")
    parser.add_argument("--transcribe", action="store_true", help="Skip local embedded subtitles and transcribe speech")
    args, extra = parser.parse_known_args(argv)

    output_args: list[str] = []
    if args.output:
        output_args = ["--output", str(args.output)]

    if host_is(args.url, "youtube.com", "youtu.be", "m.youtube.com", "music.youtube.com"):
        command = [args.url, "--format", args.format]
        if args.language:
            command += ["--languages", args.language]
        return youtube(command + output_args + extra)

    if host_is(args.url, "bilibili.com", "www.bilibili.com", "b23.tv"):
        script = Path(__file__).with_name("bilibili_srt.py")
        command = ["python3", str(script), args.url]
        if args.language:
            command += ["--lang", args.language]
        if args.page is not None:
            command += ["--page", str(args.page)]
        format_name = "txt" if args.format == "text" else args.format
        command += ["--model", args.model, "--format", format_name]
        if args.no_transcribe:
            command.append("--no-transcribe")
        return subprocess.run(command + output_args).returncode

    if host_is(args.url, "x.com", "www.x.com", "twitter.com", "www.twitter.com", "t.co"):
        script = Path(__file__).with_name("x_transcribe.py")
        format_name = "txt" if args.format == "text" else args.format
        command = ["python3", str(script), args.url, "--model", args.model, "--format", format_name]
        if args.language:
            command += ["--language", args.language]
        if args.cookies:
            command += ["--cookies-from-browser", args.cookies]
        return subprocess.run(command + output_args).returncode

    local_path = Path(args.url)
    if local_path.exists():
        script = Path(__file__).with_name("local_media.py")
        command = [
            "python3", str(script), str(local_path), "--model", args.model,
            "--format", "txt" if args.format == "text" else args.format,
            "--subtitle-track", str(args.subtitle_track),
        ]
        if args.language:
            command += ["--language", args.language]
        if args.transcribe:
            command.append("--transcribe")
        return subprocess.run(command + output_args).returncode

    print("error: Unsupported URL. Use YouTube, Bilibili, or X/Twitter.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
