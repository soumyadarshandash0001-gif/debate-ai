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
            # Flatten or structure data for Supabase table 'debates'
            # Expected schema for 'debates' table:
            # id (uuid, pk), created_at (timestamp), topic (text), 
            # winner (text), model_a (text), model_b (text), 
            # rounds (jsonb), verdict (text)
            
            payload = {
                "topic": debate_data.get("topic"),
                "model_a": debate_data.get("meta", {}).get("models", [None, None])[0],
                "model_b": debate_data.get("meta", {}).get("models", [None, None])[1],
                "rounds": debate_data.get("rounds"),
                "verdict": debate_data.get("verdict"),
            }
            
            # Try to extract winner from verdict if it's JSON
            import json
            try:
                verdict_json = json.loads(debate_data.get("verdict", "{}"))
                payload["winner"] = verdict_json.get("winner")
            except:
                payload["winner"] = "Unknown"

            response = self.client.table("debates").insert(payload).execute()
            logger.info(f"Debate saved to Supabase: {response.data}")
            return True
        except Exception as e:
            logger.error(f"Error saving debate to Supabase: {str(e)}")
            return False

# Singleton instance
db = Database()
