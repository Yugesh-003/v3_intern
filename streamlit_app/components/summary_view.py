# =============================================================================
# Section 3 — Summary Comparison
# =============================================================================

import streamlit as st
import plotly.graph_objects as go


def render_summary_comparison_section():
    """Section 3: task banner + side-by-side RAG vs Non-RAG + reference."""

    if "results" not in st.session_state or not st.session_state.results:
        st.warning("No summaries available. Run the pipeline first.")
        return

    results   = st.session_state.results
    summaries = results["summaries"]
    cfg       = results["config"]

    rag_sum    = summaries["rag"]
    nonrag_sum = summaries["non_rag"]

    # ── Task banner ───────────────────────────────────────────────────────────
    task       = cfg.get("task", cfg.get("query", "—"))
    constraint = cfg.get("summary_constraint", "—")

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1c2128, #161b22);
        border: 1px solid #30363d;
        border-left: 4px solid #a371f7;
        border-radius: 10px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.2rem;
    ">
      <div style="font-size:0.72rem; color:#8b949e; font-weight:600;
                  text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.3rem;">
        Summarization Task
      </div>
      <div style="font-size:1rem; color:#e6edf3; font-weight:600;">
        {task}
      </div>
      <div style="font-size:0.8rem; color:#a371f7; margin-top:0.2rem;">
        Constraint: <strong>{constraint}</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Latency metrics ───────────────────────────────────────────────────────
    l1, l2, l3 = st.columns(3)
    with l1:
        st.metric("⏱️ RAG Latency",    f"{rag_sum['latency']:.2f}s")
    with l2:
        st.metric("⏱️ Non-RAG Latency", f"{nonrag_sum['latency']:.2f}s")
    with l3:
        rag_wc    = len(rag_sum["text"].split())
        nonrag_wc = len(nonrag_sum["text"].split())
        faster    = "RAG" if rag_sum["latency"] <= nonrag_sum["latency"] else "Non-RAG"
        st.metric("🏆 Faster", faster)

    # ── Latency bar chart ─────────────────────────────────────────────────────
    fig_lat = go.Figure(data=[go.Bar(
        x=["RAG", "Non-RAG"],
        y=[rag_sum["latency"], nonrag_sum["latency"]],
        text=[f"{rag_sum['latency']:.2f}s", f"{nonrag_sum['latency']:.2f}s"],
        textposition="auto",
        marker_color=["#58a6ff", "#f78166"],
        marker_line=dict(color="#30363d", width=1),
        width=0.4,
    )])
    fig_lat.update_layout(
        title=dict(text="Generation Latency", font=dict(color="#e6edf3", size=13)),
        xaxis=dict(color="#8b949e", gridcolor="#21262d"),
        yaxis=dict(title="Seconds", color="#8b949e", gridcolor="#21262d"),
        plot_bgcolor="#0d1117",
        paper_bgcolor="#161b22",
        font=dict(color="#e6edf3"),
        height=260,
        margin=dict(l=40, r=20, t=50, b=30),
    )
    st.plotly_chart(fig_lat, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Side-by-side summary cards ────────────────────────────────────────────
    col_rag, col_nonrag = st.columns(2)

    def _card(col, label, color, summary_obj, extra, key_sfx):
        with col:
            wc = len(summary_obj["text"].split())
            lc = len([l for l in summary_obj["text"].splitlines() if l.strip()])
            st.markdown(f"""
            <div style="
                border-top: 3px solid {color};
                background: #161b22;
                border-radius: 10px;
                padding: 1rem 1.2rem 0.6rem 1.2rem;
                margin-bottom: 0.6rem;
            ">
              <div style="font-weight:700; color:#e6edf3; font-size:0.95rem;">{label}</div>
              <div style="font-size:0.78rem; color:#8b949e; margin-top:0.2rem;">
                ⏱ {summary_obj['latency']:.2f}s &nbsp;·&nbsp;
                📝 {wc} words &nbsp;·&nbsp;
                📄 {lc} lines &nbsp;·&nbsp;
                {extra}
              </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Read Summary", expanded=True):
                st.text_area(
                    f"{label}_text",
                    value=summary_obj["text"],
                    height=280,
                    disabled=True,
                    key=f"sum_{key_sfx}",
                    label_visibility="collapsed",
                )

    _card(col_rag,    "🎯 RAG Summary",    "#58a6ff", rag_sum,
          f"contexts: {rag_sum.get('contexts_used', '—')}", "rag")
    _card(col_nonrag, "📄 Non-RAG Summary","#f78166", nonrag_sum,
          f"input words: {nonrag_sum.get('input_words', 0):,}", "nonrag")

    # ── Reference summary (always visible) ───────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    ref_text = cfg.get("reference_summary", "")
    ref_wc   = len(ref_text.split())
    ref_lc   = len([l for l in ref_text.splitlines() if l.strip()])

    st.markdown(f"""
    <div style="
        background: #161b22;
        border: 1px solid #3fb950;
        border-radius: 10px;
        padding: 1rem 1.4rem;
    ">
      <div style="font-weight:700; color:#3fb950; font-size:0.95rem; margin-bottom:0.3rem;">
        ✅ Your Reference Summary (Ground Truth)
      </div>
      <div style="font-size:0.78rem; color:#8b949e; margin-bottom:0.7rem;">
        📝 {ref_wc} words &nbsp;·&nbsp; 📄 {ref_lc} lines
      </div>
      <div style="color:#c9d1d9; font-size:0.9rem; white-space:pre-wrap;
                  line-height:1.7; font-family:'Inter', sans-serif;">
{ref_text}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick comparison insights ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    ic1, ic2 = st.columns(2)
    with ic1:
        st.markdown("""
        <div class="feature-card">
          <h4>✅ RAG Advantages</h4>
          <ul>
            <li>Grounded in retrieved chunks only</li>
            <li>Lower hallucination risk</li>
            <li>Traceable to source passages</li>
            <li>Stays within document scope</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with ic2:
        st.markdown("""
        <div class="feature-card">
          <h4>⚠️ Non-RAG Limitations</h4>
          <ul>
            <li>Uses the entire document text</li>
            <li>May blend irrelevant sections</li>
            <li>Higher hallucination risk</li>
            <li>Harder to verify claims</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)