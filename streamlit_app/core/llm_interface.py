# =============================================================================
# LLM Interface — supports Ollama (local) and AWS Bedrock (Converse API)
# =============================================================================
# The Bedrock Converse API is a UNIFIED interface that works with every
# Bedrock model (Amazon Nova, Claude, Titan, Mistral, Llama, etc.)
# without changing any request/response parsing code.
# =============================================================================

import time
from abc import ABC, abstractmethod
from typing import Tuple

import requests
from .config import Config


# =============================================================================
# Base Interface
# =============================================================================

class BaseLLMInterface(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> Tuple[str, float]:
        """Generate a response. Returns (text, latency_seconds)."""


# =============================================================================
# Ollama — local inference
# =============================================================================

class OllamaInterface(BaseLLMInterface):
    """Communicate with a locally running Ollama server."""

    def __init__(self, config: Config):
        self.config = config

    def generate(self, prompt: str) -> Tuple[str, float]:
        start = time.time()
        try:
            resp = requests.post(
                self.config.OLLAMA_URL,
                json={
                    "model":  self.config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            resp.raise_for_status()
            latency = time.time() - start
            return resp.json()["response"].strip(), latency
        except Exception as e:
            latency = time.time() - start
            return f"Error (Ollama): {e}", latency


# =============================================================================
# AWS Bedrock — Converse API (model-agnostic)
# =============================================================================

class BedrockInterface(BaseLLMInterface):
    """
    Uses the AWS Bedrock *Converse API* — a single unified request format
    that works with ALL Bedrock models:
        amazon.nova-lite-v1:0          ← active default
        amazon.nova-micro-v1:0
        amazon.nova-pro-v1:0
        anthropic.claude-3-haiku-...   ← once use-case form is approved
        mistral.mistral-7b-instruct-v0:2
        meta.llama3-8b-instruct-v1:0

    Auth: run `aws configure` once — boto3 picks it up automatically.
    """

    def __init__(self, config: Config):
        self.config  = config
        self._client = None     # lazy init

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import boto3
        except ImportError as exc:
            raise ImportError(
                "boto3 is required for AWS Bedrock.  Run:  pip install boto3"
            ) from exc
        # boto3 reads credentials from ~/.aws/credentials (aws configure)
        self._client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.config.BEDROCK_REGION,
        )
        return self._client

    def generate(self, prompt: str) -> Tuple[str, float]:
        start = time.time()
        try:
            client = self._get_client()

            # ── Converse API — same format for every model ────────────────────
            response = client.converse(
                modelId=self.config.BEDROCK_MODEL_ID,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}],
                    }
                ],
                inferenceConfig={
                    "maxTokens":   1024,
                    "temperature": 0.3,   # lower → more format-faithful
                },
            )

            # Response shape is identical across all models
            text    = response["output"]["message"]["content"][0]["text"].strip()
            latency = time.time() - start
            return text, latency

        except Exception as e:
            latency = time.time() - start
            return f"Error (Bedrock): {e}", latency


# =============================================================================
# Factory — used by SummarizationPipeline
# =============================================================================

class LLMInterface:
    """
    Factory wrapper — returns the right backend based on config.LLM_PROVIDER.

    Usage (unchanged from the rest of the codebase):
        llm = LLMInterface(config)
        text, latency = llm.generate(prompt)
    """

    def __new__(cls, config: Config) -> BaseLLMInterface:  # type: ignore[override]
        provider = (config.LLM_PROVIDER or "ollama").lower().strip()
        if provider == "bedrock":
            return BedrockInterface(config)
        return OllamaInterface(config)