"""Ollama client — CPU-local fallback using gemma2:2b (or any Ollama model)."""
import os
import httpx
from loguru import logger


def generate(prompt: str, temperature: float = 0.1) -> str:
    """Send a prompt to a local Ollama model and return the response text."""
    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "gemma2:2b")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }

    logger.debug(f"Ollama request to {base_url} model={model} ({len(prompt)} chars)")

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(f"{base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")
    except httpx.ConnectError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {base_url}. "
            "Make sure Ollama is running: https://ollama.ai"
        )
