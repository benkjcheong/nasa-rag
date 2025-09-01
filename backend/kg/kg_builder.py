import json
from typing import List, Tuple
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from .kg_schema import BiologyKGSchema, Entity, Relation, EntityType, EvidenceTriple
from .thesaurus import BiologyThesaurus

class KnowledgeGraphBuilder:
    def __init__(self, model_name="gemma2:2b"):
        self.llm = OllamaLLM(model=model_name)
        self.kg = BiologyKGSchema()
        self.thesaurus = BiologyThesaurus()
        

    
    def extract_entities_relations(self, text: str, source_id: str = None):
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Extract biology entities and relationships from NASA space experiment text:
{text}

Return JSON with evidence-first approach:
{{"entities": [{{"id": "e1", "type": "experiment", "name": "...", "properties": {{}}}}, ...],
  "relations": [{{"subject": "e1", "predicate": "studies", "object": "e2", "confidence": 0.9, "evidence": "exact quote from text"}}]}}"""
        )
        
        response = self.llm(prompt.format(text=text))
        try:
            data = json.loads(response)
            
            # Map entities to thesaurus and add
            for e in data.get("entities", []):
                mapped_name = self.thesaurus.map_term(e["name"])
                entity = Entity(
                    id=e["id"],
                    type=EntityType(e["type"]),
                    name=mapped_name,
                    properties=e.get("properties", {})
                )
                self.kg.add_entity(entity)
            
            # Create evidence-first triples with confidence scores
            for r in data.get("relations", []):
                # Map predicate to thesaurus
                mapped_predicate = self.thesaurus.map_term(r["predicate"])
                
                # Create evidence triple
                evidence_triple = EvidenceTriple(
                    subject=r["subject"],
                    predicate=mapped_predicate,
                    object=r["object"],
                    evidence=r["evidence"],
                    confidence=r["confidence"],
                    source_id=source_id or "unknown"
                )
                
                relation = Relation(
                    subject=r["subject"],
                    predicate=mapped_predicate,
                    object=r["object"],
                    confidence=r["confidence"],
                    evidence=r["evidence"]
                )
                
                self.kg.add_evidence_triple(evidence_triple)
                self.kg.add_relation(relation)
                
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response: {response}")
    

    
    def build_from_publications(self, publications: List[Tuple[str, str]]):
        """Build KG from publications with source tracking"""
        for pub_id, pub_text in publications:
            self.extract_entities_relations(pub_text, pub_id)
        return self.kg
    
    def get_ranked_triples(self, min_confidence: float = 0.5) -> List[EvidenceTriple]:
        """Get evidence triples ranked by confidence for reranking"""
        return sorted(
            [t for t in self.kg.evidence_triples if t.confidence >= min_confidence],
            key=lambda x: x.confidence,
            reverse=True
        )