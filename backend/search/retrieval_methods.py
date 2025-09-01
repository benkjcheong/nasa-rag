from typing import List, Dict, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import json

class SparseRetrieval:
    def __init__(self, documents: List[str]):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.doc_vectors = self.vectorizer.fit_transform(documents)
        self.documents = documents
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > 0]

class KGThesaurusRetrieval:
    def __init__(self, kg_storage, thesaurus):
        self.kg_storage = kg_storage
        self.thesaurus = thesaurus
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        # Convert query to thesaurus terms
        query_terms = query.lower().split()
        expanded_terms = self.thesaurus.expand_query(query_terms)
        
        results = []
        for term in expanded_terms:
            triples = self.kg_storage.query_by_thesaurus_term(term)
            results.extend([{
                'triple': (t.subject, t.predicate, t.object),
                'confidence': t.confidence,
                'evidence': t.evidence
            } for t in triples])
        
        # Sort by confidence and return top-k
        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results[:top_k]

class DenseEmbeddingRetrieval:
    def __init__(self, documents: List[str], embedding_dim: int = 384):
        self.documents = documents
        self.embedding_dim = embedding_dim
        # Simplified embedding using TF-IDF as dense representation
        self.vectorizer = TfidfVectorizer(max_features=embedding_dim)
        self.embeddings = self.vectorizer.fit_transform(documents).toarray()
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        query_embedding = self.vectorizer.transform([query]).toarray()[0]
        similarities = cosine_similarity([query_embedding], self.embeddings).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > 0]

class GNNClassifier:
    def __init__(self, kg_storage):
        self.kg_storage = kg_storage
        self.node_features = {}
        self.adjacency = {}
    
    def build_graph(self):
        """Build graph from KG triples"""
        triples = self.kg_storage.get_all_triples()
        nodes = set()
        
        for triple in triples:
            nodes.add(triple.subject)
            nodes.add(triple.object)
            
            # Build adjacency list
            if triple.subject not in self.adjacency:
                self.adjacency[triple.subject] = []
            self.adjacency[triple.subject].append((triple.object, triple.confidence))
        
        # Simple node features based on degree and confidence
        for node in nodes:
            degree = len(self.adjacency.get(node, []))
            avg_confidence = np.mean([conf for _, conf in self.adjacency.get(node, [(None, 0)])])
            self.node_features[node] = [degree, avg_confidence]
    
    def classify_relevance(self, query_terms: List[str], top_k: int = 10) -> List[Tuple[str, float]]:
        """Classify node relevance using simple GNN-like scoring"""
        if not self.node_features:
            self.build_graph()
        
        scores = {}
        for node in self.node_features:
            # Simple relevance score based on term matching and graph features
            term_match = sum(1 for term in query_terms if term.lower() in node.lower())
            degree, avg_conf = self.node_features[node]
            
            # Combine features for relevance score
            scores[node] = (term_match * 2 + degree * 0.1 + avg_conf) / 3
        
        # Sort and return top-k
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_k]

class RetrievalMethods:
    def __init__(self, documents: List[str], kg_storage, thesaurus):
        self.sparse = SparseRetrieval(documents)
        self.kg_thesaurus = KGThesaurusRetrieval(kg_storage, thesaurus)
        self.dense = DenseEmbeddingRetrieval(documents)
        self.gnn = GNNClassifier(kg_storage)
        self.documents = documents
    
    def retrieve_all(self, query: str, top_k: int = 10) -> Dict[str, List]:
        """Run all retrieval methods and return results"""
        return {
            'sparse': self.sparse.search(query, top_k),
            'kg_thesaurus': self.kg_thesaurus.search(query, top_k),
            'dense': self.dense.search(query, top_k),
            'gnn': self.gnn.classify_relevance(query.split(), top_k)
        }