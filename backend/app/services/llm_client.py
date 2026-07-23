"""
Shared Gemini client used by Module 1's LLM tie-breaker and Module 2's entity
verification pass. Degrades gracefully — returns None whenever GEMINI_API_KEY
is unset, the `google-generativeai` package isn't usable, or the call fails —
so callers fall back to their existing rule-based behavior instead of crashing.
"""

import json
import logging

from app.config import settings

log = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

_model = None
_configured = False


def _get_model():
    global _model, _configured
    if not _GENAI_AVAILABLE or not settings.GEMINI_API_KEY:
        return None
    if not _configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True
    if _model is None:
        _model = genai.GenerativeModel("gemini-1.5-flash")
    return _model


def call_gemini_json(prompt: str, timeout: float = 8.0) -> dict | None:
    """Calls Gemini with a prompt expecting a single JSON object back.
    Returns the parsed dict, or None if the client is unavailable, the call
    failed, or the response wasn't valid JSON."""
    model = _get_model()
    if model is None:
        return None
    try:
        response = model.generate_content(
            prompt,
            request_options={"timeout": timeout},
            generation_config={"response_mime_type": "application/json"},
        )
        return json.loads(response.text)
    except Exception as e:
        log.warning("Gemini call failed (%s); caller will use its fallback.", e)
        return None
