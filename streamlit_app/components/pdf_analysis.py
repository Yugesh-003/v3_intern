# =============================================================================
# Section 1 — Document Overview
# =============================================================================

import streamlit as st
import pandas as pd


def render_document_overview_section():
    """Render Section 1: Document statistics cards + extracted text preview."""

    if "extraction_stats" not in st.session_state or not st.session_state.extraction_stats:
        st.warning("No PDF analysis available. Run the pipeline first.")
        return

    stats = st.session_state.extraction_stats

    # ── Stat cards ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)

    stat_items = [
        (c1, "📄", stats.get("pages", 0), "Pages"),
        (c2, "📊", stats.get("tables", 0), "Tables"),
        (c3, "🖼️", stats.get("images", 0), "Images"),
        (c4, "📝", f"{stats.get('text_length', 0):,}", "Words"),
        (c5, "📦", stats.get("chunks", 0), "Chunks"),
    ]

    for col, icon, value, label in stat_items:
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div class="stat-card-icon">{icon}</div>
              <div class="stat-card-value">{value}</div>
              <div class="stat-card-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Extracted text preview ────────────────────────────────────────────────
    if "main_content" in st.session_state and st.session_state.main_content:
        main_content = st.session_state.main_content

        with st.expander("📝 Extracted Text Preview", expanded=True):
            col_left, col_right = st.columns([4, 1])
            with col_right:
                preview_len = st.select_slider(
                    "Characters",
                    options=[200, 500, 1000, 2000, 5000],
                    value=1000,
                    label_visibility="collapsed"
                )
            with col_left:
                st.caption(f"Showing {min(preview_len, len(main_content)):,} of {len(main_content):,} characters")

            st.text_area(
                "Extracted Content",
                value=main_content[:preview_len] + ("…" if len(main_content) > preview_len else ""),
                height=260,
                disabled=True,
                label_visibility="collapsed"
            )

    # ── Extracted tables ──────────────────────────────────────────────────────
    tables = st.session_state.get("tables")
    if tables:
        st.markdown("**📊 Extracted Tables**")
        for idx, table_info in enumerate(tables):
            with st.expander(f"Table {idx + 1}  ·  Page {table_info['page']}", expanded=idx == 0):
                df = pd.DataFrame(table_info["data"])
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download Table {idx + 1} as CSV",
                    data=csv,
                    file_name=f"table_{idx + 1}.csv",
                    mime="text/csv",
                    key=f"dl_table_{idx}"
                )
    else:
        st.info("No tables detected in the document.")

    # ── Chunking summary ──────────────────────────────────────────────────────
    chunks = st.session_state.get("chunks")
    if chunks:
        text_chunks = [c for c in chunks if c["type"] == "text"]
        table_chunks = [c for c in chunks if c["type"] == "table"]

        st.markdown("**📦 Chunking Summary**")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Chunks", len(chunks))
        with m2:
            st.metric("Text Chunks", len(text_chunks))
        with m3:
            st.metric("Table Chunks", len(table_chunks))

        with st.expander("View Sample Chunks"):
            for i in range(min(3, len(chunks))):
                chunk = chunks[i]
                st.markdown(f"**Chunk {i + 1}** · type: `{chunk['type']}`")
                st.text_area(
                    f"Chunk {i + 1} content",
                    value=chunk["content"][:300] + ("…" if len(chunk["content"]) > 300 else ""),
                    height=90,
                    disabled=True,
                    key=f"chunk_prev_{i}",
                    label_visibility="collapsed"
                )