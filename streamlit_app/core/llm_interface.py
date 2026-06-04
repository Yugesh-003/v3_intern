# =============================================================================
# LLM Interface Module
# =============================================================================

import time
from typing import Tuple
import requests
from .config import Config


class LLMInterface:
    """Handles communication with Ollama LLM."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def generate(self, prompt: str) -> Tuple[str, float]:
        """
        Generate response from LLM.
        
        Returns:
            response: Generated text
            latency: Generation time in seconds
        """
        start_time = time.time()
        
        try:
            response = requests.post(
                self.config.OLLAMA_URL,
                json={
                    "model": self.config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            latency = time.time() - start_time
            return response.json()["response"], latency
            
        except Exception as e:
            latency = time.time() - start_time
            return f"Error: {str(e)}", latency