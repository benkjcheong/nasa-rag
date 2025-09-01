from typing import List, Tuple, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg.kg_schema import EvidenceTriple
from kg.kg_storage import KGStorage

class CrossEncoderReranker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.is_fitted = False
    
    def fit(self, documents: List[str]):
        """Fit the cross-encoder on documents"""
        self.vectorizer.fit(documents)
        self.is_fitted = True
    
    def score_query_document(self, query: str, document: str) -> float:
        """Score query-document pair using cross-encoder approach"""
        if not self.is_fitted:
            raise ValueError("CrossEncoder must be fitted first")
        
        # Simple cross-encoder simulation using TF-IDF similarity
        combined_text = f"{query} [SEP] {document}"
        query_vec = self.vectorizer.transform([query])
        doc_vec = self.vectorizer.transform([document])
        
        # Cross-attention simulation: element-wise product + cosine similarity
        similarity = cosine_similarity(query_vec, doc_vec)[0][0]
        
        # Add query-document interaction features
        query_terms = set(query.lower().split())
        doc_terms = set(document.lower().split())
        overlap = len(query_terms.intersection(doc_terms)) / max(len(query_terms), 1)
        
        return (similarity + overlap) / 2
    
    def rerank(self, query: str, candidates: List[Tuple], documents: List[str] = None) -> List[Tuple]:
        """
        Rerank candidates using cross-encoder scores
        
        Args:
            query: Search query
            candidates: List of (item_id, initial_score) tuples
            documents: Optional list of documents for item_ids that are indices
        """
        reranked = []
        
        for item_id, initial_score in candidates:
            # Get document text
            if documents and isinstance(item_id, int):
                doc_text = documents[item_id]
            elif isinstance(item_id, str):
                doc_text = item_id  # Assume item_id is the text itself
            else:
                doc_text = str(item_id)
            
            # Calculate cross-encoder score
            cross_score = self.score_query_document(query, doc_text)
            
            # Combine with initial score
            final_score = 0.7 * cross_score + 0.3 * initial_score
            reranked.append((item_id, final_score))
        
        # Sort by final score
        return sorted(reranked, key=lambda x: x[1], reverse=True)

class FeatureBasedScorer:
    def __init__(self):
        self.features = {}
    
    def extract_features(self, query: str, document: str, metadata: Dict = None) -> Dict[str, float]:
        """Extract features for scoring"""
        query_terms = query.lower().split()
        doc_terms = document.lower().split()
        
        features = {
            'term_overlap': len(set(query_terms).intersection(set(doc_terms))) / max(len(query_terms), 1),
            'doc_length': len(doc_terms),
            'query_coverage': len(set(query_terms).intersection(set(doc_terms))) / max(len(set(query_terms)), 1),
            'exact_matches': sum(1 for term in query_terms if term in document.lower())
        }
        
        if metadata:
            features.update({
                'confidence': metadata.get('confidence', 0.5),
                'evidence_strength': metadata.get('evidence_strength', 0.5)
            })
        
        return features
    
    def score(self, query: str, document: str, metadata: Dict = None) -> float:
        """Calculate feature-based score"""
        features = self.extract_features(query, document, metadata)
        
        # Simple weighted combination
        weights = {
            'term_overlap': 0.3,
            'query_coverage': 0.25,
            'exact_matches': 0.2,
            'confidence': 0.15,
            'evidence_strength': 0.1
        }
        
        score = sum(weights.get(feat, 0) * val for feat, val in features.items())
        return min(score, 1.0)  # Cap at 1.0

class EvidenceReranker:
    def __init__(self, storage: KGStorage):
        self.storage = storage
    
    def rerank_by_confidence(self, query_terms: List[str], min_confidence: float = 0.5) -> List[EvidenceTriple]:
        """Rerank evidence triples by confidence scores for query terms"""
        all_results = []
        
        for term in query_terms:
            results = self.storage.query_by_thesaurus_term(term)
            all_results.extend(results)
        
        unique_results = {}
        for triple in all_results:
            key = (triple.subject, triple.predicate, triple.object)
            if key not in unique_results or triple.confidence > unique_results[key].confidence:
                unique_results[key] = triple
        
        filtered = [t for t in unique_results.values() if t.confidence >= min_confidence]
        return sorted(filtered, key=lambda x: x.confidence, reverse=True)
    
    def get_top_evidence(self, query_terms: List[str], top_k: int = 10) -> List[EvidenceTriple]:
        """Get top-k evidence triples for reranking"""
        reranked = self.rerank_by_confidence(query_terms)
        return reranked[:top_k]

class MMRReranker:
    def __init__(self, lambda_param: float = 0.7):
        self.lambda_param = lambda_param  # Balance between relevance and diversity
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    
    def rerank_with_mmr(self, query: str, candidates: List[Tuple], documents: List[str], top_k: int = 10) -> List[Tuple]:
        """
        Rerank using Maximal Marginal Relevance for diversity
        
        Args:
            query: Search query
            candidates: List of (item_id, score) tuples
            documents: List of documents
            top_k: Number of results to return
        """
        if not candidates:
            return []
        
        # Fit vectorizer on all documents
        all_docs = [documents[item_id] if isinstance(item_id, int) and item_id < len(documents) else str(item_id) 
                   for item_id, _ in candidates]
        doc_vectors = self.vectorizer.fit_transform(all_docs + [query])
        query_vector = doc_vectors[-1]
        doc_vectors = doc_vectors[:-1]
        
        # Calculate relevance scores
        relevance_scores = cosine_similarity(query_vector, doc_vectors).flatten()
        
        selected = []
        remaining = list(range(len(candidates)))
        
        while len(selected) < top_k and remaining:
            mmr_scores = []
            
            for i in remaining:
                relevance = relevance_scores[i]
                
                # Calculate max similarity to already selected documents
                if selected:
                    selected_vectors = doc_vectors[selected]
                    similarities = cosine_similarity([doc_vectors[i]], selected_vectors).flatten()
                    max_sim = np.max(similarities)
                else:
                    max_sim = 0
                
                # MMR score
                mmr_score = self.lambda_param * relevance - (1 - self.lambda_param) * max_sim
                mmr_scores.append((i, mmr_score))
            
            # Select document with highest MMR score
            best_idx = max(mmr_scores, key=lambda x: x[1])[0]
            selected.append(best_idx)
            remaining.remove(best_idx)
        
        # Return reranked results
        return [candidates[i] for i in selected]