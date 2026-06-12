# =============================================================================
# Section 4 — Evaluation Metrics
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def _fmt(val):
    """Format a metric value for display."""
    if isinstance(val, (int, float)):
        return f"{val:.3f}"
    return str(val) if val is not None else "N/A"


def _delta(rag_val, nonrag_val):
    """Return (delta_str, delta_colour) for st.metric delta."""
    if isinstance(rag_val, (int, float)) and isinstance(nonrag_val, (int, float)):
        d = rag_val - nonrag_val
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.3f} vs Non-RAG", "normal"
    return None, "off"


def render_metrics_section():
    """Render Section 4: KPI metrics + gauge charts + RAGAS radar + analysis table."""

    if "results" not in st.session_state or not st.session_state.results:
        st.warning("No metrics available. Run the pipeline first.")
        return

    results = st.session_state.results
    rag    = results["metrics"]["rag"]
    nonrag = results["metrics"]["non_rag"]

    # ── Row 1: ROUGE + BLEU (4 metrics across 4 columns) ─────────────────────
    st.markdown("**📝 Lexical Metrics**")
    lc1, lc2, lc3, lc4 = st.columns(4)

    with lc1:
        d, dc = _delta(rag["rouge1_f1"], nonrag["rouge1_f1"])
        st.metric("ROUGE-1  (RAG)", _fmt(rag["rouge1_f1"]), delta=d, delta_color=dc,
                  help=f"Non-RAG: {_fmt(nonrag['rouge1_f1'])}")
    with lc2:
        d, dc = _delta(rag["rouge2_f1"], nonrag["rouge2_f1"])
        st.metric("ROUGE-2  (RAG)", _fmt(rag["rouge2_f1"]), delta=d, delta_color=dc,
                  help=f"Non-RAG: {_fmt(nonrag['rouge2_f1'])}")
    with lc3:
        d, dc = _delta(rag["rougeL_f1"], nonrag["rougeL_f1"])
        st.metric("ROUGE-L  (RAG)", _fmt(rag["rougeL_f1"]), delta=d, delta_color=dc,
                  help=f"Non-RAG: {_fmt(nonrag['rougeL_f1'])}")
    with lc4:
        d, dc = _delta(rag["bleu"], nonrag["bleu"])
        st.metric("BLEU  (RAG)", _fmt(rag["bleu"]), delta=d, delta_color=dc,
                  help=f"Non-RAG: {_fmt(nonrag['bleu'])}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Semantic + Cosine (3 columns) ──────────────────────────────────
    st.markdown("**🧠 Semantic Metrics**")
    sc1, sc2, sc3 = st.columns(3)

    with sc1:
        d, dc = _delta(rag["bertscore_f1"], nonrag["bertscore_f1"])
        st.metric("BERTScore F1  (RAG)", _fmt(rag["bertscore_f1"]), delta=d, delta_color=dc,
                  help=f"Non-RAG: {_fmt(nonrag['bertscore_f1'])}")
    with sc2:
        rag_cos    = rag.get("cosine_similarity", "N/A")
        nonrag_cos = nonrag.get("cosine_similarity", "N/A")
        d, dc = _delta(rag_cos, nonrag_cos)
        st.metric("Cosine Similarity  (RAG)", _fmt(rag_cos), delta=d, delta_color=dc,
                  help=f"Non-RAG: {_fmt(nonrag_cos)}")
    with sc3:
        faith = rag.get("faithfulness", "N/A")
        st.metric("Faithfulness  (RAG)", _fmt(faith),
                  help="RAGAS metric — RAG-only. Measures how grounded the answer is in retrieved context.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: RAGAS context metrics (3 columns) ──────────────────────────────
    st.markdown("**🎯 RAGAS Context Metrics  (RAG-only)**")
    rc1, rc2, rc3 = st.columns(3)

    with rc1:
        val = rag.get("answer_relevancy", "N/A")
        st.metric("Answer Relevancy", _fmt(val), help="Measures topical relevance of the answer to the query.")
    with rc2:
        val = rag.get("context_precision", "N/A")
        st.metric("Context Precision", _fmt(val), help="Fraction of retrieved chunks that are actually relevant.")
    with rc3:
        val = rag.get("context_recall", "N/A")
        st.metric("Context Recall", _fmt(val), help="Fraction of relevant information that was retrieved.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BERTScore gauges ──────────────────────────────────────────────────────
    st.markdown("#### 🧠 Semantic Similarity — BERTScore F1")

    def _gauge(value, title, bar_color):
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={"text": title, "font": {"size": 15, "color": "#e6edf3"}},
            number={"font": {"size": 38, "color": "#e6edf3"}},
            delta={
                "reference": 0.5,
                "increasing": {"color": "#3fb950"},
                "decreasing": {"color": "#f78166"},
            },
            gauge={
                "axis": {"range": [0, 1], "tickcolor": "#8b949e"},
                "bar": {"color": bar_color},
                "bgcolor": "#21262d",
                "bordercolor": "#30363d",
                "steps": [
                    {"range": [0, 0.5],   "color": "#1a1f2e"},
                    {"range": [0.5, 0.75],"color": "#1f2937"},
                    {"range": [0.75, 1],  "color": "#1a2e1a"},
                ],
                "threshold": {"line": {"color": "#f78166", "width": 2}, "value": 0.5},
            },
        ))
        fig.update_layout(
            height=300,
            paper_bgcolor="#161b22",
            font=dict(color="#e6edf3"),
            margin=dict(l=20, r=20, t=60, b=20),
        )
        return fig

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            _gauge(rag["bertscore_f1"], "RAG BERTScore F1", "#58a6ff"),
            use_container_width=True,
        )
    with g2:
        st.plotly_chart(
            _gauge(nonrag["bertscore_f1"], "Non-RAG BERTScore F1", "#f78166"),
            use_container_width=True,
        )

    # ── RAGAS radar ───────────────────────────────────────────────────────────
    st.markdown("#### 🎯 RAGAS Metrics Radar (RAG-Specific)")

    ragas_keys   = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
    ragas_labels = ["Faithfulness", "Answer Relevancy", "Context Recall", "Context Precision"]
    ragas_vals   = [
        v if isinstance(v := rag.get(k, 0), (int, float)) else 0
        for k in ragas_keys
    ]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=ragas_vals + [ragas_vals[0]],
        theta=ragas_labels + [ragas_labels[0]],
        fill="toself",
        name="RAG Pipeline",
        line=dict(color="#58a6ff"),
        fillcolor="rgba(88,166,255,0.15)",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0d1117",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#30363d", color="#8b949e"),
            angularaxis=dict(gridcolor="#30363d", color="#8b949e"),
        ),
        paper_bgcolor="#161b22",
        showlegend=True,
        legend=dict(font=dict(color="#e6edf3")),
        title=dict(text="RAGAS Metrics Radar", font=dict(color="#e6edf3", size=14)),
        height=420,
        font=dict(color="#e6edf3"),
        margin=dict(l=30, r=30, t=60, b=30),
    )

    radr_col, side_col = st.columns([2, 1])
    with radr_col:
        st.plotly_chart(fig_radar, use_container_width=True)
    with side_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for label, key in zip(ragas_labels, ragas_keys):
            val = rag.get(key, "N/A")
            st.metric(label, _fmt(val))

    # ── Analysis table ────────────────────────────────────────────────────────
    st.markdown("#### 📋 Metric Analysis: Why Traditional Metrics Fall Short")

    analysis_data = {
        "Metric": [
            "ROUGE-1/2/L", "BLEU", "BERTScore",
            "RAGAS Faithfulness", "RAGAS Answer Relevancy", "RAGAS Context Metrics",
        ],
        "What it Measures": [
            "Word/n-gram overlap",
            "Precision of n-grams",
            "Semantic similarity",
            "Context grounding",
            "Question relevance",
            "Retrieval quality",
        ],
        "Limitation": [
            "High scores for domain vocab even if facts are wrong",
            "Designed for translation; penalises paraphrasing",
            "Similar meaning ≠ factual correctness",
            "✅ Most reliable — checks claim support",
            "Measures topical match, not accuracy",
            "Evaluates retrieval, not generation",
        ],
        "RAG Score": [
            _fmt(rag["rouge1_f1"]),
            _fmt(rag["bleu"]),
            _fmt(rag["bertscore_f1"]),
            _fmt(rag.get("faithfulness")),
            _fmt(rag.get("answer_relevancy")),
            _fmt(rag.get("context_precision")),
        ],
        "Non-RAG Score": [
            _fmt(nonrag["rouge1_f1"]),
            _fmt(nonrag["bleu"]),
            _fmt(nonrag["bertscore_f1"]),
            "N/A", "N/A", "N/A",
        ],
    }

    df = pd.DataFrame(analysis_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Research insight ──────────────────────────────────────────────────────
    st.info(
        "**Research Question:** *\"Can current automated metrics reliably distinguish between "
        "a 'correct' answer and a 'plausible but wrong' answer?\"*\n\n"
        "**Answer: NO** — Traditional metrics (ROUGE, BLEU, BERTScore) measure surface-level "
        "similarity, not factual grounding. Only **RAGAS Faithfulness** directly checks "
        "whether the answer is supported by the retrieved context."
    )