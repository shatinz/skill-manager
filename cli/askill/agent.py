"""
Agent context injector and prompt formatter for askill.
Formats skills for direct inclusion into LLM system prompts, agent instructions, or tool outputs.
"""

from typing import Dict, Any, Optional
from .models import SkillDetail, SearchResult

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
        # Extract first 2 sections or ~500 characters of instructions
        lines = skill.content.strip().split("\n")
        snippet = "\n".join(lines[:15])
        if len(lines) > 15:
            snippet += "\n... [Remaining instructions truncated for token economy. Run 'askill get " + skill.id + "' for full text]"
        
        return f"""📌 **{skill.title}** (`{skill.id}`)
• Category: `{skill.category}/{skill.subcategory}` | Version: `v{skill.version}` | Trust: `{skill.trust_rating*100:.0f}%`
• Summary: {skill.description}

### Key Instructions Preview:
{snippet}
"""
