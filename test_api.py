#!/usr/bin/env python3
"""
Simple API client for testing the TriLLM Arena API.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Optional

BASE_URL = "http://localhost:8000"

sys.path.insert(0, str(Path(__file__).parent))
try:
    from trillm_arena.model_config import get_model_config
except ImportError:
    from model_config import get_model_config

MODEL_CONFIG = get_model_config()
MODEL_A_LABEL = MODEL_CONFIG.model_a_label
MODEL_B_LABEL = MODEL_CONFIG.model_b_label
JUDGE_LABEL = MODEL_CONFIG.judge_label


class TriLLMClient:
    """Client for TriLLM Arena API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    def health(self) -> dict:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def debate(self, topic: str, deep_review: bool = False) -> dict:
        """Run a debate."""
        payload = {
            "topic": topic,
            "deep_review": deep_review,
        }
        response = requests.post(
            f"{self.base_url}/debate",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def main():
    """Main function."""
    client = TriLLMClient()
    
    # Check health
    print("🔍 Checking API health...")
    try:
        health = client.health()
        print(f"✅ API is {health['status']}")
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        sys.exit(1)
    
    # Run debate
    if len(sys.argv) < 2:
        topic = "Should AI regulation be government-led or industry-led?"
    else:
        topic = " ".join(sys.argv[1:])
    
    print(f"\n📝 Running debate on: {topic}")
    print("⏳ This may take a few minutes...\n")
    
    try:
        result = client.debate(topic, deep_review=False)
        
        # Pretty print results
        print("=" * 80)
        print(f"MODEL A - {MODEL_A_LABEL}")
        print("=" * 80)
        print("\nOpening Argument:")
        print(result["model_a"]["opening"])
        print("\nRebuttal:")
        print(result["model_a"]["rebuttal"])
        print("\nDefense:")
        print(result["model_a"]["defense"])
        
        print("\n" + "=" * 80)
        print(f"MODEL B - {MODEL_B_LABEL}")
        print("=" * 80)
        print("\nOpening Argument:")
        print(result["model_b"]["opening"])
        print("\nRebuttal:")
        print(result["model_b"]["rebuttal"])
        print("\nDefense:")
        print(result["model_b"]["defense"])
        
        print("\n" + "=" * 80)
        print(f"JUDGE VERDICT ({JUDGE_LABEL})")
        print("=" * 80)
        try:
            verdict = json.loads(result["fast_verdict"])
            print(json.dumps(verdict, indent=2))
        except:
            print(result["fast_verdict"])
        
        if result.get("heavy_verdict"):
            print("\n" + "=" * 80)
            print("HEAVY JUDGE VERDICT")
            print("=" * 80)
            try:
                verdict = json.loads(result["heavy_verdict"])
                print(json.dumps(verdict, indent=2))
            except:
                print(result["heavy_verdict"])
        
        print("\n✅ Debate completed successfully!")
        
    except Exception as e:
        print(f"❌ Debate failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
