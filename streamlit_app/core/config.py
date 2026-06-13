# =============================================================================
# Configuration Class
# =============================================================================

from dataclasses import dataclass, field


@dataclass
class Config:
    """Centralized configuration for the RAG summarization benchmark pipeline."""

    # ── File paths ─────────────────────────────────────────────────────────────
    PDF_PATH:         str = "data/sample.pdf"
    CHROMA_PATH:      str = "./chroma_store"
    COLLECTION_NAME:  str = "document_chunks"
    RESULTS_PATH:     str = "results.json"

    # ── Summarization task ─────────────────────────────────────────────────────
    TASK:               str = "Summarize the document in exactly 3 lines."
    SUMMARY_CONSTRAINT: str = "exactly 3 lines"
    REFERENCE_SUMMARY:  str = ""

    # ── Chunking ───────────────────────────────────────────────────────────────
    CHUNK_SIZE:    int = 200
    CHUNK_OVERLAP: int = 30

    # ── Retrieval ──────────────────────────────────────────────────────────────
    TOP_K: int = 3

    # ── PDF extraction margins ─────────────────────────────────────────────────
    FOOTER_MARGIN: int = 50
    HEADER_MARGIN: int = 70

    # ── LLM provider selector ──────────────────────────────────────────────────
    LLM_PROVIDER: str = "ollama"   # "ollama"  |  "bedrock"

    # ── Ollama (local) ─────────────────────────────────────────────────────────
    OLLAMA_URL:   str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "gemma3:1b"

    # ── AWS Bedrock ────────────────────────────────────────────────────────────
    BEDROCK_MODEL_ID: str = "amazon.nova-lite-v1:0"   # change to claude once approved
    BEDROCK_REGION:   str = "us-east-1"
    # Auth is handled by `aws configure` or environment variables.

    # ── Embedding model ────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Non-RAG input truncation ───────────────────────────────────────────────
    NON_RAG_TRUNCATE: int = 4000