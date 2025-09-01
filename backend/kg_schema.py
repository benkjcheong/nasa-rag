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

class BiologyKGSchema:
    def __init__(self):
        self.entities = {}
        self.relations = []
        
    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity
        
    def add_relation(self, relation: Relation):
        self.relations.append(relation)
        
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