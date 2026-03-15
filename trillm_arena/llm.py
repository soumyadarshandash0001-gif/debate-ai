import logging
import requests
from typing import Optional
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 3


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


def call_llm(
    model: str,
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 0.3,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """
    Call Ollama LLM with error handling and retries.
    
    Args:
        model: Model name (e.g., 'llama3.2', 'qwen3-vl:4b')
        prompt: Prompt text to send to the model
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation (0-1)
        timeout: Request timeout in seconds
        
    Returns:
        Generated text response
        
    Raises:
        LLMError: If the request fails
    """
    
    if not model or not isinstance(model, str):
        raise LLMError(f"Invalid model: {model}")
    
    if not prompt or not isinstance(prompt, str):
        raise LLMError("Prompt must be a non-empty string")
    
    if not 0 <= temperature <= 1:
        raise LLMError(f"Temperature must be between 0 and 1, got {temperature}")
    
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
            logger.debug(f"Calling {model} (attempt {attempt + 1}/{MAX_RETRIES})")
            
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            
            result = response.json()

            if "response" not in result:
                raise LLMError(f"Invalid response format from {model}")

            text = (result.get("response") or "").strip()

            if not text and "qwen" in model.lower():
                # Qwen VL can spend its budget in internal "thinking".
                # Retry once without options to coax a final response.
                fallback_payload = {
                    "model": model,
                    "prompt": f"{prompt}\n\nRespond with only the final answer.",
                    "stream": False,
                }
                fallback = requests.post(
                    OLLAMA_URL,
                    json=fallback_payload,
                    timeout=timeout,
                )
                fallback.raise_for_status()
                fallback_result = fallback.json()
                text = (fallback_result.get("response") or "").strip()

            return text
            
        except Timeout as e:
            logger.warning(
                f"Timeout calling {model} (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}"
            )
            if attempt == MAX_RETRIES - 1:
                raise LLMError(f"Timeout after {MAX_RETRIES} attempts: {str(e)}")
        
        except RequestException as e:
            logger.error(
                f"Request error calling {model} (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}"
            )
            if attempt == MAX_RETRIES - 1:
                raise LLMError(
                    f"Failed to call {model} after {MAX_RETRIES} attempts. "
                    f"Ensure Ollama is running at {OLLAMA_URL}"
                )
        
        except Exception as e:
            logger.error(f"Unexpected error calling {model}: {str(e)}", exc_info=True)
            raise LLMError(f"Unexpected error: {str(e)}")
    
    raise LLMError("Max retries exceeded")
