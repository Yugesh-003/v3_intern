# =============================================================================
# Summarization Pipeline
# =============================================================================

from typing import List, Tuple
from .config import Config
from .llm_interface import LLMInterface


def _build_format_template(constraint: str) -> str:
    """
    Convert a constraint label into a structural fill-in-the-blank template
    that forces small LLMs to follow the format exactly.
    """
    c = constraint.strip().lower()

    if "3 line" in c:
        return (
            "Write EXACTLY 3 lines. Use this structure and fill in each line:\n"
            "Line 1: [First key point from the document]\n"
            "Line 2: [Second key point from the document]\n"
            "Line 3: [Third key point or conclusion from the document]\n"
            "Do NOT write more than 3 lines. Do NOT add headings or labels."
        )
    elif "5 bullet" in c:
        return (
            "Write EXACTLY 5 bullet points. Use this structure:\n"
            "• [First key point]\n"
            "• [Second key point]\n"
            "• [Third key point]\n"
            "• [Fourth key point]\n"
            "• [Fifth key point or conclusion]\n"
            "Do NOT add headings. Do NOT write more than 5 bullets."
        )
    elif "50 word" in c:
        return (
            "Write a summary in 50 words or fewer — a single short paragraph.\n"
            "Count your words. Stop at 50. Do NOT use bullet points or headings."
        )
    elif "one paragraph" in c or "1 paragraph" in c:
        return (
            "Write exactly ONE paragraph of 4–6 sentences.\n"
            "Do NOT use bullet points, headings, or line breaks within the paragraph."
        )
    elif "2 line" in c or "two line" in c:
        return (
            "Write EXACTLY 2 lines. Use this structure:\n"
            "Line 1: [Main topic or finding]\n"
            "Line 2: [Key conclusion or implication]\n"
            "Do NOT write more than 2 lines."
        )
    elif "2 sentence" in c or "two sentence" in c:
        return (
            "Write EXACTLY 2 sentences. No more, no less.\n"
            "Sentence 1: [Main topic]\n"
            "Sentence 2: [Key conclusion]"
        )
    else:
        # Fallback: echo back the raw constraint as a strong instruction
        return (
            f"Follow this format exactly: {constraint}\n"
            "Do NOT deviate from this format."
        )


class SummarizationPipeline:
    """RAG and Non-RAG summarization with format-enforced prompts."""

    def __init__(self, config: Config):
        self.config = config
        self.llm    = LLMInterface(config)

    # ------------------------------------------------------------------
    # RAG Summary — uses only retrieved chunks
    # ------------------------------------------------------------------
    def generate_rag_summary(self, task: str, contexts: List[str]) -> Tuple[str, float]:
        """Generate a RAG-based summary using retrieved context chunks only."""
        context_text    = "\n\n---\n\n".join(contexts)
        format_template = _build_format_template(self.config.SUMMARY_CONSTRAINT)

        prompt = f"""You are a document summarizer. Read the CONTEXT and produce a summary.

=== OUTPUT FORMAT (follow exactly) ===
{format_template}

=== RULES ===
- Use ONLY facts stated in the CONTEXT below. No outside knowledge.
- Do not copy sentences verbatim. Rephrase in your own words.
- Do not add any text before or after the summary.

=== CONTEXT ===
{context_text}

=== YOUR SUMMARY (start immediately below, no preamble) ===
"""
        return self.llm.generate(prompt)

    # ------------------------------------------------------------------
    # Non-RAG Summary — uses full document text
    # ------------------------------------------------------------------
    def generate_non_rag_summary(self, task: str, full_text: str) -> Tuple[str, float]:
        """Generate a Non-RAG summary using the full (truncated) document text."""
        words           = full_text.split()[: self.config.NON_RAG_TRUNCATE]
        truncated_text  = " ".join(words)
        format_template = _build_format_template(self.config.SUMMARY_CONSTRAINT)

        prompt = f"""You are a document summarizer. Read the DOCUMENT and produce a summary.

=== OUTPUT FORMAT (follow exactly) ===
{format_template}

=== RULES ===
- Base your summary strictly on the DOCUMENT below.
- Do not add any text before or after the summary.

=== DOCUMENT ===
{truncated_text}

=== YOUR SUMMARY (start immediately below, no preamble) ===
"""
        return self.llm.generate(prompt)