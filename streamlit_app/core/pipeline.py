# =============================================================================
# Main Pipeline Orchestration with Streamlit Integration
# =============================================================================

import json
import streamlit as st
from typing import Dict, Any
from .config import Config
from .pdf_extractor import PDFExtractor
from .chunker import TextChunker
from .vector_store import VectorStore
from .summarizer import SummarizationPipeline
from .evaluator import MetricsEvaluator


class RAGPipeline:
    """Orchestrates the RAG vs Non-RAG summarization benchmark pipeline."""

    def __init__(self, config: Config):
        self.config = config
        self.extractor  = PDFExtractor(config)
        self.chunker    = TextChunker(config)
        self.vector_store = VectorStore(config)
        self.summarizer = SummarizationPipeline(config)
        self.evaluator  = MetricsEvaluator(config)

    def run_complete_pipeline_with_progress(self) -> Dict[str, Any]:
        """Execute the complete RAG vs Non-RAG summarization benchmark."""

        progress_bar = st.progress(0)
        status_text  = st.empty()

        try:
            # ── Step 1: Extract PDF content ───────────────────────────────────
            status_text.text("📄 Step 1/8: Extracting PDF content…")
            progress_bar.progress(10)
            main_content, tables, stats = self.extractor.extract_content(self.config.PDF_PATH)

            st.session_state.main_content     = main_content
            st.session_state.tables           = tables
            st.session_state.extraction_stats = stats

            # ── Step 2: Chunk the document ────────────────────────────────────
            status_text.text("📦 Step 2/8: Chunking document…")
            progress_bar.progress(20)
            chunks, chunk_count = self.chunker.prepare_chunks(main_content, tables)
            stats["chunks"] = chunk_count
            st.session_state.chunks = chunks

            # ── Step 3: Build vector store ────────────────────────────────────
            status_text.text("🗄️ Step 3/8: Building vector store…")
            progress_bar.progress(30)
            self.vector_store.initialize()
            self.vector_store.store_chunks(chunks)

            # ── Step 4: Retrieve relevant chunks ──────────────────────────────
            # Use the summarization TASK as the retrieval query so the most
            # relevant chunks for the task are fetched.
            status_text.text("🔍 Step 4/8: Retrieving relevant chunks…")
            progress_bar.progress(40)
            contexts, distances = self.vector_store.retrieve(self.config.TASK)
            st.session_state.retrieved_contexts  = contexts
            st.session_state.retrieval_distances = distances
            self.vector_store.cleanup()

            # ── Step 5: RAG summary ───────────────────────────────────────────
            status_text.text("📝 Step 5/8: Generating RAG summary…")
            progress_bar.progress(55)
            rag_summary, rag_latency = self.summarizer.generate_rag_summary(
                self.config.TASK, contexts
            )

            # ── Step 6: Non-RAG summary ───────────────────────────────────────
            status_text.text("📝 Step 6/8: Generating Non-RAG summary…")
            progress_bar.progress(70)
            non_rag_summary, non_rag_latency = self.summarizer.generate_non_rag_summary(
                self.config.TASK, main_content
            )

            # ── Step 7: Evaluate RAG ──────────────────────────────────────────
            status_text.text("📊 Step 7/8: Computing RAG metrics…")
            progress_bar.progress(82)
            rag_lexical  = self.evaluator.compute_lexical_metrics(rag_summary,    self.config.REFERENCE_SUMMARY)
            rag_semantic = self.evaluator.compute_semantic_metrics(rag_summary,   self.config.REFERENCE_SUMMARY)
            rag_ragas    = self.evaluator.compute_ragas_metrics(
                self.config.TASK, rag_summary, contexts, self.config.REFERENCE_SUMMARY
            )
            rag_metrics = {**rag_lexical, **rag_semantic, **rag_ragas}

            # ── Step 8: Evaluate Non-RAG ──────────────────────────────────────
            status_text.text("📊 Step 8/8: Computing Non-RAG metrics…")
            progress_bar.progress(95)
            non_rag_lexical  = self.evaluator.compute_lexical_metrics(non_rag_summary,  self.config.REFERENCE_SUMMARY)
            non_rag_semantic = self.evaluator.compute_semantic_metrics(non_rag_summary, self.config.REFERENCE_SUMMARY)
            non_rag_metrics  = {**non_rag_lexical, **non_rag_semantic}

            # ── Compile results ───────────────────────────────────────────────
            status_text.text("✅ Pipeline completed!")
            progress_bar.progress(100)

            results = {
                "config": {
                    "task":              self.config.TASK,
                    "summary_constraint": self.config.SUMMARY_CONSTRAINT,
                    "reference_summary": self.config.REFERENCE_SUMMARY,
                    "model":             self.config.OLLAMA_MODEL,
                    "embedding_model":   self.config.EMBEDDING_MODEL,
                    "chunk_size":        self.config.CHUNK_SIZE,
                    "chunk_overlap":     self.config.CHUNK_OVERLAP,
                    "top_k":             self.config.TOP_K,
                },
                "extraction_stats": stats,
                "summaries": {
                    "rag": {
                        "text":          rag_summary,
                        "latency":       rag_latency,
                        "contexts_used": len(contexts),
                    },
                    "non_rag": {
                        "text":        non_rag_summary,
                        "latency":     non_rag_latency,
                        "input_words": len(main_content.split()),
                    },
                },
                "metrics": {
                    "rag":     rag_metrics,
                    "non_rag": non_rag_metrics,
                },
            }

            with open(self.config.RESULTS_PATH, "w") as f:
                json.dump(results, f, indent=2, default=str)

            return results

        except Exception as e:
            self.vector_store.cleanup()
            raise e