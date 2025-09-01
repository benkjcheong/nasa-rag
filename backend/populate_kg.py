from kg.kg_storage import KGStorage
from kg.kg_schema import EvidenceTriple

def populate_sample_data():
    kg_storage = KGStorage('biology_kg.db')
    
    # Sample evidence triples based on space biology research
    sample_triples = [
        EvidenceTriple(
            subject="microgravity",
            predicate="affects",
            object="plant_growth",
            evidence="Microgravity effects on plant growth and development in space experiments. Gene expression changes in Arabidopsis thaliana under weightless conditions.",
            confidence=0.9,
            source_id="ISS-001"
        ),
        EvidenceTriple(
            subject="radiation",
            predicate="damages",
            object="DNA",
            evidence="Radiation exposure impacts on cellular DNA repair mechanisms. DNA damage and repair pathways in space environment.",
            confidence=0.85,
            source_id="ISS-002"
        ),
        EvidenceTriple(
            subject="microgravity",
            predicate="causes",
            object="bone_loss",
            evidence="Bone density loss in astronauts during long-duration spaceflight. Calcium metabolism and bone remodeling in microgravity.",
            confidence=0.92,
            source_id="ISS-003"
        ),
        EvidenceTriple(
            subject="zero_gravity",
            predicate="induces",
            object="muscle_atrophy",
            evidence="Muscle atrophy and countermeasures in zero gravity environments. Protein synthesis and muscle fiber changes.",
            confidence=0.88,
            source_id="ISS-004"
        ),
        EvidenceTriple(
            subject="spaceflight",
            predicate="affects",
            object="cardiovascular_system",
            evidence="Cardiovascular deconditioning in space and recovery protocols. Heart function and blood flow adaptations.",
            confidence=0.87,
            source_id="ISS-005"
        )
    ]
    
    # Store triples directly
    import sqlite3
    conn = sqlite3.connect(kg_storage.db_path)
    cursor = conn.cursor()
    
    for triple in sample_triples:
        cursor.execute("""
            INSERT OR REPLACE INTO evidence_triples 
            (subject, predicate, object, evidence, confidence, source_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (triple.subject, triple.predicate, triple.object,
              triple.evidence, triple.confidence, triple.source_id))
    
    conn.commit()
    conn.close()
    print(f"Populated {len(sample_triples)} evidence triples")

if __name__ == "__main__":
    populate_sample_data()