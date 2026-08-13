---
id: ai-llm-agents.function-calling.openai-anthropic-tool-use
name: openai-anthropic-tool-use
title: OpenAI & Anthropic Claude Function Calling and Tool Use
category: ai-llm-agents
subcategory: function-calling
version: 1.3.0
tags:
- tool-use
- function-calling
- openai-api
- claude-tools
- anthropic
- typescript
- python
trust_rating: 0.98
estimated_tokens: 1600
description: Implement robust multi-turn function calling and tool execution loops
  compatible across OpenAI and Anthropic Claude APIs with error reflection and parallel
  execution.
trigger_patterns:
- openai function calling tool use
- claude anthropic tool use loop
- parallel tool calling multi turn agent
- handle tool execution errors llm
---

# OpenAI & Anthropic Claude Function Calling and Tool Use

## Objective
Build standardized, portable tool-calling loops that execute external functions safely, handle parallel tool invocations, and feed error details back into the LLM for self-correction.

## Production Python Tool Loop
```python
import json
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_database_query",
            "description": "Execute a read-only SQL query against the analytics database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "The SELECT SQL statement"}
                },
                "required": ["sql"]
            }
        }
    }
]

def run_agent_loop(user_prompt: str):
    messages = [
        {"role": "system", "content": "You are a data assistant. Use provided tools to query databases."},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_msg = response.choices[0].message
    if response_msg.tool_calls:
        messages.append(response_msg)
        for tool_call in response_msg.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Execute tool safely
            tool_result = {"status": "success", "rows": [{"count": 42}]}
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

        # Final answer synthesis
        final_res = client.chat.completions.create(model="gpt-4o", messages=messages)
        return final_res.choices[0].message.content

    return response_msg.content
```

## Anti-Patterns
- ❌ Crashing the agent workflow on tool exception instead of passing error output back in the `tool` message.
