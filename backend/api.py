from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search.search_engine import SpaceBiologySearchEngine
from kg.kg_storage import KGStorage

app = Flask(__name__)
CORS(app)

# Initialize search engine
kg_storage = KGStorage('biology_kg.db')
sample_docs = [
    "Microgravity effects on plant growth and development in space experiments",
    "Radiation exposure impacts on cellular DNA repair mechanisms",
    "Bone density loss in astronauts during long-duration spaceflight",
    "Muscle atrophy and countermeasures in zero gravity environments",
    "Cardiovascular deconditioning in space and recovery protocols"
]

search_engine = SpaceBiologySearchEngine(sample_docs, kg_storage)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)