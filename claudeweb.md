# Argus project state (claudeweb.md)

## 2026-11-12 audit and optimization
- Repo: C:\Users\PC\prj\skill-manager, branch Argus.
- Baseline: 14 configured sources, 1,427 indexed skills; 95/95 tests passing.
- Reproduction: generic Python skill-search-ranking query detected neither Python nor retrieval goal; top five repeated e2e-testing-patterns from two sources and included an unrelated frontend optimization skill.
- Implemented: search/retrieval goal ontology; Python framework recognition; Unicode-aware cross-source skill-name deduplication at top-K selection; reject empty matches; precompute per-document term frequencies for BM25; recognize secure filesystem/path-traversal requests.
- Regression tests: tests/test_argus_ranker_regressions.py adds seven tests. Full suite: 102/102 passed.
- Performance on 1,427 packages and 3 fixed queries: original BM25 loop median 10.374ms vs cached 4.271ms (7 repetitions, same checksum 598.57579). End-to-end warm match median 11.64ms (25 repetitions). These are microbenchmarks, not user-task success claims.
- Known limitation: metadata-based relevance still admits domain-adjacent but mismatched skills (e.g. Hono on a FastAPI query and OAuth on safe-path task). Semantic reranking and framework compatibility checks merit further dedicated evaluations.
- Independent A/B evaluation: C:\Users\PC\prj\_work\argus-ab-20261112\; both AGY arms use gemini-3.8-flash-medium, same inventory API requirements; Argus arm has a generated skill manifest plus fetched FastAPI skill; outside-workspace evaluator has 16 tests.
- AGY runner: first Conductor AGY call stalled and was aborted; direct CLI with the installed supported model can write files. The PC connector currently defaults to unsupported gemini-3.8-flash alias. Test direct CLI before relying on unattended runs.
- Git: stage only verified task files; .claudeweb contains generated run state and should remain untracked.

## Argus telemetry
[ARGUS TELEMETRY LOG]
Timestamp: 2026-11-12
Action: argus match / rank_candidates / BM25 scoring
Command / Tool: python -m argus.cli match "Audit and optimize Python multi-repository skill search..." --json
Error / Bottleneck: irrelevant duplicate testing skills and frontend match; repeated BM25 term-frequency dictionaries
Root Cause Analysis: missing goal ontology/framework; cross-source top-K had no name-level dedup; term frequencies recomputed per query and candidate
Remediation / Workaround Applied: add specific ontology and framework, dedupe selection, cache BM25 term frequencies; regression suite passing

