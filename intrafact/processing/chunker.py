import uuid
from typing import List, Dict

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunker(self, text: str) -> List[str]:
        if not text:
            return []

        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        i = 0
        while i < len(words):
            word = words[i]
            current_length += len(word) + 1   # Fixed: += instead of =
            current_chunk.append(word)

            if current_length >= self.chunk_size:
                chunk_str = " ".join(current_chunk)
                chunks.append(chunk_str)  

                overlap = 0
                backtrack = 0
                while overlap < self.chunk_overlap and backtrack < len(current_chunk):  # Fixed: < self.chunk_overlap
                    backtrack += 1
                    overlap += len(current_chunk[-backtrack]) + 1  # Fixed: += instead of =

                i -= backtrack - 1
                
                # Reset for next chunk
                current_chunk = []
                current_length = 0

            i += 1

        if current_chunk:
            chunks.append(" ".join(current_chunk)) 

        return chunks   

    def process_chunks(self, normalised_data: Dict) -> List[Dict]:
        raw_text = normalised_data.get("content", "") 
        text_chunks = self.chunker(raw_text)

        chunk_objects = []

        for index, text_segment in enumerate(text_chunks):
            chunk_object = {
                "id": str(uuid.uuid4()),
                "parent_id": normalised_data.get("id"),  # Fixed: consistent variable name
                "chunk_index": index,
                "content": text_segment,
                "metadata": normalised_data.get("metadata", {})  # Fixed: consistent variable name
            } 
            chunk_objects.append(chunk_object)
            
        return chunk_objects