"""
Iterative Debate Engine - Models respond to each other over multiple rounds.
"""
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from .llm import call_llm, LLMError
from .prompts import (
    opening_prompt,
    iterative_response_prompt,
    judge_prompt,
)

logger = logging.getLogger(__name__)

# ===== Configuration =====
MODEL_A = "llama3.2"
MODEL_B = "llama3.1:8b"
JUDGE_MODEL = "llama3.1:8b"

TIMEOUT_SECONDS = 120
MAX_WORKERS = 2
DEBATE_ROUNDS = 3  # Number of iterative exchange rounds


class DebateError(Exception):
    """Custom exception for debate-related errors."""
    pass


def run_iterative_debate(
    topic: str,
    num_rounds: int = DEBATE_ROUNDS,
) -> Dict[str, Any]:
    """
    Run iterative debate where models respond to each other round by round.
    
    Each round:
    1. Model A responds (based on Model B's previous message)
    2. Model B responds (based on Model A's new message)
    3. Results displayed in real-time
    
    Finally:
    - Judge evaluates all rounds and provides verdict
    
    Args:
        topic: The debate topic
        num_rounds: Number of iterative rounds (default: 3)
        
    Returns:
        Dict with all rounds and final judgment
    """
    
    if not topic or len(topic.strip()) < 3:
        raise DebateError("Topic must be at least 3 characters long")
    
    if num_rounds < 1 or num_rounds > 5:
        raise DebateError("Number of rounds must be between 1 and 5")
    
    logger.info(f"Starting {num_rounds}-round iterative debate on: {topic}")
    
    try:
        rounds: List[Dict[str, str]] = []
        model_a_context = ""  # Previous Model A response
        model_b_context = ""  # Previous Model B response
        
        # ===== OPENING ROUND =====
        logger.info("Getting opening statements...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_a = executor.submit(
                call_llm, MODEL_A, opening_prompt(topic), max_tokens=250
            )
            future_b = executor.submit(
                call_llm, MODEL_B, opening_prompt(topic), max_tokens=250
            )
            
            opening_a = future_a.result(timeout=TIMEOUT_SECONDS)
            opening_b = future_b.result(timeout=TIMEOUT_SECONDS)
        
        model_a_context = opening_a
        model_b_context = opening_b
        
        rounds.append({
            "round": 0,
            "model_a": opening_a,
            "model_b": opening_b,
            "type": "opening"
        })
        
        logger.info(f"Opening statements completed. Model A: {len(opening_a)} chars, Model B: {len(opening_b)} chars")
        
        # ===== ITERATIVE ROUNDS =====
        for round_num in range(1, num_rounds + 1):
            logger.info(f"Starting round {round_num}/{num_rounds}...")
            
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Model A responds to Model B's latest message
                prompt_a = iterative_response_prompt(
                    topic,
                    model_b_context,
                    "Model B"
                )
                future_a = executor.submit(
                    call_llm, MODEL_A, prompt_a, max_tokens=200
                )
                
                # Model B responds to Model A's latest message
                prompt_b = iterative_response_prompt(
                    topic,
                    model_a_context,
                    "Model A"
                )
                future_b = executor.submit(
                    call_llm, MODEL_B, prompt_b, max_tokens=200
                )
                
                response_a = future_a.result(timeout=TIMEOUT_SECONDS)
                response_b = future_b.result(timeout=TIMEOUT_SECONDS)
            
            model_a_context = response_a
            model_b_context = response_b
            
            rounds.append({
                "round": round_num,
                "model_a": response_a,
                "model_b": response_b,
                "type": "iterative"
            })
            
            logger.info(f"Round {round_num} completed")
        
        # ===== FINAL JUDGMENT =====
        logger.info("Getting final judgment...")
        
        # Compile full debate history
        full_debate_a = "\n\n---\n\n".join([r["model_a"] for r in rounds])
        full_debate_b = "\n\n---\n\n".join([r["model_b"] for r in rounds])
        
        try:
            verdict = call_llm(
                JUDGE_MODEL,
                judge_prompt(topic, full_debate_a, full_debate_b),
                max_tokens=300,
                temperature=0,
            )
        except Exception as e:
            logger.warning(f"Judgment failed: {str(e)}")
            verdict = json.dumps({
                "winner": "TIE",
                "reasoning": "Judge could not evaluate. Both arguments had merit.",
                "scores": {"Model A": 5.0, "Model B": 5.0}
            })
        
        # ===== COMPILE RESULTS =====
        result = {
            "topic": topic,
            "rounds": rounds,
            "num_rounds": num_rounds,
            "full_debate": {
                "model_a": full_debate_a,
                "model_b": full_debate_b,
            },
            "verdict": verdict,
            "meta": {
                "mode": "iterative",
                "models": [MODEL_A, MODEL_B],
                "judge": JUDGE_MODEL,
            }
        }
        
        logger.info("Iterative debate completed successfully")
        return result
        
    except TimeoutError as e:
        logger.error(f"Debate execution timed out: {str(e)}")
        raise DebateError(f"Debate timed out: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in iterative debate: {str(e)}", exc_info=True)
        raise DebateError(f"Debate failed: {str(e)}")


def get_debate_rounds_stream(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract debate rounds for streaming display.
    
    Returns list of rounds with timing info for UI display.
    """
    rounds = []
    for i, round_data in enumerate(result.get("rounds", [])):
        rounds.append({
            "round_number": round_data["round"],
            "is_opening": round_data["type"] == "opening",
            "model_a_response": round_data["model_a"],
            "model_b_response": round_data["model_b"],
        })
    
    return rounds
