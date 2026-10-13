# Personal AI Plugin

个人 AI Plugin 集合，统一管理可供 Codex、Claude Code 及兼容工具使用的内容。

## Featured Skills

### subtitle-extractor

把 YouTube、Bilibili、X/Twitter 以及本地视频/音频转换成 SRT、VTT 或 TXT。优先提取现成字幕轨；没有字幕轨时使用本地 faster-whisper 转写；不会把 B站弹幕当作字幕。在线体验：[Subtitle Studio](https://subtitle.powcai.top/)。

```bash
npx skills add https://github.com/powcai001/ai-plugin \
  --skill subtitle-extractor -g -y
```

发布与推广文案见 [docs/promotion/subtitle-extractor-launch.md](docs/promotion/subtitle-extractor-launch.md) 和 [docs/promotion/video-subtitle-why-and-how.md](docs/promotion/video-subtitle-why-and-how.md)。

```text
├── skills/
├── agents/
├── rules/
├── commands/
├── hooks/
├── mcp/
└── prompts/
```

每个目录对应一类 AI 工具扩展：

- `skills/`：可复用技能及其参考资料、脚本
- `agents/`：Agent 定义和角色配置
- `rules/`：共享行为规则
- `commands/`：可复用命令
- `hooks/`：生命周期钩子
- `mcp/`：MCP 服务和集成配置
- `prompts/`：提示词套件和引导模板

`siyuan-note` 使用 `SIYUAN_API_TOKEN` 或 `--token` 提供 API token；不要把真实 token 提交到仓库。

`subtitle-extractor` 的 Bilibili 字幕接口依赖 OpenCLI 登录态；本地转写依赖 `uv`/`uvx`，可选依赖 FFmpeg。不要把浏览器 Cookie 或平台凭证提交到仓库。
