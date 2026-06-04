# =============================================================================
# PDF Analysis Tab Component
# =============================================================================

import streamlit as st
import pandas as pd


def render_pdf_analysis_tab():
    """Render the PDF Analysis tab with extraction statistics and content preview."""
    
    st.markdown("## 📄 PDF Document Analysis")
    
    if "extraction_stats" not in st.session_state:
        st.warning("No PDF analysis available. Run the pipeline first.")
        return
    
    stats = st.session_state.extraction_stats
    
    # Display statistics in metric cards
    st.markdown("### Document Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📄 Pages", stats.get("pages", 0))
    
    with col2:
        st.metric("📊 Tables", stats.get("tables", 0))
    
    with col3:
        st.metric("🖼️ Images", stats.get("images", 0))
    
    with col4:
        st.metric("📝 Words", f"{stats.get('text_length', 0):,}")
    
    with col5:
        st.metric("📦 Chunks", stats.get("chunks", 0))
    
    st.markdown("---")
    
    # Extracted Text Preview
    if "main_content" in st.session_state:
        st.markdown("### 📝 Extracted Text Preview")
        
        main_content = st.session_state.main_content
        preview_length = st.slider("Preview length (characters)", 100, 5000, 1000, 100)
        
        with st.expander("View Extracted Text", expanded=True):
            st.text_area(
                "Extracted Content",
                value=main_content[:preview_length] + ("..." if len(main_content) > preview_length else ""),
                height=300,
                disabled=True
            )
            
            if len(main_content) > preview_length:
                st.info(f"Showing {preview_length} of {len(main_content)} characters")
    
    st.markdown("---")
    
    # Extracted Tables
    if "tables" in st.session_state and st.session_state.tables:
        st.markdown("### 📊 Extracted Tables")
        
        tables = st.session_state.tables
        
        for idx, table_info in enumerate(tables):
            with st.expander(f"Table {idx + 1} (Page {table_info['page']})", expanded=idx == 0):
                df = pd.DataFrame(table_info['data'])
                st.dataframe(df, use_container_width=True)
                
                # Download button for table
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download Table {idx + 1} as CSV",
                    data=csv,
                    file_name=f"table_{idx + 1}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No tables found in the document")
    
    st.markdown("---")
    
    # Chunking Information
    if "chunks" in st.session_state:
        st.markdown("### 📦 Document Chunking Summary")
        
        chunks = st.session_state.chunks
        text_chunks = [c for c in chunks if c['type'] == 'text']
        table_chunks = [c for c in chunks if c['type'] == 'table']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Chunks", len(chunks))
        
        with col2:
            st.metric("Text Chunks", len(text_chunks))
        
        with col3:
            st.metric("Table Chunks", len(table_chunks))
        
        # Show sample chunks
        with st.expander("View Sample Chunks"):
            num_samples = min(3, len(chunks))
            
            for i in range(num_samples):
                chunk = chunks[i]
                st.markdown(f"**Chunk {i + 1} ({chunk['type']})**")
                st.text_area(
                    f"Content {i + 1}",
                    value=chunk['content'][:300] + ("..." if len(chunk['content']) > 300 else ""),
                    height=100,
                    disabled=True,
                    key=f"chunk_preview_{i}"
                )