# =============================================================================
# Metrics Dashboard Tab Component
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def render_metrics_tab():
    """Render the comprehensive metrics dashboard."""
    
    st.markdown("## 📊 Evaluation Metrics Dashboard")
    
    if "results" not in st.session_state:
        st.warning("No metrics available. Run the pipeline first.")
        return
    
    results = st.session_state.results
    rag_metrics = results['metrics']['rag']
    non_rag_metrics = results['metrics']['non_rag']
    
    # Key Metrics Overview
    st.markdown("### 🎯 Key Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "RAG ROUGE-1",
            f"{rag_metrics['rouge1_f1']:.3f}",
            delta=f"{rag_metrics['rouge1_f1'] - non_rag_metrics['rouge1_f1']:.3f}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "RAG BLEU",
            f"{rag_metrics['bleu']:.3f}",
            delta=f"{rag_metrics['bleu'] - non_rag_metrics['bleu']:.3f}",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "RAG BERTScore",
            f"{rag_metrics['bertscore_f1']:.3f}",
            delta=f"{rag_metrics['bertscore_f1'] - non_rag_metrics['bertscore_f1']:.3f}",
            delta_color="normal"
        )
    
    with col4:
        faithfulness = rag_metrics.get('faithfulness', 'N/A')
        if isinstance(faithfulness, (int, float)):
            st.metric("RAGAS Faithfulness", f"{faithfulness:.3f}")
        else:
            st.metric("RAGAS Faithfulness", faithfulness)
    
    st.markdown("---")
    
    # Lexical Metrics Comparison
    st.markdown("### 📝 Lexical Metrics Comparison")
    
    lexical_metrics = ['rouge1_f1', 'rouge2_f1', 'rougeL_f1', 'bleu']
    lexical_labels = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'BLEU']
    
    rag_lexical_values = [rag_metrics[m] for m in lexical_metrics]
    non_rag_lexical_values = [non_rag_metrics[m] for m in lexical_metrics]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='RAG',
        x=lexical_labels,
        y=rag_lexical_values,
        text=[f"{v:.3f}" for v in rag_lexical_values],
        textposition='auto',
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='Non-RAG',
        x=lexical_labels,
        y=non_rag_lexical_values,
        text=[f"{v:.3f}" for v in non_rag_lexical_values],
        textposition='auto',
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title="Lexical Metrics: RAG vs Non-RAG",
        xaxis_title="Metric",
        yaxis_title="Score",
        barmode='group',
        height=500,
        yaxis_range=[0, 1]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Semantic Metrics
    st.markdown("### 🧠 Semantic Similarity Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rag_metrics['bertscore_f1'],
            title={'text': "RAG BERTScore F1"},
            number={'font': {'size': 40}},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 0.5], 'color': "#ffcccc"},
                    {'range': [0.5, 0.75], 'color': "#ffffcc"},
                    {'range': [0.75, 1], 'color': "#ccffcc"}
                ]
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=non_rag_metrics['bertscore_f1'],
            title={'text': "Non-RAG BERTScore F1"},
            number={'font': {'size': 40}},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': "#ff7f0e"},
                'steps': [
                    {'range': [0, 0.5], 'color': "#ffcccc"},
                    {'range': [0.5, 0.75], 'color': "#ffffcc"},
                    {'range': [0.75, 1], 'color': "#ccffcc"}
                ]
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # RAGAS Metrics (RAG only)
    st.markdown("### 🎯 RAGAS Metrics (RAG-Specific)")
    
    ragas_metrics_names = ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']
    ragas_labels = ['Faithfulness', 'Answer Relevancy', 'Context Recall', 'Context Precision']
    
    ragas_values = []
    for metric in ragas_metrics_names:
        val = rag_metrics.get(metric, 0)
        if isinstance(val, (int, float)):
            ragas_values.append(val)
        else:
            ragas_values.append(0)
    
    # Radar chart for RAGAS metrics
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=ragas_values,
        theta=ragas_labels,
        fill='toself',
        name='RAG Pipeline',
        marker_color='#2ca02c'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="RAGAS Metrics Radar Chart",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # RAGAS metrics table
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        val = rag_metrics.get('faithfulness', 'N/A')
        if isinstance(val, (int, float)):
            st.metric("Faithfulness", f"{val:.3f}")
        else:
            st.metric("Faithfulness", val)
    
    with col2:
        val = rag_metrics.get('answer_relevancy', 'N/A')
        if isinstance(val, (int, float)):
            st.metric("Answer Relevancy", f"{val:.3f}")
        else:
            st.metric("Answer Relevancy", val)
    
    with col3:
        val = rag_metrics.get('context_recall', 'N/A')
        if isinstance(val, (int, float)):
            st.metric("Context Recall", f"{val:.3f}")
        else:
            st.metric("Context Recall", val)
    
    with col4:
        val = rag_metrics.get('context_precision', 'N/A')
        if isinstance(val, (int, float)):
            st.metric("Context Precision", f"{val:.3f}")
        else:
            st.metric("Context Precision", val)
    
    st.markdown("---")
    
    # Metric Analysis Table
    st.markdown("### 📋 Metric Analysis: Why Traditional Metrics Fail")
    
    analysis_data = {
        "Metric": ["ROUGE-1/2/L", "BLEU", "BERTScore", "RAGAS Faithfulness", "RAGAS Answer Relevancy", "RAGAS Context Metrics"],
        "What it Measures": [
            "Word/n-gram overlap",
            "Precision of n-grams",
            "Semantic similarity",
            "Context grounding",
            "Question relevance",
            "Retrieval quality"
        ],
        "Limitation": [
            "High scores for domain vocabulary even if facts wrong",
            "Designed for translation; penalizes paraphrasing",
            "Similar meaning ≠ factual correctness",
            "✅ Most reliable - checks claim support",
            "Measures topical match, not accuracy",
            "Evaluates retrieval, not generation"
        ],
        "RAG Score": [
            f"{rag_metrics['rouge1_f1']:.3f}",
            f"{rag_metrics['bleu']:.3f}",
            f"{rag_metrics['bertscore_f1']:.3f}",
            f"{rag_metrics.get('faithfulness', 'N/A')}",
            f"{rag_metrics.get('answer_relevancy', 'N/A')}",
            f"{rag_metrics.get('context_precision', 'N/A')}"
        ],
        "Non-RAG Score": [
            f"{non_rag_metrics['rouge1_f1']:.3f}",
            f"{non_rag_metrics['bleu']:.3f}",
            f"{non_rag_metrics['bertscore_f1']:.3f}",
            "N/A",
            "N/A",
            "N/A"
        ]
    }
    
    import pandas as pd
    df = pd.DataFrame(analysis_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Key Takeaways
    st.markdown("### 🎯 Key Takeaways")
    
    st.info("""
    **Research Question:** *"Can current automated metrics reliably distinguish between a 'correct' answer and a 'plausible but wrong' answer?"*
    
    **Answer: NO** - Traditional metrics (ROUGE, BLEU, BERTScore) fail to detect hallucinations because they measure surface-level similarity, not factual grounding.
    
    **Why RAG Improves Faithfulness:**
    - Constrains generation to curated, relevant excerpts
    - Provides explicit context for verification
    - Reduces hallucination by limiting knowledge scope
    - Only RAGAS Faithfulness directly addresses factual grounding
    """)