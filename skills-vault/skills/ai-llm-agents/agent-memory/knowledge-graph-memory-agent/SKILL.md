---
id: ai-llm-agents.agent-memory.knowledge-graph-memory-agent
name: knowledge-graph-memory-agent
title: Knowledge Graph Associative Memory for Autonomous Agents
category: ai-llm-agents
subcategory: agent-memory
version: 1.2.0
tags:
- knowledge-graph
- agent-memory
- entities
- relations
- graph-rag
- networkx
- persistent-memory
trust_rating: 0.98
estimated_tokens: 1800
description: Construct persistent, graph-structured associative memory systems for
  long-running autonomous agents, enabling relational entity extraction, multi-hop
  contextual traversal, and temporal memory decay.
trigger_patterns:
- agent knowledge graph memory
- entity relation extraction agent memory
- graph rag multi hop associative recall
- persistent agent memory networkx
---

# Knowledge Graph Associative Memory for Autonomous Agents

## Objective
Enable autonomous AI agents to retain, query, and reason over complex relational facts across weeks of interaction using dynamic entity-relation knowledge graphs, multi-hop sub-graph traversal, and semantic similarity search.

## Knowledge Graph Pipeline
```
Agent Conversation / Task Execution
   -> Entity & Relation Extraction (LLM Structured Output: Source, Relation, Target)
   -> Graph Upsert (Nodes = Entities, Edges = Semantic Relations + Timestamps)
   -> Multi-Hop Subgraph Retrieval:
      Query -> Seed Entities -> 2-Hop Neighbor Expansion -> Context Injection
```

## Python Implementation (`agent_memory_graph.py`)
```python
from typing import List, Dict, Any, Tuple
import networkx as nx
from pydantic import BaseModel, Field
import json
import time

class EntityRelation(BaseModel):
    source_entity: str = Field(..., description="Subject entity name")
    relation_type: str = Field(..., description="Action, property, or link (e.g. 'owns', 'depends_on', 'prefers')")
    target_entity: str = Field(..., description="Object entity or property value")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class AgentKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_facts(self, facts: List[EntityRelation]):
        for fact in facts:
            src = fact.source_entity.strip().lower()
            tgt = fact.target_entity.strip().lower()
            self.graph.add_node(src, label=fact.source_entity)
            self.graph.add_node(tgt, label=fact.target_entity)
            self.graph.add_edge(
                src, tgt,
                relation=fact.relation_type,
                timestamp=time.time(),
                confidence=fact.confidence
            )

    def retrieve_context_subgraph(self, seed_entities: List[str], max_hops: int = 2) -> List[str]:
        """Extract associative multi-hop context surrounding the seed entities."""
        subgraph_nodes = set()
        for seed in seed_entities:
            s_clean = seed.strip().lower()
            if s_clean in self.graph:
                subgraph_nodes.add(s_clean)
                # Expand N hops
                lengths = nx.single_source_shortest_path_length(self.graph.to_undirected(), s_clean, cutoff=max_hops)
                subgraph_nodes.update(lengths.keys())

        facts_summary = []
        for u, v, data in self.graph.edges(subgraph_nodes, data=True):
            if v in subgraph_nodes:
                facts_summary.append(f"- ({u}) --[{data['relation']}]--> ({v})")

        return facts_summary
```

## Anti-Patterns
- ❌ Dumping raw unindexed conversation transcripts into flat vector stores without relational linking.
- ❌ Unbounded graph growth without edge pruning or temporal relevance decay.
