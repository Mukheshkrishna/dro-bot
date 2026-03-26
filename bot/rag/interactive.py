import argparse
import os
import sys

# Ensure we can import from src if needed, or we just rely on the scripts
# To keep things clean, we will implement the loop here.
from src.query import answer_query

def main():
    parser = argparse.ArgumentParser(description="Interactive RAG Querying")
    parser.add_argument("--db-path", default="./chroma_db", help="Path to the ChromaDB directory")
    args = parser.parse_args()

    print("==================================================")
    print("        Welcome to the Interactive RAG Agent      ")
    print("==================================================")
    print(f"Using Vector DB at: {args.db_path}")
    print("Type 'exit' or 'quit' to terminate the session.\n")

    while True:
        try:
            user_input = input("\nAsk a question: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting interactive query session. Goodbye!")
                break
            if not user_input:
                continue
                
            answer_query(query_text=user_input, db_path=args.db_path)
            
        except KeyboardInterrupt:
            print("\nSession terminated by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
