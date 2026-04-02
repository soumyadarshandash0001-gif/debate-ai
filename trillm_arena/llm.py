import logging
import requests
import os
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Defaults for production (Cloud API)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 3

# API Key for Cloud
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


def call_openrouter(model: str, prompt: str, max_tokens: int, temperature: float) -> str:
    """Call OpenRouter API (OpenAI compatible) for hosted Llama/Qwen models."""
    if not OPENROUTER_API_KEY:
        raise LLMError("OPENROUTER_API_KEY missing in environment.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://trillm-arena.streamlit.app",  # Optional
        "X-Title": "TriLLM Arena",
    }

    # Map local Ollama IDs to OpenRouter IDs if necessary
    # e.g., llama3.2 -> meta-llama/llama-3.2-3b-instruct
    model_mapping = {
        "llama3.2": "meta-llama/llama-3.2-3b-instruct",
        "llama3.1:8b": "meta-llama/llama-3.1-8b-instruct",
        "qwen3-vl:4b": "qwen/qwen-2-vl-7b-instruct", # Best fit for Qwen VL
        "llama3.1": "meta-llama/llama-3.1-8b-instruct",
    }
    
    # Use mapped ID or fall back to original (in case user provider full OpenRouter ID)
    mapped_model = model_mapping.get(model.lower(), model)
    if "/" not in mapped_model:
        # If it's still a short ID, try to make it a generic OpenRouter ID
        if "llama" in mapped_model.lower():
            mapped_model = "meta-llama/llama-3.1-8b-instruct"
        elif "qwen" in mapped_model.lower():
            mapped_model = "qwen/qwen-2-7b-instruct"

    payload = {
        "model": mapped_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            raise LLMError(f"Unexpected API response format: {result}")
            
    except Exception as e:
        logger.error(f"OpenRouter API error: {str(e)}")
        raise LLMError(f"Cloud API failed: {str(e)}")


def call_llm(
    model: str,
    prompt: str,
    max_tokens: int = 400,
    temperature: float = 0.3,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """
    Call LLM (Local Ollama or Cloud API) with error handling.
    """
    
    # Heuristic: If we are in 'production' (Cloud environment) we MUST use API
    # Streamlit Cloud sets specific env vars, but we'll check for API key
    is_cloud = os.getenv("STREAMLIT_RUNTIME_ID") is not None or os.getenv("IS_PRODUCTION", "false").lower() == "true"
    
    if is_cloud:
        if not OPENROUTER_API_KEY:
            raise LLMError(
                "In Production (Cloud), you must provide OPENROUTER_API_KEY "
                "to run Llama/Qwen models since Ollama is not available."
            )
        return call_openrouter(model, prompt, max_tokens, temperature)

    # Local Ollama Implementation
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Calling local Ollama {model} (attempt {attempt + 1}/{MAX_RETRIES})")
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            result = response.json()
            return (result.get("response") or "").strip()
            
        except (Timeout, RequestException) as e:
            if attempt == MAX_RETRIES - 1:
                raise LLMError(
                    f"Failed to call local {model}. Ensure Ollama is running at {OLLAMA_URL}. "
                    "If you are in Production, use OPENROUTER_API_KEY."
                )
            continue
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")
    
    raise LLMError("Max retries exceeded")
