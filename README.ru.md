# 🌐 Skill Manager — Инфраструктурный уровень на основе реального опыта для автономных агентов

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io/)
[![Security: Audited](https://img.shields.io/badge/Security%20Gate-Verified%200%20Vulns-success)](security_audit_report.md)
[![Ecosystem](https://img.shields.io/badge/Vault-60%20Curated%20Skills-cyan)](#-живой-каталог-навыков-60-проверенных-навыков)

**[English](README.md)** • **[فارسی (Persian)](README.fa.md)** • **[Русский (Russian)](README.ru.md)** • **[中文 (Chinese)](README.zh.md)**

</div>

---

## 💡 Ключевая философия: Реальный опыт вместо популярности

> **Skill Manager — это не статичный каталог навыков. Это инфраструктурный уровень для автономных ИИ-агентов.**

Традиционные хранилища навыков работают по принципу витрины файлов:
> *«Вот список из 500 markdown-файлов. Ищите по ключевым словам, ставьте звёздочки или установите сразу 50 штук».*

**Для автономных агентов эта модель неприменима.** Агентам не нужны звёзды на GitHub, раздутые контекстные окна и непроверенные дампы промптов.

### Смена парадигмы мышления агента

Когда автономный агент решает инженерную задачу, он не думает:
> ❌ *«Поищу-ка я в папке из 50 навыков то, что может подойти».*

Агент мыслит так:
> 🧠 **«Я отлаживаю сетевую проблему в Rust. Предоставь мне наиболее проверенный рабочий процесс отладки Rust, доказавший свою эффективность на аналогичных репозиториях».**

```
              ТРАДИЦИОННЫЕ ХРАНИЛИЩА vs. SKILL MANAGER
┌───────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│        Статичные хранилища            │   │              Skill Manager               │
├───────────────────────────────────────┤   ├──────────────────────────────────────────┤
│ • Оценка по популярности и звёздам    │   │ • Реестр реальных эмпирических данных    │
│ • Копирование статичного текста       │   │ • Динамический движок подбора под задачу │
│ • Пакетная установка десятков файлов  │   │ • Мгновенная инъекция без лишнего веса   │
│ • Устаревающие инструкции без тестов  │   │ • 7-стадийный эволюционный пайплайн      │
│ • Выполнение вслепую                  │   │ • Замкнутый цикл обратной связи          │
└───────────────────────────────────────┘   └──────────────────────────────────────────┘
```

---

## 📊 Реестр реальной телеметрии и доказательств выполнения

В Skill Manager навыки оцениваются и эволюционируют на основе фактических результатов выполнения задач на реальных кодовых базах. Каждый запуск агента фиксируется в реестре доказательств:

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

Когда другой агент сталкивается с похожей задачей, Skill Manager анализирует семантическое соответствие, подтверждённый процент успеха, среднее время решения (MTTR) и показатели используемой модели, возвращая оптимальный рабочий процесс.

---

## ⚡ 7-стадийный эволюционный пайплайн

```
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                 7-СТАДИЙНЫЙ АВТОНОМНЫЙ ПАЙПЛАЙН ЭВОЛЮЦИИ                    │
  └─────────────────────────────────────────────────────────────────────────────┘
      │
  [Стадия A: Ингестия] ────────► Парсинг AST из репозиториев, валидация по RFC
      │
  [Стадия B: Телеметрия] ──────► Фиксация реальных метрик (проект, задача, время, цена)
      │
  [Стадия C: Аккумуляция] ─────► Кластеризация предложений от агентов и людей
      │
  [Стадия D: Нелинейный мердж] ► Взвешенный синтез с защитой от Sybil-атак
      │
  [Стадия E: Sentinel-безопасность] SAST-анализ AST, канареечный песочницы, 0 уязвимостей
      │
  [Стадия F: Канареечный релиз] ► Плавный релиз с полной цепочкой версий и откатом
      │
  [Стадия G: Сервинг агентов] ──► Ранжирование под задачу, FastMCP (stdio/SSE) и REST
```

---

## 🚀 Быстрый старт для агентов и разработчиков

### 1. Установка CLI (`eshkill` / `askill`)
```bash
git clone https://github.com/shatinz/skill-manager.git
cd skill-manager
pip install -e ./cli
```

### 2. Подбор доказанного навыка под задачу (`rank`)
Вместо ручного поиска запросите подтверждённый рабочий процесс:

```bash
eshkill rank --task "Fix CI" --repo "Rust compiler plugin" --model "GPT-5"
```

### 3. Отправка телеметрии выполнения (`report-evidence`)
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

### 4. Автономное самовосстановление агентов (`auto-propose`)
При обнаружении предупреждений компилятора или устаревших API агент автоматически формирует исправление с явной меткой `🤖 Autonomous Agent`:

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

## 🔌 Интеграция по Model Context Protocol (MCP)

Skill Manager изначально поддерживает протокол MCP (JSON-RPC 2.0 stdio/SSE) для **Claude Desktop**, **Cursor**, **Windsurf** и **Antigravity**:

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

## 🏛️ Живой каталог навыков (60 проверенных навыков)

| Категория | Ключевые паттерны и архитектуры |
| :--- | :--- |
| **🤖 AI & LLM Agents** | FastMCP серверы, графовая ассоциативная память, Tree-of-Thought рассуждения, мультиагентные пайплайны LangGraph, гибридный RAG. |
| **🌐 Web Frameworks** | Next.js 15 App Router, TanStack Router & Query v5, React 19 Server Actions, FastAPI Production Craft, Hono Edge, Astro 5. |
| **🎨 UI & Anti-Slop Design** | Shadcn UI & Tailwind v4 Tokens, Dark Mode градиенты, адаптивные гибкие сетки, WCAG доступность. |
| **🗄️ Databases & Storage** | Тюнинг Postgres Explain Analyze, Supabase RLS Realtime, Prisma ORM, Drizzle Type-Safe SQL, DuckDB & Polars. |
| **☁️ DevOps & Cloud** | GitOps c ArgoCD и Helm, многоэтапные Distroless Docker сборки, GitHub Actions Matrix CI, OpenTelemetry & Prometheus. |
| **🛡️ SAST & Security** | Сканер OWASP Top 10, предотвращение утечек секретов, защита JWT OAuth2, санитайзинг XSS. |
| **🧪 Testing & QA** | Pytest моки и фикстуры, Playwright E2E автоматизация, property-based тестирование Hypothesis. |
| **📈 Business & E-Commerce** | Stripe вебхуки и подписки, мультивалютный учёт, генерация SEO-тегов, конверсионные воронки. |
| **📐 Clean Architecture** | Асинхронные микросервисы на Rust Axum & Tokio, Outbox паттерн и Event Sourcing, Architecture Decision Records (ADR). |

---

## 📄 Лицензия

Проект распространяется под лицензией **MIT License**. Подробнее см. в файле [`LICENSE`](LICENSE).
