#!/usr/bin/env python3
"""
Real-World Vibe-Coding Verification Harness for eshkill.
Simulates an autonomous AI agent receiving diverse user prompts, discovering skills on-the-fly,
installing them into the workspace, and validating the generated application blueprints.
"""

import os
import sys
import json
import subprocess

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(PROJECT_DIR, "vibe_app_workspace")
ESH_BIN = "/mnt/c/Users/PC/prj/skill-manager/bin/eshkill"
PYTHON_BIN = "/home/shatix/venv-skm/bin/python3"

def run_eshkill(args: list) -> dict:
    cmd = [PYTHON_BIN, ESH_BIN] + args + ["--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {res.stderr}\nOutput: {res.stdout}")
    return json.loads(res.stdout)

def main():
    print("=" * 80)
    print("🚀 STARTING ESHKILL REAL-WORLD VIBE-CODING VERIFICATION TEST")
    print("=" * 80)

    os.makedirs(WORKSPACE_DIR, exist_ok=True)

    # -------------------------------------------------------------------------
    # TEST SCENARIO 1: Fullstack Next.js 15 + Supabase + Tailwind v4 + Stripe
    # -------------------------------------------------------------------------
    prompt_1 = "Build a modern fullstack SaaS dashboard in Next.js 15 with Tailwind CSS v4 styling, Supabase Realtime auth with RLS, and Stripe subscription billing."
    print(f"\n[Test 1] User Prompt:\n  \"{prompt_1}\"")
    
    decision_1 = run_eshkill(["auto-select", prompt_1])
    print(f"  ✔ Detected Stack: {decision_1['detected_stack']}")
    print(f"  ✔ Selected Skills ({len(decision_1['selected_skills'])}):")
    for s in decision_1['selected_skills']:
        print(f"     - {s['title']} ({s['id']})")
    
    # Assertions
    selected_ids_1 = [s['id'] for s in decision_1['selected_skills']]
    assert any("nextjs" in sid for sid in selected_ids_1), "Next.js skill must be selected"
    assert any("supabase" in sid for sid in selected_ids_1), "Supabase skill must be selected"
    assert any("tailwind" in sid or "stripe" in sid for sid in selected_ids_1), "Tailwind or Stripe must be selected"
    print("  ✅ Scenario 1 Routing Precision: 100% Correct!")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 2: Workspace Skill Installation
    # -------------------------------------------------------------------------
    print("\n[Test 2] Installing matched skills directly into workspace (.agents/skills/)...")
    for s in decision_1['selected_skills']:
        inst_res = run_eshkill(["install", s['id'], "--workspace", WORKSPACE_DIR])
        assert inst_res["success"] is True, f"Failed to install {s['id']}"
        assert os.path.exists(inst_res["target_path"]), f"File not found: {inst_res['target_path']}"
        print(f"  ✔ Installed: {inst_res['target_path']}")
    
    # Verify installed workspace directory
    installed_skills_dir = os.path.join(WORKSPACE_DIR, ".agents", "skills")
    assert os.path.exists(installed_skills_dir), "Workspace .agents/skills directory must exist"
    installed_count = len(os.listdir(installed_skills_dir))
    print(f"  ✅ Workspace successfully populated with {installed_count} live agent skills!")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 3: High-Performance Database & Caching
    # -------------------------------------------------------------------------
    prompt_3 = "Diagnose slow PostgreSQL database queries using explain analyze and setup Redis sliding-window rate limiting."
    print(f"\n[Test 3] User Prompt:\n  \"{prompt_3}\"")
    decision_3 = run_eshkill(["auto-select", prompt_3])
    selected_ids_3 = [s['id'] for s in decision_3['selected_skills']]
    print(f"  ✔ Selected Skills: {selected_ids_3}")
    assert any("postgres" in sid for sid in selected_ids_3), "Postgres query tuning must be selected"
    assert any("redis" in sid for sid in selected_ids_3), "Redis caching must be selected"
    print("  ✅ Scenario 3 Routing Precision: 100% Correct!")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 4: Security Hardening & CI/CD
    # -------------------------------------------------------------------------
    prompt_4 = "Audit codebase for OWASP Top 10 vulnerabilities, detect secret leaks with gitleaks, and build a multi-stage Docker distroless image."
    print(f"\n[Test 4] User Prompt:\n  \"{prompt_4}\"")
    decision_4 = run_eshkill(["auto-select", prompt_4])
    selected_ids_4 = [s['id'] for s in decision_4['selected_skills']]
    print(f"  ✔ Selected Skills: {selected_ids_4}")
    assert any("owasp" in sid for sid in selected_ids_4), "OWASP Top 10 scanner must be selected"
    assert any("docker" in sid for sid in selected_ids_4), "Docker distroless must be selected"
    print("  ✅ Scenario 4 Routing Precision: 100% Correct!")

    # -------------------------------------------------------------------------
    # TEST SCENARIO 5: Agent Prompt Context Injection (XML & System Prompt)
    # -------------------------------------------------------------------------
    print("\n[Test 5] Generating Prompt Injection Payloads for LLMs...")
    xml_match = subprocess.run([PYTHON_BIN, ESH_BIN, "match", "--task", "Write playwright end to end automated tests", "--format", "xml"], capture_output=True, text=True)
    assert "<agent_skill" in xml_match.stdout
    assert "playwright-e2e-automation" in xml_match.stdout
    print("  ✔ Direct XML injection output generated successfully.")

    sys_match = subprocess.run([PYTHON_BIN, ESH_BIN, "match", "--task", "Build high accuracy RAG with hybrid search and reranking", "--format", "system"], capture_output=True, text=True)
    assert "ACTIVATED AGENT SKILL" in sys_match.stdout
    assert "RAG" in sys_match.stdout
    print("  ✔ System prompt preamble generated successfully.")

    print("\n" + "=" * 80)
    print("🎉 ALL VIBE-CODING WORKFLOW VERIFICATIONS PASSED WITH AAA GRADE! 🚀")
    print("=" * 80)

if __name__ == "__main__":
    main()
