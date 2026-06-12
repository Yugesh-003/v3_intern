# RAG Summarization Pipeline

**AI Internship Submission: RAG vs Non-RAG Comparison with Hallucination Detection**

## Research Question
*"Can current automated metrics reliably distinguish between a 'correct' answer and a 'plausible but wrong' answer?"*

This project demonstrates that traditional metrics (ROUGE, BLEU, BERTScore) fail to detect hallucinations, while RAG-specific metrics like RAGAS Faithfulness provide better factual grounding assessment.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Input     │    │   RAG Pipeline   │    │  Non-RAG Path   │
│ finance_eval.pdf│───▶│                  │    │                 │
└─────────────────┘    │ 1. Extract       │    │ 1. Extract      │
                       │ 2. Chunk (200w)  │    │ 2. Truncate     │
                       │ 3. Embed (local) │    │    (4000w)      │
                       │ 4. Store (Chroma)│    │ 3. Summarize    │
                       │ 5. Retrieve (k=3)│    │    (Ollama)     │
                       │ 6. Summarize     │    │                 │
                       │    (Ollama)      │    │                 │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────────────────────────────┐
                       │           EVALUATION METRICS            │
                       │                                         │
                       │ Lexical:    ROUGE-1/2/L, BLEU         │
                       │ Semantic:   BERTScore F1               │
                       │ RAG-aware:  RAGAS (Faithfulness, etc.) │
                       └─────────────────────────────────────────┘
                                         │
                                         ▼
                       ┌─────────────────────────────────────────┐
                       │        HALLUCINATION ANALYSIS          │
                       │                                         │
                       │ • Why ROUGE/BLEU fail (word overlap)   │
                       │ • Why BERTScore incomplete (semantic≠factual) │
                       │ • Why RAGAS Faithfulness works (grounding) │
                       └─────────────────────────────────────────┘
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and Start Ollama
```bash
# Install Ollama (see https://ollama.ai)
# Pull the required model
ollama pull gemma3:1b
```

### 3. Prepare Data
Place your PDF file at `data/finance_evaluation.pdf` or modify the path in `pipeline.py`.

### 4. Configure Query and Reference
Edit the configuration in `pipeline.py`:
```python
QUERY: str = "Your evaluation question here"
REFERENCE_SUMMARY: str = "Ground truth summary for comparison"
```

### 5. Run Pipeline
```bash
python pipeline.py
```

## Output

The pipeline generates:
- **Console output**: Extraction stats, summaries, metrics comparison, analysis
- **results.json**: Complete results with all metrics and summaries

### Sample Console Output
```
📄 PDF EXTRACTION STATS
Pages processed: 15
Tables found: 3
Images found: 2
Text length: 5247 words

📝 RAG SUMMARY
The portfolio tracks a 95% confidence interval VaR...
⏱️  Generation time: 2.34s

📊 METRICS COMPARISON
Metric               RAG             Non-RAG         Better    
rouge1_f1           0.456           0.423           RAG       
bertscore_f1        0.789           0.734           RAG       

🔍 METRIC ANALYSIS - Why Current Metrics Fail
ROUGE measures word overlap - high scores even if facts are wrong
RAGAS Faithfulness checks if claims are supported by context ✅
```

## Deliverable Mapping

| Requirement | Implementation Location |
|-------------|------------------------|
| **PDF Extraction** | `PDFExtractor` class - strips headers/footers, preserves tables |
| **Text Chunking** | `TextChunker` class - 200-word sliding windows, 30-word overlap |
| **Local Embeddings** | `VectorStore` class - sentence-transformers/all-MiniLM-L6-v2 |
| **ChromaDB Storage** | `VectorStore.initialize()` and `store_chunks()` |
| **RAG Retrieval** | `VectorStore.retrieve()` - cosine similarity, top-3 |
| **RAG Summary** | `SummarizationPipeline.generate_rag_summary()` - grounded prompt |
| **Non-RAG Summary** | `SummarizationPipeline.generate_non_rag_summary()` - full text |
| **Multi-viewpoint** | `generate_multiviewpoint_summary()` - Bull/Bear/Neutral |
| **ROUGE/BLEU** | `MetricsEvaluator.compute_lexical_metrics()` |
| **BERTScore** | `MetricsEvaluator.compute_semantic_metrics()` |
| **RAGAS Metrics** | `MetricsEvaluator.compute_ragas_metrics()` |
| **Comparison Table** | `ResultsReporter.print_metrics_comparison()` |
| **Hallucination Analysis** | `ResultsReporter.print_metric_analysis()` |
| **JSON Output** | `results.json` with all summaries and metrics |

## Key Findings

1. **Traditional metrics fail**: ROUGE and BLEU measure word overlap, not factual accuracy
2. **BERTScore is better but incomplete**: Semantic similarity ≠ factual correctness  
3. **RAGAS Faithfulness is most reliable**: Directly checks if claims are supported by retrieved context
4. **RAG improves grounding**: Constrains generation to curated, relevant excerpts

## File Structure
```
rag-summarization-pipeline/
├── pipeline.py          # Complete implementation (10 sections)
├── requirements.txt     # Pinned dependencies
├── README.md           # This file
├── data/
│   └── finance_evaluation.pdf
├── chroma_store/       # Generated ChromaDB storage
└── results.json        # Generated evaluation results
```

## Technical Details

- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (local, no API key)
- **LLM**: Ollama gemma3:1b (local inference)
- **Vector Store**: ChromaDB with cosine similarity
- **Chunking**: 200 words with 30-word overlap
- **Retrieval**: Top-3 most similar chunks
- **Evaluation**: 7 metrics across lexical, semantic, and RAG-aware categories

## Research Contribution

This implementation demonstrates that current automated evaluation metrics cannot reliably distinguish between factually correct and plausible-but-incorrect summaries. Only RAG-specific metrics like RAGAS Faithfulness directly address the grounding problem by checking whether generated claims are supported by the retrieved context.