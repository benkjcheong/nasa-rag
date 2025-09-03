from typing import List, Dict, Tuple
import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.retrieval_methods import RetrievalMethods
from search.reciprocal_rank_fusion import ReciprocalRankFusion
from search.cross_encoder_reranker import CrossEncoderReranker, FeatureBasedScorer, MMRReranker, EvidenceReranker
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
    
    def search(self, query: str, top_k: int = 10, use_mmr: bool = False) -> List[Dict]:
        print(f"DEBUG: Search query: '{query}', top_k: {top_k}")
        print(f"DEBUG: Query terms: {query.lower().split()}")
        print(f"DEBUG: Documents count: {len(self.documents)}")
        
        # Step 1: Retrieve using all methods
        retrieval_results = self.retrieval.retrieve_all(query, top_k * 2)
        print(f"DEBUG: Retrieval results: {retrieval_results}")
        
        # Step 2: Get evidence-based reranking for KG results
        query_terms = query.lower().split()
        evidence_results = self.evidence_reranker.get_top_evidence(query_terms, top_k)
        print(f"DEBUG: Evidence results count: {len(evidence_results)}")
        
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
        print(f"DEBUG: Fused results count: {len(fused_results)}")
        
        # Step 4: Cross-encoder reranking
        cross_reranked = self.cross_encoder.rerank(
            query, 
            fused_results[:top_k * 2], 
            self.documents
        )
        print(f"DEBUG: Cross-reranked count: {len(cross_reranked)}")
        
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
        print(f"DEBUG: Enhanced results count: {len(enhanced_results)}")
        
        # Step 6: MMR for diversity (optional)
        if use_mmr:
            print(f"DEBUG: Using MMR with {len(enhanced_results)} enhanced results")
            final_results = self.mmr.rerank_with_mmr(
                query, 
                enhanced_results, 
                self.documents, 
                top_k
            )
        else:
            final_results = sorted(enhanced_results, key=lambda x: x[1], reverse=True)[:top_k]
        print(f"DEBUG: Final results count: {len(final_results)}")
        print(f"DEBUG: Final results: {final_results}")
        
        # Format results - find document IDs and associated triples
        formatted_results = []
        
        for item_id, score in final_results:
            print(f"DEBUG: Processing item_id: {item_id}, type: {type(item_id)}, score: {score}")
            if (isinstance(item_id, (int, np.integer)) and int(item_id) < len(self.documents)):
                print(f"DEBUG: Processing as document ID: {item_id}")
                # Document result
                doc_text = self.documents[int(item_id)]
                result = {
                    'document_id': int(item_id),
                    'document': doc_text[:500] + "..." if len(doc_text) > 500 else doc_text,
                    'score': score,
                    'type': 'document'
                }
                print(f"DEBUG: Added document result for ID {item_id}")
                formatted_results.append(result)
            else:
                # KG result - find associated document and triple
                term = str(item_id)
                print(f"DEBUG: Processing KG term: {term}")
                
                # Find triples containing this term
                triples = self.kg_storage.get_evidence_triples_ranked(0.0)
                print(f"DEBUG: Found {len(triples)} total triples for term '{term}'")
                if len(triples) > 0:
                    print(f"DEBUG: First triple example: {triples[0].subject} -> {triples[0].predicate} -> {triples[0].object}")
                    print(f"DEBUG: First triple evidence: {triples[0].evidence[:100] if triples[0].evidence else 'None'}...")
                matching_triple = None
                doc_id = None
                
                for t in triples:
                    # Check if term matches or if evidence contains the term
                    term_match = (term.lower() in t.subject.lower() or 
                                 term.lower() in t.object.lower() or
                                 (t.evidence and term.lower() in str(t.evidence).lower()))
                    
                    if term_match or not matching_triple:  # Take first triple if no exact match
                        matching_triple = t
                        print(f"DEBUG: Checking triple for document match: {t.subject} -> {t.predicate} -> {t.object}")
                        
                        # Find document ID by matching evidence text
                        for i, doc in enumerate(self.documents):
                            if t.evidence and t.evidence.strip() in doc:
                                doc_id = i
                                print(f"DEBUG: Found document match at ID {doc_id}")
                                break
                        
                        if doc_id is not None:
                            break  # Found a match, stop looking
                
                if doc_id is not None and doc_id < len(self.documents):
                    doc_text = self.documents[doc_id]
                    result = {
                        'document_id': doc_id,
                        'document': doc_text[:500] + "..." if len(doc_text) > 500 else doc_text,
                        'score': score,
                        'type': 'document_with_triple'
                    }
                    if matching_triple:
                        result['triple'] = {
                            'subject': matching_triple.subject,
                            'predicate': matching_triple.predicate,
                            'object': matching_triple.object,
                            'confidence': matching_triple.confidence
                        }
                    formatted_results.append(result)
                else:
                    # Fallback for terms without document match
                    print(f"DEBUG: No document match found for term '{term}', using fallback")
                    formatted_results.append({
                        'term': term,
                        'score': score,
                        'type': 'knowledge_graph_term'
                    })
        
        print(f"DEBUG: Formatted results count: {len(formatted_results)}")
        return formatted_results
    
    def get_method_results(self, query: str, top_k: int = 10) -> Dict:
        """Get results from individual retrieval methods for analysis"""
        return self.retrieval.retrieve_all(query, top_k)