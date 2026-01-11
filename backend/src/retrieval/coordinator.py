from loguru import logger
from typing import List, Dict, Optional
from src.models.memory_result import MemoryResult

class RetrievalCoordinator:
    """
    Coordinates and merges results from multiple retrieval paths 
    (semantic, keyword, graph, temporal).
    """

    @staticmethod
    def merge_results(
        semantic_results: List[MemoryResult] = None,
        keyword_results: List[MemoryResult] = None,
        graph_results: List[MemoryResult] = None,
        temporal_results: List[MemoryResult] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> List[MemoryResult]:
        """
        Merges results from different retrievers, handles deduplication, 
        and re-ranks based on normalized weighted scores.
        
        This implementation ensures that scores are properly combined and
        provenance (paths_found) is maintained across all paths.
        """
        # Default weights if not provided
        if not weights:
            weights = {
                "semantic": 0.4,
                "keyword": 0.2,
                "graph": 0.3,
                "temporal": 0.1
            }

        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        norm_weights = {k: v / total_weight for k, v in weights.items()}

        merged: Dict[str, MemoryResult] = {}
        
        def process_path(results: List[MemoryResult], path_type: str):
            if not results:
                return
            
            weight = norm_weights.get(path_type, 0.0)
            for res in results:
                # Use a safe ID or content-based hash if ID is missing
                mem_id = res.id or str(hash(res.content))
                
                if mem_id in merged:
                    existing = merged[mem_id]
                    # Principle: Incremental score boost from multiple paths
                    # Score = existing_score + (new_score * path_weight)
                    # This rewards memories found via multiple retrieval paths
                    existing.score = min(1.0, existing.score + (res.score * weight))
                    
                    # Merge paths found (deduplicated)
                    if res.paths_found:
                        for path in res.paths_found:
                            if path not in existing.paths_found:
                                existing.paths_found.append(path)
                    
                    # Update layer description
                    if path_type not in existing.layer:
                        existing.layer += f"+{path_type}"
                else:
                    # Initialize with weighted score
                    res.score = res.score * weight
                    res.layer = f"{res.layer} ({path_type})"
                    merged[mem_id] = res

        process_path(semantic_results or [], "semantic")
        process_path(keyword_results or [], "keyword")
        process_path(graph_results or [], "graph")
        process_path(temporal_results or [], "temporal")

        # Sort and return
        final_results = sorted(merged.values(), key=lambda x: x.score, reverse=True)
        return final_results

    @staticmethod
    def apply_reciprocal_rank_fusion(
        result_sets: List[List[MemoryResult]], 
        k: int = 60
    ) -> List[MemoryResult]:
        """
        Implementation of Reciprocal Rank Fusion (RRF) for merging ranked lists.
        Score(d) = sum(1 / (k + rank(d, r))) for r in result_sets
        """
        rrf_scores: Dict[str, float] = {}
        memory_map: Dict[str, MemoryResult] = {}

        for results in result_sets:
            for rank, res in enumerate(results, start=1):
                if res.id not in rrf_scores:
                    rrf_scores[res.id] = 0.0
                    memory_map[res.id] = res
                
                rrf_scores[res.id] += 1.0 / (k + rank)

        # Update scores and sort
        final_results = []
        for mem_id, score in rrf_scores.items():
            mem = memory_map[mem_id]
            mem.score = score # RRF scores are usually normalized later if needed
            final_results.append(mem)

        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results

