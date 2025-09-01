import sqlite3
import json
from kg_schema import BiologyKGSchema, Entity, Relation, EntityType

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