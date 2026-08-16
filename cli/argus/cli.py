"""
Argus CLI.
The Autonomous Multi-Repository Skill Proxy & Goal-Aware Search Engine.
"""

import sys
import argparse
import json
from typing import Optional
from .proxy import ArgusProxy
from .models import SourceType
from .mcp import ArgusMCPServer
from .server import run_server


def print_banner():
    print("""
    ========================================================
      ARGUS :: Multi-Repository Skill Proxy & Goal Search
      Connecting Agent Goals with Distributed Skill Repos
    ========================================================
    """)


def handle_match(proxy: ArgusProxy, args: argparse.Namespace):
    prompt = " ".join(args.prompt) if isinstance(args.prompt, list) else args.prompt
    if not prompt:
        print("Error: Please provide a prompt or goal. (e.g. argus match 'make a 3d website')")
        sys.exit(1)

    bundle = proxy.match(prompt, top_k=args.top_k)

    if args.json:
        print(json.dumps(bundle.to_dict(), indent=2))
        return

    print(f"\n[ARGUS GOAL MATCHING REPORT]")
    print(f"User Prompt:       \"{bundle.prompt}\"")
    print(f"Synthesized Goal:  {bundle.goal_analysis.primary_goal}")
    print(f"Deliverable Type:  {bundle.goal_analysis.deliverable_type} (Complexity: {bundle.goal_analysis.complexity_level})")
    print(f"Target Domains:    {', '.join(bundle.goal_analysis.target_domains) or 'general'}")
    print(f"Detected Stacks:   {', '.join(bundle.goal_analysis.detected_frameworks) or 'standard web'}")
    print(f"Sources Queried:   {', '.join(bundle.sources_queried)} ({bundle.total_skills_evaluated} skills evaluated)\n")

    print(f"--- Top Complementary Skills for this Goal ({len(bundle.selected_matches)} selected) ---")
    for idx, match in enumerate(bundle.selected_matches, 1):
        s = match.skill
        print(f"\n[{idx}] {s.name}  (Score: {match.composite_rank_score:.2f} | Confidence: {match.confidence.upper()})")
        print(f"    Source:          {s.source_id} ({s.format.value})")
        print(f"    Assigned Role:   {match.goal_role}")
        print(f"    Goal Alignment:  {match.goal_alignment_reason}")
        print(f"    Capabilities:    {', '.join(s.capabilities) if s.capabilities else 'general'}")
        print(f"    Compatibility:   {match.compatibility_score:.2f} | Capability Fit: {match.capability_fit_score:.2f}")

    if args.agent:
        print("\n" + "=" * 60)
        print("COMPILED AGENT INSTRUCTIONS PAYLOAD:")
        print("=" * 60)
        print(bundle.compiled_agent_instructions)


def handle_search(proxy: ArgusProxy, args: argparse.Namespace):
    query = " ".join(args.query) if isinstance(args.query, list) else args.query
    if not query:
        print("Error: Please provide a search query.")
        sys.exit(1)

    results = proxy.search(query, top_k=args.top_k, source_filter=args.source)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    print(f"\nSearch results for \"{query}\" ({len(results)} found):")
    for idx, r in enumerate(results, 1):
        s = r.skill
        print(f"\n[{idx}] {s.name}  (Rank: {r.composite_rank_score:.2f})")
        print(f"    Source:      {s.source_id}")
        print(f"    Category:    {s.category}")
        print(f"    Description: {s.description[:90]}...")
        print(f"    Role:        {r.goal_role}")


def handle_fetch(proxy: ArgusProxy, args: argparse.Namespace):
    content = proxy.fetch(args.skill_id)
    if not content:
        print(f"Error: Skill '{args.skill_id}' not found in any registered repository.")
        sys.exit(1)
    print(content)


def handle_sources(proxy: ArgusProxy, args: argparse.Namespace):
    subcmd = args.sources_subcommand

    if subcmd == "list" or not subcmd:
        sources = proxy.list_sources()
        if args.json:
            print(json.dumps([s.to_dict() for s in sources], indent=2))
            return
        print("\nRegistered Skill Sources & Repositories:")
        print(f"{'ID':<24} {'TYPE':<18} {'STATUS':<8} {'SKILLS':<8} {'LOCATION'}")
        print("-" * 85)
        for s in sources:
            status = "ENABLED" if s.enabled else "DISABLED"
            print(f"{s.id:<24} {s.source_type.value:<18} {status:<8} {s.skill_count:<8} {s.location}")
        print()

    elif subcmd == "add":
        stype_str = args.type or "local_dir"
        try:
            stype = SourceType(stype_str)
        except ValueError:
            stype = SourceType.LOCAL_DIR

        src = proxy.add_source(
            id=args.id,
            name=args.name or args.id,
            source_type=stype,
            location=args.location,
            branch=args.branch
        )
        print(f"Successfully registered source '{src.name}' ({src.id}).")

    elif subcmd == "remove":
        res = proxy.remove_source(args.id)
        if res:
            print(f"Source '{args.id}' removed.")
        else:
            print(f"Source '{args.id}' not found.")

    elif subcmd == "sync":
        print("Synchronizing all enabled sources...")
        res = proxy.sync_all()
        for sid, details in res.items():
            status_icon = "✓" if details["success"] else "✗"
            print(f"[{status_icon}] {sid}: {details['message']}")


def handle_doctor(proxy: ArgusProxy, args: argparse.Namespace):
    print_banner()
    print("[RUNNING ARGUS SYSTEM DOCTOR]")
    sources = proxy.list_sources()
    print(f"- Registered Sources: {len(sources)}")
    total_skills = len(proxy.get_all_skills())
    print(f"- Total Indexed Skills: {total_skills}")
    
    for s in sources:
        print(f"  * [{s.id}] {s.name} ({s.source_type.value}) -> {s.skill_count} skills")
    
    print("\n✓ Argus Proxy is ready for AI Agent requests.")


def main():
    parser = argparse.ArgumentParser(
        prog="argus",
        description="Argus — Multi-Repository Skill Proxy & Goal-Aware Search Engine for AI Agents"
    )
    subparsers = parser.add_subparsers(dest="command", help="Argus commands")

    # match
    match_parser = subparsers.add_parser("match", help="Match & rank best skills for a user prompt goal")
    match_parser.add_argument("prompt", nargs="+", help="User prompt (e.g. 'make a 3d website')")
    match_parser.add_argument("--top-k", type=int, default=5, help="Number of complementary skills to match")
    match_parser.add_argument("--json", action="store_true", help="Output JSON result")
    match_parser.add_argument("--agent", action="store_true", help="Print compiled agent payload")

    # search
    search_parser = subparsers.add_parser("search", help="Cross-repository keyword & capability search")
    search_parser.add_argument("query", nargs="+", help="Keywords to search")
    search_parser.add_argument("--top-k", type=int, default=10, help="Max results")
    search_parser.add_argument("--source", type=str, help="Filter by source ID")
    search_parser.add_argument("--json", action="store_true", help="Output JSON")

    # fetch
    fetch_parser = subparsers.add_parser("fetch", help="Retrieve full markdown instruction for a skill")
    fetch_parser.add_argument("skill_id", help="Skill identifier (e.g. 'threejs-scene-craft')")

    # sources
    sources_parser = subparsers.add_parser("sources", aliases=["source"], help="Manage external skill repositories and vaults")
    src_sub = sources_parser.add_subparsers(dest="sources_subcommand")
    
    src_sub.add_parser("list", help="List configured sources")
    
    add_src = src_sub.add_parser("add", help="Add a new repository or vault")
    add_src.add_argument("--id", required=True, help="Unique ID")
    add_src.add_argument("--name", help="Human readable name")
    add_src.add_argument("--type", choices=["local_dir", "git_repo", "cursor_rules", "builtin_vault"], default="local_dir")
    add_src.add_argument("--location", required=True, help="Path or Git URL")
    add_src.add_argument("--branch", help="Git branch name")

    rem_src = src_sub.add_parser("remove", help="Remove a source")
    rem_src.add_argument("id", help="Source ID to remove")

    src_sub.add_parser("sync", help="Sync/pull all remote sources")
    sources_parser.add_argument("--json", action="store_true", help="Output JSON")

    # sync
    subparsers.add_parser("sync", help="Synchronize all remote and local sources")

    # mcp
    subparsers.add_parser("mcp", help="Run MCP JSON-RPC Server over STDIO")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Run HTTP REST API server")
    serve_parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host binding")

    # doctor
    subparsers.add_parser("doctor", help="Check Argus installation and repository health")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    proxy = ArgusProxy()

    if args.command == "match":
        handle_match(proxy, args)
    elif args.command == "search":
        handle_search(proxy, args)
    elif args.command == "fetch":
        handle_fetch(proxy, args)
    elif args.command in ("sources", "source"):
        handle_sources(proxy, args)
    elif args.command == "sync":
        res = proxy.sync_all()
        for sid, details in res.items():
            status_icon = "✓" if details["success"] else "✗"
            print(f"[{status_icon}] {sid}: {details['message']}")
    elif args.command == "mcp":
        server = ArgusMCPServer(proxy)
        server.run_stdio()
    elif args.command == "serve":
        run_server(host=args.host, port=args.port, proxy=proxy)
    elif args.command == "doctor":
        handle_doctor(proxy, args)


if __name__ == "__main__":
    main()
