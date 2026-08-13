"""
Agent context injector and prompt formatter for eshkill.
Formats individual skills or multi-skill routed stacks for LLM system prompts,
agent instructions, tool outputs, and IDE rules.
"""

import re
from typing import Dict, Any, Optional, List
from .models import SkillDetail, SearchResult, RoutingDecision


class AgentFormatter:
    @staticmethod
    def to_xml(skill: SkillDetail) -> str:
        tags_str = ", ".join(skill.tags)
        triggers_str = "\n".join(f"    <pattern>{t}</pattern>" for t in skill.trigger_patterns)

        return f"""<agent_skill id="{skill.id}" name="{skill.name}" version="{skill.version}" category="{skill.category}/{skill.subcategory}">
  <metadata>
    <title>{skill.title}</title>
    <trust_rating>{skill.trust_rating}</trust_rating>
    <estimated_tokens>{skill.estimated_tokens}</estimated_tokens>
    <tags>{tags_str}</tags>
  </metadata>
  <description>
    {skill.description}
  </description>
  <trigger_patterns>
{triggers_str}
  </trigger_patterns>
  <instructions>
{skill.content.strip()}
  </instructions>
</agent_skill>"""

    @staticmethod
    def to_system_prompt(skill: SkillDetail) -> str:
        return f"""================================================================================
ACTIVATED AGENT SKILL: {skill.title} (v{skill.version})
Domain: {skill.category} -> {skill.subcategory} | Trust: {skill.trust_rating * 100:.0f}%
================================================================================

MISSION & CONTEXT:
{skill.description}

OPERATIONAL INSTRUCTIONS & WORKFLOW:
{skill.content.strip()}

================================================================================"""

    @staticmethod
    def to_distilled_blueprint(skill: SkillDetail) -> str:
        """
        Token-compressed executive blueprint for small context windows.
        Extracts core architectural rules, code blocks, and anti-patterns while pruning filler text.
        """
        content = skill.content.strip()
        code_blocks = re.findall(r"```[\w\s]*\n[\s\S]*?\n```", content)
        code_joined = "\n\n".join(code_blocks) if code_blocks else ""

        # Extract bullet points
        bullet_lines = [
            line.strip() for line in content.split("\n")
            if line.strip().startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5."))
        ]
        bullets_joined = "\n".join(bullet_lines[:12])

        return f"""### ⚡ DISTILLED BLUEPRINT: {skill.title.upper()} (`{skill.id}`)
> **Category**: `{skill.category}/{skill.subcategory}` | **Trust**: `{skill.trust_rating*100:.0f}%`
> **Objective**: {skill.description}

#### Core Guidelines & Constraints:
{bullets_joined}

#### Code Implementation Blueprint:
{code_joined}
"""

    @staticmethod
    def to_json_envelope(skill: SkillDetail, search_result: Optional[SearchResult] = None) -> Dict[str, Any]:
        data = {
            "id": skill.id,
            "name": skill.name,
            "title": skill.title,
            "version": skill.version,
            "category": skill.category,
            "subcategory": skill.subcategory,
            "tags": skill.tags,
            "trust_rating": skill.trust_rating,
            "estimated_tokens": skill.estimated_tokens,
            "description": skill.description,
            "instructions_markdown": skill.content,
            "source": skill.source_url
        }
        if search_result:
            data["match_score"] = round(search_result.score, 4)
            data["match_reasons"] = search_result.match_reasons
        return data

    @staticmethod
    def to_compact_summary(skill: SkillDetail) -> str:
        lines = skill.content.strip().split("\n")
        snippet = "\n".join(lines[:15])
        if len(lines) > 15:
            snippet += "\n... [Remaining instructions truncated for token economy. Run 'eshkill get " + skill.id + "' for full text]"

        return f"""📌 **{skill.title}** (`{skill.id}`)
• Category: `{skill.category}/{skill.subcategory}` | Version: `v{skill.version}` | Trust: `{skill.trust_rating*100:.0f}%`
• Summary: {skill.description}

### Key Instructions Preview:
{snippet}
"""

    @staticmethod
    def to_unified_context(decision: RoutingDecision) -> str:
        return decision.unified_payload
