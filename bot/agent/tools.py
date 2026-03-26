def rag_tool(query: str) -> str:
    """
    This tool uses your existing RAG pipeline
    """
    from bot.rag.pipeline import run_pipeline   # adjust if function name differs
    
    response = run_pipeline(query)
    return response
