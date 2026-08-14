from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import yaml

from app.database import get_db
from app.models import ProposerProfile, Skill
from app.schemas import SeedResponse, IngestRequest, IngestResponse
from app.services.ingestion import parse_skill_from_github, ingest_skill
from app.services.trust import update_trust_score

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

@router.post("/seed", response_model=SeedResponse)
def seed_database(db: Session = Depends(get_db)):
    # Create simulated proposer profiles (Agents + Humans)
    profiles = [
        ProposerProfile(
            id="agent:claude-3-5-sonnet",
            display_name="Autonomous Agent: Claude 3.5 Sonnet",
            is_agent=True,
            account_created_at=datetime.utcnow() - timedelta(days=365),
            project_stars=2500,
            contribution_history=[{"outcome": "accepted"} for _ in range(12)]
        ),
        ProposerProfile(
            id="agent:antigravity-sentinel",
            display_name="Autonomous Agent: Antigravity Sentinel",
            is_agent=True,
            account_created_at=datetime.utcnow() - timedelta(days=200),
            project_stars=1800,
            contribution_history=[{"outcome": "accepted"} for _ in range(8)]
        ),
        ProposerProfile(
            id="veteran_dev",
            display_name="Veteran Dev",
            is_agent=False,
            account_created_at=datetime.utcnow() - timedelta(days=730),
            project_stars=5000,
            contribution_history=[{"outcome": "accepted"} for _ in range(15)]
        ),
        ProposerProfile(
            id="moderate_dev",
            display_name="Moderate Dev",
            is_agent=False,
            account_created_at=datetime.utcnow() - timedelta(days=180),
            project_stars=200,
            contribution_history=[{"outcome": "accepted"} for _ in range(3)]
        ),
        ProposerProfile(
            id="newcomer_dev",
            display_name="Newcomer Dev",
            is_agent=False,
            account_created_at=datetime.utcnow() - timedelta(days=7),
            project_stars=0,
            contribution_history=[]
        )
    ]
    for p in profiles:
        existing = db.query(ProposerProfile).filter_by(id=p.id).first()
        if not existing:
            db.add(p)
            db.flush()
            update_trust_score(db, p.id)

    db.commit()

    # 10 Curated Skills spanning diverse categories with multi-paragraph instructions
    skills_data = [
        {
            "name": "FastAPI Auto-CRUD",
            "description": "Generates complete FastAPI CRUD endpoints from SQLAlchemy models.",
            "category": "code-generation",
            "content": "This skill automatically inspects a SQLAlchemy declarative base model and generates fully functional FastAPI CRUD routers. It handles dependency injection for database sessions, Pydantic schema validation for request and response models, and common error handling like 404s for missing items.\n\nTo use this, simply point it at your models.py file. It will parse the AST and produce a routers/ directory containing a file for each model. It ensures that standard RESTful conventions are followed (GET, POST, PUT, DELETE).\n\nAdditionally, it can be customized to include pagination for GET endpoints and role-based access control annotations if your project requires them.",
            "source_repos": ["https://github.com/demo/fastapi-crud"],
            "trigger_conditions": "When user asks to generate endpoints for models"
        },
        {
            "name": "Pytest Fixture Generator",
            "description": "Creates pytest fixtures based on class definitions.",
            "category": "testing",
            "content": "This skill writes boilerplate pytest fixtures to instantiate classes or setup test environments. It analyzes the __init__ methods of your classes and attempts to provide mock objects or sensible defaults for each argument.\n\nIt can handle complex nested dependencies by recursively generating fixtures for the arguments required by the target class. It supports both function-scoped and session-scoped fixtures based on user preference.\n\nUse this skill when you have a large codebase with many interdependent components and need to rapidly bootstrap a test suite.",
            "source_repos": ["https://github.com/demo/pytest-gen"],
            "trigger_conditions": "When writing tests for new classes"
        },
        {
            "name": "Kubernetes Deployment Template",
            "description": "Generates Kubernetes Deployment and Service YAMLs.",
            "category": "devops",
            "content": "This skill simplifies the creation of Kubernetes manifests. Given a Docker image name and port, it generates standard Deployment and Service YAML configurations.\n\nIt includes best practices such as health checks (liveness and readiness probes), resource requests and limits, and standard labeling schemes. It can also configure basic ingress rules if requested.\n\nThis is ideal for quickly deploying microservices without having to manually write boilerplate YAML.",
            "source_repos": ["https://github.com/demo/k8s-templater"],
            "trigger_conditions": "When user asks to deploy to kubernetes"
        },
        {
            "name": "Pandas Data Profiler",
            "description": "Generates a comprehensive data profile using pandas.",
            "category": "data-analysis",
            "content": "This skill takes a CSV file or a pandas DataFrame and generates a statistical profile of the data. It calculates summary statistics (mean, median, standard deviation) for numerical columns and frequency counts for categorical columns.\n\nIt also identifies missing values, potential outliers, and highly correlated features. It can output this profile as a nicely formatted markdown report or a JSON object for further processing.\n\nThis is invaluable for initial exploratory data analysis (EDA) before building machine learning models.",
            "source_repos": ["https://github.com/demo/pandas-profiler"],
            "trigger_conditions": "When exploring a new dataset"
        },
        {
            "name": "SQL Injection Scanner",
            "description": "Scans Python code for potential SQL injection vulnerabilities.",
            "category": "security",
            "content": "This skill analyzes Python source code, particularly database interaction logic, to find potential SQL injection flaws. It looks for string formatting or concatenation used directly in SQL execution methods.\n\nIt flags these instances and provides remediation advice, suggesting the use of parameterized queries or prepared statements via ORMs like SQLAlchemy or query builders.\n\nRun this skill as part of a pre-commit hook or CI pipeline to catch security vulnerabilities early in the development lifecycle.",
            "source_repos": ["https://github.com/demo/sql-scanner"],
            "trigger_conditions": "When writing raw SQL queries"
        },
        {
            "name": "Asyncio Refactor",
            "description": "Converts synchronous IO code to asynchronous using asyncio.",
            "category": "refactoring",
            "content": "This skill identifies synchronous network requests (e.g., using the requests library) or file IO operations and refactors them to use asynchronous equivalents (e.g., aiohttp, aiofiles).\n\nIt handles the introduction of async/await keywords, refactors surrounding functions to be coroutines, and sets up the asyncio event loop execution where necessary.\n\nThis is particularly useful for optimizing web scrapers, API clients, or any application that is heavily IO-bound.",
            "source_repos": ["https://github.com/demo/async-refactor"],
            "trigger_conditions": "When optimizing IO bound code"
        },
        {
            "name": "Docstring Generator",
            "description": "Generates Google-style docstrings for Python functions and classes.",
            "category": "documentation",
            "content": "This skill automatically generates comprehensive docstrings for Python code. It analyzes function signatures, type hints, and return types to populate the Args and Returns sections.\n\nIt uses an LLM to infer a brief description of the function's purpose based on its implementation. It supports Google, NumPy, and Sphinx docstring styles.\n\nKeeping documentation up-to-date is easier with this skill, as it can be run iteratively as the code evolves.",
            "source_repos": ["https://github.com/demo/doc-gen"],
            "trigger_conditions": "When writing new functions"
        },
        {
            "name": "Memory Leak Detector",
            "description": "Profiles Python memory usage to find leaks.",
            "category": "debugging",
            "content": "This skill uses tools like objgraph and tracemalloc to identify memory leaks in long-running Python applications. It takes snapshots of memory allocations over time and compares them to find objects that are not being garbage collected.\n\nIt can pinpoint the exact line of code where the leaked objects were allocated and trace their reference graphs to help identify the root cause.\n\nUse this when your application's memory consumption grows steadily over time.",
            "source_repos": ["https://github.com/demo/mem-leak"],
            "trigger_conditions": "When debugging memory issues"
        },
        {
            "name": "React Component Generator",
            "description": "Generates functional React components with hooks.",
            "category": "code-generation",
            "content": "This skill generates boilerplate for React functional components. Given a component name and a list of props, it creates a structured file with prop types (or TypeScript interfaces).\n\nIt can optionally include common hooks like useState or useEffect if requested. It also generates a corresponding CSS module or styled-component template.\n\nThis speeds up UI development by automating the repetitive task of setting up new components.",
            "source_repos": ["https://github.com/demo/react-gen"],
            "trigger_conditions": "When building UI components"
        },
        {
            "name": "Log Analyzer",
            "description": "Parses and analyzes server logs for errors and anomalies.",
            "category": "devops",
            "content": "This skill parses standard web server logs (e.g., Nginx, Apache) or application logs. It aggregates error rates, identifies the most common error types, and detects sudden spikes in traffic or error responses.\n\nIt can extract structured data from semi-structured log lines using regex patterns and output the results as a time-series dataset.\n\nThis is useful for post-incident analysis or setting up basic observability.",
            "source_repos": ["https://github.com/demo/log-analyzer"],
            "trigger_conditions": "When investigating production issues"
        }
    ]

    created_skills = []
    for data in skills_data:
        existing = db.query(Skill).filter_by(name=data["name"]).first()
        if not existing:
            skill, version = ingest_skill(db, data)
            created_skills.append(skill)

    # Seed Empirical Execution Evidence (Real-World Benchmarks)
    from app.models import ExecutionEvidence, ExecutionOutcome
    if db.query(ExecutionEvidence).count() == 0:
        sample_evidences = [
            {
                "skill_name": "FastAPI Auto-CRUD",
                "repo": "Enterprise Analytics Gateway",
                "ecosystem": "python",
                "task": "Generate async CRUD endpoints for order models",
                "outcome": ExecutionOutcome.SUCCESS,
                "duration": 45.0,
                "model": "Claude 3.5 Sonnet",
                "cost": 0.04,
                "tokens": 4200,
                "version": "v1.0.0",
                "notes": "Endpoints generated cleanly with full Pydantic v2 schemas."
            },
            {
                "skill_name": "Asyncio Refactor",
                "repo": "Rust compiler plugin",
                "ecosystem": "rust",
                "task": "Fix CI compiler plugin broken async build",
                "outcome": ExecutionOutcome.SUCCESS,
                "duration": 180.0,  # 3 min
                "model": "GPT-5",
                "cost": 0.19,
                "tokens": 14500,
                "version": "v4.1.0",
                "notes": "Resolved non-blocking channel deadlock and updated tokio worker spawns."
            },
            {
                "skill_name": "Pytest Fixture Generator",
                "repo": "FastAPI Payment Service",
                "ecosystem": "python",
                "task": "Fix CI flaky tests and database mock fixtures",
                "outcome": ExecutionOutcome.SUCCESS,
                "duration": 85.0,
                "model": "GPT-4o",
                "cost": 0.08,
                "tokens": 7800,
                "version": "v1.2.0",
                "notes": "Isolated SQLite in-memory fixtures per test function."
            },
            {
                "skill_name": "Kubernetes Deployment Template",
                "repo": "Cloud Ingress Gateway",
                "ecosystem": "devops",
                "task": "Generate Zero-Downtime Helm Manifests with ArgoCD sync",
                "outcome": ExecutionOutcome.SUCCESS,
                "duration": 110.0,
                "model": "GPT-5",
                "cost": 0.12,
                "tokens": 11200,
                "version": "v1.3.0",
                "notes": "Added rolling update strategy with maxSurge=1 and readiness probes."
            },
            {
                "skill_name": "SQL Injection Scanner",
                "repo": "Legacy Fintech Billing Core",
                "ecosystem": "python",
                "task": "Audit raw SQL statements and remediate parameter binding",
                "outcome": ExecutionOutcome.SUCCESS,
                "duration": 60.0,
                "model": "Claude 3.5 Sonnet",
                "cost": 0.06,
                "tokens": 6100,
                "version": "v1.0.0",
                "notes": "Detected 3 unparameterized queries and replaced with SQLAlchemy text(:val)."
            }
        ]

        for ev in sample_evidences:
            target_skill = db.query(Skill).filter(Skill.name == ev["skill_name"]).first()
            if target_skill:
                evidence = ExecutionEvidence(
                    skill_id=target_skill.id,
                    version_id=target_skill.current_version_id,
                    skill_version_tag=ev["version"],
                    repository_name=ev["repo"],
                    ecosystem=ev["ecosystem"],
                    task_description=ev["task"],
                    outcome=ev["outcome"],
                    duration_seconds=ev["duration"],
                    model_name=ev["model"],
                    cost_usd=ev["cost"],
                    tokens_used=ev["tokens"],
                    feedback_notes=ev["notes"]
                )
                db.add(evidence)
        db.commit()

    return {
        "skills_created": len(created_skills),
        "skills": created_skills
    }

@router.post("/ingest", response_model=IngestResponse)
def ingest_from_github(request: IngestRequest, db: Session = Depends(get_db)):
    try:
        skill_data = parse_skill_from_github(request.repo_url, request.category)
        skill, version = ingest_skill(db, skill_data)
        return {
            "skill_id": skill.id,
            "name": skill.name,
            "category": skill.category,
            "version_id": version.id,
            "message": "Successfully ingested skill"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
