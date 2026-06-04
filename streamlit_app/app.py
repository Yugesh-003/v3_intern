# =============================================================================
# RAG vs Non-RAG Summarization Evaluation Dashboard
# Streamlit Application - Main Entry Point
# =============================================================================

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from components.pdf_analysis import render_pdf_analysis_tab
from components.retrieval_view import render_retrieval_tab
from components.summary_view import render_summaries_tab
from components.metrics_view import render_metrics_tab
from components.export_view import render_export_tab
from core.config import Config
from core.pipeline import RAGPipeline
from utils.helpers import initialize_session_state

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="RAG vs Non-RAG Evaluation Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================

initialize_session_state()

# =============================================================================
# SIDEBAR CONFIGURATION
# =============================================================================

with st.sidebar:
    st.markdown("### 📄 Document Upload")
    
    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Upload a PDF file for RAG evaluation"
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = Path("temp_uploads")
        temp_path.mkdir(exist_ok=True)
        pdf_path = temp_path / uploaded_file.name
        
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.pdf_path = str(pdf_path)
        st.success(f"✅ Loaded: {uploaded_file.name}")
    
    st.markdown("---")
    st.markdown("### 🔍 Query Configuration")
    
    query = st.text_input(
        "Query",
        value=st.session_state.get("query", "What is the VaR confidence interval and current portfolio allocation strategy?"),
        help="Enter your question about the document"
    )
    st.session_state.query = query
    
    reference_summary = st.text_area(
        "Reference Summary (Ground Truth)",
        value=st.session_state.get("reference_summary", ""),
        height=150,
        help="Enter the expected correct summary for evaluation"
    )
    st.session_state.reference_summary = reference_summary
    
    st.markdown("---")
    st.markdown("### ⚙️ Pipeline Configuration")
    
    with st.expander("Chunking Parameters", expanded=False):
        chunk_size = st.number_input(
            "Chunk Size (words)",
            min_value=50,
            max_value=500,
            value=200,
            step=10,
            help="Number of words per chunk"
        )
        
        chunk_overlap = st.number_input(
            "Chunk Overlap (words)",
            min_value=0,
            max_value=100,
            value=30,
            step=5,
            help="Number of overlapping words between chunks"
        )
    
    with st.expander("Retrieval Parameters", expanded=False):
        top_k = st.number_input(
            "Top K Retrieval",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="Number of chunks to retrieve for RAG"
        )
    
    with st.expander("LLM Configuration", expanded=False):
        ollama_url = st.text_input(
            "Ollama URL",
            value="http://localhost:11434/api/generate",
            help="Ollama API endpoint"
        )
        
        ollama_model = st.text_input(
            "Ollama Model",
            value="gemma3:1b",
            help="Model name in Ollama"
        )
        
        # Test Ollama connection
        if st.button("🔌 Test Ollama Connection", use_container_width=True):
            import requests
            try:
                response = requests.get(ollama_url.replace("/api/generate", "/api/tags"), timeout=5)
                if response.status_code == 200:
                    st.success("✅ Ollama is running!")
                else:
                    st.error(f"❌ Ollama responded with status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Cannot connect to Ollama: {str(e)}")
    
    with st.expander("Embedding Configuration", expanded=False):
        embedding_model = st.text_input(
            "Embedding Model",
            value="all-MiniLM-L6-v2",
            help="SentenceTransformer model name"
        )
    
    st.markdown("---")
    
    # Run Pipeline Button
    run_button = st.button(
        "🚀 Run Pipeline",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_file or not query or not reference_summary
    )
    
    if run_button:
        # Create config
        config = Config(
            PDF_PATH=st.session_state.pdf_path,
            QUERY=query,
            REFERENCE_SUMMARY=reference_summary,
            CHUNK_SIZE=chunk_size,
            CHUNK_OVERLAP=chunk_overlap,
            TOP_K=top_k,
            OLLAMA_URL=ollama_url,
            OLLAMA_MODEL=ollama_model,
            EMBEDDING_MODEL=embedding_model
        )
        
        # Run pipeline
        with st.spinner("🔄 Running RAG Pipeline..."):
            try:
                pipeline = RAGPipeline(config)
                results = pipeline.run_complete_pipeline_with_progress()
                
                # Store results in session state
                st.session_state.results = results
                st.session_state.pipeline_run = True
                
                st.success("✅ Pipeline completed successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Pipeline failed: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
    
    # Clear Results Button
    if st.session_state.get("pipeline_run", False):
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.results = None
            st.session_state.pipeline_run = False
            st.rerun()

# =============================================================================
# MAIN PAGE HEADER
# =============================================================================

st.markdown('<h1 class="main-header">🤖 RAG vs Non-RAG Summarization Evaluation Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Compare retrieval-augmented generation against traditional summarization with comprehensive metrics</p>', unsafe_allow_html=True)

# =============================================================================
# MAIN CONTENT TABS
# =============================================================================

if not st.session_state.get("pipeline_run", False):
    # Show instructions when no results
    st.info("👈 **Get Started:** Upload a PDF, configure your query, and click 'Run Pipeline' in the sidebar")
    
    st.markdown("### 📊 What This Dashboard Does")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🔍 RAG Pipeline
        - Extracts text and tables from PDFs
        - Chunks content intelligently
        - Embeds and stores in vector DB
        - Retrieves relevant context
        - Generates grounded summaries
        """)
    
    with col2:
        st.markdown("""
        #### 📈 Non-RAG Baseline
        - Uses full document text
        - No retrieval step
        - Direct summarization
        - Comparison benchmark
        - Shows RAG benefits
        """)
    
    with col3:
        st.markdown("""
        #### 🎯 Evaluation Metrics
        - ROUGE (lexical overlap)
        - BLEU (n-gram precision)
        - BERTScore (semantic similarity)
        - RAGAS (faithfulness & relevancy)
        - Hallucination detection
        """)
    
    st.markdown("---")
    st.markdown("### 🎓 Research Question")
    st.markdown("""
    > *"Can current automated metrics reliably distinguish between a 'correct' answer and a 'plausible but wrong' answer?"*
    
    This dashboard helps answer this critical question by comparing RAG and Non-RAG approaches across multiple evaluation metrics.
    """)

else:
    # Show results in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 PDF Analysis",
        "🔍 Vector Store & Retrieval",
        "📝 Summaries",
        "📊 Metrics Dashboard",
        "💾 Results Export"
    ])
    
    with tab1:
        render_pdf_analysis_tab()
    
    with tab2:
        render_retrieval_tab()
    
    with tab3:
        render_summaries_tab()
    
    with tab4:
        render_metrics_tab()
    
    with tab5:
        render_export_tab()

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>RAG Evaluation Dashboard | Built with Streamlit | 
    <a href='https://github.com' target='_blank'>Documentation</a>
    </p>
</div>
""", unsafe_allow_html=True)