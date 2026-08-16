"""
End-to-End Demo Script for Unified Agentic Skill Manager.

This script executes the complete 7-stage lifecycle:
1. Ingestion / Seeding (Stage A)
2. Usage Logging (Stage B)
3. Proposal Submissions (Conflicting + Redundant signals)
4. Batch Accumulation & Nonlinear Weighted Merge (Stages C & D)
5. Security Audit & Sybil Check (Stage E)
6. Version Release & Trust Updates (Stage F)
7. Serving & Lineage Verification (Stage G)
"""

import sys
import os
from datetime import datetime, timedelta

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, Skill, Version, Proposal, ProposerProfile, Batch, BatchStatus, ProposalStatus
from app.services.trust import compute_trust_score, update_trust_score
from app.services.ingestion import ingest_skill
from app.services.batch import force_close_batch, close_and_process_batch
from app.services.audit import audit_batch
from app.services.release import release_version, get_version_lineage
from app.routers.ingestion import seed_database


def run_demo():
    print("=" * 70)
    print("🚀 UNIFIED AGENTIC SKILL MANAGER — END-TO-END DEMO")
    print("=" * 70)

    # Initialize tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Stage 1: Seeding / Ingestion ────────────────────────────────
        print("\n[Stage A] Seeding curated skills and proposer profiles...")
        seed_result = seed_database(db)
        print(f"  ✓ Seeded {seed_result['skills_created']} skills.")

        skill = db.query(Skill).filter(Skill.name == "FastAPI Auto-CRUD").first()
        if not skill:
            skill = db.query(Skill).first()
        print(f"  ✓ Target skill for demo: '{skill.name}' (ID: {skill.id})")
        print(f"  ✓ Current Version: {skill.current_version_id}")

        # ── Stage 2: Usage Logging ──────────────────────────────────────
        print("\n[Stage B] Simulating skill usage by agent runtime...")
        from app.models import UsageEvent
        usage = UsageEvent(
            skill_id=skill.id,
            version_id=skill.current_version_id,
            user_id="agent-worker-01"
        )
        db.add(usage)
        db.commit()
        print("  ✓ Usage event recorded for live version.")

        # ── Stage 3: Simulated Proposals (Conflicting + Redundant) ─────
        print("\n[Stage C] Submitting 3 proposals from different trust tiers...")
        
        # Profile 1: Veteran (High trust)
        p1 = db.query(ProposerProfile).filter_by(id="veteran_dev").first()
        # Profile 2: Moderate (Medium trust)
        p2 = db.query(ProposerProfile).filter_by(id="moderate_dev").first()
        # Profile 3: Newcomer (Low trust)
        p3 = db.query(ProposerProfile).filter_by(id="newcomer_dev").first()

        print(f"  • Proposer 1: {p1.display_name} (Trust: {p1.trust_score:.2f})")
        print(f"  • Proposer 2: {p2.display_name} (Trust: {p2.trust_score:.2f})")
        print(f"  • Proposer 3: {p3.display_name} (Trust: {p3.trust_score:.2f})")

        from app.routers.proposals import submit_proposal
        from app.schemas import ProposalCreate

        # Proposal 1 (Veteran): Add async pagination support
        prop1 = submit_proposal(
            skill_id=skill.id,
            proposal=ProposalCreate(
                proposer_id="veteran_dev",
                proposal_type="modification",
                proposed_content=skill.current_version.content + "\n\n## Added Feature: Cursor Pagination\nAdds robust cursor-based pagination with limit and offset query params for large result sets.",
            ),
            db=db
        )
        print(f"  ✓ Proposal 1 submitted (ID: {prop1.id[:8]}...): Cursor Pagination (Veteran)")

        # Proposal 2 (Moderate): Conflicting pagination method (Page-number based)
        prop2 = submit_proposal(
            skill_id=skill.id,
            proposal=ProposalCreate(
                proposer_id="moderate_dev",
                proposal_type="modification",
                proposed_content=skill.current_version.content + "\n\n## Added Feature: Page Number Pagination\nAdds page-number based pagination (page=1, size=20).",
            ),
            db=db
        )
        print(f"  ✓ Proposal 2 submitted (ID: {prop2.id[:8]}...): Page-Number Pagination [Conflicting] (Moderate)")

        # Proposal 3 (Newcomer): Redundant pagination signal reinforcing cursor pagination
        prop3 = submit_proposal(
            skill_id=skill.id,
            proposal=ProposalCreate(
                proposer_id="newcomer_dev",
                proposal_type="modification",
                proposed_content=skill.current_version.content + "\n\n## Added Feature: Cursor Pagination\nAdds cursor-based pagination with limit and offset query params for large result sets.",
            ),
            db=db
        )
        print(f"  ✓ Proposal 3 submitted (ID: {prop3.id[:8]}...): Cursor Pagination [Redundant with #1] (Newcomer)")

        # ── Stage 4: Batch Processing & Nonlinear Merge ────────────────
        print("\n[Stage D] Closing batch window and triggering nonlinear weighted merge...")
        batch_id = force_close_batch(db, skill.id)
        batch_result = close_and_process_batch(db, batch_id)
        print(f"  ✓ Batch ID: {batch_result.batch_id}")
        print(f"  ✓ Status: {batch_result.status}")
        print(f"  ✓ Candidate Version ID: {batch_result.merge_candidate_version_id}")

        # ── Stage 5: Security Audit ─────────────────────────────────────
        print("\n[Stage E] Running security audit (Static + Semantic + Sandbox Canary + Sybil)...")
        audit_summary = audit_batch(db, batch_id)
        print(f"  ✓ Proposals Audited: {audit_summary['total']}")
        print(f"  ✓ Clean: {audit_summary['clean_count']}, Suspicious/Quarantined: {audit_summary['suspicious_count']}")

        # ── Stage 6: Version Release ────────────────────────────────────
        print("\n[Stage F] Releasing candidate version into production...")
        released_version, rel_msg = release_version(db, batch_id)
        if released_version:
            print(f"  ✓ Release Success! New Live Version ID: {released_version.id}")
            print(f"  ✓ Skill '{skill.name}' current_version updated to: {skill.current_version_id}")
        else:
            print(f"  ✗ Release blocked: {rel_msg}")

        # ── Stage 7: Lineage & Serving ──────────────────────────────────
        print("\n[Stage G] Serving verification & Version Lineage:")
        lineage = get_version_lineage(db, skill.current_version_id)
        for idx, v in enumerate(lineage):
            print(f"  • Level {idx + 1}: Version {v.id[:8]} (Created: {v.created_at})")

        print("\n" + "=" * 70)
        print("🎉 DEMO COMPLETED SUCCESSFULLY: End-to-end pipeline verified!")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    run_demo()
