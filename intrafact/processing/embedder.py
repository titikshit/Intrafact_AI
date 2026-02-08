from sentence_transformers import SentenceTransformer
from typing import List, Dict

class embed_chunks:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"......Loading embedding model: {model_name} ....")
        self.model = SentenceTransformer(model_name)

    def text_embed(self, chunks: List[Dict]) -> List[Dict]:
        if not chunks:
            return []
        
        texts = (chunk["content"] for chunk in chunks)

        print(f"....Embedding {len(texts)} chunks....")
        embeddings = self.model.encode(texts) # converted to numpy array, also giving batch for chunks not individual texts

        for i,chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist() # converted to list

        return chunks

