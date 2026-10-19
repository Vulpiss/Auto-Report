import time
from typing import Optional

from app.config import USE_LLM


class LLMError(Exception):
    pass


def call_llm(prompt: str) -> str:
    """
    Placeholder for real LLM provider integration.

    In MVP mode, USE_LLM is usually False, so this function raises
    and the system falls back to deterministic insights.
    """
    if not USE_LLM:
        raise RuntimeError("LLM disabled")

    # TODO: Add OpenAI / other LLM provider integration here.
    raise NotImplementedError("LLM provider is not configured.")


def call_llm_with_retry(
    prompt: str,
    max_retries: int = 3,
    delay: float = 1.5
) -> str:
    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            return call_llm(prompt)
        except Exception as error:
            last_error = error
            time.sleep(delay * (attempt + 1))

    raise LLMError(f"LLM failed after {max_retries} attempts: {last_error}")