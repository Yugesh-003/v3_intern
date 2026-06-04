# =============================================================================
# Text Chunking Module
# =============================================================================

import json
from typing import List, Dict, Tuple
from .config import Config


class TextChunker:
    """Handles text chunking with overlap and table preservation."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping word-based chunks."""
        words = text.split()
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.config.CHUNK_SIZE
            chunks.append(" ".join(words[start:end]))
            start += self.config.CHUNK_SIZE - self.config.CHUNK_OVERLAP
        
        return chunks
    
    def table_to_text(self, table_data: List[Dict]) -> str:
        """Convert table data to readable text."""
        if not table_data or not isinstance(table_data, list):
            return json.dumps(table_data)
        
        if not table_data or not isinstance(table_data[0], dict):
            return json.dumps(table_data)
        
        headers = list(table_data[0].keys())
        lines = [f"Table columns: {' | '.join(headers)}"]
        
        for row in table_data:
            row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
            lines.append(row_text)
        
        return "\n".join(lines)
    
    def prepare_chunks(self, main_content: str, tables: List[Dict]) -> Tuple[List[Dict], int]:
        """
        Prepare document chunks for embedding.
        
        Returns:
            chunks: List of chunk dictionaries
            total_count: Total number of chunks
        """
        chunks = []
        chunk_id = 0
        
        # Process main content
        for chunk_text in self.chunk_text(main_content):
            chunks.append({
                "id": f"text_{chunk_id}",
                "type": "text",
                "content": chunk_text,
                "metadata": {"chunk_index": chunk_id}
            })
            chunk_id += 1
        
        # Process tables (never split)
        for idx, table in enumerate(tables):
            chunks.append({
                "id": f"table_{idx}",
                "type": "table",
                "content": self.table_to_text(table["data"]),
                "metadata": {
                    "table_index": idx,
                    "page": table["page"]
                }
            })
        
        return chunks, len(chunks)