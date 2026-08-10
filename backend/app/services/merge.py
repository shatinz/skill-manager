import json
import difflib
from typing import List, Tuple
from app.services.clustering import ProposalCluster
from app.services.weighting import ClusterScore
from app.config import settings

def synthesize_merge(current_content: str, ranked_clusters: List[Tuple[ProposalCluster, ClusterScore]], skill_name: str) -> str:
    """LLM merge synthesis based on ranked proposal clusters."""
    if not ranked_clusters:
        return current_content
        
    if settings.llm_provider == 'openai':
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        
        clusters_info = []
        for cluster, score in ranked_clusters:
            clusters_info.append({
                "weight": score.effective_weight,
                "proposed_text": cluster.centroid_text,
                "reasoning": score.reasoning
            })
            
        prompt = (
            f"You are synthesizing changes for the skill: {skill_name}.\n"
            f"Current content:\n{current_content}\n\n"
            f"Proposed changes (ranked by effective weight):\n{json.dumps(clusters_info, indent=2)}\n\n"
            "Produce a merged version where high-weight changes have strong influence and low-weight changes are folded in lightly or dropped.\n"
            "Return JSON with 'merged_content' and 'merge_reasoning' fields."
        )
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a code/text merging assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('merged_content', current_content)
        
    else:
        # Mock provider: deterministically apply diffs based on highest weight
        merged = current_content
        for cluster, _ in ranked_clusters:
            # Find highest trust proposal in this cluster
            best_prop = max(cluster.proposals, key=lambda p: p.proposer.trust_score if p.proposer else 0.0)
            target = best_prop.proposed_content
            
            # Simple diff patching logic using difflib sequence matcher
            matcher = difflib.SequenceMatcher(None, merged.splitlines(keepends=True), target.splitlines(keepends=True))
            new_lines = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    new_lines.extend(merged.splitlines(keepends=True)[i1:i2])
                elif tag in ('replace', 'insert'):
                    new_lines.extend(target.splitlines(keepends=True)[j1:j2])
                # Delete is ignored (left intact or handled implicitly depending on desired behavior)
            merged = "".join(new_lines)
            
        return merged
