---
id: ai-llm-agents.rag-retrieval.llamaindex-hierarchical-rag
name: llamaindex-hierarchical-rag
title: LlamaIndex Hierarchical Indexing & Sub-Question Query Routing
category: ai-llm-agents
subcategory: rag-retrieval
version: 1.3.0
tags:
- llamaindex
- hierarchical-rag
- sub-question-query-engine
- document-summary
- vector-store
trust_rating: 0.96
estimated_tokens: 1600
description: Construct advanced hierarchical RAG architectures with LlamaIndex using
  parent-child node parsers, recursive retrievers, and SubQuestionQueryEngine query
  routing.
trigger_patterns:
- llamaindex hierarchical node parser
- llamaindex sub question query engine
- llamaindex parent child retriever
- llamaindex auto merging retriever
---

# LlamaIndex Hierarchical Indexing & Sub-Question Query Routing

## Objective
Solve complex multi-part questions across disparate knowledge bases by decoupling small retrieval nodes from larger context chunks using LlamaIndex HierarchicalNodeParser and AutoMergingRetriever.

## Hierarchical Index Blueprint
```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

def build_hierarchical_engine(doc_dir: str):
    documents = SimpleDirectoryReader(doc_dir).load_data()
    
    # 1. Split into hierarchy: 2048 (Parent) -> 512 (Child) -> 128 (Leaf)
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512, 128])
    nodes = node_parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)

    # 2. Index leaf nodes into vector store
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)
    index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)

    # 3. Create AutoMergingRetriever
    base_retriever = index.as_retriever(similarity_top_k=10)
    retriever = AutoMergingRetriever(
        base_retriever, 
        storage_context=storage_context, 
        verbose=True
    )

    query_engine = RetrieverQueryEngine.from_args(retriever)
    return query_engine
```

## Anti-Patterns
- ❌ Feeding small 100-token chunks directly to the LLM without surrounding parent context.
