#!/usr/bin/env python3
"""
Public Agentic Skill Vault Generator & Index Compiler for eshkill
Generates rich, battle-tested, production-grade SKILL.md documents organized by 9 core categories.
Compiles everything into vault.json and README.md.
"""

import os
import json
import yaml
import shutil
import sys

# Ensure skills_data can be imported when running generate_vault.py directly
VAULT_DIR = os.path.dirname(os.path.abspath(__file__))
if VAULT_DIR not in sys.path:
    sys.path.insert(0, VAULT_DIR)

from skills_data import ALL_SKILLS

SKILLS_DIR = os.path.join(VAULT_DIR, "skills")
SKILLS_DATA = ALL_SKILLS

def generate_vault():
    print(f"[*] Compiling eshkill Agentic Skill Vault ({len(SKILLS_DATA)} skills)...")
    
    # Wipe SKILLS_DIR cleanly to ensure no orphaned old directories
    if os.path.exists(SKILLS_DIR):
        shutil.rmtree(SKILLS_DIR)
    os.makedirs(SKILLS_DIR, exist_ok=True)

    vault_index = {
        "version": "2.0.0",
        "total_skills": len(SKILLS_DATA),
        "categories": {},
        "skills": []
    }

    categories_tree = {}

    for item in SKILLS_DATA:
        cat = item["category"]
        subcat = item["subcategory"]
        skill_name = item["name"]
        
        target_dir = os.path.join(SKILLS_DIR, cat, subcat, skill_name)
        os.makedirs(target_dir, exist_ok=True)
        
        skill_file = os.path.join(target_dir, "SKILL.md")
        
        # Frontmatter
        frontmatter = {
            "id": item["id"],
            "name": item["name"],
            "title": item["title"],
            "category": item["category"],
            "subcategory": item["subcategory"],
            "version": item["version"],
            "tags": item["tags"],
            "trust_rating": item["trust_rating"],
            "estimated_tokens": item["estimated_tokens"],
            "description": item["description"],
            "trigger_patterns": item["trigger_patterns"]
        }
        
        yaml_header = yaml.dump(frontmatter, sort_keys=False).strip()
        full_document = f"---\n{yaml_header}\n---\n\n{item['content'].strip()}\n"
        
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(full_document)
            
        # Index entry
        index_entry = {
            "id": item["id"],
            "name": item["name"],
            "title": item["title"],
            "category": item["category"],
            "subcategory": item["subcategory"],
            "version": item["version"],
            "tags": item["tags"],
            "trust_rating": item["trust_rating"],
            "estimated_tokens": item["estimated_tokens"],
            "description": item["description"],
            "trigger_patterns": item["trigger_patterns"],
            "relative_path": f"skills/{cat}/{subcat}/{skill_name}/SKILL.md"
        }
        vault_index["skills"].append(index_entry)
        
        # Update categories tree
        if cat not in categories_tree:
            categories_tree[cat] = {}
        if subcat not in categories_tree[cat]:
            categories_tree[cat][subcat] = []
        categories_tree[cat][subcat].append(item["name"])

    vault_index["categories"] = categories_tree

    # Write vault.json index
    index_path = os.path.join(VAULT_DIR, "vault.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(vault_index, f, indent=2)

    # Generate Vault README.md
    readme_path = os.path.join(VAULT_DIR, "README.md")
    readme_content = f"""# 🏛️ Public Agentic Skill Vault for eshkill

> The production-grade registry and repository of reusable agentic capabilities, instructions, workflows, and blueprints for autonomous AI agents.

## 📊 Overview
- **Total Skills**: {len(SKILLS_DATA)}
- **Categories**: {len(categories_tree)}
- **Subcategories**: {sum(len(v) for v in categories_tree.values())}

## 🗂️ Categories & Taxonomy

"""
    for cat, subcats in sorted(categories_tree.items()):
        readme_content += f"### 📁 `{cat}`\n"
        for subcat, skill_list in sorted(subcats.items()):
            readme_content += f"- **`{subcat}`** ({len(skill_list)} skills)\n"
            for sk in skill_list:
                readme_content += f"  - [`{sk}`](skills/{cat}/{subcat}/{sk}/SKILL.md)\n"
        readme_content += "\n"

    readme_content += """## ⚡ Using with the `askill` CLI

AI agents and developers can discover, fetch, and match skills on-demand without cloning or prompt bloat:

```bash
# Smart search across the vault by task intent
askill search "build production nextjs 15 app with server actions"

# Match and inject relevant skill directly into agent system prompt
askill match --task "write playwright e2e tests for checkout flow" --format system

# Output skill in structured XML format
askill match --task "optimize slow postgres queries with explain buffers" --format xml

# Fetch full skill markdown on demand
askill get web-frameworks.react-fullstack.nextjs-15-app-router

# Propose an improvement or patch
askill propose --skill nextjs-15-app-router --file patch.diff --reason "Added React 19 useActionState support"
```

## 🤝 Contributing
Every skill is a living, battle-tested document. Propose updates via PR or submit proposals through the `askill propose` CLI.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[+] Successfully generated {len(SKILLS_DATA)} skills, vault.json, and README.md in {VAULT_DIR}!")

if __name__ == "__main__":
    generate_vault()
