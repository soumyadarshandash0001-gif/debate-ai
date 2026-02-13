"""
TriLLM Arena - Main entry point for Streamlit Cloud deployment
"""
import sys
from pathlib import Path

# Add trillm_arena to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the app
from trillm_arena.app_v2 import *
