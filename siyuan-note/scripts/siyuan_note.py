#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from urllib import error, request

# Ensure stdout uses UTF-8 on Windows to avoid garbled Chinese output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_API_URL = os.environ.get("SIYUAN_API_URL") or "http://127.0.0.1:6806"
DEFAULT_TOKEN = os.environ.get("SIYUAN_API_TOKEN")
NO_PROXY_OPENER = request.build_opener(request.ProxyHandler({}))
SIYUAN_ID_RE = re.compile(r"^[0-9]{14}-[0-9a-z]{7}$")


def validate_connection_args(args):
    if not getattr(args, "api_url", None):
        fail("config", "missing Siyuan API URL; set SIYUAN_API_URL or pass --api-url")
    if not getattr(args, "token", None):
        fail("config", "missing Siyuan API token; set SIYUAN_API_TOKEN or pass --token")


def api_post(api_url, token, path, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        api_url.rstrip("/") + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        method="POST",
    )
    with NO_PROXY_OPENER.open(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)


def api_post_safe(api_url, token, path, payload):
    try:
        return api_post(api_url, token, path, payload)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        print(json.dumps({
            "status": "error",
            "code": e.code,
            "path": path,
            "response": parsed,
        }, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "path": path,
            "message": str(e),
        }, ensure_ascii=False))
        sys.exit(1)


def fail(action, message, **extra):
    payload = {"status": "error", "action": action, "message": message}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(1)


def resolve_markdown_arg(args, action):
    markdown = getattr(args, "markdown", None)
    markdown_file = getattr(args, "markdown_file", None)
    if markdown is not None and markdown_file:
        fail(action, "provide either --markdown or --markdown-file, not both")
    if markdown_file:
        file_path = Path(markdown_file).expanduser()
        if not file_path.exists() or not file_path.is_file():
            fail(action, f"markdown file not found: {markdown_file}")
        return file_path.read_text(encoding="utf-8")
    if markdown is not None:
        return markdown
    fail(action, "missing markdown content; provide --markdown or --markdown-file")


def validate_siyuan_id(value, label="id"):
    if not value or not SIYUAN_ID_RE.match(str(value)):
        fail("validate-id", f"invalid Siyuan {label}: {value}")
    return value


def ensure_ok(result, action):
    if result.get("code") != 0:
        print(json.dumps({
            "status": "error",
            "action": action,
            "response": result,
        }, ensure_ascii=False))
        sys.exit(1)


def print_success(args, payload, response=None):
    if getattr(args, "verbose", False) and response is not None:
        payload["response"] = response
    print(json.dumps(payload, ensure_ascii=False))


def sanitize_doc_path(path):
    if path is None:
        return path

    value = str(path).replace('\\', '/').strip()
    if not value:
        return '/'

    # Git Bash / MSYS may rewrite a virtual Siyuan path like /Foo into
    # /C:/Users/.../Foo before Python sees argv. When that happens, recover the
    # intended hpath by keeping only the trailing doc segment.
    if re.match(r'^/[A-Za-z]:/', value):
        tail = value.rsplit('/', 1)[-1].strip()
        if tail:
            value = '/' + tail
        else:
            value = '/'

    if not value.startswith('/'):
        value = '/' + value

    value = re.sub(r'/+', '/', value)
    return value


def normalize_path(path):
    return sanitize_doc_path(path)


def list_notebooks_data(api_url, token):
    result = api_post_safe(api_url, token, "/api/notebook/lsNotebooks", {})
    ensure_ok(result, "list-notebooks")
    return result.get("data", {}).get("notebooks", [])


def resolve_notebook_id(args, required=True):
    if getattr(args, "notebook", None):
        return args.notebook
    notebook_name = getattr(args, "notebook_name", None)
    if not notebook_name:
        if required:
            fail("resolve-notebook", "missing notebook target; provide --notebook or --notebook-name")
        return None

    notebooks = list_notebooks_data(args.api_url, args.token)
    matches = [item for item in notebooks if item.get("name") == notebook_name]
    if not matches:
        fail("resolve-notebook", f"notebook not found: {notebook_name}")
    if len(matches) > 1:
        fail("resolve-notebook", f"multiple notebooks matched name: {notebook_name}", matches=[{"id": i.get("id"), "name": i.get("name")} for i in matches])
    return matches[0].get("id")


def resolve_doc_ids(api_url, token, notebook_id, path):
    result = api_post_safe(api_url, token, "/api/filetree/getIDsByHPath", {
        "notebook": notebook_id,
        "path": normalize_path(path),
    })
    ensure_ok(result, "get-doc-id")
    return result.get("data") or []


def list_docs_by_path(api_url, token, notebook_id, path):
    result = api_post_safe(api_url, token, "/api/filetree/listDocsByPath", {
        "notebook": notebook_id,
        "path": path,
    })
    ensure_ok(result, "list-paths")
    return result.get("data", {}).get("files", [])


def find_doc_by_name(files, name):
    expected = str(name or "")
    expected_stem = expected[:-3] if expected.endswith(".sy") else expected
    for item in files:
        actual = str(item.get("name") or "")
        actual_stem = actual[:-3] if actual.endswith(".sy") else actual
        if actual == expected or actual_stem == expected_stem:
            return item
    return None


def parse_date_or_today(value):
    if value:
        return datetime.date.fromisoformat(value)
    return datetime.date.today()


def get_block_info(api_url, token, block_id):
    result = api_post_safe(api_url, token, "/api/block/getBlockInfo", {"id": block_id})
    ensure_ok(result, "get-block-info")
    return result.get("data", {})


def get_hpath_by_id(api_url, token, doc_id):
    doc_id = validate_siyuan_id(doc_id, "document id")
    result = api_post_safe(api_url, token, "/api/query/sql", {
        "stmt": f"SELECT hpath, box FROM blocks WHERE id='{doc_id}' LIMIT 1",
    })
    ensure_ok(result, "get-hpath")
    rows = result.get("data", [])
    if not rows:
        fail("get-hpath", f"document not found: {doc_id}")
    return rows[0].get("hpath"), rows[0].get("box")


def create_doc_raw(api_url, token, notebook_id, path, markdown):
    result = api_post_safe(api_url, token, "/api/filetree/createDocWithMd", {
        "notebook": notebook_id,
        "path": path,
        "markdown": markdown,
    })
    ensure_ok(result, "create")
    return result


def update_doc_raw(api_url, token, doc_id, markdown):
    result = api_post_safe(api_url, token, "/api/block/updateBlock", {
        "id": doc_id,
        "dataType": "markdown",
        "data": markdown,
    })
    ensure_ok(result, "update")
    return result


def append_doc_raw(api_url, token, doc_id, markdown):
    result = api_post_safe(api_url, token, "/api/block/appendBlock", {
        "parentID": doc_id,
        "dataType": "markdown",
        "data": markdown,
    })
    ensure_ok(result, "append")
    return result


def export_preview_html_raw(api_url, token, doc_id, keep_fold=False, merge=True):
    result = api_post_safe(api_url, token, "/api/export/exportPreviewHTML", {
        "id": doc_id,
        "keepFold": keep_fold,
        "merge": merge,
    })
    ensure_ok(result, "export-pdf")
    return result.get("data") or {}


def find_pdf_browser(explicit_path=None):
    candidates = []
    if explicit_path:
        candidates.append(explicit_path)
    env_browser = os.environ.get("SIYUAN_PDF_BROWSER")
    if env_browser:
        candidates.append(env_browser)

    candidates.extend([
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome"),
        shutil.which("microsoft-edge"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ])

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def build_pdf_html(api_url, preview_data, title):
    base_url = api_url.rstrip("/") + "/"
    content = preview_data.get("content") or ""
    attrs = preview_data.get("attrs") or {}
    doc_type = preview_data.get("type") or "NodeDocument"
    attr_html = " ".join(f'{key}="{str(value).replace(chr(34), "&quot;")}"' for key, value in attrs.items())
    safe_title = (title or preview_data.get("name") or "SiYuan Export").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html>
<html lang="zh-CN" data-theme-mode="light">
<head>
  <base href="{base_url}">
  <meta charset="utf-8">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="{base_url}stage/build/export/base.css">
  <link rel="stylesheet" href="{base_url}appearance/themes/daylight/theme.css">
  <style>
    @page {{ size: A4; margin: 16mm 14mm; }}
    body {{
      margin: 0;
      background: #fff;
      color: #1f2328;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    #preview {{
      max-width: 800px;
      margin: 0 auto;
    }}
    img, svg, video, canvas {{
      max-width: 100%;
    }}
    pre, code {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }}
    table {{
      max-width: 100%;
      border-collapse: collapse;
    }}
  </style>
</head>
<body>
  <main id="preview" class="protyle-wysiwyg" data-doc-type="{doc_type}" {attr_html}>{content}</main>
</body>
</html>
"""


def render_pdf_with_browser(browser_path, html_path, output_path, timeout):
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-dev-shm-usage",
        f"--print-to-pdf={str(output)}",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        Path(html_path).resolve().as_uri(),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        fail("export-pdf", "browser PDF rendering failed", exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    if not output.exists() or output.stat().st_size == 0:
        fail("export-pdf", "browser finished but PDF file was not created", output=str(output), stdout=proc.stdout, stderr=proc.stderr)
    return output, proc


def build_multipart(fields, files):
    boundary = f"----ClaudeCode{uuid.uuid4().hex}"
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for name, file_name, content_type, content in files:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{file_name}"\r\n'.encode())
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
        body.extend(content)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())
    return boundary, bytes(body)


def upload_asset(api_url, token, file_path, assets_dir_path):
    file_obj = Path(file_path)
    if not file_obj.exists() or not file_obj.is_file():
        fail("upload-asset", f"file not found: {file_path}")

    boundary, body = build_multipart(
        {"assetsDirPath": assets_dir_path},
        [("file[]", file_obj.name, "application/octet-stream", file_obj.read_bytes())],
    )
    req = request.Request(
        api_url.rstrip("/") + "/api/asset/upload",
        data=body,
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with NO_PROXY_OPENER.open(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8", errors="replace"))
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        fail("upload-asset", "http error during asset upload", code=e.code, response=parsed)
    except Exception as e:
        fail("upload-asset", str(e))

    ensure_ok(result, "upload-asset")
    data = result.get("data") or {}
    if isinstance(data, list) and data:
        data = data[0]
    asset_path = data.get("succMap", {}).get(file_obj.name) if isinstance(data, dict) else None
    if not asset_path and isinstance(data, dict):
        asset_path = data.get("path")
    if not asset_path:
        fail("upload-asset", "upload succeeded but asset path missing", response=result)
    return {
        "file_name": file_obj.name,
        "asset_path": asset_path,
        "response": result,
    }


def build_attachment_markdown(file_name, asset_path, label=None):
    link_text = label or f"附件：{file_name}"
    return f"[{link_text}]({asset_path})"


def resolve_doc_id_from_args(args, allow_missing=False):
    if getattr(args, "doc_id", None):
        return validate_siyuan_id(args.doc_id, "document id"), None, None
    path = getattr(args, "path", None)
    if not path:
        fail("resolve-doc", "missing target document; provide --doc-id or --path with notebook info")
    notebook_id = resolve_notebook_id(args, required=True)
    doc_ids = resolve_doc_ids(args.api_url, args.token, notebook_id, path)
    if not doc_ids:
        if allow_missing:
            return None, notebook_id, normalize_path(path)
        fail("resolve-doc", "document not found by path", notebook=notebook_id, path=normalize_path(path))
    return doc_ids[0], notebook_id, normalize_path(path)


def resolve_daily_note(args, ensure_exists=False):
    notebook_id = resolve_notebook_id(args, required=True)
    target_date = parse_date_or_today(getattr(args, "date", None))

    root_files = list_docs_by_path(args.api_url, args.token, notebook_id, "/")
    daily_root = find_doc_by_name(root_files, "daily note.sy")
    if not daily_root:
        fail("resolve-daily-note", "daily note root not found", notebook=notebook_id)

    year_files = list_docs_by_path(args.api_url, args.token, notebook_id, daily_root.get("path"))
    year_name = f"{target_date.year}.sy"
    year_doc = find_doc_by_name(year_files, year_name)
    if not year_doc:
        fail("resolve-daily-note", f"daily note year not found: {year_name}", notebook=notebook_id, daily_root=daily_root.get("path"))

    month_files = list_docs_by_path(args.api_url, args.token, notebook_id, year_doc.get("path"))
    month_name = f"{target_date.month:02d}.sy"
    month_doc = find_doc_by_name(month_files, month_name)
    if not month_doc:
        fail("resolve-daily-note", f"daily note month not found: {month_name}", notebook=notebook_id, year_path=year_doc.get("path"))

    day_files = list_docs_by_path(args.api_url, args.token, notebook_id, month_doc.get("path"))
    day_name = f"{target_date.isoformat()}.sy"
    day_doc = find_doc_by_name(day_files, day_name)

    day_path = f"{month_doc.get('path')[:-3]}/{target_date.isoformat()}.sy"
    if not day_doc and ensure_exists:
        create_result = create_doc_raw(
            args.api_url,
            args.token,
            notebook_id,
            day_path,
            f"# {target_date.isoformat()}\n",
        )
        day_doc = {
            "id": create_result.get("data"),
            "name": day_name,
            "path": day_path,
        }

    if not day_doc:
        fail("resolve-daily-note", f"daily note day not found: {day_name}", notebook=notebook_id, month_path=month_doc.get("path"))

    return {
        "date": target_date.isoformat(),
        "notebook": notebook_id,
        "doc_id": day_doc.get("id"),
        "path": day_doc.get("path"),
        "daily_root_path": daily_root.get("path"),
        "year_path": year_doc.get("path"),
        "month_path": month_doc.get("path"),
    }


def list_notebooks(args):
    notebooks = list_notebooks_data(args.api_url, args.token)
    print(json.dumps({
        "status": "success",
        "action": "list-notebooks",
        "count": len(notebooks),
        "notebooks": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "closed": item.get("closed"),
            }
            for item in notebooks
        ],
    }, ensure_ascii=False))


def list_paths(args):
    notebook_id = resolve_notebook_id(args, required=True)
    path = normalize_path(args.path or "/")
    files = list_docs_by_path(args.api_url, args.token, notebook_id, path)
    print(json.dumps({
        "status": "success",
        "action": "list-paths",
        "notebook": notebook_id,
        "path": path,
        "count": len(files),
        "files": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "path": item.get("path"),
                "sub_file_count": item.get("subFileCount"),
            }
            for item in files
        ],
    }, ensure_ascii=False))


def create_doc(args):
    parent_id = getattr(args, "parent_id", None)
    doc_title = args.path.strip("/")
    if parent_id:
        parent_hpath, parent_box = get_hpath_by_id(args.api_url, args.token, parent_id)
        notebook_id = parent_box or resolve_notebook_id(args, required=True)
        child_path = parent_hpath.rstrip("/") + "/" + doc_title
    else:
        notebook_id = resolve_notebook_id(args, required=True)
        child_path = normalize_path(args.path)
    markdown = resolve_markdown_arg(args, "create")
    result = create_doc_raw(args.api_url, args.token, notebook_id, child_path, markdown)
    print_success(args, {
        "status": "success",
        "action": "create",
        "notebook": notebook_id,
        "path": child_path,
        "parent_id": parent_id,
        "doc_id": result.get("data"),
    }, result)


def get_doc_id(args):
    notebook_id = resolve_notebook_id(args, required=True)
    path = normalize_path(args.path)
    doc_ids = resolve_doc_ids(args.api_url, args.token, notebook_id, path)
    print(json.dumps({
        "status": "success",
        "action": "get-doc-id",
        "notebook": notebook_id,
        "path": path,
        "doc_ids": doc_ids,
        "doc_id": doc_ids[0] if doc_ids else None,
    }, ensure_ascii=False))


def update_doc(args):
    doc_id, notebook_id, path = resolve_doc_id_from_args(args)
    markdown = resolve_markdown_arg(args, "update")
    result = update_doc_raw(args.api_url, args.token, doc_id, markdown)
    print_success(args, {
        "status": "success",
        "action": "update",
        "doc_id": doc_id,
        "notebook": notebook_id,
        "path": path,
    }, result)


def append_doc(args):
    doc_id, notebook_id, path = resolve_doc_id_from_args(args)
    markdown = resolve_markdown_arg(args, "append")
    result = append_doc_raw(args.api_url, args.token, doc_id, markdown)
    print_success(args, {
        "status": "success",
        "action": "append",
        "doc_id": doc_id,
        "notebook": notebook_id,
        "path": path,
    }, result)


def upsert_doc(args):
    markdown = resolve_markdown_arg(args, "upsert")
    parent_id = getattr(args, "parent_id", None)
    if parent_id:
        parent_hpath, parent_box = get_hpath_by_id(args.api_url, args.token, parent_id)
        notebook_id = parent_box or resolve_notebook_id(args, required=True)
        child_title = args.path.strip("/").replace("\\", "/").split("/")[-1]
        if not child_title:
            fail("upsert", "missing child document title")
        path = parent_hpath.rstrip("/") + "/" + child_title
    else:
        notebook_id = resolve_notebook_id(args, required=True)
        path = normalize_path(args.path)
    doc_ids = resolve_doc_ids(args.api_url, args.token, notebook_id, path)
    if doc_ids:
        doc_id = doc_ids[0]
        result = update_doc_raw(args.api_url, args.token, doc_id, markdown)
        print_success(args, {
            "status": "success",
            "action": "upsert",
            "mode": "update",
            "notebook": notebook_id,
            "path": path,
            "parent_id": parent_id,
            "doc_id": doc_id,
        }, result)
        return

    result = create_doc_raw(args.api_url, args.token, notebook_id, path, markdown)
    print_success(args, {
        "status": "success",
        "action": "upsert",
        "mode": "create",
        "notebook": notebook_id,
        "path": path,
        "parent_id": parent_id,
        "doc_id": result.get("data"),
    }, result)


def show_today_note_path(args):
    info = resolve_daily_note(args, ensure_exists=False)
    print(json.dumps({
        "status": "success",
        "action": "show-today-note-path",
        **info,
    }, ensure_ascii=False))


def append_today_note(args):
    info = resolve_daily_note(args, ensure_exists=getattr(args, "ensure_exists", False))
    markdown = resolve_markdown_arg(args, "append-today-note")
    result = append_doc_raw(args.api_url, args.token, info["doc_id"], markdown)
    print(json.dumps({
        "status": "success",
        "action": "append-today-note",
        **info,
        "response": result,
    }, ensure_ascii=False))


def upsert_today_note(args):
    info = resolve_daily_note(args, ensure_exists=True)
    markdown = resolve_markdown_arg(args, "upsert-today-note")
    result = append_doc_raw(args.api_url, args.token, info["doc_id"], markdown)
    print(json.dumps({
        "status": "success",
        "action": "upsert-today-note",
        "mode": "append",
        **info,
        "response": result,
    }, ensure_ascii=False))


def create_child_today_note(args):
    info = resolve_daily_note(args, ensure_exists=True)
    title = args.title.strip().strip('/').replace('\\', '/').split('/')[-1]
    if not title:
        fail("create-child-today-note", "missing child document title")

    parent_hpath, parent_box = get_hpath_by_id(args.api_url, args.token, info["doc_id"])
    notebook_id = parent_box or info["notebook"]
    child_path = parent_hpath.rstrip('/') + '/' + title
    markdown = resolve_markdown_arg(args, "create-child-today-note")
    result = create_doc_raw(args.api_url, args.token, notebook_id, child_path, markdown)
    print(json.dumps({
        "status": "success",
        "action": "create-child-today-note",
        **info,
        "parent_id": info["doc_id"],
        "child_title": title,
        "path": child_path,
        "doc_id": result.get("data"),
        "response": result,
    }, ensure_ascii=False))


def attach_file(args):
    upload = upload_asset(args.api_url, args.token, args.file, args.assets_dir_path)
    markdown = build_attachment_markdown(upload["file_name"], upload["asset_path"], args.label)
    doc_id, notebook_id, path = resolve_doc_id_from_args(args)
    result = append_doc_raw(args.api_url, args.token, doc_id, markdown)
    print(json.dumps({
        "status": "success",
        "action": "attach-file",
        "doc_id": doc_id,
        "notebook": notebook_id,
        "path": path,
        "asset_path": upload["asset_path"],
        "markdown": markdown,
        "response": result,
        "upload_response": upload["response"],
    }, ensure_ascii=False))


def attach_today_note(args):
    upload = upload_asset(args.api_url, args.token, args.file, args.assets_dir_path)
    markdown = build_attachment_markdown(upload["file_name"], upload["asset_path"], args.label)
    info = resolve_daily_note(args, ensure_exists=True)
    result = append_doc_raw(args.api_url, args.token, info["doc_id"], markdown)
    print(json.dumps({
        "status": "success",
        "action": "attach-today-note",
        **info,
        "asset_path": upload["asset_path"],
        "markdown": markdown,
        "response": result,
        "upload_response": upload["response"],
    }, ensure_ascii=False))


def export_pdf(args):
    doc_id, notebook_id, path = resolve_doc_id_from_args(args)
    preview_data = export_preview_html_raw(
        args.api_url,
        args.token,
        doc_id,
        keep_fold=args.keep_fold,
        merge=args.merge,
    )
    title = args.title or preview_data.get("name") or doc_id
    output = args.output
    if not output:
        output_name = util_filter_filename(title) + ".pdf"
        output = str(Path.cwd() / output_name)

    browser = find_pdf_browser(args.browser)
    if not browser:
        fail(
            "export-pdf",
            "Chrome/Chromium/Edge executable not found; install one or pass --browser /path/to/browser. "
            "You can also set SIYUAN_PDF_BROWSER.",
        )

    with tempfile.TemporaryDirectory(prefix="siyuan-pdf-") as tmp_dir:
        html_path = Path(tmp_dir) / "export.html"
        html_path.write_text(build_pdf_html(args.api_url, preview_data, title), encoding="utf-8")
        pdf_path, proc = render_pdf_with_browser(browser, html_path, output, args.timeout)

    print(json.dumps({
        "status": "success",
        "action": "export-pdf",
        "doc_id": doc_id,
        "notebook": notebook_id,
        "path": path,
        "title": title,
        "output": str(pdf_path),
        "browser": browser,
        "size": pdf_path.stat().st_size,
        "stderr": proc.stderr.strip(),
    }, ensure_ascii=False))


def util_filter_filename(value):
    value = str(value or "siyuan-export").strip()
    value = re.sub(r'[\\/:*?"<>|]+', "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value or "siyuan-export"


def add_notebook_args(parser):
    parser.add_argument("--notebook", required=False, help="Notebook ID")
    parser.add_argument("--notebook-name", required=False, help="Notebook name")


def add_doc_target_args(parser):
    parser.add_argument("--doc-id", required=False, help="Document ID")
    parser.add_argument("--path", required=False, help="Document path")
    parser.add_argument("--notebook", required=False, help="Notebook ID")
    parser.add_argument("--notebook-name", required=False, help="Notebook name")


def add_date_arg(parser):
    parser.add_argument("--date", required=False, help="Target date in YYYY-MM-DD")


def add_attachment_args(parser):
    parser.add_argument("--file", required=True, help="Local file path to upload")
    parser.add_argument("--assets-dir-path", default="/assets/", help="Asset directory path in Siyuan data")
    parser.add_argument("--label", required=False, help="Custom markdown link label")


def add_markdown_args(parser, required=True):
    group = parser.add_mutually_exclusive_group(required=required)
    group.add_argument("--markdown", required=False, help="Markdown content")
    group.add_argument("--markdown-file", required=False, help="Read Markdown content from a UTF-8 file")


def build_parser():
    parser = argparse.ArgumentParser(description="Send markdown to Siyuan Note")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Siyuan API base URL")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Siyuan API token")
    parser.add_argument("--verbose", action="store_true", help="Include raw Siyuan API responses in output")

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-notebooks", help="List notebooks")
    list_parser.set_defaults(func=list_notebooks)

    list_paths_parser = subparsers.add_parser("list-paths", help="List paths under notebook path")
    add_notebook_args(list_paths_parser)
    list_paths_parser.add_argument("--path", default="/", help="Parent path")
    list_paths_parser.set_defaults(func=list_paths)

    create_parser = subparsers.add_parser("create", help="Create document from markdown")
    add_notebook_args(create_parser)
    create_parser.add_argument("--parent-id", required=False, help="Parent document ID (creates as child)")
    create_parser.add_argument("--path", required=True, help="Document path or title")
    add_markdown_args(create_parser)
    create_parser.set_defaults(func=create_doc)

    get_parser = subparsers.add_parser("get-doc-id", help="Get document ID by notebook and path")
    add_notebook_args(get_parser)
    get_parser.add_argument("--path", required=True, help="Document path")
    get_parser.set_defaults(func=get_doc_id)

    update_parser = subparsers.add_parser("update", help="Overwrite document markdown")
    add_doc_target_args(update_parser)
    add_markdown_args(update_parser)
    update_parser.set_defaults(func=update_doc)

    append_parser = subparsers.add_parser("append", help="Append markdown to document")
    add_doc_target_args(append_parser)
    add_markdown_args(append_parser)
    append_parser.set_defaults(func=append_doc)

    upsert_parser = subparsers.add_parser("upsert", help="Create or update document by path")
    add_notebook_args(upsert_parser)
    upsert_parser.add_argument("--parent-id", required=False, help="Parent document ID (upserts as child by title)")
    upsert_parser.add_argument("--path", required=True, help="Document path")
    add_markdown_args(upsert_parser)
    upsert_parser.set_defaults(func=upsert_doc)

    show_today_parser = subparsers.add_parser("show-today-note-path", help="Show resolved daily note path for a date")
    add_notebook_args(show_today_parser)
    add_date_arg(show_today_parser)
    show_today_parser.set_defaults(func=show_today_note_path)

    append_today_parser = subparsers.add_parser("append-today-note", help="Append markdown to the daily note for a date")
    add_notebook_args(append_today_parser)
    add_date_arg(append_today_parser)
    append_today_parser.add_argument("--ensure-exists", action="store_true", help="Create today's note if missing")
    add_markdown_args(append_today_parser)
    append_today_parser.set_defaults(func=append_today_note)

    upsert_today_parser = subparsers.add_parser("upsert-today-note", help="Ensure daily note exists and append markdown")
    add_notebook_args(upsert_today_parser)
    add_date_arg(upsert_today_parser)
    add_markdown_args(upsert_today_parser)
    upsert_today_parser.set_defaults(func=upsert_today_note)

    create_child_today_parser = subparsers.add_parser("create-child-today-note", help="Create a child document under today's daily note")
    add_notebook_args(create_child_today_parser)
    add_date_arg(create_child_today_parser)
    create_child_today_parser.add_argument("--title", required=True, help="Child document title")
    add_markdown_args(create_child_today_parser)
    create_child_today_parser.set_defaults(func=create_child_today_note)

    attach_file_parser = subparsers.add_parser("attach-file", help="Upload asset and append link to a document")
    add_doc_target_args(attach_file_parser)
    add_attachment_args(attach_file_parser)
    attach_file_parser.set_defaults(func=attach_file)

    attach_today_parser = subparsers.add_parser("attach-today-note", help="Upload asset and append link to a daily note")
    add_notebook_args(attach_today_parser)
    add_date_arg(attach_today_parser)
    add_attachment_args(attach_today_parser)
    attach_today_parser.set_defaults(func=attach_today_note)

    export_pdf_parser = subparsers.add_parser("export-pdf", help="Export a document to PDF via SiYuan export HTML and headless Chrome/Edge")
    add_doc_target_args(export_pdf_parser)
    export_pdf_parser.add_argument("--output", required=False, help="Output PDF path. Defaults to ./<document title>.pdf")
    export_pdf_parser.add_argument("--browser", required=False, help="Chrome/Chromium/Edge executable path. Can also use SIYUAN_PDF_BROWSER")
    export_pdf_parser.add_argument("--title", required=False, help="Override PDF title and default output name")
    export_pdf_parser.add_argument("--keep-fold", action="store_true", help="Keep folded content folded in export")
    export_pdf_parser.add_argument("--no-merge", dest="merge", action="store_false", help="Do not merge subdocuments")
    export_pdf_parser.set_defaults(merge=True)
    export_pdf_parser.add_argument("--timeout", type=int, default=120, help="Browser render timeout in seconds")
    export_pdf_parser.set_defaults(func=export_pdf)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    validate_connection_args(args)
    args.func(args)


if __name__ == "__main__":
    main()
