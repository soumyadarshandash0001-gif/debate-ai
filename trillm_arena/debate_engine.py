import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional

from .llm import call_llm, LLMError
from .prompts import (
    opening_prompt,
    rebuttal_prompt,
    defense_prompt,
    judge_prompt,
)

logger = logging.getLogger(__name__)

# ===== Configuration =====
MODEL_A = "mistral"
MODEL_B = "llama3"
FAST_JUDGE = "llama3"
HEAVY_JUDGE = "mixtral"

TIMEOUT_SECONDS = 120
MAX_WORKERS = 4


class DebateError(Exception):
    """Custom exception for debate-related errors."""
    pass


def _run_fast_judge(topic: str, a_text: str, b_text: str) -> str:
    """Run fast judgment on debate."""
    logger.debug("Running fast judge...")
    try:
        return call_llm(
            FAST_JUDGE,
            judge_prompt(topic, a_text, b_text),
            max_tokens=150,
            temperature=0,
        )
    except Exception as e:
        logger.error(f"Fast judge failed: {str(e)}")
        raise DebateError(f"Fast judge error: {str(e)}")


def _run_heavy_judge(topic: str, a_text: str, b_text: str) -> Optional[str]:
    """Run heavy judgment on debate."""
    logger.debug("Running heavy judge...")
    try:
        return call_llm(
            HEAVY_JUDGE,
            judge_prompt(topic, a_text, b_text),
            max_tokens=200,
            temperature=0,
        )
    except Exception as e:
        logger.warning(f"Heavy judge failed: {str(e)}")
        return None


def _validate_debate_result(result: Dict[str, Any]) -> bool:
    """Validate debate result structure."""
    required_keys = ["model_a", "model_b", "fast_verdict"]
    required_subkeys = ["opening", "rebuttal", "defense"]
    
    for key in required_keys:
        if key not in result:
            return False
    
    for model_key in ["model_a", "model_b"]:
        for subkey in required_subkeys:
            if subkey not in result[model_key]:
                return False
    
    return True


def run_debate_fast(
    topic: str,
    deep_review: bool = False,
) -> Dict[str, Any]:
    """
    Run a production-grade debate with parallel execution.
    
    Args:
        topic: The debate topic
        deep_review: Enable heavy judge for deeper analysis
        
    Returns:
        Dict containing debate results and verdicts
        
    Raises:
        DebateError: If debate execution fails
    """
    
    if not topic or len(topic.strip()) < 3:
        raise DebateError("Topic must be at least 3 characters long")
    
    logger.info(f"Starting debate on topic: {topic}")
    
    try:
        # ===== Parallel Debate Rounds =====
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {}
            
            # Openings
            futures["a_open"] = executor.submit(
                call_llm, MODEL_A, opening_prompt(topic)
            )
            futures["b_open"] = executor.submit(
                call_llm, MODEL_B, opening_prompt(topic)
            )
            
            # Get opening results
            a_open = futures["a_open"].result(timeout=TIMEOUT_SECONDS)
            b_open = futures["b_open"].result(timeout=TIMEOUT_SECONDS)
            
            # Rebuttals (dependent on openings)
            futures["a_rebut"] = executor.submit(
                call_llm, MODEL_A, rebuttal_prompt(topic, b_open)
            )
            futures["b_rebut"] = executor.submit(
                call_llm, MODEL_B, rebuttal_prompt(topic, a_open)
            )
            
            # Get rebuttal results
            a_rebut = futures["a_rebut"].result(timeout=TIMEOUT_SECONDS)
            b_rebut = futures["b_rebut"].result(timeout=TIMEOUT_SECONDS)
            
            # Defense (dependent on rebuttals)
            futures["a_def"] = executor.submit(
                call_llm, MODEL_A, defense_prompt(topic, b_rebut)
            )
            futures["b_def"] = executor.submit(
                call_llm, MODEL_B, defense_prompt(topic, a_rebut)
            )
            
            # Get defense results
            a_def = futures["a_def"].result(timeout=TIMEOUT_SECONDS)
            b_def = futures["b_def"].result(timeout=TIMEOUT_SECONDS)
        
        logger.info("Debate rounds completed successfully")
        
        # Combine debate texts
        model_a_text = f"{a_open}\n\n{a_rebut}\n\n{a_def}"
        model_b_text = f"{b_open}\n\n{b_rebut}\n\n{b_def}"
        
        # ===== Stage 1: Fast Judge =====
        fast_verdict = _run_fast_judge(topic, model_a_text, model_b_text)
        
        heavy_verdict = None
        auto_trigger = False
        
        # ===== Auto-trigger Logic for Heavy Judge =====
        try:
            verdict_json = json.loads(fast_verdict)
            scores = verdict_json.get("scores", {})
            
            score_a = scores.get("Model A")
            score_b = scores.get("Model B")
            
            if (
                isinstance(score_a, (int, float))
                and isinstance(score_b, (int, float))
                and abs(score_a - score_b) < 0.5
            ):
                auto_trigger = True
                logger.info("Auto-triggering heavy judge due to close scores")
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse fast verdict for auto-trigger: {str(e)}")
        
        # ===== Stage 2: Heavy Judge (Optional) =====
        if deep_review or auto_trigger:
            heavy_verdict = _run_heavy_judge(
                topic, model_a_text, model_b_text
            )
        
        # ===== Final Result =====
        result = {
            "model_a": {
                "opening": a_open,
                "rebuttal": a_rebut,
                "defense": a_def,
            },
            "model_b": {
                "opening": b_open,
                "rebuttal": b_rebut,
                "defense": b_def,
            },
            "fast_verdict": fast_verdict,
            "heavy_verdict": heavy_verdict,
            "meta": {
                "auto_heavy_judge": auto_trigger,
                "manual_deep_review": deep_review,
                "topic": topic,
            },
        }
        
        if not _validate_debate_result(result):
            logger.error("Debate result validation failed")
            raise DebateError("Invalid debate result structure")
        
        logger.info("Debate completed successfully")
        return result
        
    except TimeoutError as e:
        logger.error(f"Debate execution timed out: {str(e)}")
        raise DebateError(f"Debate timed out: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in debate: {str(e)}", exc_info=True)
        raise DebateError(f"Debate failed: {str(e)}")
