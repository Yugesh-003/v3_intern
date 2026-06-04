# =============================================================================
# Retrieval View Tab Component
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def render_retrieval_tab():
    """Render the Vector Store & Retrieval tab."""
    
    st.markdown("## 🔍 Vector Store & Retrieval Analysis")
    
    if "chunks" not in st.session_state:
        st.warning("No vector store data available. Run the pipeline first.")
        return
    
    chunks = st.session_state.chunks
    
    # Chunk Statistics
    st.markdown("### 📦 Generated Chunks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Chunks Created", len(chunks))
        text_chunks = [c for c in chunks if c['type'] == 'text']
        st.metric("Text Chunks", len(text_chunks))
    
    with col2:
        table_chunks = [c for c in chunks if c['type'] == 'table']
        st.metric("Table Chunks", len(table_chunks))
        avg_length = sum(len(c['content']) for c in chunks) / len(chunks) if chunks else 0
        st.metric("Avg Chunk Length", f"{int(avg_length)} chars")
    
    # Show all chunks
    with st.expander("📋 View All Chunks"):
        for idx, chunk in enumerate(chunks):
            st.markdown(f"**Chunk {idx + 1}** - Type: `{chunk['type']}` | ID: `{chunk['id']}`")
            st.text_area(
                f"Content",
                value=chunk['content'][:500] + ("..." if len(chunk['content']) > 500 else ""),
                height=150,
                disabled=True,
                key=f"all_chunks_{idx}"
            )
            st.markdown("---")
    
    st.markdown("---")
    
    # Retrieved Chunks Analysis
    if "retrieved_contexts" in st.session_state:
        st.markdown("### 🎯 Retrieved Contexts for Query")
        
        st.info(f"**Query:** {st.session_state.results['config']['query']}")
        
        contexts = st.session_state.retrieved_contexts
        distances = st.session_state.retrieval_distances
        
        # Retrieval metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Contexts Retrieved", len(contexts))
        
        with col2:
            avg_distance = sum(distances) / len(distances) if distances else 0
            st.metric("Avg Distance", f"{avg_distance:.4f}")
        
        with col3:
            # Convert distance to similarity (1 - normalized distance)
            avg_similarity = 1 - avg_distance if distances else 0
            st.metric("Avg Similarity", f"{avg_similarity:.2%}")
        
        # Visualize retrieval scores
        st.markdown("#### 📊 Retrieval Similarity Scores")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[f"Context {i+1}" for i in range(len(distances))],
            y=[1 - d for d in distances],  # Convert to similarity
            text=[f"{(1-d):.2%}" for d in distances],
            textposition='auto',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title="Similarity Scores (Higher is Better)",
            xaxis_title="Retrieved Context",
            yaxis_title="Similarity Score",
            yaxis_range=[0, 1],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show retrieved contexts
        st.markdown("#### 📄 Retrieved Context Details")
        
        for idx, (context, distance) in enumerate(zip(contexts, distances)):
            similarity = 1 - distance
            
            with st.expander(f"Context {idx + 1} - Similarity: {similarity:.2%}", expanded=idx == 0):
                st.markdown(f"**Distance:** {distance:.4f}")
                st.markdown(f"**Similarity:** {similarity:.4f}")
                st.markdown("**Content:**")
                st.text_area(
                    f"Context {idx + 1} content",
                    value=context,
                    height=200,
                    disabled=True,
                    key=f"retrieved_context_{idx}"
                )
    
    else:
        st.warning("No retrieval data available. Run the pipeline first.")