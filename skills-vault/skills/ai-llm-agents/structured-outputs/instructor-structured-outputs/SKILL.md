---
id: ai-llm-agents.structured-outputs.instructor-structured-outputs
name: instructor-structured-outputs
title: Instructor & Pydantic Structured Output Validation
category: ai-llm-agents
subcategory: structured-outputs
version: 1.4.0
tags:
- instructor
- pydantic
- structured-outputs
- validation
- openai
- anthropic
trust_rating: 0.99
estimated_tokens: 1550
description: Extract validated, type-safe data structures from LLMs using Instructor
  with Pydantic v2 validation models, automated retry loops, and streamable partial
  schemas.
trigger_patterns:
- instructor pydantic structured output
- validate llm json response pydantic
- instructor retry validation error
- instructor streaming partial models
---

# Instructor & Pydantic Structured Output Validation

## Objective
Guarantee 100% schema-compliant structured data extraction from LLMs with automatic validation error feedback and self-correction loops using Instructor and Pydantic v2.

## Blueprint (`extract_entities.py`)
```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
from typing import List

client = instructor.from_openai(OpenAI())

class ActionItem(BaseModel):
    task: str = Field(..., description="Actionable task item")
    assignee: str = Field(..., description="Person responsible")
    priority: str = Field(..., description="High, Medium, or Low")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid = {"High", "Medium", "Low"}
        if v.capitalize() not in valid:
            raise ValueError(f"Priority must be one of {valid}")
        return v.capitalize()

class MeetingExtraction(BaseModel):
    summary: str = Field(..., description="High level meeting summary")
    action_items: List[ActionItem] = Field(default_factory=list)

def extract_meeting_data(transcript: str) -> MeetingExtraction:
    return client.chat.completions.create(
        model="gpt-4o",
        response_model=MeetingExtraction,
        max_retries=3,
        messages=[
            {"role": "system", "content": "Extract structured action items from transcript."},
            {"role": "user", "content": transcript}
        ]
    )
```

## Anti-Patterns
- ❌ Parsing LLM responses with manual regex or `json.loads()` without schema validation.
