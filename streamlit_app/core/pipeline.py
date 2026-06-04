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
    """Main orchestrator for the complete RAG vs Non-RAG comparison pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.extractor = PDFExtractor(config)
        self.chunker = TextChunker(config)
        self.vector_store = VectorStore(config)
        self.summarizer = SummarizationPipeline(config)
        self.evaluator = MetricsEvaluator(config)
    
    def run_complete_pipeline_with_progress(self) -> Dict[str, Any]:
        """Execute the complete RAG vs Non-RAG comparison pipeline with Streamlit progress tracking."""
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. Extract PDF content
            status_text.text("📄 Step 1/9: Extracting PDF content...")
            progress_bar.progress(10)
            main_content, tables, stats = self.extractor.extract_content(self.config.PDF_PATH)
            
            # Store intermediate results in session state
            st.session_state.main_content = main_content
            st.session_state.tables = tables
            st.session_state.extraction_stats = stats
            
            # 2. Prepare chunks
            status_text.text("📦 Step 2/9: Preparing chunks...")
            progress_bar.progress(20)
            chunks, chunk_count = self.chunker.prepare_chunks(main_content, tables)
            stats["chunks"] = chunk_count
            st.session_state.chunks = chunks
            
            # 3. Build vector store
            status_text.text("🔍 Step 3/9: Building vector store...")
            progress_bar.progress(30)
            self.vector_store.initialize()
            self.vector_store.store_chunks(chunks)
            
            # 4. Retrieve contexts
            status_text.text("🔍 Step 4/9: Retrieving relevant contexts...")
            progress_bar.progress(40)
            contexts, distances = self.vector_store.retrieve(self.config.QUERY)
            st.session_state.retrieved_contexts = contexts
            st.session_state.retrieval_distances = distances
            
            # Clean up vector store resources after retrieval is complete
            self.vector_store.cleanup()
            
            # 5. Generate RAG summary
            status_text.text("📝 Step 5/9: Generating RAG summary...")
            progress_bar.progress(50)
            rag_summary, rag_latency = self.summarizer.generate_rag_summary(self.config.QUERY, contexts)
            
            # 6. Generate Non-RAG summary
            status_text.text("📝 Step 6/9: Generating Non-RAG summary...")
            progress_bar.progress(60)
            non_rag_summary, non_rag_latency = self.summarizer.generate_non_rag_summary(self.config.QUERY, main_content)
            
            # 7. Generate multi-viewpoint summary
            status_text.text("📝 Step 7/9: Generating multi-viewpoint summary...")
            progress_bar.progress(70)
            multiview_summary, multiview_latency = self.summarizer.generate_multiviewpoint_summary(contexts)
            
            # 8. Evaluate RAG summary
            status_text.text("📊 Step 8/9: Computing RAG metrics...")
            progress_bar.progress(80)
            rag_lexical = self.evaluator.compute_lexical_metrics(rag_summary, self.config.REFERENCE_SUMMARY)
            rag_semantic = self.evaluator.compute_semantic_metrics(rag_summary, self.config.REFERENCE_SUMMARY)
            rag_ragas = self.evaluator.compute_ragas_metrics(
                self.config.QUERY, rag_summary, contexts, self.config.REFERENCE_SUMMARY
            )
            rag_metrics = {**rag_lexical, **rag_semantic, **rag_ragas}
            
            # 9. Evaluate Non-RAG summary
            status_text.text("📊 Step 9/9: Computing Non-RAG metrics...")
            progress_bar.progress(90)
            non_rag_lexical = self.evaluator.compute_lexical_metrics(non_rag_summary, self.config.REFERENCE_SUMMARY)
            non_rag_semantic = self.evaluator.compute_semantic_metrics(non_rag_summary, self.config.REFERENCE_SUMMARY)
            non_rag_metrics = {**non_rag_lexical, **non_rag_semantic}
            
            # Compile results
            status_text.text("✅ Pipeline completed successfully!")
            progress_bar.progress(100)
            
            results = {
                "config": {
                    "query": self.config.QUERY,
                    "reference_summary": self.config.REFERENCE_SUMMARY,
                    "model": self.config.OLLAMA_MODEL,
                    "embedding_model": self.config.EMBEDDING_MODEL,
                    "chunk_size": self.config.CHUNK_SIZE,
                    "chunk_overlap": self.config.CHUNK_OVERLAP,
                    "top_k": self.config.TOP_K
                },
                "extraction_stats": stats,
                "summaries": {
                    "rag": {
                        "text": rag_summary,
                        "latency": rag_latency,
                        "contexts_used": len(contexts)
                    },
                    "non_rag": {
                        "text": non_rag_summary,
                        "latency": non_rag_latency,
                        "input_words": self.config.NON_RAG_TRUNCATE
                    },
                    "multiviewpoint": {
                        "text": multiview_summary,
                        "latency": multiview_latency
                    }
                },
                "metrics": {
                    "rag": rag_metrics,
                    "non_rag": non_rag_metrics
                }
            }
            
            # Save to file
            with open(self.config.RESULTS_PATH, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            return results
            
        except Exception as e:
            # Clean up on error
            self.vector_store.cleanup()
            raise e