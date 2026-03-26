# Excel RAG Agent

A Retrieval-Augmented Generation (RAG) agent that reads Excel files, converts them to Markdown, computes embeddings via Google Gemini, and allows you to chat with your data interactively using ChromaDB.

## 1. Prerequisites & Installation

This project uses `uv` for lightning-fast Python dependency management.

### Install `uv`
If you don't have `uv` installed, install it via PowerShell:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
*(Make sure to restart your shell afterwards, or add the output directory to your PATH as prompted).*

### Create and Activate Virtual Environment
You can let `uv` handle the environment automatically by just prefixing commands with `uv run`, or you can explicitly create and activate it:
```powershell
# Create the virtual environment folder (.venv)
uv venv --python 3.12

# Activate the virtual environment directly in PowerShell
.venv\Scripts\activate
```

### Install Dependencies
If you have a `pyproject.toml` and `uv.lock` file, you can install everything rapidly:
```powershell
uv sync
```
*(If you are setting this up from scratch, the required packages are: `pandas openpyxl tabulate chromadb google-generativeai python-dotenv langchain-text-splitters`)*

---

## 2. API Key Setup

You need an active Google Gemini API key to generate embeddings and run the conversational LLM.
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and generate a new API key.
2. In the root of this project, rename the template `.env-example` file to `.env`.
3. Open `.env` in a text editor and paste your API key:
   ```env
   GEMINI_API_KEY=AIzaSyYourKeyHere...
   ```

---

## 3. Ingesting Excel Data

Prepare your Excel file (e.g., `tests/test_data.xlsx`) containing the data you want to query.
Run the data pipeline to read, chunk, and index the Excel file into the local vector database (`ChromaDB`).

```powershell
uv run src/pipeline.py tests/test_data.xlsx
```
*(Note: If your script is at the root level, run `uv run pipeline.py test_data.xlsx` instead)*

This script converts the Excel sheets to Markdown and generates embeddings. You will notice a new `chroma_db/` folder created in your project, which holds the vectorized data.

---

## 4. Querying the Data

### Interactive Chat Mode (Recommended)
You can continually ask questions against your data without waiting to reload the database and models every single time. 

Start the interactive console:
```powershell
uv run interactive.py
```
Wait for it to load, then type your query (e.g., *"What is the total revenue?"*) and hit Enter. Type `exit` or `quit` to close the session.

### Single Query Mode
If you prefer to ask a single question directly via the command line and exit immediately:
```powershell
uv run src/query.py "What were the sales figures for Q3?"
```
