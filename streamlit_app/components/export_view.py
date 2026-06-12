# =============================================================================
# Section 6 — Results & Export
# =============================================================================

import streamlit as st
import json
import pandas as pd
from datetime import datetime


def render_export_section():
    """Render Section 6: verdict card, best approach, download buttons, preview."""

    if "results" not in st.session_state or not st.session_state.results:
        st.warning("No results available to export. Run the pipeline first.")
        return

    results    = st.session_state.results
    rag        = results["metrics"]["rag"]
    nonrag     = results["metrics"]["non_rag"]
    sums       = results["summaries"]
    stats      = results["extraction_stats"]
    cfg        = results["config"]
    task       = cfg.get("task", cfg.get("query", "—"))
    constraint = cfg.get("summary_constraint", "—")

    # ── Verdict ───────────────────────────────────────────────────────────────
    rag_avg    = (rag["rouge1_f1"] + rag["rouge2_f1"] + rag["rougeL_f1"] + rag["bleu"] + rag["bertscore_f1"]) / 5
    nonrag_avg = (nonrag["rouge1_f1"] + nonrag["rouge2_f1"] + nonrag["rougeL_f1"] + nonrag["bleu"] + nonrag["bertscore_f1"]) / 5
    best       = "RAG" if rag_avg >= nonrag_avg else "Non-RAG"
    diff       = abs(rag_avg - nonrag_avg)

    faithfulness = rag.get("faithfulness")
    faithfulness_note = (
        f"RAGAS Faithfulness is **{faithfulness:.3f}**, indicating the RAG "
        f"summary is {'well' if isinstance(faithfulness, float) and faithfulness > 0.6 else 'partially'} grounded in the retrieved context."
        if isinstance(faithfulness, (int, float)) else
        "RAGAS Faithfulness could not be computed for this run."
    )

    st.markdown(f"""
    <div class="verdict-card">
      <div class="verdict-title">🏆 Final Evaluation Verdict</div>
      <div class="verdict-text">
        <strong>Task:</strong> {task}<br>
        <strong>Constraint:</strong> {constraint}<br><br>
        <strong>{best}</strong> outperforms on average lexical + semantic metrics
        by <strong>{diff:.3f}</strong> points
        (RAG avg: {rag_avg:.3f} &nbsp;·&nbsp; Non-RAG avg: {nonrag_avg:.3f}).<br><br>
        {faithfulness_note}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick summary ─────────────────────────────────────────────────────────
    vs1, vs2, vs3 = st.columns(3)
    with vs1:
        st.markdown("**📄 Document Stats**")
        st.write(f"• Pages: {stats['pages']}")
        st.write(f"• Tables: {stats['tables']}")
        st.write(f"• Words: {stats['text_length']:,}")
        st.write(f"• Chunks: {stats['chunks']}")

    with vs2:
        st.markdown("**⏱️ Performance**")
        st.write(f"• RAG latency: {sums['rag']['latency']:.2f}s")
        st.write(f"• Non-RAG latency: {sums['non_rag']['latency']:.2f}s")

    with vs3:
        st.markdown("**🎯 Best Scores (RAG)**")
        st.write(f"• ROUGE-1: {rag['rouge1_f1']:.3f}")
        st.write(f"• BERTScore: {rag['bertscore_f1']:.3f}")
        faith_val = rag.get("faithfulness", "N/A")
        st.write(f"• Faithfulness: {faith_val:.3f}" if isinstance(faith_val, (int, float)) else f"• Faithfulness: {faith_val}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download buttons ───────────────────────────────────────────────────────
    st.markdown("#### 📥 Export Results")
    dl1, dl2, dl3 = st.columns(3)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    with dl1:
        json_str = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"rag_results_{ts}.json",
            mime="application/json",
            use_container_width=True
        )

    with dl2:
        csv_data = _build_csv(results)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"rag_metrics_{ts}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with dl3:
        report_txt = _build_report(results)
        st.download_button(
            label="📋 Download Report (TXT)",
            data=report_txt,
            file_name=f"rag_report_{ts}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # ── JSON preview ──────────────────────────────────────────────────────────
    with st.expander("🔍 Full JSON Results Preview", expanded=False):
        st.json(results)


# =============================================================================
# Helpers
# =============================================================================

def _build_csv(results: dict) -> str:
    rag    = results["metrics"]["rag"]
    nonrag = results["metrics"]["non_rag"]
    rows = [
        {"Metric": "ROUGE-1",   "RAG": rag["rouge1_f1"],    "Non-RAG": nonrag["rouge1_f1"]},
        {"Metric": "ROUGE-2",   "RAG": rag["rouge2_f1"],    "Non-RAG": nonrag["rouge2_f1"]},
        {"Metric": "ROUGE-L",   "RAG": rag["rougeL_f1"],    "Non-RAG": nonrag["rougeL_f1"]},
        {"Metric": "BLEU",      "RAG": rag["bleu"],          "Non-RAG": nonrag["bleu"]},
        {"Metric": "BERTScore", "RAG": rag["bertscore_f1"],  "Non-RAG": nonrag["bertscore_f1"]},
        {"Metric": "Faithfulness",      "RAG": rag.get("faithfulness", "N/A"),      "Non-RAG": "N/A"},
        {"Metric": "Answer Relevancy",  "RAG": rag.get("answer_relevancy", "N/A"),  "Non-RAG": "N/A"},
        {"Metric": "Context Recall",    "RAG": rag.get("context_recall", "N/A"),    "Non-RAG": "N/A"},
        {"Metric": "Context Precision", "RAG": rag.get("context_precision", "N/A"), "Non-RAG": "N/A"},
    ]
    return pd.DataFrame(rows).to_csv(index=False)


def _build_report(results: dict) -> str:
    rag    = results["metrics"]["rag"]
    nonrag = results["metrics"]["non_rag"]
    sums   = results["summaries"]
    stats  = results["extraction_stats"]
    cfg    = results["config"]

    lines = [
        "=" * 80,
        "RAG vs Non-RAG EVALUATION REPORT",
        "=" * 80,
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "-" * 80, "CONFIGURATION", "-" * 80,
        f"Task:        {cfg.get('task', cfg.get('query','N/A'))}",
        f"Constraint:  {cfg.get('summary_constraint','N/A')}",
        f"Model:       {cfg.get('model','N/A')}",
        f"Embedding:   {cfg.get('embedding_model','N/A')}",
        f"Chunk Size:  {cfg.get('chunk_size','N/A')}",
        f"Top-K:       {cfg.get('top_k','N/A')}",
        "-" * 80, "DOCUMENT STATISTICS", "-" * 80,
        f"Pages:       {stats['pages']}",
        f"Tables:      {stats['tables']}",
        f"Images:      {stats['images']}",
        f"Words:       {stats['text_length']:,}",
        f"Chunks:      {stats['chunks']}",
        "-" * 80, "GENERATED SUMMARIES", "-" * 80,
        "\n[RAG SUMMARY]",
        f"Latency: {sums['rag']['latency']:.2f}s  |  Contexts: {sums['rag']['contexts_used']}",
        sums['rag']['text'],
        "\n[NON-RAG SUMMARY]",
        f"Latency: {sums['non_rag']['latency']:.2f}s",
        sums['non_rag']['text'],
        "\n[HUMAN REFERENCE (Option A)]",
        cfg.get('reference_summary', 'N/A'),
        "-" * 80, "EVALUATION METRICS", "-" * 80,
        f"  ROUGE-1:   RAG {rag['rouge1_f1']:.3f}  |  Non-RAG {nonrag['rouge1_f1']:.3f}",
        f"  ROUGE-2:   RAG {rag['rouge2_f1']:.3f}  |  Non-RAG {nonrag['rouge2_f1']:.3f}",
        f"  ROUGE-L:   RAG {rag['rougeL_f1']:.3f}  |  Non-RAG {nonrag['rougeL_f1']:.3f}",
        f"  BLEU:      RAG {rag['bleu']:.3f}  |  Non-RAG {nonrag['bleu']:.3f}",
        f"  BERTScore: RAG {rag['bertscore_f1']:.3f}  |  Non-RAG {nonrag['bertscore_f1']:.3f}",
        "\nRAGAS (RAG-only):",
    ]
    for key in ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]:
        val = rag.get(key, "N/A")
        lines.append(f"  {key.replace('_',' ').title()}: {val}")

    lines += [
        "-" * 80, "KEY FINDINGS", "-" * 80,
        "- Traditional metrics (ROUGE, BLEU) fail to detect hallucinations",
        "- RAGAS Faithfulness provides better factual grounding assessment",
        "- RAG constrains generation to retrieved context, improving accuracy",
        "=" * 80, "END OF REPORT", "=" * 80,
    ]
    return "\n".join(lines)