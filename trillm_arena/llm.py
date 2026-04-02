import logging
import requests
import os
from typing import Optional
from requests.exceptions import RequestException, Timeout
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 3

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


def call_gemini(model: str, prompt: str, max_tokens: int, temperature: float) -> str:
    """Call Google Gemini API."""
    try:
        # Map specific model names if needed
        model_name = model
        if "gemini" not in model:
            model_name = "gemini-1.5-flash"
            
        gen_model = genai.GenerativeModel(model_name)
        response = gen_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise LLMError(f"Gemini API error: {str(e)}")


def call_llm(
    model: str,
    prompt: str,
    max_tokens: int = 400,
    temperature: float = 0.3,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """
    Call LLM (Gemini or Ollama) with error handling and retries.
    """
    
    if not model or not isinstance(model, str):
        raise LLMError(f"Invalid model: {model}")
    
    if "gemini" in model.lower() or os.getenv("USE_CLOUD_MODELS", "true").lower() == "true":
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found, trying local Ollama...")
        else:
            return call_gemini(model, prompt, max_tokens, temperature)

    # Fallback to Ollama logic
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
            logger.debug(f"Calling Ollama {model} (attempt {attempt + 1}/{MAX_RETRIES})")
            
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            text = (result.get("response") or "").strip()
            
            if not text and "qwen" in model.lower():
                # Qwen VL can spend its budget in internal "thinking".
                fallback_payload = {
                    "model": model,
                    "prompt": f"{prompt}\n\nRespond with only the final answer.",
                    "stream": False,
                }
                fallback = requests.post(OLLAMA_URL, json=fallback_payload, timeout=timeout)
                fallback.raise_for_status()
                text = (fallback.json().get("response") or "").strip()

            return text
            
        except (Timeout, RequestException) as e:
            if attempt == MAX_RETRIES - 1:
                raise LLMError(f"Failed to call {model} after {MAX_RETRIES} attempts.")
            continue
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")
    
    raise LLMError("Max retries exceeded")
