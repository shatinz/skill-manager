"""
Lightweight Command Line Interface for askill.
Provides human-friendly ANSI terminal views and zero-noise JSON / XML streams for AI agents.
"""

import sys
import os
import argparse
import json
from typing import Optional

from .vault import VaultConnector
from .search import SmartSkillSearch
from .agent import AgentFormatter
from .propose import ProposalManager
from .server import run_server
from . import __version__

# ANSI Colors
CYAN = "\033[96m"
PURPLE = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def print_banner():
    print(f"""{CYAN}{BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║   ⚡ askill — Lightweight Agentic Skill Vault CLI v{__version__}  ║
    ║   Autonomous Skill Discovery & Prompt Injection Core      ║
    ╚═══════════════════════════════════════════════════════════╝{RESET}""")

def main():
    # Common parent parser for flags like --json and --source
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON for AI agent integration")
    parent_parser.add_argument("--source", type=str, help="Custom local directory or remote URL for skill vault")

    parser = argparse.ArgumentParser(
        prog="askill",
        parents=[parent_parser],
        description="Lightweight CLI and Smart Search Engine for the Public Agentic Skill Vault."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. Search
    p_search = subparsers.add_parser("search", parents=[parent_parser], help="Smart search skills by query or task intent")
    p_search.add_argument("query", nargs="?", default="", help="Search query or task description")
    p_search.add_argument("-c", "--category", help="Filter by category")
    p_search.add_argument("-s", "--subcategory", help="Filter by subcategory")
    p_search.add_argument("-t", "--tag", help="Filter by tag")
    p_search.add_argument("-k", "--top", type=int, default=5, help="Maximum results to return (default: 5)")

    # 2. Match (Direct Agent Injection)
    p_match = subparsers.add_parser("match", parents=[parent_parser], help="Find the single best matching skill and format for prompt injection")
    p_match.add_argument("--task", "-t", required=True, help="Agent task description or prompt to match")
    p_match.add_argument("-f", "--format", choices=["xml", "system", "json", "compact"], default="xml", help="Output injection format (default: xml)")

    # 3. Get / Fetch
    p_get = subparsers.add_parser("get", parents=[parent_parser], help="Fetch and print skill content on-demand without cloning vault")
    p_get.add_argument("skill_id", help="Skill ID (e.g. 'coding.api-design.fastapi-rest-craft') or name")
    p_get.add_argument("-f", "--format", choices=["markdown", "xml", "system", "json"], default="markdown", help="Output format (default: markdown)")
    p_get.add_argument("-o", "--save", help="Save skill content to local file path")

    # 4. List
    p_list = subparsers.add_parser("list", parents=[parent_parser], help="List available skills in the vault")
    p_list.add_argument("-c", "--category", help="Filter by category")
    p_list.add_argument("-t", "--tag", help="Filter by tag")

    # 5. Categories
    p_cat = subparsers.add_parser("categories", parents=[parent_parser], help="Display categories and subcategories tree")

    # 6. Info
    p_info = subparsers.add_parser("info", parents=[parent_parser], help="Display rich metadata and trigger patterns for a skill")
    p_info.add_argument("skill_id", help="Skill ID or name")

    # 7. Propose / PR
    p_prop = subparsers.add_parser("propose", parents=[parent_parser], help="Propose a modification or PR for a living skill")
    p_prop.add_argument("--skill", "-s", required=True, help="Skill ID or name to modify")
    p_prop.add_argument("--file", "-f", help="Path to modified SKILL.md or patch file")
    p_prop.add_argument("--content", "-c", help="Direct string content of proposed modification")
    p_prop.add_argument("--reason", "-r", default="", help="Reason for proposal / changes made")
    p_prop.add_argument("--proposer", "-p", default="agent_worker", help="Proposer ID or GitHub username")
    p_prop.add_argument("--patch-out", help="Path to save generated .patch file")

    # 8. Serve (Daemon)
    p_serve = subparsers.add_parser("serve", parents=[parent_parser], help="Run lightweight local HTTP REST daemon for subagents")
    p_serve.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")

    # 9. Sync
    p_sync = subparsers.add_parser("sync", parents=[parent_parser], help="Force refresh local cache from remote GitHub vault")

    args = parser.parse_args()

    if not args.command:
        if args.json:
            print(json.dumps({"error": "No command provided. Use 'askill --help'."}))
        else:
            print_banner()
            parser.print_help()
        sys.exit(0)

    vault = VaultConnector(vault_path_or_url=args.source)

    # --- COMMAND: SYNC ---
    if args.command == "sync":
        try:
            idx = vault.load_index(force_refresh=True)
            if args.json:
                print(json.dumps({"status": "synced", "total_skills": idx.total_skills, "version": idx.version}))
            else:
                print(f"{GREEN}✔ Successfully synced vault index! Total skills: {idx.total_skills} (v{idx.version}){RESET}")
        except Exception as e:
            if args.json:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"{RED}✖ Sync failed: {e}{RESET}")
            sys.exit(1)
        return

    # --- COMMAND: SEARCH ---
    if args.command == "search":
        index = vault.load_index()
        engine = SmartSkillSearch(index)
        results = engine.search(
            query=args.query,
            category=args.category,
            subcategory=args.subcategory,
            tag=args.tag,
            top_k=args.top
        )

        if args.json:
            print(json.dumps({
                "query": args.query,
                "total_results": len(results),
                "results": [r.to_dict() for r in results]
            }, indent=2))
            return

        print(f"\n{BOLD}🔍 Smart Skill Search Results for: {CYAN}'{args.query}'{RESET} ({len(results)} matches)\n")
        if not results:
            print(f"{YELLOW}No matching skills found. Run 'askill list' to browse the catalog.{RESET}")
            return

        for i, res in enumerate(results, 1):
            s = res.skill
            score_bar = "█" * int(res.score * 10) + "░" * (10 - int(res.score * 10))
            print(f"{GREEN}{i}. {BOLD}{s.title}{RESET} {DIM}({s.id}){RESET}")
            print(f"   {CYAN}Category:{RESET} {s.category} / {s.subcategory}  {PURPLE}Trust:{RESET} {s.trust_rating*100:.0f}%  {YELLOW}Score:{RESET} {res.score:.2f} [{score_bar}]")
            print(f"   {DIM}{s.description}{RESET}")
            if res.matched_triggers:
                print(f"   {GREEN}Matched Trigger:{RESET} {res.matched_triggers[0]}")
            print()

        print(f"{DIM}💡 Tip: Use 'askill get <id>' to read skill, or 'askill match --task \"...\"' to inject.{RESET}\n")

    # --- COMMAND: MATCH ---
    elif args.command == "match":
        index = vault.load_index()
        engine = SmartSkillSearch(index)
        best = engine.find_best_match(args.task)

        if not best:
            if args.json:
                print(json.dumps({"error": "No matching skill found", "task": args.task}))
            else:
                print(f"{RED}No matching skill found for task: '{args.task}'{RESET}")
            sys.exit(1)

        skill_detail = vault.get_skill(best.skill.id)

        if args.json or args.format == "json":
            print(json.dumps(AgentFormatter.to_json_envelope(skill_detail, best), indent=2))
        elif args.format == "xml":
            print(AgentFormatter.to_xml(skill_detail))
        elif args.format == "system":
            print(AgentFormatter.to_system_prompt(skill_detail))
        elif args.format == "compact":
            print(AgentFormatter.to_compact_summary(skill_detail))

    # --- COMMAND: GET ---
    elif args.command == "get":
        try:
            skill = vault.get_skill(args.skill_id)
        except KeyError as e:
            if args.json:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"{RED}✖ {e}{RESET}")
            sys.exit(1)

        if args.save:
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(skill.content)
            if args.json:
                print(json.dumps({"saved_to": args.save, "skill_id": skill.id}))
            else:
                print(f"{GREEN}✔ Saved skill '{skill.id}' to {args.save}{RESET}")
            return

        if args.json or args.format == "json":
            print(json.dumps(AgentFormatter.to_json_envelope(skill), indent=2))
        elif args.format == "xml":
            print(AgentFormatter.to_xml(skill))
        elif args.format == "system":
            print(AgentFormatter.to_system_prompt(skill))
        else:
            print(skill.content)

    # --- COMMAND: LIST ---
    elif args.command == "list":
        index = vault.load_index()
        filtered = [
            s for s in index.skills
            if (not args.category or s.category == args.category) and
               (not args.tag or args.tag in s.tags)
        ]

        if args.json:
            print(json.dumps({"total": len(filtered), "skills": [s.to_dict() for s in filtered]}, indent=2))
            return

        print(f"\n{BOLD}📚 Skill Vault Catalog ({len(filtered)} skills available){RESET}\n")
        current_cat = None
        for s in sorted(filtered, key=lambda x: (x.category, x.subcategory, x.name)):
            if s.category != current_cat:
                current_cat = s.category
                print(f"\n{PURPLE}{BOLD}📁 [{current_cat.upper()}]{RESET}")
            print(f"  • {GREEN}{s.name}{RESET} {DIM}({s.subcategory}){RESET} — {s.title} {DIM}[v{s.version} | Trust: {s.trust_rating*100:.0f}%]{RESET}")
        print()

    # --- COMMAND: CATEGORIES ---
    elif args.command == "categories":
        tree = vault.list_categories()
        if args.json:
            print(json.dumps(tree, indent=2))
            return

        print(f"\n{BOLD}🗂️  Skill Vault Category Hierarchy{RESET}\n")
        for cat, subcats in sorted(tree.items()):
            print(f"{PURPLE}{BOLD}📁 {cat}{RESET}")
            for subcat, skills in sorted(subcats.items()):
                print(f"   └── {CYAN}{subcat}{RESET} ({len(skills)} skills: {DIM}{', '.join(skills[:3])}{'...' if len(skills)>3 else ''}{RESET})")
        print()

    # --- COMMAND: INFO ---
    elif args.command == "info":
        try:
            skill = vault.get_skill(args.skill_id)
        except KeyError as e:
            if args.json:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"{RED}✖ {e}{RESET}")
            sys.exit(1)

        if args.json:
            print(json.dumps(skill.to_dict(), indent=2))
            return

        print(f"\n{BOLD}📋 Skill Metadata: {GREEN}{skill.title}{RESET}\n")
        print(f"• {BOLD}ID:{RESET}           {skill.id}")
        print(f"• {BOLD}Version:{RESET}      v{skill.version}")
        print(f"• {BOLD}Category:{RESET}     {skill.category} -> {skill.subcategory}")
        print(f"• {BOLD}Trust Score:{RESET}  {skill.trust_rating * 100:.0f}% (Community verified)")
        print(f"• {BOLD}Tokens:{RESET}       ~{skill.estimated_tokens} tokens")
        print(f"• {BOLD}Tags:{RESET}         {', '.join(skill.tags)}")
        print(f"• {BOLD}Description:{RESET}  {skill.description}")
        print(f"\n{BOLD}🎯 Trigger Patterns (Auto-Activation):{RESET}")
        for tp in skill.trigger_patterns:
            print(f"  • {CYAN}\"{tp}\"{RESET}")
        print(f"\n{DIM}Source: {skill.source_url}{RESET}\n")

    # --- COMMAND: PROPOSE ---
    elif args.command == "propose":
        proposer = ProposalManager(vault)
        res = proposer.submit_proposal(
            skill_id=args.skill,
            proposer_id=args.proposer,
            proposed_content=args.content,
            file_path=args.file,
            reason=args.reason,
            output_patch=args.patch_out
        )

        if args.json:
            print(json.dumps({
                "success": res.success,
                "message": res.message,
                "proposal_id": res.proposal_id,
                "status": res.status,
                "patch_file": res.patch_file
            }, indent=2))
            return

        if res.success:
            print(f"\n{GREEN}{BOLD}✔ Proposal successfully generated!{RESET}")
            print(f"• Status: {CYAN}{res.status}{RESET}")
            if res.proposal_id:
                print(f"• Proposal ID: {res.proposal_id}")
            if res.patch_file:
                print(f"• Patch Saved: {res.patch_file}")
            print(f"\n{DIM}{res.message}{RESET}\n")
        else:
            print(f"\n{RED}{BOLD}✖ Proposal submission failed:{RESET} {res.message}\n")
            sys.exit(1)

    # --- COMMAND: SERVE ---
    elif args.command == "serve":
        run_server(port=args.port, host=args.host)

if __name__ == "__main__":
    main()
