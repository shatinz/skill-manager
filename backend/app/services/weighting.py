from dataclasses import dataclass
from typing import List, Tuple
import math
from app.config import settings
from app.services.clustering import ProposalCluster
from app.services.vector_store import TextSimilarity

@dataclass
class ClusterScore:
    raw_trust_sum: float
    redundancy_bonus: float
    disruptiveness: float
    effective_weight: float
    reasoning: str

def score_cluster(cluster: ProposalCluster, current_content: str) -> ClusterScore:
    """Nonlinear scoring for a proposal cluster."""
    raw_trust_sum = sum(p.proposer.trust_score if p.proposer else 0.0 for p in cluster.proposals)
    
    # Redundancy MULTIPLIES trust, not adds to it
    redundancy_bonus = raw_trust_sum * (1.0 + math.log(cluster.cluster_size) * settings.redundancy_trust_multiplier)
    
    # Disruptiveness: cosine distance between cluster centroid and current live content
    sim_engine = TextSimilarity()
    sim = sim_engine.compute_similarity(cluster.centroid_text, current_content)
    disruptiveness = 1.0 - sim
    
    # Dampening
    if cluster.avg_trust < settings.disruptiveness_trust_threshold:
        dampening = settings.disruptiveness_low_trust_dampener
    else:
        dampening = settings.disruptiveness_high_trust_dampener
        
    # Disruptive changes from low-trust proposers get dampened MORE than from high-trust
    effective_weight = redundancy_bonus * (1.0 - disruptiveness * dampening)
    
    reasoning = (
        f"Score calculated based on raw_trust_sum={raw_trust_sum:.3f}, "
        f"cluster_size={cluster.cluster_size}, "
        f"redundancy_bonus={redundancy_bonus:.3f}, "
        f"disruptiveness={disruptiveness:.3f}, "
        f"dampening={dampening:.3f} (avg_trust={cluster.avg_trust:.3f}). "
        f"Final effective weight: {effective_weight:.3f}."
    )
    
    return ClusterScore(
        raw_trust_sum=raw_trust_sum,
        redundancy_bonus=redundancy_bonus,
        disruptiveness=disruptiveness,
        effective_weight=effective_weight,
        reasoning=reasoning
    )

def rank_clusters(clusters: List[ProposalCluster], current_content: str) -> List[Tuple[ProposalCluster, ClusterScore]]:
    """Score and sort clusters descending by effective_weight."""
    scored = []
    for cluster in clusters:
        score = score_cluster(cluster, current_content)
        scored.append((cluster, score))
        
    scored.sort(key=lambda x: x[1].effective_weight, reverse=True)
    return scored

def resolve_conflicts(ranked: List[Tuple[ProposalCluster, ClusterScore]]) -> List[Tuple[ProposalCluster, ClusterScore]]:
    """When clusters conflict, keep the higher-weighted one."""
    resolved = []
    dropped_indices = set()
    
    for cluster, score in ranked:
        if cluster.cluster_index in dropped_indices:
            continue
            
        resolved.append((cluster, score))
        
        # Drop all conflicting clusters as this one has higher weight
        for conflict_idx in cluster.is_conflicting_with:
            dropped_indices.add(conflict_idx)
            
    return resolved
