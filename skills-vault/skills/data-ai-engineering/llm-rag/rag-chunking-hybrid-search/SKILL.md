---
id: data-ai-engineering.llm-rag.rag-chunking-hybrid-search
name: rag-chunking-hybrid-search
title: RAG Chunking, Hybrid Vector-BM25 Search & Reranking
category: data-ai-engineering
subcategory: llm-rag
version: 1.3.0
tags:
- rag
- llm
- embeddings
- bm25
- hybrid-search
- reranker
- vector-db
trust_rating: 0.98
estimated_tokens: 1650
description: Build high-accuracy Retrieval-Augmented Generation (RAG) pipelines using
  semantic chunking, Reciprocal Rank Fusion (RRF) hybrid search, cross-encoder rerankers,
  and context compression.
trigger_patterns:
- build rag pipeline
- hybrid search vector bm25
- semantic chunking rag
- cross-encoder reranking
- optimize rag accuracy
---

# RAG Chunking, Hybrid Vector-BM25 Search & Reranking

## Complete RAG Architecture Flow
1. **Semantic Chunking**: Split by document headings, paragraph boundaries, or embedding distance spikes rather than naive token counts.
2. **Dense Vector Search**: Compute embedding cosine similarity for semantic concepts.
3. **Sparse Lexical Search**: Run BM25 for exact keyword matches, code tokens, and acronyms.
4. **Reciprocal Rank Fusion (RRF)**:
   $$	ext{RRF Score}(d) = \sum_{m \in \{dense, sparse\}} rac{1}{60 + 	ext{rank}_m(d)}$$
5. **Cross-Encoder Reranker**: Pass top 25 RRF candidates through BGE-Reranker or Cohere Rerank to pick top 5.
