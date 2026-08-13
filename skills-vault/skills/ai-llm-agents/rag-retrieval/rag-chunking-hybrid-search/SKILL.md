---
id: ai-llm-agents.rag-retrieval.rag-chunking-hybrid-search
name: rag-chunking-hybrid-search
title: RAG Context Chunking, Hybrid Vector & Sparse BM25 Search
category: ai-llm-agents
subcategory: rag-retrieval
version: 1.5.0
tags:
- rag
- embeddings
- bm25
- hybrid-search
- reciprocal-rank-fusion
- reranking
trust_rating: 0.99
estimated_tokens: 1750
description: Construct high-precision Retrieval-Augmented Generation (RAG) pipelines
  with structure-aware chunking, hybrid dense vector and sparse BM25 retrieval, Reciprocal
  Rank Fusion (RRF), and cross-encoder reranking.
trigger_patterns:
- implement hybrid search rag
- bm25 vector dense sparse retrieval
- reciprocal rank fusion rrf rag
- cohere reranker rag pipeline
- semantic chunking markdown headers
---

# RAG Context Chunking, Hybrid Vector & Sparse BM25 Search

## Objective
Maximize retrieval accuracy and eliminate LLM hallucinations in RAG systems by combining dense semantic embeddings with sparse keyword matching (BM25), merged through Reciprocal Rank Fusion (RRF) and validated via cross-encoder rerankers.

## Architectural Pipeline
```
Raw Documents 
  -> Structure-Aware Chunking (Header/Paragraph semantics with overlap)
  -> Dual Indexing (Dense Vector Store + Sparse BM25 Inverted Index)
  -> User Query
  -> Parallel Query Execution (Dense Retrieval Top-K + Sparse BM25 Top-K)
  -> Reciprocal Rank Fusion (RRF Score = 1 / (60 + rank))
  -> Cross-Encoder / Cohere Rerank (Top-N final passages)
  -> Context-Injected LLM Generation
```

## Production Python Implementation
```python
from typing import List, Dict, Any
import numpy as np

def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]], 
    bm25_results: List[Dict[str, Any]], 
    k: int = 60,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    # Combines vector and sparse rankings into a unified score
    scores: Dict[str, float] = {}
    doc_lookup: Dict[str, Dict[str, Any]] = {}

    for rank, doc in enumerate(vector_results):
        doc_id = doc["id"]
        doc_lookup[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

    for rank, doc in enumerate(bm25_results):
        doc_id = doc["id"]
        doc_lookup[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

    sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    ranked_output = []
    for doc_id, score in sorted_docs[:top_n]:
        item = doc_lookup[doc_id].copy()
        item["rrf_score"] = score
        ranked_output.append(item)

    return ranked_output
```

## Anti-Patterns
- ❌ Fixed-size character chunking that splits sentences, tables, or code blocks in half.
- ❌ Vector-only retrieval for domain terms, product SKUs, or exact error codes (always augment with BM25).
