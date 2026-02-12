import sys
from intrafact.ingestion.file_ingestor import ingestor
from intrafact.normalization.normalizer import TextNormalizer
from intrafact.processing.chunker import TextChunker 
from intrafact.processing.embedder import TextEmbedder 
from intrafact.storage.metadata_store import MetadataStore
from intrafact.storage.vector_store import VectorDB
import uuid
from intrafact.reasoning.rag_pipeline import RAGPipeline
from dotenv import load_dotenv

def run_pipeline():
    print("-----Starting Pipeline------")
    
    meta_store = MetadataStore()
    vector_db = VectorDB()

    #Step 1 Ingestion
    print("-----Starting Ingestion------")

    raw_data = ingestor()

    if not raw_data:
        print("No raw data found")
        return
    
    print(f"Found {len(raw_data)} files in raw data")

    #Step 2 processing
    print("-----Starting Normalisation-----")
    
    norm = TextNormalizer()
    chunker = TextChunker()
    embedder = TextEmbedder()

    processed_count = 0
    for file in raw_data:
        original_file_name = file["metadata"]["file_name"]
        file_hash = file["metadata"]["file_hash"]

        print(f"Normalising {original_file_name}")
        # Step 3 normalising
        if meta_store.document_exists(file_hash):
            print("File already processed, skipped")
            continue

        try:
            doc_id = str(uuid.uuid4())
            normalized_data = norm.normalize(
                file['raw_text'], 
                file['metadata']
            )
            # Step 4 chunking
            chunks = chunker.process_chunks(normalized_data)
        
            
            for chunk in chunks:
                chunk["parent_id"] = doc_id
            
            print(f"   ↳ Split into {len(chunks)} chunks.")

            # Step 5 embedding
            chunks_with_vectors = embedder.embed_chunks(chunks)
            print(f"   ↳ Generated {len(chunks_with_vectors[0]['embedding'])}-dimension vectors.")
            
            # Step 6 saving vectors
            vector_db.add_chunks(chunks_with_vectors)

            # Step 7 saving metadata
            meta_store.register_document(doc_id, original_file_name, file["metadata"])

            processed_count += 1
            
            print("   ✅ Processing Complete!")

        except Exception as e:
            print(f"❌ Error processing {original_file_name}: {e}")

    print(f"\n----- Processed {processed_count} new files. -----")

def start_chat_session():
        print("---- Chat Mode (type 'exit' to quit) ----")
        try:
            rag = RAGPipeline()

        except Exception as e:
            print("Error initialising AI")
            return
        
        while True:
            try:
                query = input("\nUser: ").strip()
                if query.lower() in ['exit', 'quit']:
                    print("Goodbye")
                    break
                if not query:
                    continue
                
                answer = rag.answer_question(query)
                print(f"\nAI: {answer}")

            except KeyboardInterrupt:
                print("Goodbye")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__== "__main__":
    print("==========================================")
    print("   INTRAFACT AI - PERSONAL KNOWLEDGE BASE  ")
    print("==========================================")
    run_pipeline()
    start_chat_session()
           