from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class EntityType(Enum):
    EXPERIMENT = "experiment"
    ORGANISM = "organism"
    GENE = "gene"
    PROTEIN = "protein"
    CONDITION = "condition"
    RESULT = "result"
    PUBLICATION = "publication"

@dataclass
class Entity:
    id: str
    type: EntityType
    name: str
    properties: Dict[str, str]

@dataclass
class Relation:
    subject: str
    predicate: str
    object: str
    confidence: float
    evidence: str

@dataclass
class EvidenceTriple:
    """Evidence-first triple with confidence for reranking"""
    subject: str
    predicate: str
    object: str
    evidence: str
    confidence: float
    source_id: str

class BiologyKGSchema:
    def __init__(self):
        self.entities = {}
        self.relations = []
        self.evidence_triples = []
        
    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity
        
    def add_relation(self, relation: Relation):
        self.relations.append(relation)
        
    def add_evidence_triple(self, triple: EvidenceTriple):
        self.evidence_triples.append(triple)
        
    def get_schema(self):
        return {
            "entities": {
                "experiment": ["name", "mission", "duration", "environment"],
                "organism": ["species", "strain", "type"],
                "gene": ["symbol", "function", "pathway"],
                "protein": ["name", "function", "location"],
                "condition": ["type", "value", "unit"],
                "result": ["measurement", "value", "significance"],
                "publication": ["title", "authors", "journal", "year"]
            },
            "relations": [
                "studies", "expresses", "regulates", "interacts_with",
                "affects", "measured_in", "published_in", "conducted_on"
            ]
        }