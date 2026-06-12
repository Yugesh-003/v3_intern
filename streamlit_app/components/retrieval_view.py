# =============================================================================
# Section 2 — Retrieval Analysis
# =============================================================================

import streamlit as st
import plotly.graph_objects as go


def render_retrieval_section():
    """Render Section 2: chunking config, retrieval params, similarity scores, context preview."""

    chunks = st.session_state.get("chunks")
    if not chunks:
        st.warning("No vector store data available. Run the pipeline first.")
        return

    text_chunks = [c for c in chunks if c["type"] == "text"]
    table_chunks = [c for c in chunks if c["type"] == "table"]
    avg_length = sum(len(c["content"]) for c in chunks) / len(chunks) if chunks else 0

    # ── Chunk stats ───────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Chunks", len(chunks))
    with col2:
        st.metric("Text Chunks", len(text_chunks))
    with col3:
        st.metric("Table Chunks", len(table_chunks))
    with col4:
        st.metric("Avg Chunk Length", f"{int(avg_length)} chars")

    with st.expander("📋 All Chunks", expanded=False):
        for idx, chunk in enumerate(chunks):
            st.markdown(
                f"**Chunk {idx + 1}** &nbsp;·&nbsp; type: `{chunk['type']}` &nbsp;·&nbsp; id: `{chunk['id']}`"
            )
            st.text_area(
                f"chunk_{idx}",
                value=chunk["content"][:500] + ("…" if len(chunk["content"]) > 500 else ""),
                height=120,
                disabled=True,
                key=f"all_chunk_{idx}",
                label_visibility="collapsed"
            )
            st.markdown("---")

    # ── Retrieved contexts ────────────────────────────────────────────────────
    retrieved_contexts = st.session_state.get("retrieved_contexts")
    distances = st.session_state.get("retrieval_distances")

    if not retrieved_contexts:
        st.info("No retrieval data yet.")
        return

    st.markdown("#### 🎯 Retrieved Contexts")

    results = st.session_state.get("results", {})
    query_text = results.get("config", {}).get("query", st.session_state.get("query", ""))
    if query_text:
        st.info(f"**Query:** {query_text}")

    similarities = [max(0.0, 1 - d) for d in distances]
    avg_sim = sum(similarities) / len(similarities) if similarities else 0

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Contexts Retrieved", len(retrieved_contexts))
    with r2:
        st.metric("Avg Distance", f"{sum(distances) / len(distances):.4f}")
    with r3:
        st.metric("Avg Similarity", f"{avg_sim:.1%}")

    # ── Similarity bar chart ───────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Context {i+1}" for i in range(len(distances))],
        y=similarities,
        text=[f"{s:.1%}" for s in similarities],
        textposition="auto",
        marker=dict(
            color=similarities,
            colorscale=[[0, "#21262d"], [0.5, "#1f6feb"], [1, "#58a6ff"]],
            showscale=False,
            line=dict(color="#30363d", width=1)
        )
    ))
    fig.update_layout(
        title=dict(text="Retrieval Similarity Scores", font=dict(color="#e6edf3", size=14)),
        xaxis=dict(title="Retrieved Context", color="#8b949e", gridcolor="#21262d"),
        yaxis=dict(title="Similarity Score", range=[0, 1], color="#8b949e", gridcolor="#21262d"),
        plot_bgcolor="#0d1117",
        paper_bgcolor="#161b22",
        font=dict(color="#e6edf3"),
        height=340,
        margin=dict(l=40, r=20, t=50, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Context details ────────────────────────────────────────────────────────
    st.markdown("#### 📄 Retrieved Context Details")
    for idx, (context, distance) in enumerate(zip(retrieved_contexts, distances)):
        similarity = max(0.0, 1 - distance)
        with st.expander(
            f"Context {idx + 1}  ·  Similarity: {similarity:.1%}  ·  Distance: {distance:.4f}",
            expanded=(idx == 0)
        ):
            st.text_area(
                f"ctx_{idx}",
                value=context,
                height=190,
                disabled=True,
                key=f"ret_ctx_{idx}",
                label_visibility="collapsed"
            )