from kg_builder import KnowledgeGraphBuilder
from kg_storage import KGStorage

# Example usage
def main():
    # Initialize builder
    builder = KnowledgeGraphBuilder()
    
    # Sample NASA publication text
    sample_text = """
    The ISS experiment studied gene expression in Arabidopsis thaliana under microgravity conditions.
    Results showed upregulation of stress response genes and altered protein synthesis pathways.
    """
    
    # Build knowledge graph
    kg = builder.build_from_publications([sample_text])
    
    # Store in database
    storage = KGStorage()
    storage.store_kg(kg)
    
    print("Knowledge graph built and stored successfully!")
    print(f"Schema: {kg.get_schema()}")

if __name__ == "__main__":
    main()