# Personal AI Plugin

个人 AI Plugin 集合，统一管理可供 Codex、Claude Code 及兼容工具使用的内容。

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
