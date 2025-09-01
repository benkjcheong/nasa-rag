from typing import List, Dict
from kg_schema import EvidenceTriple
from kg_storage import KGStorage

class EvidenceReranker:
    def __init__(self, storage: KGStorage):
        self.storage = storage
    
    def rerank_by_confidence(self, query_terms: List[str], min_confidence: float = 0.5) -> List[EvidenceTriple]:
        """Rerank evidence triples by confidence scores for query terms"""
        all_results = []
        
        # Get results for each query term
        for term in query_terms:
            results = self.storage.query_by_thesaurus_term(term)
            all_results.extend(results)
        
        # Remove duplicates and filter by confidence
        unique_results = {}
        for triple in all_results:
            key = (triple.subject, triple.predicate, triple.object)
            if key not in unique_results or triple.confidence > unique_results[key].confidence:
                unique_results[key] = triple
        
        # Filter and sort by confidence
        filtered = [t for t in unique_results.values() if t.confidence >= min_confidence]
        return sorted(filtered, key=lambda x: x.confidence, reverse=True)
    
    def get_top_evidence(self, query_terms: List[str], top_k: int = 10) -> List[EvidenceTriple]:
        """Get top-k evidence triples for reranking"""
        reranked = self.rerank_by_confidence(query_terms)
        return reranked[:top_k]