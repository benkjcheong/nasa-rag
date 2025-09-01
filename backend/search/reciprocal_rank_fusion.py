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
        # Normalize different result formats to (item, score) tuples
        normalized_rankings = {}
        
        # Sparse and Dense results: (doc_idx, score)
        for method in ['sparse', 'dense']:
            if method in retrieval_results:
                normalized_rankings[method] = retrieval_results[method]
        
        # KG Thesaurus results: convert to (triple_str, confidence)
        if 'kg_thesaurus' in retrieval_results:
            kg_results = []
            for result in retrieval_results['kg_thesaurus']:
                triple_str = f"{result['triple'][0]}_{result['triple'][1]}_{result['triple'][2]}"
                kg_results.append((triple_str, result['confidence']))
            normalized_rankings['kg_thesaurus'] = kg_results
        
        # GNN results: already in (node, score) format
        if 'gnn' in retrieval_results:
            normalized_rankings['gnn'] = retrieval_results['gnn']
        
        return self.fuse_rankings(normalized_rankings)