from dataclasses import dataclass
from typing import List
from app.models import Proposal
from app.services.vector_store import TextSimilarity

@dataclass
class ProposalCluster:
    proposals: List[Proposal]
    centroid_text: str
    avg_trust: float
    cluster_size: int
    is_conflicting_with: List[int]
    cluster_index: int = 0

def cluster_proposals(proposals: List[Proposal], threshold: float) -> List[ProposalCluster]:
    """Cluster similar proposals together based on TF-IDF cosine similarity."""
    if not proposals:
        return []
    
    similarity_engine = TextSimilarity()
    
    texts = [p.proposed_content for p in proposals]
    
    # TextSimilarity.cluster_texts returns a list of lists of indices
    raw_clusters = similarity_engine.cluster_texts(texts, threshold)
    
    clusters = []
    for idx, indices in enumerate(raw_clusters):
        cluster_props = [proposals[i] for i in indices]
        
        # Use the first proposal in the cluster as the centroid text for simplicity
        centroid_text = cluster_props[0].proposed_content
        
        total_trust = sum(p.proposer.trust_score if p.proposer else 0.0 for p in cluster_props)
        avg_trust = total_trust / len(cluster_props) if cluster_props else 0.0
        
        clusters.append(ProposalCluster(
            proposals=cluster_props,
            centroid_text=centroid_text,
            avg_trust=avg_trust,
            cluster_size=len(cluster_props),
            is_conflicting_with=[],
            cluster_index=idx
        ))
    
    # Conflict detection: Two clusters conflict if their centroids have similarity < threshold
    # but modify overlapping sections. For our current heuristic, we assume all different clusters
    # with similarity < threshold might be conflicting if they touch the same areas.
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            sim = similarity_engine.compute_similarity(clusters[i].centroid_text, clusters[j].centroid_text)
            if sim < threshold:
                clusters[i].is_conflicting_with.append(j)
                clusters[j].is_conflicting_with.append(i)
                
    return clusters
