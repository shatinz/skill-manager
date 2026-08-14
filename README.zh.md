# 🌐 Skill Manager — 面向自主智能体的实证工程基础设施层

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io/)
[![Security: Audited](https://img.shields.io/badge/Security%20Gate-Verified%200%20Vulns-success)](security_audit_report.md)
[![Ecosystem](https://img.shields.io/badge/Vault-60%20Curated%20Skills-cyan)](#-动态技能宝库-60-项经过验证的生产级技能)

**[English](README.md)** • **[فارسی (Persian)](README.fa.md)** • **[Русский (Russian)](README.ru.md)** • **[中文 (Chinese)](README.zh.md)**

</div>

---

## 💡 核心哲学：用真实工程证据替代虚荣流行度

> **Skill Manager 绝非一个静态的技能收集仓库，它是为自主 AI 智能体（Autonomous AI Agents）构建的底层基础设施。**

传统的技能库往往类似于静态的应用商店或 Markdown 堆砌列表：
> *“这里有 500 个文件，请自行搜索、按 Star 数排序，或一次性安装 50 个技能。”*

**这种模式在自主智能体时代已经彻底失效。** 智能体不需要虚荣的 GitHub Star，不需要未经验证的 Prompt 文本，更不需要被无用信息撑爆的上下文窗口。

### 智能体视角的范式转变

当一个自主智能体开始执行工程任务时，它不应该这样思考：
> ❌ *“让我在包含 50 个技能的文件目录里漫无目的地翻找可能相关的规则。”*

智能体真正的决策思维是：
> 🧠 **“我正在排查一个 Rust 网络层并发问题。请直接为我检索在同类代码仓库中经过实证检验、成功率最高的 Rust 调试工作流。”**

```
               传统静态技能库 vs. SKILL MANAGER 基础设施
┌───────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│              传统技能库               │   │              Skill Manager               │
├───────────────────────────────────────┤   ├──────────────────────────────────────────┤
│ • 依赖 GitHub Star 和虚荣热度排序     │   │ • 基于真实项目执行结果的实证数据账本     │
│ • 静态 Markdown 复制粘贴              │   │ • 依据具体任务与代码库的动态感知排序引擎 │
│ • 机械式批量安装数十个冗余技能        │   │ • 毫秒级按需注入，零上下文膨胀           │
│ • 未经验证、易过期的静态指令          │   │ • 7 阶段非线性进化与可信融合流水线       │
│ • 缺乏反馈的盲目提示词执行            │   │ • 闭环工程遥测反馈（成功率、耗时、成本） │
└───────────────────────────────────────┘   └──────────────────────────────────────────┘
```

---

## 📊 真实项目工程遥测与实证账本（Evidence Ledger）

在 Skill Manager 中，所有技能的基准测试与演进均基于真实代码库上的工程执行结果。每一次智能体运行都会向实证账本提交数据：

<div align="center">

```yaml
Repository:    "Rust compiler plugin"
Task:          "Fix CI async deadlock in worker channels"
Outcome:       ✅ Success
Time (MTTR):   3 min (180s)
Model:         GPT-5
Cost:          $0.19
Tokens:        14,500
Skill Version: v4.1.0
Evidence Note: "Resolved non-blocking tokio task channels and updated lifetime bounds."
```

</div>

当其他智能体遇到类似任务时，Skill Manager 会综合语义匹配度、实证成功率、平均解决时长（MTTR）及模型兼容性，精准返回已被证明有效的最优工作流。

---

## ⚡ 7 阶段自主进化架构流水线

```
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                        7 阶段自主智能体进化流水线                           │
  └─────────────────────────────────────────────────────────────────────────────┘
      │
  [阶段 A: 摄取解析] ────► 摄取 GitHub 仓库，AST 语法树解析与 RFC 架构校验
      │
  [阶段 B: 实证遥测] ────► 记录真实项目运行指标（代码库、任务、耗时、开销）
      │
  [阶段 C: 批次聚合] ────► 聚合人类开发者与自主智能体在时间窗口内的提案
      │
  [阶段 D: 非线性融合] ──► 基于注意力与不可伪造信誉的动态加权融合算法
      │
  [阶段 E: 安全哨兵] ────► SAST AST 漏洞扫描、金丝雀沙箱隔离，确保 0 风险
      │
  [阶段 F: 金丝雀发布] ──► 渐进式发布，附带完整版本血统链与自动回滚机制
      │
  [阶段 G: 智能体服务] ──► 任务感知动态排序、FastMCP (stdio/SSE) 与 REST 守护进程
```

---

## 🚀 智能体与开发者快速上手

### 1. 安装命令行工具 (`eshkill` / `askill`)
```bash
git clone https://github.com/shatinz/skill-manager.git
cd skill-manager
pip install -e ./cli
```

### 2. 基于任务与实证检索最优工作流 (`rank`)
无需手动浏览，直接根据具体任务获取验证过的高可信技能：

```bash
eshkill rank --task "Fix CI" --repo "Rust compiler plugin" --model "GPT-5"
```

**输出示例：**
```text
⚡ EMPIRICAL SKILL RANKING (EVIDENCE-BASED ENGINE)
• Target Task: Fix CI
• Repository Context: Rust compiler plugin
• Target Model: GPT-5
────────────────────────────────────────────────────────────

🏆 #1 TOP PROVEN WORKFLOW: Rust Axum & Tokio High-Throughput Async Architecture
• Empirical Reliability: 99% Success Rate
• Avg Resolution Time (MTTR): 2.0 min
• Avg Cost Efficiency: $0.12
• Real-World Runs: 42 evidence records
• Recommended Version: v1.3.0

Selected based on verified real-world runs on similar Rust compiler plugins.
```

### 3. 上报执行遥测证据 (`report-evidence`)
在任务完成后，将工程结果回传给平台：

```bash
eshkill report-evidence \
  --skill rust-axum-tokio-async \
  --repo "Rust compiler plugin" \
  --task "Fix CI" \
  --outcome success \
  --duration 180 \
  --model "GPT-5" \
  --cost 0.19 \
  --version "4.1.0" \
  --notes "Resolved non-blocking tokio task channels"
```

### 4. 智能体自主自愈与提案提交 (`auto-propose`)
当智能体在运行时捕获到编译警告、废弃 API 或错误时，可自动生成附带 `🤖 Autonomous Agent` 明确标识的改进提案：

```bash
eshkill auto-propose \
  --skill fastapi-production-craft \
  --feedback "DeprecationWarning: Starlette 0.40 form parsing changed" \
  --fix "Enforce async request.form() with python-multipart>=0.0.20" \
  --reason "Resolve Starlette async form deprecation" \
  --agent-id "agent:autonomous-debugger" \
  --model "claude-3-5-sonnet"
```

---

## 🔌 Model Context Protocol (MCP) 标准集成

Skill Manager 原生支持 Model Context Protocol (MCP) 标准（JSON-RPC 2.0 stdio/SSE），完全兼容 **Claude Desktop**、**Cursor**、**Windsurf** 与 **Antigravity**：

```json
{
  "mcpServers": {
    "skill-manager": {
      "command": "python",
      "args": ["-m", "eshkill.cli", "mcp"],
      "env": {
        "SKILL_MANAGER_API_URL": "http://127.0.0.1:8000/api"
      }
    }
  }
}
```

---

## 🏛️ 动态技能宝库 (60 项经过验证的生产级技能)

| 分类 | 核心设计模式与技术栈 |
| :--- | :--- |
| **🤖 AI 与 LLM 智能体** | FastMCP 服务器开发、知识图谱关联记忆、思维树 (Tree-of-Thought) 顺序推理、LangGraph 多智能体编排、混合检索 RAG。 |
| **🌐 Web 现代全栈框架** | Next.js 15 App Router、TanStack Router & Query v5、React 19 Server Actions、FastAPI 生产架构、Hono Edge、Astro 5。 |
| **🎨 现代化 UI 设计** | Shadcn UI 与 Tailwind v4 语义设计 Token、暗色模式氛围渐变、流体自适应网格、WCAG AA 无障碍交互。 |
| **🗄️ 数据库与持久化** | Postgres Explain Analyze 调优、Supabase RLS 实时期、Prisma ORM、Drizzle 类型安全 SQL、DuckDB & Polars 数据分析。 |
| **☁️ 云原生与 DevOps** | ArgoCD GitOps 与 Kubernetes Helm 编排、Distroless 多阶段 Docker、GitHub Actions 矩阵构建、OpenTelemetry 全链路追踪。 |
| **🛡️ 代码审计与 SAST 安全** | OWASP Top 10 防护、密钥提交拦截守卫、JWT OAuth2 权限防线、输入过滤与 XSS 防御。 |
| **🧪 自动化测试与质量保障** | Pytest 模块化 Mock 与 Fixture、Playwright 端到端自动化、Hypothesis 基于属性的健壮性测试。 |
| **📈 商业与电商增长工程** | Stripe 计费与 Webhook、多币种复式账本、自动化 SEO 元数据生成、转化漏斗性能调优。 |
| **📐 整洁架构与系统工程** | Rust Axum 与 Tokio 极速异步微服务、Transactional Outbox 事件驱动、Michael Nygard 架构决策记录 (ADR)。 |

---

## 📄 开源许可证

本项目采用 **MIT License** 授权。详情参见 [`LICENSE`](LICENSE) 文件。
