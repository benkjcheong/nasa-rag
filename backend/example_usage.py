from kg.kg_builder import KnowledgeGraphBuilder
from kg.kg_storage import KGStorage

def main():
    builder = KnowledgeGraphBuilder()
    
    # Sample NASA publications with IDs
    publications = [
        ("ISS-001", """The ISS experiment studied gene expression in Arabidopsis thaliana under microgravity conditions.
        Results showed upregulation of stress response genes and altered protein synthesis pathways."""),
        ("ISS-002", """Cell culture experiments in weightlessness revealed increased apoptosis rates.
        Transcription levels of oxidative stress markers were significantly elevated.""")
    ]
    
    # Build KG with thesaurus mapping
    kg = builder.build_from_publications(publications)
    
    # Store with evidence triples
    storage = KGStorage()
    storage.store_kg(kg)
    
    # Demonstrate thesaurus mapping
    print("Thesaurus mappings:")
    print(f"'weightlessness' -> '{builder.thesaurus.map_term('weightlessness')}'")
    print(f"'transcription' -> '{builder.thesaurus.map_term('transcription')}'")
    print(f"'ROS' -> '{builder.thesaurus.map_term('ROS')}'")
    
    # Show ranked evidence triples
    ranked_triples = builder.get_ranked_triples()
    print(f"\nTop evidence triples (confidence >= 0.5): {len(ranked_triples)}")
    
    # Query by thesaurus term
    microgravity_results = storage.query_by_thesaurus_term("microgravity")
    print(f"\nMicrogravity-related triples: {len(microgravity_results)}")
    
    # Show query expansion
    expanded_terms = builder.thesaurus.expand_query(["stress", "microgravity"])
    print(f"\nExpanded query terms: {expanded_terms}")
    
    print("\nKG with dedicated thesaurus mapping and evidence scoring complete!")

if __name__ == "__main__":
    main()