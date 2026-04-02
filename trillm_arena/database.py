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

    # --- ADVANCED: Task Queue for Local-Cloud Hybrid ---
    def create_debate_request(self, topic: str, rounds: int, models: list) -> Optional[str]:
        """Create a pending request for local models to process."""
        if not self.client: return None
        try:
            payload = {
                "topic": topic,
                "rounds": rounds,
                "models": models,
                "status": "pending",
                "created_at": "now()"
            }
            res = self.client.table("debate_requests").insert(payload).execute()
            return res.data[0]['id'] if res.data else None
        except Exception as e:
            logger.error(f"Failed to create request: {e}")
            return None

    def get_pending_request(self) -> Optional[Dict]:
        """Local worker calls this to see if there is any work to do."""
        if not self.client: return None
        try:
            res = self.client.table("debate_requests")\
                .select("*")\
                .eq("status", "pending")\
                .order("created_at")\
                .limit(1)\
                .execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error fetching pending: {e}")
            return None

    def update_request_status(self, request_id: str, status: str, result_id: str = None):
        """Update the status of a request."""
        if not self.client: return
        try:
            payload = {"status": status}
            if result_id: payload["result_id"] = result_id
            self.client.table("debate_requests").update(payload).eq("id", request_id).execute()
        except Exception as e:
            logger.error(f"Error updating request: {e}")

    def check_request_status(self, request_id: str) -> Optional[Dict]:
        """App UI calls this to see if the local worker finished."""
        if not self.client: return None
        try:
            res = self.client.table("debate_requests").select("*").eq("id", request_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return None

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
