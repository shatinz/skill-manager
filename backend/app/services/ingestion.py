import httpx
import yaml
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models import Skill, Version
from app.schemas import SkillCreate
from app.services.vector_store import vector_store

def parse_skill_from_github(repo_url: str, category: str) -> Dict[str, Any]:
    raw_url = repo_url.replace("github.com", "raw.githubusercontent.com").replace("/tree/", "/").replace("/blob/", "/")
    if not raw_url.endswith(".md"):
        raw_url = raw_url.rstrip("/") + "/main/SKILL.md"

    try:
        response = httpx.get(raw_url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch skill from GitHub: {str(e)}")
    
    text = response.text
    content = text
    name = repo_url.split("/")[-1]
    description = ""
    trigger_conditions = ""

    # parse frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                name = frontmatter.get("name", name)
                description = frontmatter.get("description", description)
                trigger_conditions = frontmatter.get("trigger_conditions", trigger_conditions)
                content = parts[2].strip()
            except yaml.YAMLError:
                pass

    return {
        "name": name,
        "description": description,
        "category": category,
        "content": content,
        "source_repos": [repo_url],
        "trigger_conditions": trigger_conditions
    }

def ingest_skill(db: Session, skill_data: Dict[str, Any]) -> Tuple[Skill, Version]:
    # Check for near duplicates using vector_store
    existing_skills = db.query(Skill).all()
    if existing_skills:
        texts = [s.description for s in existing_skills]
        similars = vector_store.find_similar(skill_data.get("description", ""), texts)
        # We perform the check, though we do not necessarily block ingestion here.

    skill = Skill(
        name=skill_data["name"],
        description=skill_data["description"],
        category=skill_data["category"],
        source_repos=skill_data.get("source_repos", []),
        trigger_conditions=skill_data.get("trigger_conditions", "")
    )
    db.add(skill)
    db.flush()

    version = Version(
        skill_id=skill.id,
        content=skill_data["content"]
    )
    db.add(version)
    db.flush()

    skill.current_version_id = version.id
    db.commit()
    db.refresh(skill)
    db.refresh(version)

    return skill, version
