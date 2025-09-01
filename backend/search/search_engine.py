from typing import List, Dict, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval_methods import RetrievalMethods
from reciprocal_rank_fusion import ReciprocalRankFusion
from cross_encoder_reranker import CrossEncoderReranker, FeatureBasedScorer, MMRReranker, EvidenceReranker
from kg.kg_storage import KGStorage
from thesaurus import BiologyThesaurus

class SpaceBiologySearchEngine:
    def __init__(self, documents: List[str], kg_storage: KGStorage):
        self.documents = documents
        self.kg_storage = kg_storage
        self.thesaurus = BiologyThesaurus()
        
        # Initialize retrieval methods
        self.retrieval = RetrievalMethods(documents, kg_storage, self.thesaurus)
        
        # Initialize fusion and reranking
        self.rrf = ReciprocalRankFusion()
        self.cross_encoder = CrossEncoderReranker()
        self.feature_scorer = FeatureBasedScorer()
        self.mmr = MMRReranker()
        self.evidence_reranker = EvidenceReranker(kg_storage)
        
        # Fit cross-encoder
        self.cross_encoder.fit(documents)
    
    def search(self, query: str, top_k: int = 10, use_mmr: bool = True) -> List[Dict]:
        """
        Complete search pipeline with all retrieval methods and reranking
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_mmr: Whether to use MMR for diversity
        """
        # Step 1: Retrieve using all methods
        retrieval_results = self.retrieval.retrieve_all(query, top_k * 2)
        
        # Step 2: Get evidence-based reranking for KG results
        query_terms = query.lower().split()
        evidence_results = self.evidence_reranker.get_top_evidence(query_terms, top_k)
        
        # Add evidence results to retrieval results
        if evidence_results:
            evidence_formatted = [{
                'triple': (t.subject, t.predicate, t.object),
                'confidence': t.confidence,
                'evidence': t.evidence
            } for t in evidence_results]
            retrieval_results['evidence'] = evidence_formatted
        
        # Step 3: Fuse rankings using RRF
        fused_results = self.rrf.fuse_retrieval_results(retrieval_results)
        
        # Step 4: Cross-encoder reranking
        cross_reranked = self.cross_encoder.rerank(
            query, 
            fused_results[:top_k * 2], 
            self.documents
        )
        
        # Step 5: Feature-based scoring enhancement
        enhanced_results = []
        for item_id, score in cross_reranked:
            if isinstance(item_id, int) and item_id < len(self.documents):
                doc_text = self.documents[item_id]
                feature_score = self.feature_scorer.score(query, doc_text)
                final_score = 0.6 * score + 0.4 * feature_score
                enhanced_results.append((item_id, final_score))
            else:
                enhanced_results.append((item_id, score))
        
        # Step 6: MMR for diversity (optional)
        if use_mmr:
            final_results = self.mmr.rerank_with_mmr(
                query, 
                enhanced_results, 
                self.documents, 
                top_k
            )
        else:
            final_results = sorted(enhanced_results, key=lambda x: x[1], reverse=True)[:top_k]
        
        # Format results
        formatted_results = []
        for item_id, score in final_results:
            if isinstance(item_id, int) and item_id < len(self.documents):
                formatted_results.append({
                    'document_id': item_id,
                    'document': self.documents[item_id][:500] + "..." if len(self.documents[item_id]) > 500 else self.documents[item_id],
                    'score': score,
                    'type': 'document'
                })
            else:
                formatted_results.append({
                    'item_id': item_id,
                    'content': str(item_id),
                    'score': score,
                    'type': 'knowledge_graph'
                })
        
        return formatted_results
    
    def get_method_results(self, query: str, top_k: int = 10) -> Dict:
        """Get results from individual retrieval methods for analysis"""
        return self.retrieval.retrieve_all(query, top_k)