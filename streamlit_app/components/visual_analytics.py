# =============================================================================
# Section 5 — Visual Analytics
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def render_visual_analytics_section():
    """Render Section 5: Metric bar chart, RAG vs Non-RAG performance,
    retrieval score distribution, summary length comparison."""

    if "results" not in st.session_state or not st.session_state.results:
        st.warning("No results available. Run the pipeline first.")
        return

    results = st.session_state.results
    rag     = results["metrics"]["rag"]
    nonrag  = results["metrics"]["non_rag"]
    sums    = results["summaries"]

    _DARK_LAYOUT = dict(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#161b22",
        font=dict(color="#e6edf3"),
        xaxis=dict(gridcolor="#21262d", color="#8b949e"),
        yaxis=dict(gridcolor="#21262d", color="#8b949e"),
        legend=dict(bgcolor="#1c2128", bordercolor="#30363d", font=dict(color="#e6edf3")),
        margin=dict(l=50, r=30, t=60, b=50),
    )

    # ── Row 1: Metric comparison + RAG vs Non-RAG performance ─────────────────
    row1_l, row1_r = st.columns(2)

    with row1_l:
        # All metrics side-by-side
        metric_names = ["ROUGE-1", "ROUGE-2", "ROUGE-L", "BLEU", "BERTScore"]
        rag_vals     = [rag["rouge1_f1"], rag["rouge2_f1"], rag["rougeL_f1"], rag["bleu"], rag["bertscore_f1"]]
        nonrag_vals  = [nonrag["rouge1_f1"], nonrag["rouge2_f1"], nonrag["rougeL_f1"], nonrag["bleu"], nonrag["bertscore_f1"]]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="RAG",
            x=metric_names,
            y=rag_vals,
            text=[f"{v:.3f}" for v in rag_vals],
            textposition="auto",
            marker_color="#58a6ff",
            marker_line=dict(color="#30363d", width=1),
        ))
        fig_bar.add_trace(go.Bar(
            name="Non-RAG",
            x=metric_names,
            y=nonrag_vals,
            text=[f"{v:.3f}" for v in nonrag_vals],
            textposition="auto",
            marker_color="#f78166",
            marker_line=dict(color="#30363d", width=1),
        ))
        fig_bar.update_layout(
            **_DARK_LAYOUT,
            title=dict(text="📊 Metric Comparison — RAG vs Non-RAG", font=dict(color="#e6edf3", size=14)),
            barmode="group",
            yaxis_range=[0, 1],
            height=390,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with row1_r:
        # Performance spider / filled-area chart
        categories = ["ROUGE-1", "ROUGE-2", "ROUGE-L", "BLEU", "BERTScore"]
        rag_spider  = [rag["rouge1_f1"], rag["rouge2_f1"], rag["rougeL_f1"], rag["bleu"], rag["bertscore_f1"]]
        nr_spider   = [nonrag["rouge1_f1"], nonrag["rouge2_f1"], nonrag["rougeL_f1"], nonrag["bleu"], nonrag["bertscore_f1"]]

        fig_spider = go.Figure()
        fig_spider.add_trace(go.Scatterpolar(
            r=rag_spider + [rag_spider[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="RAG",
            line=dict(color="#58a6ff"),
            fillcolor="rgba(88,166,255,0.18)",
        ))
        fig_spider.add_trace(go.Scatterpolar(
            r=nr_spider + [nr_spider[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Non-RAG",
            line=dict(color="#f78166"),
            fillcolor="rgba(247,129,102,0.12)",
        ))
        fig_spider.update_layout(
            polar=dict(
                bgcolor="#0d1117",
                radialaxis=dict(visible=True, range=[0, 1], gridcolor="#30363d", color="#8b949e"),
                angularaxis=dict(gridcolor="#30363d", color="#8b949e"),
            ),
            paper_bgcolor="#161b22",
            showlegend=True,
            legend=dict(bgcolor="#1c2128", bordercolor="#30363d", font=dict(color="#e6edf3")),
            title=dict(text="📈 Performance Profile", font=dict(color="#e6edf3", size=14)),
            height=390,
            font=dict(color="#e6edf3"),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        st.plotly_chart(fig_spider, use_container_width=True)

    # ── Row 2: Retrieval score distribution + Summary length ──────────────────
    row2_l, row2_r = st.columns(2)

    with row2_l:
        distances = st.session_state.get("retrieval_distances") or []
        if distances:
            similarities = [max(0.0, 1 - d) for d in distances]
            ctx_labels   = [f"Context {i+1}" for i in range(len(similarities))]

            fig_dist = go.Figure()
            fig_dist.add_trace(go.Bar(
                x=ctx_labels,
                y=similarities,
                text=[f"{s:.1%}" for s in similarities],
                textposition="auto",
                marker=dict(
                    color=similarities,
                    colorscale=[[0, "#21262d"], [0.5, "#1f6feb"], [1, "#58a6ff"]],
                    showscale=True,
                    colorbar=dict(
                        title="Sim.",
                        tickfont=dict(color="#8b949e"),
                        title_font=dict(color="#8b949e"),
                    ),
                    line=dict(color="#30363d", width=1),
                ),
            ))
            fig_dist.update_layout(
                **_DARK_LAYOUT,
                title=dict(text="🔍 Retrieval Score Distribution", font=dict(color="#e6edf3", size=14)),
                yaxis_range=[0, 1],
                height=370,
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("No retrieval scores available.")

    with row2_r:
        rag_wc    = len(sums["rag"]["text"].split())
        nonrag_wc = len(sums["non_rag"]["text"].split())

        ref_text = results.get("config", {}).get("reference_summary", "")
        ref_wc   = len(ref_text.split()) if ref_text else 0

        labels = ["RAG", "Non-RAG", "Reference (Human)"]
        values = [rag_wc, nonrag_wc, ref_wc]
        colors = ["#58a6ff", "#f78166", "#3fb950"]

        fig_len = go.Figure()
        fig_len.add_trace(go.Bar(
            x=labels,
            y=values,
            text=[f"{v} words" for v in values],
            textposition="auto",
            marker_color=colors,
            marker_line=dict(color="#30363d", width=1),
        ))
        fig_len.update_layout(
            **_DARK_LAYOUT,
            title=dict(text="📏 Summary Length Comparison", font=dict(color="#e6edf3", size=14)),
            yaxis_title="Word Count",
            height=370,
        )
        st.plotly_chart(fig_len, use_container_width=True)

    # ── Row 3: RAGAS metrics bar ───────────────────────────────────────────────
    st.markdown("#### 🎯 RAGAS Metrics Detail")
    ragas_keys   = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
    ragas_labels = ["Faithfulness", "Answer Relevancy", "Context Recall", "Context Precision"]
    ragas_vals   = [
        v if isinstance(v := rag.get(k, 0), (int, float)) else 0
        for k in ragas_keys
    ]

    fig_ragas = go.Figure(go.Bar(
        x=ragas_labels,
        y=ragas_vals,
        text=[f"{v:.3f}" for v in ragas_vals],
        textposition="auto",
        marker=dict(
            color=ragas_vals,
            colorscale=[[0, "#f78166"], [0.5, "#ffa500"], [1, "#3fb950"]],
            showscale=True,
            colorbar=dict(
                title="Score",
                tickfont=dict(color="#8b949e"),
                title_font=dict(color="#8b949e"),
            ),
            line=dict(color="#30363d", width=1),
        ),
    ))
    fig_ragas.update_layout(
        **_DARK_LAYOUT,
        title=dict(text="RAGAS Metrics (RAG Pipeline — higher is better)", font=dict(color="#e6edf3", size=14)),
        yaxis_range=[0, 1],
        height=340,
    )
    st.plotly_chart(fig_ragas, use_container_width=True)
