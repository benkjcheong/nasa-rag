from typing import List, Set
try:
    from goatools.obo_parser import GODag
    HAS_GO = True
except ImportError:
    HAS_GO = False

class BiologyThesaurus:
    def __init__(self):
        self.go_dag = None
        
        if HAS_GO:
            try:
                import os
                if not os.path.exists('go-basic.obo'):
                    import urllib.request
                    urllib.request.urlretrieve(
                        'http://purl.obolibrary.org/obo/go/go-basic.obo',
                        'go-basic.obo'
                    )
                self.go_dag = GODag('go-basic.obo')
            except Exception:
                pass
    
    def map_term(self, term: str) -> str:
        """Map term to canonical GO form"""
        if self.go_dag:
            go_term = self._search_go_term(term)
            if go_term:
                return go_term.replace(" ", "_").lower()
        
        return term.lower().strip().replace(" ", "_")
    
    def _search_go_term(self, term: str) -> str:
        """Search GO ontology for term"""
        if not self.go_dag:
            return None
            
        term_lower = term.lower()
        for go_id, go_term in self.go_dag.items():
            if term_lower in go_term.name.lower():
                return go_term.name
        return None
    
    def get_synonyms(self, canonical_term: str) -> List[str]:
        """Get GO synonyms for term"""
        if not self.go_dag:
            return []
            
        for go_id, go_term in self.go_dag.items():
            if canonical_term.replace("_", " ").lower() == go_term.name.lower():
                return list(go_term.alt_ids) if hasattr(go_term, 'alt_ids') else []
        return []
    
    def expand_query(self, terms: List[str]) -> Set[str]:
        """Expand query terms with GO synonyms"""
        expanded = set()
        for term in terms:
            canonical = self.map_term(term)
            expanded.add(canonical)
            expanded.update(self.get_synonyms(canonical))
        return expanded