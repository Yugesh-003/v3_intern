# =============================================================================
# RAG vs Non-RAG Summarization Evaluation Dashboard
# Single-Page Analytics Dashboard — Main Entry Point
# =============================================================================

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from components.pdf_analysis import render_document_overview_section
from components.retrieval_view import render_retrieval_section
from components.summary_view import render_summary_comparison_section
from components.metrics_view import render_metrics_section
from components.visual_analytics import render_visual_analytics_section
from components.export_view import render_export_section
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

# =============================================================================
# GLOBAL CSS — Dark, Premium, Executive Style
# =============================================================================

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Page background ── */
.stApp {
    background: #0d1117;
    color: #e6edf3;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #c9d1d9 !important;
}

/* ── Main header ── */
.dashboard-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1117 60%);
    border-bottom: 1px solid #21262d;
    padding: 2rem 0 1.5rem 0;
    margin-bottom: 0;
}
.dashboard-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #58a6ff, #a371f7, #3fb950);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.dashboard-subtitle {
    font-size: 1rem;
    color: #8b949e;
    margin-top: 0.4rem;
    font-weight: 400;
}

/* ── Section headers (sticky) ── */
.section-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: linear-gradient(180deg, #0d1117 85%, transparent);
    padding: 0.8rem 0 0.4rem 0;
    margin-bottom: 1rem;
    border-bottom: 2px solid #21262d;
}
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e6edf3;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}
.section-badge {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #58a6ff;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── KPI / Stat cards ── */
.stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: border-color 0.2s, transform 0.2s;
}
.stat-card:hover {
    border-color: #58a6ff;
    transform: translateY(-2px);
}
.stat-card-icon {
    font-size: 1.6rem;
    margin-bottom: 0.3rem;
}
.stat-card-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #58a6ff;
    line-height: 1;
}
.stat-card-label {
    font-size: 0.78rem;
    color: #8b949e;
    margin-top: 0.3rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Summary comparison cards ── */
.summary-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.4rem;
    height: 100%;
}
.summary-card-rag {
    border-top: 3px solid #58a6ff;
}
.summary-card-nonrag {
    border-top: 3px solid #f78166;
}
.summary-card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.8rem;
}

/* ── st.metric overrides (used by Section 4 KPI rows) ── */
/* Hover accent on individual metric cells */
[data-testid="metric-container"]:hover {
    border-color: #a371f7 !important;
    box-shadow: 0 0 12px rgba(163,113,247,0.15);
    transform: translateY(-2px);
    transition: all 0.2s ease;
}

/* ── Verdict card ── */
.verdict-card {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid #30363d;
    border-left: 4px solid #3fb950;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
}
.verdict-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #3fb950;
    margin-bottom: 0.5rem;
}
.verdict-text {
    font-size: 0.95rem;
    color: #c9d1d9;
    line-height: 1.6;
}

/* ── Info welcome panel ── */
.welcome-panel {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 2.5rem;
    text-align: center;
    margin: 2rem 0;
}
.welcome-panel h2 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.6rem;
}
.welcome-panel p {
    color: #8b949e;
    font-size: 1rem;
}

/* ── Feature cards on welcome ── */
.feature-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1.4rem 1.2rem;
    text-align: left;
    transition: border-color 0.2s;
}
.feature-card:hover {
    border-color: #58a6ff;
}
.feature-card h4 {
    font-size: 0.95rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.5rem;
}
.feature-card ul {
    color: #8b949e;
    font-size: 0.85rem;
    padding-left: 1.1rem;
    margin: 0;
}
.feature-card li {
    margin-bottom: 0.2rem;
}

/* ── Section divider ── */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #30363d 20%, #30363d 80%, transparent);
    margin: 2.5rem 0;
}

/* ── Streamlit overrides ── */
.stMetric {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 0.8rem 1rem !important;
}
.stMetric label { color: #8b949e !important; font-size: 0.75rem !important; }
.stMetric [data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 700 !important; }
.stMetric [data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

div[data-testid="stExpander"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}

.stTextArea textarea {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
    font-family: 'Inter', monospace;
    font-size: 0.85rem;
}

.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950);
    box-shadow: 0 4px 12px rgba(63,185,80,0.3);
    transform: translateY(-1px);
}

/* ── Progress / spinner ── */
.stSpinner > div { color: #58a6ff !important; }

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #58a6ff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s;
}
.stDownloadButton > button:hover {
    border-color: #58a6ff !important;
    box-shadow: 0 0 8px rgba(88,166,255,0.2) !important;
}

/* ── Info / warning / success ── */
.stAlert {
    border-radius: 10px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #58a6ff; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

initialize_session_state()

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### 📄 Document Upload")

    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Upload a PDF file for RAG evaluation"
    )

    if uploaded_file:
        temp_path = Path("temp_uploads")
        temp_path.mkdir(exist_ok=True)
        pdf_path = temp_path / uploaded_file.name

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.pdf_path = str(pdf_path)
        st.success(f"✅ Loaded: {uploaded_file.name}")

    st.markdown("---")
    st.markdown("### 🎯 Summarization Task")

    # ── Preset task selector ───────────────────────────────────────────────
    TASK_PRESETS = {
        "3 lines": "Summarize the document in exactly 3 lines.",
        "5 bullet points": "Summarize the document in exactly 5 bullet points.",
        "50 words": "Summarize the document in 50 words or fewer.",
        "One paragraph": "Summarize the document in one concise paragraph.",
        "Custom": "",
    }
    preset_choice = st.selectbox(
        "Summary Format",
        options=list(TASK_PRESETS.keys()),
        index=0,
        help="Choose how you want both AIs to summarize the document."
    )

    if preset_choice == "Custom":
        task = st.text_input(
            "Custom Task",
            value=st.session_state.get("task", "Summarize the document in exactly 3 lines."),
            placeholder="e.g. Summarize the document in 2 sentences.",
        )
        summary_constraint = task  # use full task as constraint label
    else:
        task = TASK_PRESETS[preset_choice]
        summary_constraint = preset_choice
        st.caption(f"📋 Prompt: *\"{task}\"*")

    st.session_state.task = task

    st.markdown("---")
    st.markdown("### ✍️ Your Reference Summary")
    st.caption(
        "Read the PDF yourself and write a **human summary** matching the format above. "
        "Both AI summaries are scored against this."
    )

    reference_summary = st.text_area(
        "Reference Summary (Option A — Human Written)",
        value=st.session_state.get("reference_summary", ""),
        height=160,
        placeholder=(
            "Write your own summary here matching the chosen format.\n"
            "Example for '3 lines':\n"
            "Line 1: Main topic of the document.\n"
            "Line 2: Key finding or statistic.\n"
            "Line 3: Conclusion or implication."
        ),
        help="This is your ground truth. Be concise and accurate — match the format constraint."
    )
    st.session_state.reference_summary = reference_summary

    # Live word count hint
    if reference_summary.strip():
        wc = len(reference_summary.strip().split())
        lc = len([l for l in reference_summary.strip().splitlines() if l.strip()])
        st.caption(f"📊 {wc} words · {lc} lines")

    st.markdown("---")
    st.markdown("### ⚙️ Pipeline Configuration")

    with st.expander("Chunking Parameters", expanded=False):
        chunk_size = st.number_input(
            "Chunk Size (words)", min_value=50, max_value=500,
            value=200, step=10, help="Number of words per chunk"
        )
        chunk_overlap = st.number_input(
            "Chunk Overlap (words)", min_value=0, max_value=100,
            value=30, step=5, help="Number of overlapping words between chunks"
        )

    with st.expander("Retrieval Parameters", expanded=False):
        top_k = st.number_input(
            "Top K Retrieval", min_value=1, max_value=10,
            value=3, step=1, help="Number of chunks to retrieve for RAG"
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
        if st.button("🔌 Test Ollama Connection", use_container_width=True):
            import requests
            try:
                response = requests.get(
                    ollama_url.replace("/api/generate", "/api/tags"), timeout=5
                )
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

    run_disabled = not uploaded_file or not task or not reference_summary
    run_button = st.button(
        "🚀 Run Pipeline",
        type="primary",
        use_container_width=True,
        disabled=run_disabled
    )
    if run_disabled and uploaded_file:
        missing = []
        if not reference_summary:
            missing.append("✍️ reference summary")
        if missing:
            st.caption(f"Still needed: {', '.join(missing)}")

    if run_button:
        config = Config(
            PDF_PATH=st.session_state.pdf_path,
            TASK=task,
            SUMMARY_CONSTRAINT=summary_constraint,
            REFERENCE_SUMMARY=reference_summary,
            CHUNK_SIZE=chunk_size,
            CHUNK_OVERLAP=chunk_overlap,
            TOP_K=top_k,
            OLLAMA_URL=ollama_url,
            OLLAMA_MODEL=ollama_model,
            EMBEDDING_MODEL=embedding_model
        )
        with st.spinner("🔄 Running RAG Pipeline..."):
            try:
                pipeline = RAGPipeline(config)
                results = pipeline.run_complete_pipeline_with_progress()
                st.session_state.results = results
                st.session_state.pipeline_run = True
                st.success("✅ Pipeline completed!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Pipeline failed: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

    if st.session_state.get("pipeline_run", False):
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.results = None
            st.session_state.pipeline_run = False
            st.rerun()

    # Sidebar navigation anchors
    if st.session_state.get("pipeline_run", False):
        st.markdown("---")
        st.markdown("### 🧭 Jump to Section")
        st.markdown("""
- [📄 Document Overview](#section-1-document-overview)
- [🔍 Retrieval Analysis](#section-2-retrieval-analysis)
- [📝 Summary Comparison](#section-3-summary-comparison)
- [📊 Evaluation Metrics](#section-4-evaluation-metrics)
- [📈 Visual Analytics](#section-5-visual-analytics)
- [💾 Results & Export](#section-6-results-export)
        """)

# =============================================================================
# MAIN CONTENT — SINGLE PAGE
# =============================================================================

# Dashboard Header
st.markdown("""
<div class="dashboard-header">
  <h1 class="dashboard-title">🤖 RAG Evaluation Dashboard</h1>
  <p class="dashboard-subtitle">
    Compare retrieval-augmented generation against traditional summarization
    with comprehensive automated metrics
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Welcome / Landing (no results yet) ───────────────────────────────────────
if not st.session_state.get("pipeline_run", False):
    st.markdown("""
    <div class="welcome-panel">
      <h2>👈 Get Started</h2>
      <p>Upload a PDF, configure your query and ground truth in the sidebar, then click <strong>Run Pipeline</strong>.<br>
      All analysis results will populate below on this single page — no tab switching required.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
          <h4>🔍 RAG Pipeline</h4>
          <ul>
            <li>Extracts text &amp; tables from PDFs</li>
            <li>Chunks content intelligently</li>
            <li>Embeds &amp; stores in vector DB</li>
            <li>Retrieves relevant context</li>
            <li>Generates grounded summaries</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
          <h4>📈 Non-RAG Baseline</h4>
          <ul>
            <li>Uses full document text</li>
            <li>No retrieval step</li>
            <li>Direct summarization</li>
            <li>Comparison benchmark</li>
            <li>Highlights RAG benefits</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
          <h4>🎯 Evaluation Metrics</h4>
          <ul>
            <li>ROUGE (lexical overlap)</li>
            <li>BLEU (n-gram precision)</li>
            <li>BERTScore (semantic similarity)</li>
            <li>RAGAS (faithfulness &amp; relevancy)</li>
            <li>Hallucination detection</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.info(
        "**Research Question:** *\"Can current automated metrics reliably distinguish "
        "between a 'correct' answer and a 'plausible but wrong' answer?\"*\n\n"
        "This dashboard helps answer that critical question by comparing RAG and "
        "Non-RAG approaches across multiple evaluation dimensions."
    )

else:
    # ─── Results are available → render all sections ──────────────────────────

    # ── SECTION 1: Document Overview ──────────────────────────────────────────
    st.markdown('<div id="section-1-document-overview"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2 class="section-title">📄 Document Overview</h2>
    </div>
    """, unsafe_allow_html=True)

    render_document_overview_section()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── SECTION 2: Retrieval Analysis ─────────────────────────────────────────
    st.markdown('<div id="section-2-retrieval-analysis"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2 class="section-title">🔍 Retrieval Analysis</h2>
    </div>
    """, unsafe_allow_html=True)

    render_retrieval_section()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── SECTION 3: Summary Comparison ─────────────────────────────────────────
    st.markdown('<div id="section-3-summary-comparison"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2 class="section-title">📝 Summary Comparison</h2>
    </div>
    """, unsafe_allow_html=True)

    render_summary_comparison_section()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── SECTION 4: Evaluation Metrics ─────────────────────────────────────────
    st.markdown('<div id="section-4-evaluation-metrics"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2 class="section-title">📊 Evaluation Metrics</h2>
    </div>
    """, unsafe_allow_html=True)

    render_metrics_section()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── SECTION 5: Visual Analytics ───────────────────────────────────────────
    st.markdown('<div id="section-5-visual-analytics"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2 class="section-title">📈 Visual Analytics</h2>
    </div>
    """, unsafe_allow_html=True)

    render_visual_analytics_section()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── SECTION 6: Results & Export ───────────────────────────────────────────
    st.markdown('<div id="section-6-results-export"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2 class="section-title">💾 Results &amp; Export</h2>
    </div>
    """, unsafe_allow_html=True)

    render_export_section()

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#484f58; padding:1rem 0 2rem 0; font-size:0.82rem;'>
  RAG Evaluation Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Plotly
  &nbsp;·&nbsp; Single-Page Analytics
</div>
""", unsafe_allow_html=True)