---
id: data-ai-engineering.llm-rag.prompt-engineering-distiller
name: prompt-engineering-distiller
title: System Prompt Engineering & Chain-of-Thought Distiller
category: data-ai-engineering
subcategory: llm-rag
version: 1.2.0
tags:
- prompt-engineering
- cot
- llm
- system-prompts
- evals
trust_rating: 0.95
estimated_tokens: 1400
description: Engineer high-leverage agent system prompts with strict XML/JSON formatting,
  few-shot grounding examples, step-by-step reasoning triggers, and anti-hallucination
  guardrails.
trigger_patterns:
- write system prompt for agent
- prompt engineering best practices
- chain of thought prompt template
- reduce llm hallucinations
---

# System Prompt Engineering & Chain-of-Thought Distiller

## Anatomy of an Unbeatable Agent Prompt
- **Identity & Mission**: Concrete role, purpose, and operating boundaries.
- **Explicit Constraints**: Negative constraints, disallowed assumptions, output constraints.
- **Input Formatting**: Clean XML tags (`<user_request>`, `<context>`, `<tools>`).
- **Chain of Thought**: Mandate hidden `<thinking>` scratchpad before producing final answer.
