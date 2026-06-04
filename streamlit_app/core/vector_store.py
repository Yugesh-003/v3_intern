# =============================================================================
# Vector Store Management
# =============================================================================

import os
import shutil
from typing import List, Dict, Tuple
import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from .config import Config


@st.cache_resource
def load_embedding_model(model_name: str) -> SentenceTransformer:
    """Load and cache the embedding model."""
    return SentenceTransformer(model_name)


class VectorStore:
    """Manages ChromaDB operations for document storage and retrieval."""
    
    def __init__(self, config: Config):
        self.config = config
        self.embed_model = load_embedding_model(config.EMBEDDING_MODEL)
        self.client = None
        self.collection = None
    
    def initialize(self) -> None:
        """Initialize fresh ChromaDB store."""
        import gc
        import time
        
        # Close existing client if any
        if self.client is not None:
            try:
                del self.collection
                del self.client
                gc.collect()
                time.sleep(0.5)  # Give Windows time to release file handles
            except:
                pass
        
        # Clean existing store with retry logic for Windows
        if os.path.exists(self.config.CHROMA_PATH):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shutil.rmtree(self.config.CHROMA_PATH)
                    break
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                        gc.collect()
                    else:
                        # If all retries fail, try to work with existing store
                        st.warning("Could not delete existing ChromaDB store. Using existing data.")
                        break
        
        # Create fresh client and collection
        self.client = chromadb.PersistentClient(path=self.config.CHROMA_PATH)
        
        # Try to delete existing collection if it exists
        try:
            self.client.delete_collection(name=self.config.COLLECTION_NAME)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=self.config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def store_chunks(self, chunks: List[Dict]) -> None:
        """Store document chunks with embeddings."""
        if not self.collection:
            raise RuntimeError("Vector store not initialized")
        
        ids, embeddings, documents, metadatas = [], [], [], []
        
        for chunk in chunks:
            embedding = self.embed_model.encode(chunk["content"]).tolist()
            
            # Prepare metadata (ChromaDB requires string values)
            metadata = {"type": chunk["type"]}
            for k, v in chunk["metadata"].items():
                metadata[k] = str(v)
            
            ids.append(chunk["id"])
            embeddings.append(embedding)
            documents.append(chunk["content"])
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def retrieve(self, query: str) -> Tuple[List[str], List[float]]:
        """
        Retrieve most similar chunks for query.
        
        Returns:
            contexts: List of retrieved text chunks
            distances: Similarity distances
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized")
        
        query_embedding = self.embed_model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.config.TOP_K,
            include=["documents", "distances"]
        )
        
        return results["documents"][0], results["distances"][0]
    
    def cleanup(self) -> None:
        """Clean up resources and close ChromaDB client."""
        try:
            if self.collection is not None:
                del self.collection
                self.collection = None
            if self.client is not None:
                del self.client
                self.client = None
            import gc
            gc.collect()
        except Exception as e:
            st.warning(f"Warning during cleanup: {e}")