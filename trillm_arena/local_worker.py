import time
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from trillm_arena.database import db
from trillm_arena.debate_engine_iterative import run_iterative_debate
from trillm_arena.llm import LLMError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WORKER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

WORKER_ID = f"local-node-{os.uname().nodename}"

def start_worker():
    """
    Infinite loop monitoring Supabase for pending debate requests.
    When a request is found, it runs the debate locally using Ollama
    and pushes the result back to Supabase.
    """
    logger.info(f"🚀 RATIO Local Worker [{WORKER_ID}] Started")
    logger.info("Monitoring Supabase for pending debate requests...")
    
    while True:
        try:
            # 1. Poll for work
            request = db.get_pending_request()
            
            if request:
                req_id = request['id']
                topic = request['topic']
                rounds = request['rounds']
                models = request['models']
                
                logger.info(f"🔔 NEW REQUEST: {topic} ({rounds} rounds)")
                
                # 2. Update status to 'processing'
                db.update_request_status(req_id, "processing")
                
                try:
                    # 3. Execute debate LOCALLY using Ollama
                    # We ensure IS_PRODUCTION is false for the worker to force Ollama
                    os.environ["IS_PRODUCTION"] = "false"
                    
                    logger.info(f"⚔️ Executing debate via Local Ollama...")
                    result = run_iterative_debate(
                        topic=topic,
                        num_rounds=rounds,
                        model_a_id=models[0],
                        model_b_id=models[1],
                        judge_id="llama3.1:8b" # Fixed judge for quality
                    )
                    
                    # 4. Save result permanently
                    success = db.save_debate(result)
                    
                    if success:
                        # 5. Link the request to the finished debate
                        # We need to get the ID of the debate we just saved
                        # For simplicity, we just fetch the latest from the user
                        recent = db.get_recent_debates(limit=1)
                        debate_id = recent[0]['id'] if recent else None
                        
                        db.update_request_status(req_id, "completed", result_id=debate_id)
                        logger.info(f"✅ COMPLETED: {topic}")
                    else:
                        db.update_request_status(req_id, "failed")
                        logger.error(f"❌ FAILED to save result for {topic}")
                        
                except Exception as e:
                    logger.error(f"💥 EXECUTION ERROR: {str(e)}")
                    db.update_request_status(req_id, "failed")
                
            else:
                # No work, sleep for a bit
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Worker heartbeat error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set in your terminal environment.")
        sys.exit(1)
        
    start_worker()
