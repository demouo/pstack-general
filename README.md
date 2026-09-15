# pstack · 通用 harness 版

将 [Cursor pstack](https://github.com/cursor/plugins/tree/main/pstack) 的工程工作流移植为普通 Markdown 技能包。保留代码理解、设计评审、实现、验证、PR 监控、长任务恢复和原则技能，去掉 Cursor 插件安装、私有路径、专属模型 ID 和工具参数依赖。

**基础要求：harness 能读取文件并遵循指令。** 执行代码需要 shell；多代理、跨模型、浏览器、历史记录和自动调度均按当前会话实际能力启用。没有多代理时可串行执行角色；不会把串行自审声称为独立评审。

## 快速开始

安装器只需要 Python 3.9+。克隆本仓库或解压 Release 压缩包后运行：

```sh
python3 scripts/install.py --target /absolute/path/to/project --entrypoint AGENTS.md
```

安装到目标项目的 `.pstack/`，并在指定指令文件追加一个带标记的入口块。保留原有指令、用户配置和非托管文件；重复运行可更新。若源文件与本地修改冲突，整次更新在写入前停止，先检查合并再重试。预览使用 `--dry-run`。

如果已有指令文件，选择该 harness 实际读取的文件；无需使用默认路径猜测其技能发现机制：

```sh
# 使用 CLAUDE.md 的环境
python3 scripts/install.py --target /absolute/path/to/project --entrypoint CLAUDE.md

# 使用 GEMINI.md 的环境
python3 scripts/install.py --target /absolute/path/to/project --entrypoint GEMINI.md

# 无自动指令加载的环境：仅安装，然后在对话中指定文件
python3 scripts/install.py --target /absolute/path/to/project
```

在 Codex、Claude Code、Gemini CLI、OpenCode、Cursor 或其他 harness 中，最通用的调用方式是：

> 读取 `.pstack/skills/how/SKILL.md`，按其中流程解释这个仓库的认证模块。

> 读取 `.pstack/skills/poteto-mode/SKILL.md`，使用完整 pstack 工作流完成这个功能。

这是**文件指令接入**，不是对各厂商原生插件、斜杠命令或全部运行能力的兼容承诺。若入口文件未被自动加载，在会话中直接指明上述路径。安装不更改全局配置，也不注册后台任务。

## 常用工作流

| 任务 | 技能 |
| --- | --- |
| 完整工程流程、playbook 路由 | `poteto-mode` |
| 理解实现 / 追查设计原因 | `how` / `why` |
| 竞争方案 / 架构设计 | `arena` / `architect` |
| 对抗评审 / 并行覆盖 | `interrogate` / `swarm` |
| 测试驱动 / 影响分析 | `tdd` / `blast-radius` |
| 技术写作 / 去冗余 | `technical-writing` / `unslop` / `deslop` |
| 复盘 / 找回上下文 / 决策记录 | `reflect` / `recall` / `show-me-your-work` |
| 创建或维护真实应用验证流程 | `create-verification-skill` / `maintain-verification-skill` |
| 设置模型策略 | `setup-pstack` |
| Slack 报告分诊和复现 | `automations/benny/FOR_AGENTS.md` |

全部技能见 [技能目录](skills/)。模型配置可放在目标项目 `.pstack/models.md`；未配置时继承当前会话。配置由技能读取，不修改宿主模型设置。

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

迁移细节见 [PORTABILITY.md](docs/PORTABILITY.md)，源版本与 MIT 授权见 [UPSTREAM.md](UPSTREAM.md) 和 [LICENSE](LICENSE)。已在本机 pi 0.84.1 的真实模型会话中验证文件/原生技能加载、评审降级、TDD 修复、历史缺失和调度缺失五个场景，见 [pi 实测报告](docs/validation/pi-2026-09-15.md)。其他 harness 尚未逐一执行端到端验证。
