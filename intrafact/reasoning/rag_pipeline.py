import os
from openai import OpenAI
from dotenv import load_dotenv
from intrafact.retrieval.retriever import Retriever

load_dotenv()

class RAGPipeline:
    def __init__(self, model_name: str = None):
        print("....Initialising Rag pipeline....")

        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found!")
        
        self.model_name = model_name or os.getenv("LLM_MODEL") or "deepseek/deepseek-r1-0528:free"

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key = self.api_key
        )
        self.retriever = Retriever()

    def answer_question(self, query: str) -> str:
        results = self.retriever.retrieve(query, limit=5)
        if not results:
            return("I could not find any information in your documents ")

        context_text = "\n\n---\n\n".join(doc["content"] for doc in results)

        system_prompt = """
        You are a highly precise AI assistant for RAG (Retrieval Augmented Generation) system.
        You will be provided with context documents.
        Answer the user's question ONLY based on the provided context.
        If the answer is not in the context, say "I dont know based on the provided documents."
        """

        user_prompt = f"""
        CONTEXT DOCUMENTS:
        {context_text}

        USER QUESTION:
        {query}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature = 0.3 # keep it factual
            )
            return response.choices[0].message.content
        
        except Exception as e:
            return f"API error {e}"

        
