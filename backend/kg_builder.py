import json
from typing import List
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from kg_schema import BiologyKGSchema, Entity, Relation, EntityType

class KnowledgeGraphBuilder:
    def __init__(self, model_name="gemma2:2b"):
        self.llm = OllamaLLM(model=model_name)
        self.kg = BiologyKGSchema()
        self.thesaurus = self._load_thesaurus()
        
    def _load_thesaurus(self):
        # Biology thesaurus mapping
        return {
            "microgravity": ["weightlessness", "zero gravity", "space environment"],
            "gene expression": ["transcription", "mRNA levels", "protein synthesis"],
            "cell culture": ["in vitro", "cultured cells", "cell lines"],
            "stress response": ["adaptation", "cellular stress", "environmental response"]
        }
    
    def extract_entities_relations(self, text: str):
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Extract biology entities and relationships from this NASA space experiment text:
{text}

Return JSON format:
{{"entities": [{{"id": "e1", "type": "experiment", "name": "...", "properties": {{}}}}, ...],
  "relations": [{{"subject": "e1", "predicate": "studies", "object": "e2", "confidence": 0.9, "evidence": "..."}}]}}"""
        )
        
        response = self.llm(prompt.format(text=text))
        try:
            data = json.loads(response)
            
            # Add entities
            for e in data.get("entities", []):
                entity = Entity(
                    id=e["id"],
                    type=EntityType(e["type"]),
                    name=e["name"],
                    properties=e.get("properties", {})
                )
                self.kg.add_entity(entity)
            
            # Add relations
            for r in data.get("relations", []):
                relation = Relation(
                    subject=r["subject"],
                    predicate=r["predicate"],
                    object=r["object"],
                    confidence=r["confidence"],
                    evidence=r["evidence"]
                )
                self.kg.add_relation(relation)
                
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response: {response}")
    
    def map_to_thesaurus(self, term: str):
        for key, synonyms in self.thesaurus.items():
            if term.lower() in [s.lower() for s in synonyms] or term.lower() == key.lower():
                return key
        return term
    
    def build_from_publications(self, publications: list[str]):
        for pub_text in publications:
            self.extract_entities_relations(pub_text)
        return self.kg