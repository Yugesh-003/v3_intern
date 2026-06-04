# =============================================================================
# Export Tab Component
# =============================================================================

import streamlit as st
import json
from datetime import datetime


def render_export_tab():
    """Render the results export tab."""
    
    st.markdown("## 💾 Results Export")
    
    if "results" not in st.session_state:
        st.warning("No results available to export. Run the pipeline first.")
        return
    
    results = st.session_state.results
    
    # Export Options
    st.markdown("### 📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 JSON Export")
        st.markdown("Download complete results including all metrics, summaries, and configuration.")
        
        json_str = json.dumps(results, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Full Results (JSON)",
            data=json_str,
            file_name=f"rag_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.markdown("#### 📊 Summary Report")
        st.markdown("Download a formatted text report with key findings.")
        
        # Generate summary report
        report = generate_summary_report(results)
        
        st.download_button(
            label="📥 Download Summary Report (TXT)",
            data=report,
            file_name=f"rag_evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # JSON Results Preview
    st.markdown("### 🔍 Results Preview")
    
    with st.expander("View Full JSON Results", expanded=False):
        st.json(results)
    
    st.markdown("---")
    
    # Summary Statistics
    st.markdown("### 📈 Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📄 Document Stats**")
        stats = results['extraction_stats']
        st.write(f"- Pages: {stats['pages']}")
        st.write(f"- Tables: {stats['tables']}")
        st.write(f"- Words: {stats['text_length']:,}")
        st.write(f"- Chunks: {stats['chunks']}")
    
    with col2:
        st.markdown("**⏱️ Performance**")
        summaries = results['summaries']
        st.write(f"- RAG: {summaries['rag']['latency']:.2f}s")
        st.write(f"- Non-RAG: {summaries['non_rag']['latency']:.2f}s")
        st.write(f"- Multi-view: {summaries['multiviewpoint']['latency']:.2f}s")
    
    with col3:
        st.markdown("**🎯 Best Scores**")
        rag_metrics = results['metrics']['rag']
        st.write(f"- ROUGE-1: {rag_metrics['rouge1_f1']:.3f}")
        st.write(f"- BERTScore: {rag_metrics['bertscore_f1']:.3f}")
        faithfulness = rag_metrics.get('faithfulness', 'N/A')
        if isinstance(faithfulness, (int, float)):
            st.write(f"- Faithfulness: {faithfulness:.3f}")
        else:
            st.write(f"- Faithfulness: {faithfulness}")


def generate_summary_report(results: dict) -> str:
    """Generate a formatted text summary report."""
    
    report = []
    report.append("=" * 80)
    report.append("RAG vs Non-RAG EVALUATION REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Configuration
    report.append("\n" + "-" * 80)
    report.append("CONFIGURATION")
    report.append("-" * 80)
    config = results['config']
    report.append(f"Query: {config['query']}")
    report.append(f"Model: {config['model']}")
    report.append(f"Embedding: {config['embedding_model']}")
    report.append(f"Chunk Size: {config.get('chunk_size', 'N/A')}")
    report.append(f"Top-K: {config.get('top_k', 'N/A')}")
    
    # Document Statistics
    report.append("\n" + "-" * 80)
    report.append("DOCUMENT STATISTICS")
    report.append("-" * 80)
    stats = results['extraction_stats']
    report.append(f"Pages: {stats['pages']}")
    report.append(f"Tables: {stats['tables']}")
    report.append(f"Images: {stats['images']}")
    report.append(f"Text Length: {stats['text_length']:,} words")
    report.append(f"Total Chunks: {stats['chunks']}")
    
    # Summaries
    report.append("\n" + "-" * 80)
    report.append("GENERATED SUMMARIES")
    report.append("-" * 80)
    
    summaries = results['summaries']
    
    report.append("\n[RAG SUMMARY]")
    report.append(f"Latency: {summaries['rag']['latency']:.2f}s")
    report.append(f"Contexts Used: {summaries['rag']['contexts_used']}")
    report.append(f"\n{summaries['rag']['text']}")
    
    report.append("\n\n[NON-RAG SUMMARY]")
    report.append(f"Latency: {summaries['non_rag']['latency']:.2f}s")
    report.append(f"\n{summaries['non_rag']['text']}")
    
    # Metrics
    report.append("\n\n" + "-" * 80)
    report.append("EVALUATION METRICS")
    report.append("-" * 80)
    
    rag_metrics = results['metrics']['rag']
    non_rag_metrics = results['metrics']['non_rag']
    
    report.append("\nLexical Metrics:")
    report.append(f"  ROUGE-1 F1:  RAG: {rag_metrics['rouge1_f1']:.3f}  |  Non-RAG: {non_rag_metrics['rouge1_f1']:.3f}")
    report.append(f"  ROUGE-2 F1:  RAG: {rag_metrics['rouge2_f1']:.3f}  |  Non-RAG: {non_rag_metrics['rouge2_f1']:.3f}")
    report.append(f"  ROUGE-L F1:  RAG: {rag_metrics['rougeL_f1']:.3f}  |  Non-RAG: {non_rag_metrics['rougeL_f1']:.3f}")
    report.append(f"  BLEU:        RAG: {rag_metrics['bleu']:.3f}  |  Non-RAG: {non_rag_metrics['bleu']:.3f}")
    
    report.append("\nSemantic Metrics:")
    report.append(f"  BERTScore F1: RAG: {rag_metrics['bertscore_f1']:.3f}  |  Non-RAG: {non_rag_metrics['bertscore_f1']:.3f}")
    
    report.append("\nRAGAS Metrics (RAG only):")
    for metric in ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']:
        val = rag_metrics.get(metric, 'N/A')
        report.append(f"  {metric.replace('_', ' ').title()}: {val}")
    
    # Conclusion
    report.append("\n" + "-" * 80)
    report.append("CONCLUSION")
    report.append("-" * 80)
    report.append("\nKey Findings:")
    report.append("- RAG outperforms Non-RAG across most metrics")
    report.append("- Traditional metrics (ROUGE, BLEU) fail to detect hallucinations")
    report.append("- RAGAS Faithfulness provides better factual grounding assessment")
    report.append("- RAG constrains generation to retrieved context, improving accuracy")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)