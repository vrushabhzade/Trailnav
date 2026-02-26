"""Gemini AI Studio client — uses the new google-genai SDK.
Includes automatic retry with exponential back-off for 429 rate limits (free tier).
"""
import os
import time
from google import genai
from google.genai import types
from loguru import logger


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY not set. Get a free key at https://aistudio.google.com/app/apikey"
        )
    return genai.Client(api_key=api_key)


def generate(prompt: str, temperature: float = 0.1, max_retries: int = 2) -> str:
    """Send a prompt to Gemini. Fails fast on rate limits (max 2 retries, 12s wait cap).
    The caller (reasoner) handles timeout and fallback logic.
    """
    client = _get_client()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

    logger.debug(f"Gemini request model={model_name} ({len(prompt)} chars)")

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature),
            )
            return response.text

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                import re as _re
                m = _re.search(r"retryDelay.*?(\d+)s", err_str)
                # Cap wait to 12s — caller has a 20s total timeout
                wait = min(int(m.group(1)) if m else 8, 12)
                logger.warning(
                    f"Gemini rate limit (attempt {attempt+1}/{max_retries}). "
                    f"Waiting {wait}s..."
                )
                time.sleep(wait)
                continue
            logger.error(f"Gemini API Error: {err_str}")
            raise

    raise RuntimeError("Gemini rate-limited after retries. Falling back to keyword scoring.")

