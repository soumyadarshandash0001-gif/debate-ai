import os
import logging
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class Database:
    def __init__(self):
        self.client: Optional[Client] = None
        if SUPABASE_URL and SUPABASE_KEY and "your_supabase" not in SUPABASE_URL:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {str(e)}")

    def save_debate(self, debate_data: Dict[str, Any]) -> bool:
        """Save debate results to Supabase."""
        if not self.client:
            logger.warning("Supabase client not initialized. Skipping save.")
            return False

        try:
            # Try to extract winner from verdict if it's JSON
            import json
            verdict_text = debate_data.get("verdict", "{}")
            winner = "Unknown"
            reasoning = ""
            scores = {}
            
            try:
                verdict_json = json.loads(verdict_text)
                winner = verdict_json.get("winner", "TIE")
                reasoning = verdict_json.get("reasoning", "")
                scores = verdict_json.get("scores", {})
            except:
                reasoning = verdict_text

            payload = {
                "topic": debate_data.get("topic"),
                "model_a": debate_data.get("meta", {}).get("models", [None, None])[0],
                "model_b": debate_data.get("meta", {}).get("models", [None, None])[1],
                "rounds": debate_data.get("rounds"),
                "verdict": verdict_text,
                "winner": winner,
                "reasoning": reasoning,
                "scores": scores,
                "num_rounds": debate_data.get("num_rounds", 0)
            }
            
            response = self.client.table("debates").insert(payload).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving debate to Supabase: {str(e)}")
            return False

    def get_recent_debates(self, limit: int = 5) -> list:
        """Fetch recent debates for the gallery."""
        if not self.client:
            return []
        try:
            response = self.client.table("debates")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching debates: {str(e)}")
            return []

# Singleton instance
db = Database()
