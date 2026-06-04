# =============================================================================
# Summarization Pipeline
# =============================================================================

from typing import List, Tuple
from .config import Config
from .llm_interface import LLMInterface


class SummarizationPipeline:
    """Main pipeline for RAG and Non-RAG summarization."""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMInterface(config)
    
    def generate_rag_summary(self, query: str, contexts: List[str]) -> Tuple[str, float]:
        """Generate RAG-based summary using retrieved contexts."""
        context_text = "\n\n---\n\n".join(contexts)
        
        prompt = f"""You are a financial document analyst. Generate a {self.config.SUMMARY_LENGTH} summary answering the question below.

CRITICAL INSTRUCTIONS:
- Use ONLY the provided context below
- Do not use any outside knowledge or assumptions
- If information is not in the context, state "Information not available in document"
- Be precise and factual

CONTEXT:
{context_text}

QUESTION: {query}

SUMMARY:"""
        
        return self.llm.generate(prompt)
    
    def generate_non_rag_summary(self, query: str, full_text: str) -> Tuple[str, float]:
        """Generate Non-RAG summary using full document text."""
        # Truncate to specified word limit
        words = full_text.split()[:self.config.NON_RAG_TRUNCATE]
        truncated_text = " ".join(words)
        
        prompt = f"""You are a financial document analyst. Generate a {self.config.SUMMARY_LENGTH} summary answering the question below.

Use the provided document content to create a comprehensive and accurate summary.

DOCUMENT:
{truncated_text}

QUESTION: {query}

SUMMARY:"""
        
        return self.llm.generate(prompt)
    
    def generate_multiviewpoint_summary(self, contexts: List[str]) -> Tuple[str, float]:
        """Generate Bull/Bear/Neutral viewpoint summary."""
        context_text = "\n\n---\n\n".join(contexts)
        
        prompt = f"""Based on the financial document context below, provide three different investment perspectives (2-3 sentences each):

BULL CASE: Optimistic investor perspective focusing on growth opportunities and positive indicators.

BEAR CASE: Conservative perspective focusing on risks and potential downsides.

NEUTRAL CASE: Balanced perspective weighing both opportunities and risks.

Use ONLY the information provided in the context below.

CONTEXT:
{context_text}

MULTI-VIEWPOINT ANALYSIS:"""
        
        return self.llm.generate(prompt)