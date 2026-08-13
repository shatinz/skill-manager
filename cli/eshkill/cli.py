"""
Command Line Interface for eshkill — The npm/apt for AI Agent Skills.
Provides human-friendly ANSI terminal views, fast developer tools, and zero-noise JSON streams for AI agents.
"""

import sys
import os
import argparse
import json
from typing import Optional

from .vault import VaultConnector
from .search import SmartSkillSearch
from .router import AutoRouter
from .installer import SkillInstaller
from .agent import AgentFormatter
from .propose import ProposalManager
from .mcp import MCPServer
from .server import run_server
from . import __version__

# ANSI Color Codes
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
    ║   ⚡ eshkill — The Package Manager for Agent Skills v{__version__}  ║
    ║   Autonomous Skill Routing & Prompt Injection Engine      ║
    ╚═══════════════════════════════════════════════════════════╝{RESET}""")


def run_test_router_suite(router: AutoRouter, verbose: bool = True):
    """Built-in test suite verifying router accuracy across diverse vibe coding scenarios."""
    test_cases = [
        {
            "prompt": "build a real-time chat with supabase and nextjs 15 and tailwind styling",
            "expected_contains": ["nextjs-15-app-router", "tailwind-v4-tokens", "supabase-realtime-auth-rls", "postgres-query-tuning"]
        },
        {
            "prompt": "create a fastapi backend with pydantic schemas and postgres database",
            "expected_contains": ["fastapi-production-craft", "postgres-query-tuning"]
        },
        {
            "prompt": "deploy a dockerized microservices app on aws using terraform modules",
            "expected_contains": ["docker-multi-stage-distroless", "terraform-aws-modules"]
        },
        {
            "prompt": "build a high-accuracy RAG pipeline with hybrid search and vector embeddings",
            "expected_contains": ["rag-chunking-hybrid-search"]
        },
        {
            "prompt": "write end-to-end browser tests with playwright and unit tests with pytest",
            "expected_contains": ["playwright-e2e-automation", "pytest-mocking-mastery"]
        },
        {
            "prompt": "secure our api against owasp vulnerabilities, prevent jwt leaks and sanitize user input",
            "expected_contains": ["owasp-top10-scanner", "jwt-oauth2-secureshop", "input-sanitization-xss-defense"]
        }
    ]

    print(f"\n{BOLD}🧪 Running eshkill Auto-Router Validation Suite ({len(test_cases)} test cases)...{RESET}\n")
    passed = 0
    for i, tc in enumerate(test_cases, 1):
        decision = router.route(tc["prompt"], max_skills=3)
        selected_ids = [s.id for s in decision.selected_skills]
        selected_names = [s.name for s in decision.selected_skills]

        # Check if at least some of the expected skills were captured
        matches = [exp for exp in tc["expected_contains"] if any(exp in sid for sid in selected_ids) or any(exp in sname for sname in selected_names)]
        is_success = len(matches) >= 1

        if is_success:
            passed += 1
            print(f"  {GREEN}✔ [{i}/{len(test_cases)}] PASSED{RESET}: \"{tc['prompt'][:60]}...\"")
        else:
            print(f"  {RED}✖ [{i}/{len(test_cases)}] FAILED{RESET}: \"{tc['prompt'][:60]}...\"")

        print(f"     {CYAN}Detected Stack:{RESET} {', '.join(decision.detected_stack)}")
        print(f"     {PURPLE}Selected Skills ({len(decision.selected_skills)}):{RESET} {', '.join(selected_names)}")
        print()

    print(f"{BOLD}Result:{RESET} {GREEN if passed == len(test_cases) else YELLOW}{passed}/{len(test_cases)} tests passed.{RESET}\n")
    return passed == len(test_cases)


def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON for AI agent integration")
    parent_parser.add_argument("--source", type=str, help="Custom local directory or remote URL for skill vault")

    prog_name = "eshkill"
    if sys.argv and len(sys.argv) > 0:
        base = os.path.basename(sys.argv[0])
        if "askill" in base:
            prog_name = "askill"
        elif "eshkill" in base:
            prog_name = "eshkill"

    parser = argparse.ArgumentParser(
        prog=prog_name,
        parents=[parent_parser],
        description=f"{prog_name} — The Package Manager and Smart Router for AI Agent Skills."
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

    # 2. Auto-Select / Router (Multi-skill Vibe Coding)
    p_auto = subparsers.add_parser("auto-select", aliases=["router"], parents=[parent_parser], help="Autonomous vibe-coding router: selects 1-3 complementary skills and compiles unified context")
    p_auto.add_argument("prompt", help="Raw user vibe-coding prompt (e.g. 'build a real-time chat with supabase and nextjs 15')")
    p_auto.add_argument("-m", "--max-skills", type=int, default=3, help="Maximum complementary skills to orchestrate (default: 3)")
    p_auto.add_argument("--mode", choices=["full", "condensed", "minimal"], default="full", help="Prompt condensation mode for token budgeting (default: full)")
    p_auto.add_argument("--max-tokens", type=int, default=None, help="Optional strict token budget limit")
    p_auto.add_argument("-f", "--format", choices=["unified", "json", "summary", "cursor", "windsurf", "copilot", "claude"], default="unified", help="Output format (default: unified)")

    # 3. Match (Single Skill Injection)
    p_match = subparsers.add_parser("match", parents=[parent_parser], help="Find the single best matching skill and format for prompt injection")
    p_match.add_argument("--task", "-t", required=True, help="Agent task description or prompt to match")
    p_match.add_argument("-f", "--format", choices=["xml", "system", "distilled", "json", "compact"], default="xml", help="Output injection format (default: xml)")

    # 4. Install
    p_inst = subparsers.add_parser("install", parents=[parent_parser], help="Install a skill into workspace (.agents/skills/), IDE rules (.cursor/, .windsurfrules, .github/), or global")
    p_inst.add_argument("skill_id", help="Skill ID or name to install")
    p_inst.add_argument("-w", "--workspace", nargs="?", const=".", default=None, help="Install into workspace (.agents/skills/<id>/SKILL.md) [optional custom workspace path]")
    p_inst.add_argument("-g", "--global", dest="is_global", action="store_true", help="Install into global config (~/.gemini/config/skills/)")
    p_inst.add_argument("--ide", choices=["workspace", "cursor", "windsurf", "copilot", "claude", "all"], default="workspace", help="Target IDE rule format (default: workspace)")
    p_inst.add_argument("--temp", action="store_true", help="Install to ephemeral temp directory and print contents")
    p_inst.add_argument("-d", "--dir", help="Custom workspace directory")

    # 4b. Install-Stack (One-command Auto-Route & Multi-IDE Install)
    p_inst_stack = subparsers.add_parser("install-stack", parents=[parent_parser], help="Auto-route prompt, select skills, and install entire stack into workspace & IDEs")
    p_inst_stack.add_argument("prompt", help="Vibe-coding project description or architecture prompt")
    p_inst_stack.add_argument("-m", "--max-skills", type=int, default=3, help="Max skills to install (default: 3)")
    p_inst_stack.add_argument("--ide", choices=["workspace", "cursor", "windsurf", "copilot", "claude", "all"], default="all", help="Target IDE rule format (default: all)")
    p_inst_stack.add_argument("-d", "--dir", help="Custom workspace directory")

    # 5. Get / Fetch
    p_get = subparsers.add_parser("get", parents=[parent_parser], help="Fetch and print skill content on-demand without cloning vault")
    p_get.add_argument("skill_id", help="Skill ID (e.g. 'coding.api-design.fastapi-rest-craft') or name")
    p_get.add_argument("-f", "--format", choices=["markdown", "xml", "system", "json"], default="markdown", help="Output format (default: markdown)")
    p_get.add_argument("-o", "--save", help="Save skill content to local file path")

    # 6. List
    p_list = subparsers.add_parser("list", parents=[parent_parser], help="List available skills in the vault")
    p_list.add_argument("-c", "--category", help="Filter by category")
    p_list.add_argument("-t", "--tag", help="Filter by tag")

    # 7. Categories
    p_cat = subparsers.add_parser("categories", parents=[parent_parser], help="Display categories and subcategories tree")

    # 8. Info
    p_info = subparsers.add_parser("info", parents=[parent_parser], help="Display rich metadata and trigger patterns for a skill")
    p_info.add_argument("skill_id", help="Skill ID or name")

    # 9. Propose / PR
    p_prop = subparsers.add_parser("propose", parents=[parent_parser], help="Propose a modification or PR for a living skill")
    p_prop.add_argument("--skill", "-s", required=True, help="Skill ID or name to modify")
    p_prop.add_argument("--file", "-f", help="Path to modified SKILL.md or patch file")
    p_prop.add_argument("--content", "-c", help="Direct string content of proposed modification")
    p_prop.add_argument("--reason", "-r", default="", help="Reason for proposal / changes made")
    p_prop.add_argument("--proposer", "-p", default="agent_worker", help="Proposer ID or GitHub username")
    p_prop.add_argument("--patch-out", help="Path to save generated .patch file")

    # 10. MCP (Model Context Protocol)
    p_mcp = subparsers.add_parser("mcp", parents=[parent_parser], help="Launch Model Context Protocol (MCP) server for Claude / Cursor / Antigravity via stdio")

    # 11. Serve (Daemon)
    p_serve = subparsers.add_parser("serve", parents=[parent_parser], help="Run lightweight local HTTP REST daemon for subagents")
    p_serve.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")

    # 12. Sync
    p_sync = subparsers.add_parser("sync", parents=[parent_parser], help="Force refresh local cache from remote GitHub vault")

    # 13. Test Router
    p_test_router = subparsers.add_parser("test-router", parents=[parent_parser], help="Run automated test suite for vibe coding auto-router")

    args = parser.parse_args()

    if not args.command:
        if args.json:
            print(json.dumps({"error": "No command provided. Use 'eshkill --help'."}))
        else:
            print_banner()
            parser.print_help()
        sys.exit(0)

    vault = VaultConnector(vault_path_or_url=args.source)

    # --- COMMAND: MCP ---
    if args.command == "mcp":
        server = MCPServer(vault)
        server.run_stdio()
        return

    # --- COMMAND: SYNC ---
    elif args.command == "sync":
        try:
            idx = vault.load_index(force_refresh=True)
            if args.json:
                print(json.dumps({"status": "synced", "total_skills": idx.total_skills, "version": idx.version}))
            else:
                print(f"{GREEN}✔ Successfully synced skill vault index! Total skills: {idx.total_skills} (v{idx.version}){RESET}")
        except Exception as e:
            if args.json:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"{RED}✖ Sync failed: {e}{RESET}")
            sys.exit(1)
        return

    # --- COMMAND: AUTO-SELECT / ROUTER ---
    elif args.command in ("auto-select", "router"):
        router = AutoRouter(vault)
        decision = router.route(
            args.prompt,
            max_skills=args.max_skills,
            max_tokens=args.max_tokens,
            mode=args.mode
        )

        if args.json or args.format == "json":
            print(json.dumps(decision.to_dict(), indent=2))
            return

        if args.format == "summary":
            print(f"\n{BOLD}⚡ Auto-Routed Stack for:{RESET} {CYAN}'{decision.prompt}'{RESET}\n")
            print(f"• {BOLD}Detected Stack:{RESET}   {', '.join(decision.detected_stack)}")
            print(f"• {BOLD}Selected Skills:{RESET}  {', '.join(s.name for s in decision.selected_skills)}")
            print(f"• {BOLD}Est. Tokens:{RESET}      ~{decision.total_estimated_tokens} tokens")
            print(f"\n{BOLD}Routing Reasons:{RESET}")
            for r in decision.routing_reasons:
                print(f"  • {r}")
            print()
            return

        if args.format == "cursor":
            print(AutoRouter.to_cursor_rules(decision))
            return
        elif args.format == "windsurf":
            print(AutoRouter.to_windsurf_rules(decision))
            return
        elif args.format == "copilot":
            print(AutoRouter.to_copilot_instructions(decision))
            return
        elif args.format == "claude":
            print(AutoRouter.to_claude_instructions(decision))
            return

        # Default: Unified Context Payload
        print(decision.unified_payload)

    # --- COMMAND: TEST-ROUTER ---
    elif args.command == "test-router":
        router = AutoRouter(vault)
        success = run_test_router_suite(router)
        if not success:
            sys.exit(1)

    # --- COMMAND: INSTALL ---
    elif args.command == "install":
        installer = SkillInstaller(vault)
        mode = args.ide if args.ide != "workspace" else "workspace"
        if args.is_global:
            mode = "global"
        elif args.temp:
            mode = "temp"

        ws_dir = args.dir
        if not ws_dir and isinstance(args.workspace, str) and args.workspace != ".":
            ws_dir = args.workspace

        result = installer.install(
            skill_id_or_name=args.skill_id,
            mode=mode,
            workspace_dir=ws_dir
        )

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
            if not result.success:
                sys.exit(1)
            return

        if result.success:
            print(f"\n{GREEN}{BOLD}✔ Skill successfully installed!{RESET}")
            print(f"• Skill ID: {CYAN}{result.skill_id}{RESET}")
            print(f"• Mode:     {PURPLE}{result.mode}{RESET}")
            print(f"• Location: {BOLD}{result.target_path}{RESET}\n")
        else:
            print(f"\n{RED}{BOLD}✖ Installation failed:{RESET} {result.message}\n")
            sys.exit(1)

    # --- COMMAND: INSTALL-STACK ---
    elif args.command == "install-stack":
        installer = SkillInstaller(vault)
        router = AutoRouter(vault)
        decision = router.route(args.prompt, max_skills=args.max_skills)
        results = installer.install_stack(decision, mode=args.ide, workspace_dir=args.dir)

        if args.json:
            print(json.dumps({
                "prompt": args.prompt,
                "installed_count": len(results),
                "detected_stack": decision.detected_stack,
                "selected_skills": [s.id for s in decision.selected_skills],
                "results": [r.to_dict() for r in results]
            }, indent=2))
            return

        print(f"\n{BOLD}⚡ Auto-Routed & Installed Stack for:{RESET} {CYAN}'{args.prompt}'{RESET}\n")
        print(f"• {BOLD}Detected Stack:{RESET}   {', '.join(decision.detected_stack)}")
        print(f"• {BOLD}Active Skills:{RESET}    {', '.join(s.name for s in decision.selected_skills)}")
        print(f"• {BOLD}Target IDE(s):{RESET}    {PURPLE}{args.ide}{RESET}\n")
        for res in results:
            status_icon = f"{GREEN}✔{RESET}" if res.success else f"{RED}✖{RESET}"
            print(f"  {status_icon} [{res.skill_id}] -> {res.target_path}")
        print()

    # --- COMMAND: SEARCH ---
    elif args.command == "search":
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
            print(f"{YELLOW}No matching skills found. Run 'eshkill list' to browse the catalog.{RESET}")
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

        print(f"{DIM}💡 Tip: Use 'eshkill get <id>' to read skill, or 'eshkill auto-select \"<prompt>\"' to orchestrate stack.{RESET}\n")

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
        elif args.format == "distilled":
            print(AgentFormatter.to_distilled_blueprint(skill_detail))
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
            print(json.dumps(res.to_dict(), indent=2))
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
