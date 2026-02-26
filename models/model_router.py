"""
Model router — auto-selects AI backend.

Priority:
  1. Gemini 2.0 Flash (Google AI Studio, free) — default
  2. Ollama local model (CPU, free) — when USE_OLLAMA=true
"""
import os
from loguru import logger


def generate(prompt: str, temperature: float = 0.1) -> str:
    """Route prompt to the appropriate AI backend."""
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"

    if use_ollama:
        logger.info("Using Ollama (USE_OLLAMA=true)")
        from models import ollama_client
        return ollama_client.generate(prompt, temperature=temperature)

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        logger.info("Using Gemini 2.0 Flash (Google AI Studio)")
        from models import gemini_client
        return gemini_client.generate(prompt, temperature=temperature)

    # Attempt Ollama as fallback even if USE_OLLAMA not set
    logger.warning("No GEMINI_API_KEY found — falling back to Ollama")
    from models import ollama_client
    return ollama_client.generate(prompt, temperature=temperature)
