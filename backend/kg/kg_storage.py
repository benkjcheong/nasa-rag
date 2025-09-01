import sqlite3
import json
from typing import List
from .kg_schema import BiologyKGSchema, Entity, Relation, EntityType, EvidenceTriple

class KGStorage:
    def __init__(self, db_path="biology_kg.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT,
                name TEXT,
                properties TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                predicate TEXT,
                object TEXT,
                confidence REAL,
                evidence TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_triples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                predicate TEXT,
                object TEXT,
                evidence TEXT,
                confidence REAL,
                source_id TEXT,
                UNIQUE(subject, predicate, object, source_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_confidence 
            ON evidence_triples(confidence DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def store_kg(self, kg: BiologyKGSchema):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store entities
        for entity in kg.entities.values():
            cursor.execute("""
                INSERT OR REPLACE INTO entities (id, type, name, properties)
                VALUES (?, ?, ?, ?)
            """, (entity.id, entity.type.value, entity.name, json.dumps(entity.properties)))
        
        # Store relations
        for relation in kg.relations:
            cursor.execute("""
                INSERT INTO relations (subject, predicate, object, confidence, evidence)
                VALUES (?, ?, ?, ?, ?)
            """, (relation.subject, relation.predicate, relation.object, 
                  relation.confidence, relation.evidence))
        
        # Store evidence triples
        for triple in kg.evidence_triples:
            cursor.execute("""
                INSERT OR REPLACE INTO evidence_triples 
                (subject, predicate, object, evidence, confidence, source_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (triple.subject, triple.predicate, triple.object,
                  triple.evidence, triple.confidence, triple.source_id))
        
        conn.commit()
        conn.close()
    
    def query_relations(self, entity_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM relations 
            WHERE subject = ? OR object = ?
            ORDER BY confidence DESC
        """, (entity_id, entity_id))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_evidence_triples_ranked(self, min_confidence: float = 0.5) -> List[EvidenceTriple]:
        """Get evidence triples ranked by confidence for reranking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT subject, predicate, object, evidence, confidence, source_id
            FROM evidence_triples 
            WHERE confidence >= ?
            ORDER BY confidence DESC
        """, (min_confidence,))
        
        results = []
        for row in cursor.fetchall():
            results.append(EvidenceTriple(
                subject=row[0], predicate=row[1], object=row[2],
                evidence=row[3], confidence=row[4], source_id=row[5]
            ))
        
        conn.close()
        return results
    
    def query_by_thesaurus_term(self, term: str) -> List[EvidenceTriple]:
        """Query evidence triples by thesaurus-mapped term"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT subject, predicate, object, evidence, confidence, source_id
            FROM evidence_triples 
            WHERE subject LIKE ? OR predicate LIKE ? OR object LIKE ?
            ORDER BY confidence DESC
        """, (f"%{term}%", f"%{term}%", f"%{term}%"))
        
        results = []
        for row in cursor.fetchall():
            results.append(EvidenceTriple(
                subject=row[0], predicate=row[1], object=row[2],
                evidence=row[3], confidence=row[4], source_id=row[5]
            ))
        
        conn.close()
        return results