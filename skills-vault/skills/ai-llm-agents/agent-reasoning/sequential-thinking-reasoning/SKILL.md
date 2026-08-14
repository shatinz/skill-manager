---
id: ai-llm-agents.agent-reasoning.sequential-thinking-reasoning
name: sequential-thinking-reasoning
title: Sequential Thinking & Tree-of-Thought Dynamic Reasoning
category: ai-llm-agents
subcategory: agent-reasoning
version: 1.3.0
tags:
- sequential-thinking
- tree-of-thought
- chain-of-thought
- reasoning
- self-correction
- backtracking
trust_rating: 0.99
estimated_tokens: 1750
description: Implement structured sequential reasoning and tree-of-thought exploration
  loops for complex multi-step coding, debugging, and architecture design tasks with
  branch evaluation, backtracking, and hypothesis testing.
trigger_patterns:
- sequential thinking reasoning loop
- tree of thought branch backtracking
- agent self reflection hypothesis testing
- dynamic step by step problem solving
---

# Sequential Thinking & Tree-of-Thought Dynamic Reasoning

## Objective
Guide autonomous AI agents through complex, ambiguous, or multi-faceted engineering problems by enforcing dynamic, hypothesis-driven sequential reasoning steps that support hypothesis branching, self-critique, and backtracking.

## Reasoning Loop Protocol
```
Task Prompt
  ├── Step 1: Problem Decomposition & Hypothesis Formulation (Branch 1)
  ├── Step 2: Intermediate Evidence Evaluation & Reality Check
  ├── Step 3: Self-Critique / Contradiction Discovery -> Backtrack to Step 1 (Branch 2)
  ├── Step 4: Refined Execution Path Verification
  └── Step 5: Final Synthesis & Concrete Action Plan
```

## Structured Step Schema
```json
{
  "thought_number": 3,
  "total_thoughts_estimated": 6,
  "is_revision": true,
  "revises_thought": 1,
  "branch_id": "branch-B",
  "branch_from_thought": 1,
  "thought_content": "Hypothesis A assumed SQLite locked during concurrent writes in WAL mode. But WAL mode permits 1 writer and concurrent readers. Therefore the root cause must be unclosed transaction handles.",
  "next_action": "search_code_for_unclosed_sessions"
}
```

## Golden Rules
1. **Never commit prematurely to an unverified assumption**: Formulate at least two rival hypotheses for puzzling bug reports.
2. **Explicitly mark revisions and branches**: When new observations contradict earlier conclusions, acknowledge the discrepancy and prune the dead branch.
3. **Verify edge conditions**: Check boundary values (0, 1, empty, negative, max limits) before declaring a solution complete.
