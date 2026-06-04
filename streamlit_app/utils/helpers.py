# =============================================================================
# Helper Utilities
# =============================================================================

import streamlit as st


def initialize_session_state():
    """Initialize all session state variables."""
    
    # Pipeline state
    if "pipeline_run" not in st.session_state:
        st.session_state.pipeline_run = False
    
    if "results" not in st.session_state:
        st.session_state.results = None
    
    # PDF processing
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    
    if "main_content" not in st.session_state:
        st.session_state.main_content = None
    
    if "tables" not in st.session_state:
        st.session_state.tables = None
    
    if "extraction_stats" not in st.session_state:
        st.session_state.extraction_stats = None
    
    # Chunking
    if "chunks" not in st.session_state:
        st.session_state.chunks = None
    
    # Retrieval
    if "retrieved_contexts" not in st.session_state:
        st.session_state.retrieved_contexts = None
    
    if "retrieval_distances" not in st.session_state:
        st.session_state.retrieval_distances = None
    
    # Configuration
    if "query" not in st.session_state:
        st.session_state.query = "What is the VaR confidence interval and current portfolio allocation strategy?"
    
    if "reference_summary" not in st.session_state:
        st.session_state.reference_summary = """The portfolio tracks a 95% confidence interval VaR that potential weekly downside variance will not exceed 2.1%. Current allocations show Domestic Large-Cap Equities over-allocated at 32.4% vs 30.0% target requiring trimming, while Emerging Markets Equities are under-allocated at 4.1% vs 5.0% target. The portfolio maintains a Beta of 0.88 against broader market indices with strategic rebalancing planned for Q2."""


def format_metric(value, metric_type="percentage"):
    """Format metric values for display."""
    if isinstance(value, (int, float)):
        if metric_type == "percentage":
            return f"{value * 100:.1f}%"
        elif metric_type == "decimal":
            return f"{value:.3f}"
        elif metric_type == "time":
            return f"{value:.2f}s"
        else:
            return f"{value}"
    else:
        return str(value)


def create_metric_card(title, value, delta=None, help_text=None):
    """Create a styled metric card."""
    return st.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text
    )