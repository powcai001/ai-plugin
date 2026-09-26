---
name: opencli-telegram-download
description: Use when downloading authorized files from Telegram Web with OpenCLI, especially course/resource batches, PDF-only requests, .crdownload cleanup, or repeated Telegram download tasks.
---

# OpenCLI Telegram Download

## Core Rule

Use OpenCLI against the logged-in Telegram Web session. Only download files the user confirms they are authorized to save. When the user says "只下载 PDF" or mentions PDF-only, do not click audio controls.

## Setup

1. Check the browser bridge:

```bash
opencli doctor
```

2. This machine's OpenCLI browser syntax is:

```bash
opencli browser <session> open '<url>'
opencli browser <session> state
opencli browser <session> find --css '<selector>'
opencli browser <session> click '<selector>' --nth <n>
```

Do not assume `opencli doctor -f json` or `browser open --focus` exists on this machine.

## Locate Telegram Files

Open the chat and inspect before acting:

```bash
opencli browser telegram-pdf open '<telegram-web-url>'
opencli browser telegram-pdf wait time 8
opencli browser telegram-pdf state
```

For course batches, use Telegram's chat search for the course name, then inspect the DOM:

```bash
opencli browser telegram-pdf find --css '.File.interactive' --limit 120
```

Useful read-only probe:

```bash
opencli browser telegram-pdf eval "(() => [...document.querySelectorAll('*')].filter(e => /\\.pdf/i.test(e.textContent || '')).slice(0, 20).map(e => ({ tag: e.tagName, cls: String(e.className), text: (e.textContent || '').slice(0, 200) })))()"
```

## Selectors

| Content | Selector | Action |
| --- | --- | --- |
| PDF/EPUB document card | `.File.interactive` | Inspect text first |
| PDF download hot area | `.File.interactive .file-icon-container` | Click only when card text includes `.pdf` |
| MP3 audio component | `.Audio.inline` | Inspect only unless user requests audio |
| MP3 download button | `.Audio.inline .download-button` | Do not click for PDF-only tasks |

Batch clicks should be small and paced:

```bash
for n in $(seq 0 20); do
  opencli browser telegram-pdf click '.File.interactive .file-icon-container' --nth "$n"
  sleep 1
done
```

If the selector list includes non-PDF entries, avoid blind loops. Use `find --css '.File.interactive'` output to choose PDF `nth` values.

## Organize Downloads

Downloads land in `~/Downloads`. Create a course folder and move only matching target files:

```bash
mkdir -p ~/Downloads/'<course-name>'
```

Telegram/Chrome may leave complete PDFs with `.pdf.crdownload`. Verify before renaming:

```bash
file -b ~/Downloads/*.pdf.crdownload
```

If the output says `PDF document`, remove `.crdownload` and move it:

```bash
dest=~/Downloads/'<course-name>'
for f in ~/Downloads/*.pdf.crdownload; do
  [ -e "$f" ] || continue
  base=$(basename "$f" .crdownload)
  case "$base" in
    *.pdf) mv "$f" "$dest/$base" ;;
  esac
done
```

Clean duplicate browser suffixes after moving:

```bash
for f in "$dest"/*' (1).pdf'; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  clean=${base% \\(1\\).pdf}.pdf
  [ -e "$dest/$clean" ] && rm -f "$f" || mv "$f" "$dest/$clean"
done
```

## Interruptions

If a bulk loop is interrupted, stop any remaining process before continuing:

```bash
ps -axo pid,command | rg 'opencli browser .*telegram|opencli-audio'
kill <pid>
```

Do not delete unknown `未确认 *.crdownload` files unless their origin is confirmed. Report partial counts clearly.

## Verification

Before claiming completion, verify:

```bash
find "$dest" -maxdepth 1 -type f -name '*.pdf' | wc -l
find "$dest" -maxdepth 1 -type f ! -name '*.pdf' -print
```

For PDF-only tasks, the target folder should contain PDFs only, aside from harmless system files such as `.DS_Store`.
