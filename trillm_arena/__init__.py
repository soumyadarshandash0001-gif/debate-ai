"""TriLLM Arena - Production-grade multi-LLM debate engine."""

__version__ = "1.0.0"
__author__ = "TriLLM Team"

from .debate_engine import run_debate_fast, DebateError

__all__ = ["run_debate_fast", "DebateError"]
