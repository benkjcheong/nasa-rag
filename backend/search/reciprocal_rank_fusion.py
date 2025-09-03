from typing import List, Dict, Tuple
import numpy as np

class ReciprocalRankFusion:
    def __init__(self, k: int = 60):
        self.k = k
    
    def fuse_rankings(self, rankings: Dict[str, List[Tuple]], weights: Dict[str, float] = None) -> List[Tuple]:
        """
        Fuse multiple rankings using Reciprocal Rank Fusion
        
        Args:
            rankings: Dict with method names as keys and ranked results as values
            weights: Optional weights for each ranking method
        """
        if weights is None:
            weights = {method: 1.0 for method in rankings.keys()}
        
        # Collect all unique items
        all_items = set()
        for ranking in rankings.values():
            all_items.update([item[0] for item in ranking])
        
        # Calculate RRF scores
        rrf_scores = {}
        for item in all_items:
            score = 0
            for method, ranking in rankings.items():
                # Find rank of item in this ranking (1-indexed)
                rank = None
                for i, (ranked_item, _) in enumerate(ranking):
                    if ranked_item == item:
                        rank = i + 1
                        break
                
                if rank is not None:
                    score += weights[method] / (self.k + rank)
            
            rrf_scores[item] = score
        
        # Sort by RRF score and return
        fused_ranking = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return fused_ranking
    
    def fuse_retrieval_results(self, retrieval_results: Dict[str, List]) -> List[Tuple]:
        """
        Fuse results from different retrieval methods
        
        Args:
            retrieval_results: Results from RetrievalMethods.retrieve_all()
        """
        # All methods now return (doc_id, score) tuples for articles
        normalized_rankings = {}
        
        for method in ['sparse', 'dense', 'gnn']:
            if method in retrieval_results and retrieval_results[method]:
                normalized_rankings[method] = retrieval_results[method]
        
        return self.fuse_rankings(normalized_rankings)