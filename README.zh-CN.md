# pstack · 通用 harness 版

[English](README.md) | **简体中文**

将 [Cursor pstack](https://github.com/cursor/plugins/tree/main/pstack) 的工程工作流移植为普通 Markdown 技能包。保留代码理解、设计评审、实现、验证、PR 监控、长任务恢复和原则技能，去掉 Cursor 插件安装、私有路径、专属模型 ID 和工具参数依赖。

**基础要求：harness 能读取文件并遵循指令。** 执行代码需要 shell；多代理、跨模型、浏览器、历史记录和自动调度均按当前会话实际能力启用。没有多代理时可串行执行角色；不会把串行自审声称为独立评审。

## 快速开始

### 一句话安装

把下面这句话复制给你正在使用的 harness：

```text
请从 https://github.com/demouo/pstack-general 获取最新版 pstack，按仓库 README 将技能安装到当前项目的 .agents/skills/ 并接入当前 harness，保留已有技能、指令和用户配置，完成后验证技能可以加载。
```

### 手动安装

安装器只需要 Python 3.9+。克隆本仓库或解压 Release 压缩包后运行：

```sh
python3 scripts/install.py --target /absolute/path/to/project
```

技能直接安装到 `.agents/skills/<skill-name>/`，这是 [Agent Skills 推荐的共享发现位置](https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx)。每个目录包含 `SKILL.md` 和配套资源。支持该目录的 harness 可以原生发现技能；[pi 已支持](https://pi.dev/docs/latest/skills)。其他环境可使用显式路径或指令文件接入。

`.pstack/` 只保留安装清单、授权、来源记录和可选自动化包；用户模型配置与运行状态也继续存放在那里。保留已有技能和用户配置；本地修改或其他同名技能文件发生冲突时，在写入前停止。重新运行可更新，预览使用 `--dry-run`。

如果通过指令文件接入，可选该 harness 实际读取的文件：

```sh
# 使用 AGENTS.md 的环境
python3 scripts/install.py --target /absolute/path/to/project --entrypoint AGENTS.md

# 使用 CLAUDE.md 的环境
python3 scripts/install.py --target /absolute/path/to/project --entrypoint CLAUDE.md

# 使用 GEMINI.md 的环境
python3 scripts/install.py --target /absolute/path/to/project --entrypoint GEMINI.md

```

在 Codex、Claude Code、Gemini CLI、OpenCode、Cursor 或其他 harness 中，最通用的调用方式是：

> 读取 `.agents/skills/how/SKILL.md`，按其中流程解释这个仓库的认证模块。

> 读取 `.agents/skills/poteto-mode/SKILL.md`，使用完整 pstack 工作流完成这个功能。

原生发现、斜杠命令和运行能力因 harness 而异；无法自动加载时，在会话中直接指明上述路径。安装不更改全局配置，也不注册后台任务。

### 升级旧版安装

在同一目标项目重跑安装器。它将未修改的托管技能从 `.pstack/skills/` 迁移到 `.agents/skills/`，并刷新 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 中已有的 pstack 标记块。其他入口文件名需通过 `--entrypoint` 指定。本地修改或目标冲突会在写入前中止迁移。非托管旧文件、模型配置和运行状态保留原处，详见 [目录迁移说明](docs/updates/2026-10-05-skill-layout.md)。

## 常用工作流

| 任务 | 技能 |
| --- | --- |
| 完整工程流程、playbook 路由 | `poteto-mode` |
| 理解实现 / 追查设计原因 | `how` / `why` |
| 竞争方案 / 架构设计 | `arena` / `architect` |
| 对抗评审 / 并行覆盖 | `interrogate` / `swarm` |
| 测试驱动 / 影响分析 | `tdd` / `blast-radius` |
| 性能测量审查 / 解释测量数值 | `benchmark-checklist` / `principle-explain-the-number` |
| 消除代理反复犯的错误 | `correct` |
| 技术写作 / 去冗余 | `technical-writing` / `unslop` / `deslop` |
| 复盘 / 找回上下文 / 决策记录 | `reflect` / `recall` / `show-me-your-work` |
| 创建或维护真实应用验证流程 | `create-verification-skill` / `maintain-verification-skill` |
| 设置模型策略 | `setup-pstack` |
| Slack 报告分诊和复现 | `automations/benny/FOR_AGENTS.md` |

全部 53 个技能见 [技能目录](skills/)。模型配置可放在目标项目 `.pstack/models.md`；未配置时继承当前会话。配置由技能读取，不修改宿主模型设置。

当前通用版 `v0.3.0` 使用 `.agents/skills/` 安装目录，选择性同步至上游 pstack `0.15.9`（2026-10-05）。包含性能证据审查、重复错误治理，以及架构、日志、验证和自主任务流程，继续保留通用能力降级。上游适配的具体取舍见 [更新记录](docs/updates/2026-10-05.md)。

## 可选工具依赖

- `worktree-audit.sh`：Python 3.9+、Git；纯本地读取，无需聊天记录。
- `check-plan.mjs`：Node.js；检查多 PR 计划格式。
- `scripts/orch/orch.ts`：Bun；显式指定 `--store`。`frontier set` 仍需 Graphite `gt` 的栈元数据，其余状态操作不需要。它管理状态，不负责启动或唤醒代理。
- `scripts/watch-pr/watch-pr`：Bun、GitHub CLI `gh` 和相应仓库权限。只支持 GitHub。
- Bun 工具首次运行会按锁文件安装依赖。它们不是读取技能的前提。
- Benny 和 webhook UI：需要用户选定的事件运行器、连接器和密钥配置；未配置时产出草稿，不会实际运行。

## 验证

```sh
python3 -m unittest discover -s tests -v
cd skills/poteto-mode/scripts
bun install --frozen-lockfile
bun test orch watch-pr
bun run typecheck
```

迁移细节见 [PORTABILITY.md](docs/PORTABILITY.md)，源版本与 MIT 授权见 [UPSTREAM.md](UPSTREAM.md) 和 [LICENSE](LICENSE)。已在本机 pi 0.84.1 的真实模型会话中验证文件/原生技能加载、评审降级、TDD 修复、历史缺失和调度缺失五个场景，见 [初版 pi 实测报告](docs/validation/pi-2026-09-15.md)。另有性能测量审查与重复错误治理两个实测场景，见 [10 月 pi 实测报告](docs/validation/pi-2026-10-05.md)。[目录改造验证](docs/validation/pi-agents-layout-2026-10-05.md) 确认 pi 原生发现 `.agents/skills/` 中全部 53 个技能、两个真实会话正常执行，以及 v0.2.0 安装迁移成功。其他 harness 尚未逐一执行端到端验证。
