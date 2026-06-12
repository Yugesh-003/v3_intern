"""
RAG Pipeline — Financial Document Summarization
Production-Quality Refactored Version

A clean, modular RAG pipeline for financial document analysis with:
- PDF extraction (text + tables + headers/footers)
- Intelligent chunking (section-aware, table-preserving)
- Local embeddings (all-MiniLM-L6-v2)
- Vector storage (ChromaDB)
- Multi-viewpoint summarization
- RAGAS evaluation
"""

# =============================================================================
# IMPORTS & DEPENDENCIES
# =============================================================================

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

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

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

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def setup_models() -> Tuple[SentenceTransformer, Optional[Any]]:
    """Initialize embedding model and optional Gemini client."""
    embed_model = SentenceTransformer(Config.EMBEDDING_MODEL)
    
    gemini_client = None
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel("gemini-2.0-flash")
    
    return embed_model, gemini_client

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

# =============================================================================
# PDF EXTRACTION
# =============================================================================

def extract_pdf_content(pdf_path: str) -> Tuple[List[Dict], str, List[Dict], List[Dict], int]:
    """
    Extract structured content from PDF including text, tables, headers, and footers.
    
    Returns:
        Tuple of (header_content, main_content, footer_content, tables_json, image_count)
    """
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

# =============================================================================
# TEXT CHUNKING
# =============================================================================

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

# =============================================================================
# VECTOR STORAGE
# =============================================================================

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

# =============================================================================
# RAG QUERY & RESPONSE
# =============================================================================

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

# =============================================================================
# MULTI-VIEWPOINT SUMMARIZATION
# =============================================================================

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

# =============================================================================
# EVALUATION WITH RAGAS
# =============================================================================

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

# =============================================================================
# MAIN PIPELINE CLASS
# =============================================================================

class RAGPipeline:
    """Main RAG pipeline orchestrator."""
    
    def __init__(self, config: Config = Config()):
        self.config = config
        self.embed_model = None
        self.gemini_client = None
        self.chroma_manager = None
        self.documents = None
    
    def initialize(self) -> None:
        """Initialize all pipeline components."""
        print("🚀 Initializing RAG Pipeline...")
        
        # Setup models
        self.embed_model, self.gemini_client = setup_models()
        print("✅ Models loaded")
        
        # Setup ChromaDB
        self.chroma_manager = ChromaDBManager(
            self.config.CHROMA_PATH,
            self.config.COLLECTION_NAME,
            self.embed_model
        )
        print("✅ ChromaDB manager ready")
    
    def extract_and_process_pdf(self) -> None:
        """Extract and process PDF content."""
        print(f"📄 Extracting PDF: {self.config.PDF_PATH}")
        
        header_content, main_content, footer_content, tables_json, image_count = extract_pdf_content(
            self.config.PDF_PATH
        )
        
        print(f"   📊 Found {len(tables_json)} tables, {image_count} images")
        
        # Prepare document chunks
        self.documents = prepare_document_chunks(
            main_content, header_content, footer_content, tables_json
        )
        
        main_chunks = sum(1 for d in self.documents if d['type'] == 'main_content')
        table_chunks = sum(1 for d in self.documents if d['type'] == 'table')
        print(f"   📝 Created {main_chunks} text chunks, {table_chunks} table chunks")
    
    def build_vector_store(self) -> None:
        """Build and populate vector store."""
        print("🔍 Building vector store...")
        
        self.chroma_manager.initialize_fresh_store()
        self.chroma_manager.store_documents(self.documents)
        
        total_docs = self.chroma_manager.get_count()
        print(f"✅ Stored {total_docs} documents in ChromaDB")
    
    def run_demo_queries(self) -> None:
        """Run demonstration queries."""
        print("\n💬 Running demo queries...")
        
        demo_questions = [
            "What is the VaR confidence interval for the portfolio?",
            "What strategic actions are planned for over-allocated assets?"
        ]
        
        for question in demo_questions:
            print(f"\nQ: {question}")
            answer, _ = generate_rag_response(question, self.chroma_manager)
            print(f"A: {answer}")
    
    def run_multi_viewpoint_analysis(self) -> Dict[str, str]:
        """Generate multi-viewpoint summaries."""
        print("\n👥 Generating multi-viewpoint summaries...")
        
        summaries, _ = generate_multi_viewpoint_summaries(self.chroma_manager)
        
        for viewpoint, summary in summaries.items():
            print(f"\n{'='*60}")
            print(f"  {viewpoint.upper()} VIEW")
            print(f"{'='*60}")
            print(summary)
        
        return summaries
    
    def run_evaluation(self) -> Dict:
        """Run RAGAS evaluation."""
        print("\n📊 Running RAGAS evaluation...")
        
        try:
            results = run_ragas_evaluation(self.chroma_manager)
            results_df = results.to_pandas()
            
            print("\nEvaluation Results:")
            print(results_df[["question", "faithfulness", "answer_relevancy", 
                            "context_recall", "context_precision"]].to_string())
            
            print("\nMean Scores:")
            mean_scores = results_df[["faithfulness", "answer_relevancy", 
                                    "context_recall", "context_precision"]].mean()
            print(mean_scores)
            
            return results
        except Exception as e:
            print(f"⚠️  Evaluation failed: {str(e)}")
            return {}
    
    def run_full_pipeline(self) -> None:
        """Execute the complete RAG pipeline."""
        try:
            self.initialize()
            self.extract_and_process_pdf()
            self.build_vector_store()
            self.run_demo_queries()
            self.run_multi_viewpoint_analysis()
            self.run_evaluation()
            print("\n🎉 Pipeline completed successfully!")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
            raise

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Create and run pipeline
    pipeline = RAGPipeline()
    pipeline.run_full_pipeline()