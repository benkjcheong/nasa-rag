from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search.search_engine import SpaceBiologySearchEngine
from kg.kg_storage import KGStorage
from kg.kg_builder import KnowledgeGraphBuilder

app = Flask(__name__)
CORS(app)

# Initialize knowledge graph and search engine
kg_storage = KGStorage('biology_kg.db')

# Check if KG is populated, if not, populate with sample data
triples = kg_storage.get_evidence_triples_ranked(0.0)
if not triples:
    from populate_kg import populate_sample_data
    populate_sample_data()

# Get documents from KG evidence
triples = kg_storage.get_evidence_triples_ranked(0.0)
documents = [t.evidence for t in triples if t.evidence]
if not documents:
    documents = ["No knowledge graph data available"]

search_engine = SpaceBiologySearchEngine(documents, kg_storage)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = search_engine.search(query, top_k)
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/methods', methods=['POST'])
def get_method_results():
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        results = search_engine.get_method_results(query, top_k)
        
        return jsonify({
            'query': query,
            'method_results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kg/query', methods=['POST'])
def query_kg():
    try:
        data = request.get_json()
        term = data.get('term', '')
        
        if not term:
            return jsonify({'error': 'Term is required'}), 400
        
        # Query KG by thesaurus term
        triples = kg_storage.query_by_thesaurus_term(term)
        
        results = [{
            'subject': t.subject,
            'predicate': t.predicate,
            'object': t.object,
            'evidence': t.evidence,
            'confidence': t.confidence,
            'source_id': t.source_id
        } for t in triples]
        
        return jsonify({
            'term': term,
            'triples': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)