# =============================================================================
# RAG Pipeline — Financial Document Summarization (Notebook Version)
# Production-Quality Refactored Code
# =============================================================================

# %% [markdown]
# # RAG Pipeline — Financial Document Summarization
# **Production-Quality Implementation**
# 
# ### Pipeline Overview
# ```
# PDF Input
#   → Extract (text + tables + headers + footers)
#   → Chunk (by section, keep tables whole)  
#   → Embed (all-MiniLM-L6-v2, local, free)
#   → Store (ChromaDB, local)
#   → Retrieve (cosine similarity)
#   → Answer (Ollama/Gemini)
#   → Multi-viewpoint Summarization
#   → Evaluation (RAGAS)
# ```

# %% [markdown]
# ## 1. Dependencies & Setup

# %%
# Install required packages (run once)
# !pip install pymupdf pdfplumber sentence-transformers chromadb google-generativeai ragas langchain langchain-community langchain-ollama datasets

# %% [markdown]
# ## 2. Imports & Configuration

# %%
import os
import re
import json
import shutil
import gc
from typing import List, Dict, Tuple, Any, Optional

# PDF Processing
import fitz  # PyMuPDF
import pdfplumber

# ML & Embeddings
from sentence_transformers import SentenceTransformer
import chromadb

# LLM Integration
import requests
import google.generativeai as genai

# Evaluation
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from datasets import Dataset

print("✅ All imports successful")

# %% [markdown]
# ## 3. Configuration

# %%
class Config:
    """Centralized configuration for the RAG pipeline."""
    
    # File paths
    PDF_PATH = "data/finance_evaluation.pdf"
    CHROMA_PATH = "./chroma_store"
    COLLECTION_NAME = "financial_report"
    
    # Chunking parameters
    CHUNK_SIZE = 200  # words per chunk
    CHUNK_OVERLAP = 30
    
    # Retrieval parameters
    TOP_K = 3  # chunks to retrieve
    
    # PDF extraction margins
    FOOTER_MARGIN = 50
    HEADER_MARGIN = 70
    
    # LLM endpoints
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "gemma3:1b"
    
    # Embedding model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # API keys (set via environment or direct assignment)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize models
embed_model = SentenceTransformer(Config.EMBEDDING_MODEL)

# Optional Gemini setup
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

print("✅ Configuration loaded")

# %% [markdown]
# ## 4. Utility Functions

# %%
def ask_llm(prompt: str) -> str:
    """Send prompt to local Ollama LLM and return response."""
    try:
        response = requests.post(Config.OLLAMA_URL, json={
            "model": Config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error calling LLM: {str(e)}"

print("✅ Utility functions defined")

# %% [markdown]
# ## 5. PDF Extraction Functions

# %%
def extract_pdf_content(pdf_path: str) -> Tuple[List[Dict], str, List[Dict], List[Dict], int]:
    """Extract structured content from PDF including text, tables, headers, and footers."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    header_content = []
    footer_content = []
    main_content = ""
    all_tables_json = []
    image_count = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(len(doc)):
            page = doc[page_num]
            plumber_page = pdf.pages[page_num]

            page_height = page.rect.height
            footer_y_start = page_height - Config.FOOTER_MARGIN
            header_y_end = Config.HEADER_MARGIN

            # Get text blocks and sort by position
            blocks = page.get_text("blocks")
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

            # Extract tables using pdfplumber
            tables = plumber_page.find_tables()
            table_regions = []

            for table in tables:
                table_regions.append(table.bbox)
                extracted = table.extract()

                if extracted and len(extracted) > 1:
                    headers = [
                        h.replace("\n", " ").strip() if h else f"column_{i}"
                        for i, h in enumerate(extracted[0])
                    ]

                    table_json = []
                    for row in extracted[1:]:
                        cleaned_row = [
                            cell.replace("\n", " ").strip() if cell else ""
                            for cell in row
                        ]
                        row_dict = dict(zip(headers, cleaned_row))
                        table_json.append(row_dict)

                    all_tables_json.append({
                        "page": page_num + 1,
                        "table_data": table_json
                    })

            # Process text blocks
            for block in blocks:
                x0, y0, x1, y1, text = block[:5]
                text = text.strip()

                if not text:
                    continue

                # Classify as header, footer, or main content
                if y1 <= header_y_end:
                    header_content.append({
                        "page": page_num + 1,
                        "text": text
                    })
                elif y0 >= footer_y_start:
                    footer_content.append({
                        "page": page_num + 1,
                        "text": text
                    })
                else:
                    # Skip text that's inside table regions
                    inside_table = any(
                        y0 >= ty0 and y1 <= ty1
                        for tx0, ty0, tx1, ty1 in table_regions
                    )
                    
                    if not inside_table:
                        main_content += text + "\n\n"

            image_count += len(page.get_images())

    doc.close()
    return header_content, main_content, footer_content, all_tables_json, image_count

print("✅ PDF extraction functions defined")

# %% [markdown]
# ## 6. Text Chunking Functions

# %%
def chunk_text(text: str, chunk_size: int = Config.CHUNK_SIZE, 
               overlap: int = Config.CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
        
    return chunks

def split_by_sections(text: str) -> List[Dict[str, str]]:
    """Split text on SECTION headings to maintain topical coherence."""
    parts = re.split(r'(SECTION\s+\d+[:\s][^\n]*)', text)
    results = []
    current_section = "INTRODUCTION"
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if re.match(r'SECTION\s+\d+', part):
            current_section = part
        else:
            results.append({
                "section": current_section,
                "text": part
            })
    
    return results

def table_to_readable_text(table_data: List[Dict]) -> str:
    """Convert table data to natural language text for embedding."""
    if not table_data or not isinstance(table_data, list):
        return json.dumps(table_data)
    
    if not table_data or not isinstance(table_data[0], dict):
        return json.dumps(table_data)
    
    headers = list(table_data[0].keys())
    lines = [f"Columns: {' | '.join(headers)}"]
    
    for row in table_data:
        row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
        lines.append(row_text)
    
    return "\n".join(lines)

def prepare_document_chunks(main_content: str, header_content: List[Dict], 
                          footer_content: List[Dict], tables_json: List[Dict]) -> List[Dict]:
    """Prepare all document content as structured chunks for embedding."""
    documents = []
    header_text = " | ".join(h["text"] for h in header_content) if header_content else ""

    # Process main content by sections
    sections = split_by_sections(main_content)
    chunk_id = 0
    
    for section in sections:
        for chunk in chunk_text(section["text"]):
            documents.append({
                "type": "main_content",
                "chunk_id": chunk_id,
                "text": chunk,
                "metadata": {
                    "chunk_index": chunk_id,
                    "section": section["section"],
                    "document_header": header_text,
                }
            })
            chunk_id += 1

    # Process tables (keep whole, never split)
    for idx, table in enumerate(tables_json):
        documents.append({
            "type": "table",
            "chunk_id": f"table_{idx}",
            "text": table_to_readable_text(table["table_data"]),
            "raw": table["table_data"],
            "metadata": {
                "table_index": idx,
                "page": table["page"],
                "document_header": header_text,
            }
        })

    return documents

print("✅ Chunking functions defined")

# %% [markdown]
# ## 7. Vector Store Management

# %%
class ChromaDBManager:
    """Manages ChromaDB operations for the RAG pipeline."""
    
    def __init__(self, persist_path: str, collection_name: str, embed_model: SentenceTransformer):
        self.persist_path = persist_path
        self.collection_name = collection_name
        self.embed_model = embed_model
        self.client = None
        self.collection = None
    
    def initialize_fresh_store(self) -> None:
        """Initialize a fresh ChromaDB store, removing any existing data."""
        # Clean up existing client
        if self.client:
            try:
                self.client.reset()
            except:
                pass
        
        # Remove existing store
        if os.path.exists(self.persist_path):
            shutil.rmtree(self.persist_path)
        
        # Create fresh client and collection
        self.client = chromadb.PersistentClient(path=self.persist_path)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def store_documents(self, documents: List[Dict]) -> None:
        """Store document chunks in ChromaDB with embeddings."""
        if not self.collection:
            raise RuntimeError("ChromaDB not initialized. Call initialize_fresh_store() first.")
        
        ids, embeddings, texts, metadatas = [], [], [], []

        for doc in documents:
            chunk_id = f"{doc['type']}_{doc['chunk_id']}"
            embedding = self.embed_model.encode(doc["text"]).tolist()

            # Prepare metadata (ChromaDB requires string values)
            meta = {"type": doc["type"]}
            if "metadata" in doc:
                for k, v in doc["metadata"].items():
                    if isinstance(v, (str, int, float)):
                        meta[k] = str(v)

            ids.append(chunk_id)
            embeddings.append(embedding)
            texts.append(doc["text"])
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def retrieve_similar(self, query: str, top_k: int = Config.TOP_K) -> Dict:
        """Retrieve most similar chunks for a query."""
        if not self.collection:
            raise RuntimeError("ChromaDB not initialized.")
        
        query_embedding = self.embed_model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
            where={"type": {"$in": ["main_content", "table"]}}
        )
        return results
    
    def get_count(self) -> int:
        """Get total number of documents in collection."""
        return self.collection.count() if self.collection else 0

print("✅ ChromaDB manager defined")

# %% [markdown]
# ## 8. Extract and Process PDF

# %%
# Extract PDF content
print(f"📄 Extracting PDF: {Config.PDF_PATH}")

header_content, main_content, footer_content, tables_json, image_count = extract_pdf_content(Config.PDF_PATH)

print(f"   📊 Found {len(tables_json)} tables, {image_count} images")

# Prepare document chunks
documents = prepare_document_chunks(main_content, header_content, footer_content, tables_json)

main_chunks = sum(1 for d in documents if d['type'] == 'main_content')
table_chunks = sum(1 for d in documents if d['type'] == 'table')
print(f"   📝 Created {main_chunks} text chunks, {table_chunks} table chunks")

# Show sample content
if documents:
    print(f"\nSample main chunk:\n{documents[0]['text'][:300]}...")

# %% [markdown]
# ## 9. Build Vector Store

# %%
# Initialize ChromaDB manager
chroma_manager = ChromaDBManager(Config.CHROMA_PATH, Config.COLLECTION_NAME, embed_model)

print("🔍 Building vector store...")
chroma_manager.initialize_fresh_store()
chroma_manager.store_documents(documents)

total_docs = chroma_manager.get_count()
print(f"✅ Stored {total_docs} documents in ChromaDB")

# %% [markdown]
# ## 10. RAG Query & Response Functions

# %%
def generate_rag_response(question: str, chroma_manager: ChromaDBManager) -> Tuple[str, List[str]]:
    """Generate response to question using RAG approach."""
    # Retrieve relevant chunks
    results = chroma_manager.retrieve_similar(question)
    chunks = results["documents"][0]
    context = "\n\n---\n\n".join(chunks)

    # Construct prompt
    prompt = f"""You are a financial document analyst.
Answer the question using ONLY the context provided below.
If the answer is not in the context, say: "Not found in document."
Do not use any outside knowledge.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    # Generate response
    answer = ask_llm(prompt)
    return answer, chunks

print("✅ RAG response function defined")

# %% [markdown]
# ## 11. Demo Queries

# %%
print("💬 Running demo queries...")

demo_questions = [
    "What is the VaR confidence interval for the portfolio?",
    "What is the current allocation for Emerging Markets Equities?",
    "What strategic actions are planned for over-allocated assets?"
]

for question in demo_questions:
    print(f"\nQ: {question}")
    answer, chunks = generate_rag_response(question, chroma_manager)
    print(f"A: {answer}")
    print(f"   (Used {len(chunks)} chunks)")

# %% [markdown]
# ## 12. Multi-Viewpoint Summarization

# %%
VIEWPOINT_PROMPTS = {
    "Investor": (
        "Summarize this quarterly financial report from an investor's perspective. "
        "Focus on portfolio returns, asset performance, and growth opportunities."
    ),
    "Compliance Officer": (
        "Summarize this quarterly financial report from a compliance officer's perspective. "
        "Focus on risk controls, regulatory posture, VaR limits, and conservative guidelines."
    ),
    "C-Suite Executive": (
        "Summarize this quarterly financial report from a C-suite executive's perspective. "
        "Focus on strategic decisions, rebalancing actions, and forward outlook."
    ),
    "Risk Manager": (
        "Summarize this quarterly financial report from a risk manager's perspective. "
        "Focus on volatility metrics, stress testing, downside risks, and defensive positions."
    ),
}

def generate_multi_viewpoint_summaries(chroma_manager: ChromaDBManager, 
                                     viewpoints: Dict[str, str] = VIEWPOINT_PROMPTS) -> Tuple[Dict[str, str], List[str]]:
    """Generate summaries from multiple stakeholder perspectives."""
    # Retrieve broader context for summarization
    results = chroma_manager.retrieve_similar(
        "quarterly financial portfolio performance risk strategy outlook", 
        top_k=5
    )
    chunks = results["documents"][0]
    context = "\n\n---\n\n".join(chunks)

    summaries = {}
    for viewpoint, instruction in viewpoints.items():
        prompt = f"""{instruction}
Use ONLY the information in the context below. Do not add outside knowledge.
Keep the summary to 3-5 sentences.

CONTEXT:
{context}

SUMMARY:"""

        summaries[viewpoint] = ask_llm(prompt)

    return summaries, chunks

# Generate multi-viewpoint summaries
print("👥 Generating multi-viewpoint summaries...")
summaries, summary_chunks = generate_multi_viewpoint_summaries(chroma_manager)

for viewpoint, summary in summaries.items():
    print(f"\n{'='*60}")
    print(f"  {viewpoint.upper()} VIEW")
    print(f"{'='*60}")
    print(summary)

# %% [markdown]
# ## 13. RAGAS Evaluation

# %%
EVALUATION_QUESTIONS = [
    {
        "question": "What is the VaR confidence interval for the portfolio?",
        "ground_truth": "The VaR parameters track a 95% confidence interval that potential weekly downside variance will not exceed 2.1%."
    },
    {
        "question": "What is the current allocation for Emerging Markets Equities?",
        "ground_truth": "The current allocation for Emerging Markets Equities is 4.1%, below the 5.0% target, with a Q1 return of -2.4%."
    },
    {
        "question": "What strategic actions are planned for Domestic Large-Cap Equities?",
        "ground_truth": "Domestic Large-Cap Equities are over-allocated at 32.4% vs the 30.0% target and the strategic action is to Trim to Target."
    },
    {
        "question": "What is the Beta benchmark for the portfolio?",
        "ground_truth": "Volatility metrics are calibrated to a Beta of 0.88 against the broader market index."
    },
]

def run_ragas_evaluation(chroma_manager: ChromaDBManager, 
                        eval_questions: List[Dict] = EVALUATION_QUESTIONS) -> Dict:
    """Run RAGAS evaluation on the RAG pipeline."""
    try:
        # Setup RAGAS with Ollama
        judge_llm = LangchainLLMWrapper(OllamaLLM(model=Config.OLLAMA_MODEL))
        judge_embed = LangchainEmbeddingsWrapper(OllamaEmbeddings(model=Config.OLLAMA_MODEL))

        # Build evaluation dataset
        eval_data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

        for item in eval_questions:
            answer, chunks = generate_rag_response(item["question"], chroma_manager)
            eval_data["question"].append(item["question"])
            eval_data["answer"].append(answer)
            eval_data["contexts"].append(chunks)
            eval_data["ground_truth"].append(item["ground_truth"])

        dataset = Dataset.from_dict(eval_data)

        # Run evaluation
        results = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
            llm=judge_llm,
            embeddings=judge_embed,
        )

        return results
    except Exception as e:
        print(f"⚠️  Evaluation setup failed: {str(e)}")
        return None

# Run evaluation
print("📊 Running RAGAS evaluation...")
evaluation_results = run_ragas_evaluation(chroma_manager)

if evaluation_results:
    results_df = evaluation_results.to_pandas()
    
    print("\nEvaluation Results:")
    print(results_df[["faithfulness", "answer_relevancy", 
                    "context_recall", "context_precision"]].to_string())
    
    print("\nMean Scores:")
    mean_scores = results_df[["faithfulness", "answer_relevancy", 
                            "context_recall", "context_precision"]].mean()
    print(mean_scores)
else:
    print("⚠️  Evaluation could not be completed. Check Ollama server and model availability.")
# %% 
results_df.head()
    # %% [markdown]
# ## 14. Evaluation Metrics Interpretation
# 
# | Metric | What it means | Good score |
# |---|---|---|
# | **Faithfulness** | Answer only uses retrieved context, no hallucination | > 0.8 |
# | **Answer Relevancy** | Answer actually addresses the question | > 0.8 |
# | **Context Recall** | Retrieved chunks covered the right information | > 0.7 |
# | **Context Precision** | Retrieved chunks were all useful (no noise) | > 0.7 |
# 
# ### If scores are LOW — what to fix:
# ```
# Low Faithfulness      → LLM is going off-script. Strengthen your prompt:
#                          add "Do not use outside knowledge" more explicitly.
# 
# Low Answer Relevancy  → Retrieved chunks don't match the question well.
#                          Try smaller chunk_size (100-150 words).
# 
# Low Context Recall    → Right chunks not being retrieved.
#                          Try larger top_k (5 instead of 3).
# 
# Low Context Precision → Too many irrelevant chunks retrieved.
#                          Try smaller top_k or stricter filtering.
# ```

# %% [markdown]
# ## 15. Pipeline Summary

# %%
print("\n🎉 RAG Pipeline Complete!")
print("\nPipeline Summary:")
print(f"   📄 PDF processed: {Config.PDF_PATH}")
print(f"   📝 Total chunks: {total_docs}")
print(f"   🔍 Embedding model: {Config.EMBEDDING_MODEL}")
print(f"   🤖 LLM: {Config.OLLAMA_MODEL}")
print(f"   📊 Evaluation: {'✅ Completed' if evaluation_results else '⚠️  Skipped'}")
print("\nKey improvements in this refactored version:")
print("   ✅ Modular, reusable functions")
print("   ✅ Centralized configuration")
print("   ✅ Proper error handling")
print("   ✅ Clean separation of concerns")
print("   ✅ Type hints and documentation")
print("   ✅ Removed duplicate code")
print("   ✅ Production-ready structure")