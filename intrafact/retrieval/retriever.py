from typing import List, Dict
from intrafact.storage.vector_store import VectorDB
from intrafact.processing.embedder import TextEmbedder

class Retriever:
    def __init__(self):
        self.embedder = TextEmbedder()
        self.vector_db = VectorDB()

    def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        print("....Searching....")

        query_vector = self.embedder.model.encode(query).tolist()
        results = self.vector_db.search(query_vector, limit)

        cleaned_results = []
        if not results['ids'] or len(results['ids'][0]) == 0:
            return []
        
        ids = results['ids'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results.get('distances', [[]])[0]

        for i in range(len(ids)):
            cleaned_results.append({
                "id": ids[i],
                "content": documents[i],
                "metadata": metadatas[i],
                "score": distances[i] if len(distances) > i else 0.0
            })
        
        print(f"Found {len(cleaned_results)} relevant chunks")
        return cleaned_results
