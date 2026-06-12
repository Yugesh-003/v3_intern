# =============================================================================
# Configuration Class
# =============================================================================

from dataclasses import dataclass


@dataclass
class Config:
    """Centralized configuration for the RAG summarization benchmark pipeline."""

    # File paths
    PDF_PATH: str = "data/sample.pdf"
    CHROMA_PATH: str = "./chroma_store"
    COLLECTION_NAME: str = "document_chunks"
    RESULTS_PATH: str = "results.json"

    # Summarization task
    TASK: str = "Summarize the document in exactly 3 lines."
    SUMMARY_CONSTRAINT: str = "exactly 3 lines"   # injected into LLM prompts
    REFERENCE_SUMMARY: str = ""                    # user's hand-written reference (Option A)

    # Chunking parameters
    CHUNK_SIZE: int = 200       # words per chunk
    CHUNK_OVERLAP: int = 30

    # Retrieval parameters
    TOP_K: int = 3              # chunks to retrieve

    # PDF extraction margins
    FOOTER_MARGIN: int = 50
    HEADER_MARGIN: int = 70

    # LLM configuration
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "gemma3:1b"

    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Non-RAG input truncation
    NON_RAG_TRUNCATE: int = 4000   # words fed to non-RAG LLM