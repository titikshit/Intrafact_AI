import os
from openai import OpenAI
from dotenv import load_dotenv
from intrafact.retrieval.retriever import Retriever

load_dotenv()

class RAGPipeline:
    def __init__(self, model_name: str = None):
        # Load Config
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = model_name or os.getenv("LLM_MODEL") or "google/gemma-3n-e4b-it:free"
        
        if not self.api_key:
            raise ValueError("❌ Missing API Key in .env")

        print(f"   ...Initializing Pipeline (Model: {self.model_name})...")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        self.retriever = Retriever()

    def _should_search(self, query: str) -> bool:
        """
        Step 1: The Router.
        """
        # We merge instructions into the user prompt to be safe for all models
        full_prompt = f"""
        INSTRUCTIONS:
        You are an intelligent query router. Decide if a user's question requires retrieving external documents.
        Reply "SEARCH" if the user asks about specific projects, files, or facts.
        Reply "DIRECT" if the user is greeting you (Hi, Hello), asking for general knowledge (2+2), or general advice.
        Reply ONLY with "SEARCH" or "DIRECT".

        USER QUERY:
        "{query}"
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": full_prompt} # <--- CHANGED TO USER ROLE
                ],
                temperature=0.1,
                max_tokens=5
            )
            decision = response.choices[0].message.content.strip().upper()
            print(f"   🚦 Router Decision: {decision}")
            return "SEARCH" in decision
            
        except Exception as e:
            print(f"   ⚠️ Router Error: {e}. Defaulting to SEARCH.")
            return True

    def answer_question(self, query: str) -> str:
        """
        Step 2: The Execution.
        """
        # --- DECISION TIME ---
        if self._should_search(query):
            # PATH A: RAG
            print("   🔍 Route: Searching Database...")
            results = self.retriever.retrieve(query, limit=5)
            
            if not results:
                # Fallback if search yields nothing
                context_text = "No relevant documents found."
            else:
                context_text = "\n\n---\n\n".join([doc['content'] for doc in results])
            
            # Combine System + Context + Question into one block
            final_prompt = f"""
            SYSTEM INSTRUCTIONS:
            You are a helpful AI assistant answering based strictly on the provided context.
            If the answer is not in the context, say "I don't know."

            CONTEXT DOCUMENTS:
            {context_text}

            USER QUESTION:
            {query}
            """
            
        else:
            # PATH B: Direct Answer
            print("   ⚡ Route: Direct Answer...")
            final_prompt = f"""
            SYSTEM INSTRUCTIONS:
            You are a helpful AI assistant. Answer the user's question politely and directly.

            USER QUESTION:
            {query}
            """

        # --- GENERATE ANSWER ---
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    # We send EVERYTHING as a single user message
                    {"role": "user", "content": final_prompt} 
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ API Error: {e}"