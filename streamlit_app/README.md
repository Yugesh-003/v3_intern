# RAG vs Non-RAG Summarization Evaluation Dashboard

A production-quality Streamlit application for evaluating Retrieval-Augmented Generation (RAG) against traditional summarization with comprehensive metrics and visualizations.

## 🚀 Features

### Core Functionality
- **PDF Document Analysis** - Extract text, tables, images with intelligent chunking
- **Vector Store Management** - ChromaDB-powered semantic search
- **Dual Summarization** - RAG vs Non-RAG comparison
- **Multi-Viewpoint Analysis** - Bull/Bear/Neutral perspectives
- **Comprehensive Evaluation** - ROUGE, BLEU, BERTScore, RAGAS metrics

### Interactive Dashboard
- **5 Main Tabs:**
  1. PDF Analysis - Document statistics and content preview
  2. Vector Store & Retrieval - Chunk visualization and similarity scores
  3. Summaries - Side-by-side comparison with latency metrics
  4. Metrics Dashboard - Interactive charts and radar plots
  5. Results Export - JSON and formatted text reports

### Professional Features
- Real-time progress tracking
- Cached embedding models
- Ollama connection testing
- Configurable parameters
- Download capabilities
- Responsive design

## 📋 Prerequisites

### Required Software
- Python 3.8+
- Ollama (running locally on port 11434)
- Git (for cloning)

### Ollama Setup
```bash
# Install Ollama from https://ollama.ai
# Pull the required model
ollama pull gemma3:1b
```

## 🔧 Installation

### 1. Clone or Navigate to Directory
```bash
cd streamlit_app
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Start the Application
```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Workflow

1. **Upload PDF** - Use the sidebar file uploader
2. **Configure Query** - Enter your question about the document
3. **Set Reference Summary** - Provide ground truth for evaluation
4. **Adjust Parameters** (Optional):
   - Chunk size and overlap
   - Top-K retrieval
   - LLM model and endpoint
5. **Test Ollama** - Verify connection before running
6. **Run Pipeline** - Click the button and watch progress
7. **Explore Results** - Navigate through 5 analysis tabs
8. **Export Data** - Download JSON or formatted reports

## 📁 Project Structure

```
streamlit_app/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── components/                 # UI Components
│   ├── pdf_analysis.py        # PDF analysis tab
│   ├── retrieval_view.py      # Vector store visualization
│   ├── summary_view.py        # Summary comparison
│   ├── metrics_view.py        # Metrics dashboard
│   └── export_view.py         # Export functionality
│
├── core/                       # Core Pipeline Logic
│   ├── config.py              # Configuration dataclass
│   ├── pdf_extractor.py       # PDF processing
│   ├── chunker.py             # Text chunking
│   ├── vector_store.py        # ChromaDB management
│   ├── llm_interface.py       # Ollama integration
│   ├── summarizer.py          # Summary generation
│   ├── evaluator.py           # Metrics computation
│   └── pipeline.py            # Main orchestration
│
└── utils/                      # Utilities
    └── helpers.py             # Helper functions
```

## 🎨 Dashboard Tabs

### Tab 1: PDF Analysis
- Document statistics (pages, tables, images, words)
- Extracted text preview with adjustable length
- Table visualization as DataFrames
- CSV export for tables
- Chunk distribution summary

### Tab 2: Vector Store & Retrieval
- Chunk creation statistics
- All chunks browser
- Retrieved context details
- Similarity score visualization
- Distance vs similarity metrics

### Tab 3: Summaries
- Three-column comparison (RAG, Non-RAG, Multi-viewpoint)
- Generation latency chart
- Word count statistics
- Reference summary display
- Comparison insights

### Tab 4: Metrics Dashboard
- Key metrics overview with deltas
- Lexical metrics comparison (ROUGE, BLEU)
- Semantic similarity gauges (BERTScore)
- RAGAS metrics radar chart
- Analysis table explaining metric limitations
- Research question answer

### Tab 5: Results Export
- Full JSON download
- Formatted text report
- Results preview
- Summary statistics

## 📊 Evaluation Metrics

### Lexical Metrics
- **ROUGE-1/2/L** - Word and n-gram overlap
- **BLEU** - Translation-based precision

### Semantic Metrics
- **BERTScore** - Contextual embedding similarity

### RAG-Specific Metrics
- **Faithfulness** - Claims supported by context
- **Answer Relevancy** - Topical alignment
- **Context Recall** - Retrieval coverage
- **Context Precision** - Retrieval relevance

## 🔬 Research Question

**"Can current automated metrics reliably distinguish between a 'correct' answer and a 'plausible but wrong' answer?"**

**Finding:** Traditional metrics (ROUGE, BLEU, BERTScore) fail to detect hallucinations. Only RAGAS Faithfulness directly addresses factual grounding.

## ⚙️ Configuration Options

### Sidebar Parameters
- **Chunk Size** - Words per chunk (50-500)
- **Chunk Overlap** - Overlapping words (0-100)
- **Top K** - Retrieval count (1-10)
- **Ollama URL** - API endpoint
- **Ollama Model** - Model identifier
- **Embedding Model** - SentenceTransformer model

### Default Values
- Chunk Size: 200 words
- Chunk Overlap: 30 words
- Top K: 3 chunks
- Model: gemma3:1b
- Embeddings: all-MiniLM-L6-v2

## 🐛 Troubleshooting

### Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### Model Not Found
```bash
# Pull the model
ollama pull gemma3:1b
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### ChromaDB Permission Issues
```bash
# Remove existing store
rm -rf chroma_store
```

## 🚀 Performance Tips

1. **Use smaller PDFs** for faster processing (<10 pages)
2. **Reduce chunk size** for quicker embedding
3. **Lower Top-K** for faster retrieval
4. **Cache is automatic** - subsequent runs are faster
5. **Keep Ollama warm** - run a test query first

## 📝 Example Use Cases

### Financial Document Analysis
- Upload quarterly reports
- Query about VaR, allocations, risks
- Compare RAG vs full-document summarization
- Evaluate hallucination detection

### Research Paper Summarization
- Extract key findings
- Multi-viewpoint analysis (positive/negative/neutral)
- Verify factual accuracy against reference

### Technical Documentation
- Query-specific information retrieval
- Context-grounded responses
- Compare retrieval quality

## 🤝 Contributing

This is a production-ready implementation. For modifications:

1. **Add new metrics** - Extend `evaluator.py`
2. **Add visualizations** - Update component files
3. **Change LLM** - Modify `llm_interface.py`
4. **Customize UI** - Edit component rendering functions

## 📄 License

MIT License - See original project for details

## 🙏 Acknowledgments

- Built with Streamlit
- Powered by Ollama
- ChromaDB for vector storage
- SentenceTransformers for embeddings
- RAGAS framework for evaluation

## 📧 Support

For issues or questions:
1. Check troubleshooting section
2. Verify Ollama is running
3. Review browser console logs
4. Check terminal output

---

**Built for AI internship evaluation project**  
**Research focus: RAG evaluation and hallucination detection**