import argparse
import os
import pandas as pd
import google.generativeai as genai
import chromadb

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We need a custom EmbeddingFunction wrapper for ChromaDB to use Google Gemini direct API


class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="models/gemini-embedding-2-preview"):
        self.model_name = model_name
        # Ensure API key is configured
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError(
                "GEMINI_API_KEY environment variable not set. Please set it in .env file.")
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    def __call__(self, input: Documents) -> Embeddings:
        # Generate embeddings for a list of documents
        # Uses TaskType.RETRIEVAL_DOCUMENT as per standard RAG document indexing best practice
        results = genai.embed_content(
            model=self.model_name,
            content=input,
            task_type="RETRIEVAL_DOCUMENT",
            # Title applies only if task_type is RETRIEVAL_DOCUMENT, we can just pass a generic title or None
            title="RAG Context"
        )
        # embed_content returns a dict like {'embedding': [[...], [...]]} if batched
        # If input is a list, embeddings is a list of lists
        if isinstance(input, list) and isinstance(results['embedding'][0], list):
            return results['embedding']
        elif isinstance(input, list):
            # Single document case unexpectedly returned
            return [results['embedding']]
        return [results['embedding']]  # Ensure list of lists


def read_excel_to_markdown(file_path: str) -> str:
    """Reads all sheets from an Excel file and converts them to a single Markdown string."""
    print(f"Reading {file_path}...")
    xls = pd.ExcelFile(file_path)
    md_content = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        # Create a header for the sheet
        md_content.append(f"# {sheet_name}\n")
        # Convert DataFrame to Markdown table
        md_content.append(df.to_markdown(index=False))
        md_content.append("\n\n")

    return "".join(md_content)


def chunk_markdown(md_text: str):
    """Chunks the Markdown text intelligently using headers and character limits."""
    print("Chunking Markdown text...")

    # First, split by headers to retain logical structure
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(md_text)

    # Then apply a character splitter to ensure no chunk is too large for the embedding model
    chunk_size = 1000
    chunk_overlap = 100
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    splits = text_splitter.split_documents(md_header_splits)
    print(f"Created {len(splits)} chunks.")
    return splits


def index_into_chroma(chunks, db_path="./chroma_db"):
    """Embeds and indexes the chunks into a ChromaDB collection."""
    print("Initializing ChromaDB and Gemini Embeddings...")

    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path=db_path)

    # Setup custom Gemini Embedding Function
    gemini_ef = GeminiEmbeddingFunction()

    # Get or create a collection
    collection = chroma_client.get_or_create_collection(
        name="excel_rag_collection",
        embedding_function=gemini_ef
    )

    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk.page_content)
        # Store header metadata if available
        metadatas.append(chunk.metadata if chunk.metadata else {
                         "source": "excel"})
        ids.append(f"chunk_{i}")

    print(f"Adding {len(documents)} documents to Vector DB...")
    # Add to ChromaDB (this will automatically call the embedding function)
    # We process in batches if there are many, but ChromaDB can usually handle a large batch
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Indexing complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest an Excel file into a vector database for RAG.")
    parser.add_argument("excel_file", help="Path to the Excel file to ingest")
    parser.add_argument("--db-path", default="./chroma_db",
                        help="Path to persist the ChromaDB")
    args = parser.parse_args()

    if not os.path.exists(args.excel_file):
        print(f"Error: File {args.excel_file} does not exist.")
        return

    # 1. Read Excel to Markdown
    md_text = read_excel_to_markdown(args.excel_file)

    # 2. Chunk the Markdown
    chunks = chunk_markdown(md_text)

    # 3. Index embeddings into Vector DB
    index_into_chroma(chunks, args.db_path)


if __name__ == "__main__":
    main()
