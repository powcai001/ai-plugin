---
name: siyuan-note
description: 发送 Markdown 内容到思源笔记，支持新建文档、覆盖更新、追加内容、按路径查看文档、直接写入今日日记、读取日记子文档、上传附件并插入链接、导出文档为 PDF。适用于”发到思源””保存到思源笔记””追加到思源文档””覆盖更新思源文档””查看思源有哪些路径””写到今日日记””读取今天日记下的文章””上传压缩包到思源””导出 PDF”等场景。
version: 1.5.0
---

# 思源笔记助手

用于通过反向 SSH 隧道访问思源 API，把 Markdown 内容直接写入思源笔记，并支持上传附件到思源 assets 目录后插入链接。

## 快速规则

- 用户说“发到思源/保存到思源/放到某路径下”时，优先使用本 skill 的脚本，不要直接写 `.sy` 文件。
- 对本地 Markdown 文件，优先用 `--markdown-file`，不要用 shell 变量或命令替换传大段正文，避免只创建标题或正文丢失。
- 若目标是已有父文档下的子文档，优先用 `upsert --parent-id <父文档ID> --path "/标题" --markdown-file <文件>`，可一次完成“存在则覆盖，不存在则创建”。
- 写入后，如用户关心结果，调用 `exportMdContent` 或 `list-paths` 验证；无需让用户反复确认。
- 用户要求“导出 PDF / 保存成 PDF”时，使用 `export-pdf` 子命令；它会调用思源 `/api/export/exportPreviewHTML` 获取导出 HTML，再用本机 Chrome/Chromium/Edge headless 打印为 PDF。
- 成功输出默认是精简 JSON；只有排查问题时才加 `--verbose`。
- 如果出现 `<urlopen error [Errno 1] Operation not permitted>`，这是本地 API 被沙箱拦截，直接用提升权限重跑同一命令。

### 常用：把当前简历写入专题研究/简历

「4.专题研究」ID：`20220105210605-bw4ygl5`  
「简历」父文档 ID：`20260427210445-nv2jbke`

```bash
python3 ~/.claude/skills/siyuan-note/scripts/siyuan_note.py \
  --api-url http://127.0.0.1:6806 \
  --token "$SIYUAN_API_TOKEN" \
  upsert \
  --parent-id "20260427210445-nv2jbke" \
  --path "/蔡威-简历" \
  --markdown-file "/path/to/Resume.md"
```

必须通过 SIYUAN_API_TOKEN 环境变量或 --token 参数提供 token。

思源连接参数**不提供任何默认值**：
- `SIYUAN_API_URL` 必须通过环境变量提供，或命令行 `--api-url` 临时传入
- `SIYUAN_API_TOKEN` 必须设置或通过 --token 提供；skill 不存储 token

## Windows / Git Bash 特别注意

如果在 Windows 下通过 Git Bash 调用，`/OpenCLI教程` 这种思源虚拟路径，可能会在 **Python 启动前** 被 Git Bash 自动改写成 `/D:/Git/OpenCLI教程`，从而把文档错误创建到盘符样式路径下。

为避免这个问题，**在 Windows + Git Bash 下调用本技能时，统一在命令前加：**

```bash
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py <subcommand> [args]
```

也就是说，后续凡是带 `--path "/..."` 的命令，都应该优先用这个前缀。

## 适用场景

- "把这段内容发到思源笔记"
- "保存到思源，标题叫今日总结"
- "在 1.收集 里新建一篇文档"
- "把这段 markdown 追加到某个思源文档"
- "覆盖更新这个思源文档内容"
- "列出思源笔记本"
- "看看 1.收集 下面有哪些路径"
- "按路径更新思源文档，不要先查 doc id"
- "如果文档不存在就创建"
- "写到今日日记"
- "把这次回答追加到 today daily note"
- "查看今日日记路径"
- "上传压缩包到思源"
- "把 PDF 挂到某篇笔记"
- "把某篇思源文档导出成 PDF"
- "导出 PDF 到本地路径"
- "把附件插到今日日记"
- "读取今天日记下的第一篇文章"
- "读今天日记下「休息」这篇文章"

## 关键信息

### 笔记本列表

| 笔记本名称 | ID | 用途 |
|------------|-----|------|
| 1.收集箱 | 20220105205758-vniy8zc | 日记、日常收集 |
| 2.将来可能 | 20220105210423-08168mp | |
| 3.归档资料 | 20220105210509-msogj94 | |
| 4.专题研究 | 20220105210605-bw4ygl5 | |
| 5.垃圾箱 | 20220105212959-jv2sjks | |
| 6.暂存 | 20210821122109-u5tnws7 | |
| 7.书籍 | 20230920201746-fhhrbnd | |
| 知识库 | 20260405220603-b25nhzf | Wiki 知识页（来源摘要、概念、实体等） |

**注意**：日记在「1.收集箱」下，不在「知识库」。涉及日记操作时，notebook-name 统一用 `"1.收集箱"`。

### API 连接

默认 API URL 是 `http://127.0.0.1:6806`。Token 必须通过环境变量或命令行参数提供：

```bash
export SIYUAN_API_TOKEN="你的思源 API Token"
```

### 1. 列出笔记本
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py list-notebooks
```

### 2. 查看某个路径下有哪些文档
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py list-paths --notebook-name "1.收集箱" --path "/"
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py list-paths --notebook-name "1.收集箱" --path "/Claude"
```

### 3. 新建文档
```bash
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py create --notebook-name "1.收集箱" --path "/Claude/今日总结.md" --markdown "# 今日总结\n\n内容"
```

也可以从 Markdown 文件读取正文，推荐用于长文档：

```bash
python3 ~/.claude/skills/siyuan-note/scripts/siyuan_note.py create --notebook-name "1.收集箱" --path "/Claude/今日总结.md" --markdown-file "/tmp/today.md"
```

### 3b. 在父文档下创建子文档
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py create --parent-id "20260331104128-yxsimke" --path "/子文档标题" --markdown "# 子文档标题\n\n内容"
```
使用 `--parent-id` 时，自动通过父文档的 hpath 拼接子文档路径，无需手动提供 notebook。`--path` 只需提供子文档标题（如 `/春日随想`）。

### 4. 按路径查文档 ID
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py get-doc-id --notebook-name "1.收集箱" --path "/Claude/今日总结.md"
```

### 5. 覆盖更新文档
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py update --doc-id "20260331103536-twdusp7" --markdown "# 新内容\n\n这是覆盖后的内容"
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py update --notebook-name "1.收集箱" --path "/Claude/今日总结.md" --markdown "# 新内容\n\n这是覆盖后的内容"
```

### 6. 追加内容到文档
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py append --notebook-name "1.收集箱" --path "/Claude/今日总结.md" --markdown "## 追加内容\n\n这里是新增内容"
```

### 7. 文档不存在则创建，存在则更新
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py upsert --notebook-name "1.收集箱" --path "/Claude/今日总结.md" --markdown "# 今日总结\n\n内容"
```

父文档下创建/更新子文档：

```bash
python3 ~/.claude/skills/siyuan-note/scripts/siyuan_note.py upsert --parent-id "20260331104128-yxsimke" --path "/子文档标题" --markdown-file "/tmp/content.md"
```

### 8. 查看今日日记路径
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py show-today-note-path --notebook-name "1.收集箱"
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py show-today-note-path --notebook-name "1.收集箱" --date "2026-03-30"
```

### 9. 直接追加到今日日记
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py append-today-note --notebook-name "1.收集箱" --markdown "## 测试\n\n写入今日日记"
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py append-today-note --notebook-name "1.收集箱" --date "2026-03-30" --markdown "## 补记\n\n补写历史日记"
```

### 10. 确保今日日记存在并写入
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py upsert-today-note --notebook-name "1.收集箱" --markdown "## 测试\n\n自动创建并写入"
```

### 10b. 在今日日记下面创建子文档
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py create-child-today-note --notebook-name "1.收集箱" --title "OpenCLI教程" --markdown "# OpenCLI教程\n\n内容"
```
这个命令会先定位今日日记，再通过 **父文档 ID** 在今日日记下创建子文档，避免普通 `--path` 创建时的路径歧义。

### 11. 上传附件并插入到指定文档
支持压缩包、PDF、图片等，先上传到思源 `/assets/`，再在文档末尾追加 Markdown 链接。

```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py attach-file --notebook-name "1.收集箱" --path "/Claude/资料.md" --file "/tmp/test.zip"
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py attach-file --doc-id "20260331103750-uhhpwq6" --file "/tmp/test.pdf" --label "附件：测试 PDF"
```

### 12. 上传附件并插入到今日日记
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py attach-today-note --notebook-name "1.收集箱" --file "/tmp/test.zip"
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py attach-today-note --notebook-name "1.收集箱" --date "2026-03-30" --file "/tmp/test.pdf" --assets-dir-path "/assets/claude/"
```

### 13. 导出文档为 PDF

脚本实现路径：调用思源 `/api/export/exportPreviewHTML` 获取导出 HTML，再用本机 Chrome/Chromium/Edge headless 打印为 PDF。macOS 会自动查找：

- `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- `/Applications/Chromium.app/Contents/MacOS/Chromium`
- `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`

也可以通过 `--browser` 或 `SIYUAN_PDF_BROWSER` 指定浏览器可执行文件。

```bash
python3 ~/.claude/skills/siyuan-note/scripts/siyuan_note.py export-pdf \
  --notebook-name "4.专题研究" \
  --path "/Claude Code 类 Agent 框架学习" \
  --output "/path/to/output.pdf"
```

按文档 ID 导出：

```bash
python3 ~/.claude/skills/siyuan-note/scripts/siyuan_note.py export-pdf \
  --doc-id "20260517133321-vizsopy" \
  --output "/path/to/output.pdf"
```

常用选项：

- `--no-merge`：不合并子文档。
- `--keep-fold`：保留折叠状态。
- `--browser /path/to/browser`：指定 Chrome/Chromium/Edge。
- `--timeout 120`：设置浏览器渲染超时秒数。

注意：思源后端本身不直接生成最终 PDF；桌面端导出 PDF 依赖 Electron 打印流程。本脚本在 CLI 场景下用 headless Chrome/Edge 补齐这一步。

### 14. 读取今日日记下的子文档

当用户说"读今天日记下的第一篇文章"时，分两步操作：

**第一步：找到今日日记 doc_id**
```bash
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py show-today-note-path --notebook-name "1.收集箱"
```

**第二步：列出子文档**
```bash
curl -s -X POST "http://127.0.0.1:6806/api/filetree/listDocsByPath" \
  -H "Authorization: Token ${SIYUAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notebook":"20220105205758-vniy8zc","path":"/日记路径.sy","sort":4}'
```
用第一步返回的 `path` 字段拼接 `.sy` 后缀作为 `path` 参数。

**第三步：读取具体文章内容**
```bash
curl -s -X POST "http://127.0.0.1:6806/api/export/exportMdContent" \
  -H "Authorization: Token ${SIYUAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"id":"子文档ID"}'
```
从第二步返回的 `files` 数组中取 `id` 字段。

### 完整流程示例（读取今天日记下第一篇）

```bash
# 1. 获取今日日记
python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py show-today-note-path --notebook-name "1.收集箱"
# → 得到 doc_id 和 path

# 2. 列出子文档（path 需加 .sy 后缀）
curl -s -X POST "http://127.0.0.1:6806/api/filetree/listDocsByPath" \
  -H "Authorization: Token ${SIYUAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notebook":"20220105205758-vniy8zc","path":"/.../日记doc_id.sy","sort":4}'

# 3. 读取第一篇文章
curl -s -X POST "http://127.0.0.1:6806/api/export/exportMdContent" \
  -H "Authorization: Token ${SIYUAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"id":"files[0].id"}'
```

也支持用标题定位：用户说"读今天日记下「休息」"时，从第二步返回的 `files` 中按 `name` 匹配（去掉 `.sy` 后缀）。

## 参数规则

### 环境变量
- `SIYUAN_API_URL`：思源 API 地址，例如 `http://127.0.0.1:9000`
- `SIYUAN_API_TOKEN`：思源 API Token
- 必须设置 `SIYUAN_API_TOKEN`，或通过 `--token` 临时提供

### action
支持以下子命令：
- `list-notebooks`
- `list-paths`
- `create`
- `get-doc-id`
- `update`
- `append`
- `upsert`
- `show-today-note-path`
- `append-today-note`
- `upsert-today-note`
- `attach-file`
- `attach-today-note`

### notebook / notebook-name
- `--notebook`：笔记本 ID
- `--notebook-name`：笔记本名称
- 推荐优先使用 `--notebook-name`
- 不再写死默认笔记本，必须由用户明确指定目标笔记本

### path
- create / get-doc-id / upsert 时必填
- update / append / attach-file 在不传 `--doc-id` 时必填
- list-paths 时可选，默认 `/`
- 必须以 `/` 开头
- 在 Windows / Git Bash 下，路径也要按思源虚拟路径写，例如 `/OpenCLI教程`，不要传磁盘路径如 `D:/Git/OpenCLI教程`
- 脚本会自动清理常见的 Git Bash 路径改写问题，避免把思源文档错误创建到磁盘盘符样式路径下

### doc-id
- update / append / attach-file 时可选
- 如果未提供，则脚本会通过 `notebook + path` 自动查找

### date
- `show-today-note-path` / `append-today-note` / `upsert-today-note` / `attach-today-note` 可选
- 格式：`YYYY-MM-DD`
- 不传时默认当天

### file
- `attach-file` / `attach-today-note` 必填
- 需要提供本地文件绝对路径

### assets-dir-path
- 附件上传目录，默认 `/assets/`
- 可自定义为 `/assets/claude/` 等子目录

### label
- 附件链接显示文字，可选
- 不传时默认 `附件：文件名`

### markdown
- create / update / append / upsert / append-today-note / upsert-today-note 时必须提供 `--markdown` 或 `--markdown-file` 之一
- 长文档、本地文件、简历、报告等优先用 `--markdown-file`
- 保持用户原始 Markdown，不要擅自改写，除非用户明确要求润色

## 返回要求

- 成功时，简洁返回执行结果、目标笔记本/文档、上传后的资源路径等关键信息
- 失败时，返回接口错误信息
- 如果缺少 notebook/path/doc-id/markdown/file，提示补充

## 说明

- daily note 快捷能力依赖目标笔记本中已经存在 `daily note` 目录结构
- 附件通过 `/api/asset/upload` 上传到思源 assets 目录
- 上传后会自动在目标文档末尾追加 Markdown 链接，例如：`[附件：test.zip](assets/xxx.zip)`

## 实现说明

脚本路径：`~/.claude/skills/siyuan-note/scripts/siyuan_note.py`
（Windows 上对应 `%USERPROFILE%\.claude\skills\siyuan-note\scripts\siyuan_note.py`）

macOS / Linux 调用方式：

```bash
python3 ~/.claude/skills/siyuan-note/scripts/siyuan_note.py <subcommand> [args]
```

Windows + Git Bash 调用方式：

```bash
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" python ~/.claude/skills/siyuan-note/scripts/siyuan_note.py <subcommand> [args]
```

注意：
- macOS 上优先使用 `python3`
- 在 Windows + Git Bash 下，保留上面的 `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*"` 前缀，避免 `/路径` 被自动改写成磁盘路径
