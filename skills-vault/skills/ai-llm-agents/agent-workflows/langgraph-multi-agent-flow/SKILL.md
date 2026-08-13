---
id: ai-llm-agents.agent-workflows.langgraph-multi-agent-flow
name: langgraph-multi-agent-flow
title: LangGraph Multi-Agent Stateful Flow & Human-in-the-Loop
category: ai-llm-agents
subcategory: agent-workflows
version: 1.4.0
tags:
- langgraph
- langchain
- state-graph
- multi-agent
- human-in-the-loop
- checkpoints
trust_rating: 0.98
estimated_tokens: 1700
description: Architect cyclic, stateful multi-agent workflows using LangGraph, persistent
  Postgres/Memory checkpointers, dynamic conditional routing, and human-in-the-loop
  approval interrupts.
trigger_patterns:
- langgraph multi agent workflow
- langgraph stategraph conditional edges
- langgraph human in the loop interrupt
- langgraph checkpointer persistent state
---

# LangGraph Multi-Agent Stateful Flow & Human-in-the-Loop

## Objective
Orchestrate complex autonomous multi-agent teams with shared state schemas, cyclic feedback loops, tool execution nodes, and human approval interrupts.

## Blueprint (`agent_flow.py`)
```python
from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 1. State Definition
class AgentState(TypedDict):
    task: str
    plan: str
    code: str
    review_feedback: str
    iterations: int
    approved: bool

# 2. Agent Nodes
def planner_node(state: AgentState) -> dict:
    # Generates initial plan
    return {"plan": f"Plan for: {state['task']}", "iterations": state["iterations"] + 1}

def coder_node(state: AgentState) -> dict:
    # Generates or updates code based on review
    return {"code": f"# Implementation\nprint('{state['task']}')"}

def reviewer_node(state: AgentState) -> dict:
    # Evaluates code quality
    if state["iterations"] >= 3:
        return {"approved": True, "review_feedback": "Passed quality gates."}
    return {"approved": False, "review_feedback": "Needs optimization."}

# 3. Router Edge
def should_continue(state: AgentState) -> str:
    if state["approved"]:
        return "human_approval"
    return "coder"

# 4. Graph Construction
builder = StateGraph(AgentState)
builder.add_node("planner", planner_node)
builder.add_node("coder", coder_node)
builder.add_node("reviewer", reviewer_node)

builder.set_entry_point("planner")
builder.add_edge("planner", "coder")
builder.add_edge("coder", "reviewer")
builder.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "coder": "coder",
        "human_approval": END
    }
)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer, interrupt_before=["human_approval"])
```

## Anti-Patterns
- ❌ Unbounded recursion loops without maximum iteration guards.
- ❌ Storing huge non-serializable objects (database connections, open sockets) inside the agent state.
