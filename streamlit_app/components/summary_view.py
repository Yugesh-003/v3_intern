# =============================================================================
# Summaries Tab Component
# =============================================================================

import streamlit as st
import plotly.graph_objects as go


def render_summaries_tab():
    """Render the Summaries comparison tab."""
    
    st.markdown("## 📝 Summary Comparison")
    
    if "results" not in st.session_state:
        st.warning("No summaries available. Run the pipeline first.")
        return
    
    results = st.session_state.results
    summaries = results['summaries']
    
    # Latency Comparison Chart
    st.markdown("### ⏱️ Generation Latency Comparison")
    
    latencies = {
        'RAG': summaries['rag']['latency'],
        'Non-RAG': summaries['non_rag']['latency'],
        'Multi-Viewpoint': summaries['multiviewpoint']['latency']
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(latencies.keys()),
            y=list(latencies.values()),
            text=[f"{v:.2f}s" for v in latencies.values()],
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
    ])
    
    fig.update_layout(
        title="Summary Generation Time",
        xaxis_title="Method",
        yaxis_title="Latency (seconds)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Side-by-side summary comparison
    st.markdown("### 📊 Summary Outputs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 RAG Summary")
        st.markdown(f"**Latency:** {summaries['rag']['latency']:.2f}s")
        st.markdown(f"**Contexts Used:** {summaries['rag']['contexts_used']}")
        
        with st.container():
            st.text_area(
                "RAG Generated Summary",
                value=summaries['rag']['text'],
                height=400,
                disabled=True,
                key="rag_summary_display"
            )
        
        # Word count
        word_count = len(summaries['rag']['text'].split())
        st.info(f"📊 Word Count: {word_count}")
    
    with col2:
        st.markdown("#### 📄 Non-RAG Summary")
        st.markdown(f"**Latency:** {summaries['non_rag']['latency']:.2f}s")
        st.markdown(f"**Input Words:** {summaries['non_rag']['input_words']:,}")
        
        with st.container():
            st.text_area(
                "Non-RAG Generated Summary",
                value=summaries['non_rag']['text'],
                height=400,
                disabled=True,
                key="non_rag_summary_display"
            )
        
        # Word count
        word_count = len(summaries['non_rag']['text'].split())
        st.info(f"📊 Word Count: {word_count}")
    
    with col3:
        st.markdown("#### 🎭 Multi-Viewpoint Summary")
        st.markdown(f"**Latency:** {summaries['multiviewpoint']['latency']:.2f}s")
        st.markdown("**Perspectives:** Bull / Bear / Neutral")
        
        with st.container():
            st.text_area(
                "Multi-Viewpoint Analysis",
                value=summaries['multiviewpoint']['text'],
                height=400,
                disabled=True,
                key="multiview_summary_display"
            )
        
        # Word count
        word_count = len(summaries['multiviewpoint']['text'].split())
        st.info(f"📊 Word Count: {word_count}")
    
    st.markdown("---")
    
    # Reference Summary
    st.markdown("### 📚 Reference Summary (Ground Truth)")
    
    with st.expander("View Reference Summary", expanded=False):
        st.text_area(
            "Reference Summary",
            value=results['config']['reference_summary'],
            height=150,
            disabled=True,
            key="reference_summary_display"
        )
    
    st.markdown("---")
    
    # Comparison Insights
    st.markdown("### 💡 Summary Comparison Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ RAG Advantages")
        st.markdown("""
        - **Grounded in retrieved context**
        - **Focused on relevant information**
        - **Lower hallucination risk**
        - **Traceable to source**
        - **More factually accurate**
        """)
    
    with col2:
        st.markdown("#### ⚠️ Non-RAG Limitations")
        st.markdown("""
        - **Uses full document**
        - **May add unsupported details**
        - **Higher hallucination risk**
        - **Less targeted response**
        - **Harder to verify claims**
        """)