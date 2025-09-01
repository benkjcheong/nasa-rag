https://www.spaceappschallenge.org/2025/challenges/build-a-space-biology-knowledge-engine

Enable a new era of human space exploration! NASA has been performing biology experiments in space for decades, generating a tremendous amount of information that will need to be considered as humans prepare to revisit the Moon and explore Mars. Although this knowledge is publicly available, it can be difficult for potential users to find information that pertains to their specific interests. Your challenge is to build a dynamic dashboard that leverages artificial intelligence (AI), knowledge graphs, and/or other tools to summarize a set of NASA bioscience publications and enables users to explore the impacts and results of the experiments these publications describe.

Build KG:
Decide schema
Populate KG using LangChain and Gemma 270 m mapped to thesaurus; Store evidence-first triple with confidence score for reranking later

Search:
Retrieval Methods: Sparse search; Query KG after converting prompt to thesaurus; Dense embedding; Use GNN as classifier
Use Reciprocal Rank Function to join to one list; Rerank via cross-encoders and feature-based scoring and MMR