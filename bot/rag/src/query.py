import argparse
import os
import google.generativeai as genai
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We need the same EmbeddingFunction used for indexing
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="models/gemini-embedding-2-preview"):
        self.model_name = model_name
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in .env file.")
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    def __call__(self, input: Documents) -> Embeddings:
        # Generate embeddings for a list of documents
        # Uses TaskType.RETRIEVAL_QUERY for user queries
        results = genai.embed_content(
            model=self.model_name,
            content=input,
            task_type="RETRIEVAL_QUERY"
        )
        if isinstance(input, list) and isinstance(results['embedding'][0], list):
             return results['embedding']
        elif isinstance(input, list):
             return [results['embedding']]
        return [results['embedding']]

def answer_query(query_text: str, db_path: str = "./chroma_db", n_results: int = 3):
    """Retrieves context from ChromaDB and uses Gemini API to answer the user query."""
    print("Connecting to ChromaDB and configuring Gemini...")
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    gemini_ef = GeminiEmbeddingFunction()
    collection = chroma_client.get_collection(
        name="excel_rag_collection",
        embedding_function=gemini_ef
    )
    
    print(f"Executing semantic search for: '{query_text}'")
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Check if we got results
    if not results['documents'] or not results['documents'][0]:
        print("No relevant context found in Vector DB.")
        return
        
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    context_str = "\n\n---\n\n".join(
        f"Context Metadata: {meta}\nContent: {doc}" 
        for meta, doc in zip(metadatas, documents)
    )
    
    prompt = f"""You are a helpful assistant answering an English query based strictly on the provided context retrieved from an Excel document.

Query: {query_text}

Context:
{context_str}

If the context does not contain enough information to answer the query, kindly reply that you don't know based on the provided data.
"""

    print("Formulating context prompt and generating answer...")
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    print("\n================== ASSISTANT RESPONSE ==================\n")
    print(response.text)
    print("\n========================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Query the RAG system based on indexed Excel data.")
    parser.add_argument("query", help="The English query to ask the RAG system")
    parser.add_argument("--db-path", default="./chroma_db", help="Path to the existing ChromaDB")
    args = parser.parse_args()

    answer_query(args.query, args.db_path)

if __name__ == "__main__":
    main()
