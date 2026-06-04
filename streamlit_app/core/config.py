# =============================================================================
# Configuration Class
# =============================================================================

from dataclasses import dataclass


@dataclass
class Config:
    """Centralized configuration for the RAG pipeline."""
    
    # File paths
    PDF_PATH: str = "data/finance_evaluation.pdf"
    CHROMA_PATH: str = "./chroma_store"
    COLLECTION_NAME: str = "financial_report"
    RESULTS_PATH: str = "results.json"
    
    # User-defined query and reference
    QUERY: str = "What is the VaR confidence interval and current portfolio allocation strategy?"
    REFERENCE_SUMMARY: str = """The portfolio tracks a 95% confidence interval VaR that potential weekly downside variance will not exceed 2.1%. Current allocations show Domestic Large-Cap Equities over-allocated at 32.4% vs 30.0% target requiring trimming, while Emerging Markets Equities are under-allocated at 4.1% vs 5.0% target. The portfolio maintains a Beta of 0.88 against broader market indices with strategic rebalancing planned for Q2."""
    
    # Chunking parameters
    CHUNK_SIZE: int = 200  # words per chunk
    CHUNK_OVERLAP: int = 30
    
    # Retrieval parameters
    TOP_K: int = 3  # chunks to retrieve
    
    # PDF extraction margins
    FOOTER_MARGIN: int = 50
    HEADER_MARGIN: int = 70
    
    # LLM configuration
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "gemma3:1b"
    
    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Summary parameters
    SUMMARY_LENGTH: str = "150-200 words"
    NON_RAG_TRUNCATE: int = 4000  # words for non-RAG input