# Personal Skills

个人 Agent Skills 集合，可供 Codex、Claude Code 及支持 Agent Skills 目录结构的工具使用。CC Switch 可以将此仓库作为 Git 技能源同步。

## 同步使用

在 CC Switch 中添加 GitHub 仓库 `https://github.com/powcai001/skills` 作为技能源。仓库为私有，需要 CC Switch 所在环境具备 GitHub 访问权限。更新后可通过 CC Switch 拉取同步。

## 目录

每个技能独立放在一个目录中，目录内包含 `SKILL.md`，并可带有 `references/`、`scripts/`、`agents/` 等资源。

## 敏感配置

`siyuan-note` 使用 `SIYUAN_API_TOKEN` 或 `--token` 提供 API token；不要把真实 token 提交到仓库。示例中的个人路径已替换为占位路径。
