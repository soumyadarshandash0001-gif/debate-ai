"""
Open-source fact-checking bot for debate analysis
Uses Wikipedia API + rule-based verification
"""

import requests
from typing import Dict, List, Any
import re
from datetime import datetime

class FactBot:
    """Fact-checking bot using open-source APIs (Wikipedia, Wikidata)"""
    
    def __init__(self):
        self.wikipedia_url = "https://en.wikipedia.org/w/api.php"
        self.wikidata_url = "https://www.wikidata.org/w/api.php"
        self.timeout = 5
    
    def check_claim(self, claim: str) -> Dict[str, Any]:
        """Fact-check a claim using Wikipedia search"""
        
        results = {
            "claim": claim,
            "timestamp": datetime.now().isoformat(),
            "facts_found": [],
            "confidence": 0.0,
            "sources": [],
            "grounding_score": 0.0,  # 0.0-1.0
        }
        
        # Extract keywords
        keywords = self._extract_keywords(claim)
        
        if not keywords:
            results["confidence"] = 0.5
            results["grounding_score"] = 0.3
            return results
        
        # Search Wikipedia for each keyword
        for keyword in keywords[:3]:  # Limit to 3 searches
            facts = self._search_wikipedia(keyword)
            if facts:
                results["facts_found"].extend(facts)
                results["sources"].append(f"Wikipedia: {keyword}")
        
        # Calculate grounding score
        if results["facts_found"]:
            results["confidence"] = min(1.0, len(results["facts_found"]) / 3.0)
            results["grounding_score"] = min(1.0, 0.4 + (len(results["facts_found"]) * 0.2))
        else:
            results["grounding_score"] = 0.2  # Ungrounded claim
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Remove common words
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "and", "or",
            "but", "in", "on", "at", "to", "for", "of", "with", "by"
        }
        
        # Simple tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        return keywords[:5]  # Return top 5 keywords
    
    def _search_wikipedia(self, keyword: str) -> List[Dict[str, str]]:
        """Search Wikipedia for information"""
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": keyword,
                "format": "json",
                "srlimit": 3,
            }
            
            response = requests.get(
                self.wikipedia_url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("query", {}).get("search", []):
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", "")[:200],
                        "url": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}"
                    })
                
                return results
        except:
            pass
        
        return []
    
    def analyze_debate_side(self, argument: str) -> Dict[str, Any]:
        """Analyze one debate side for factual grounding"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', argument)
        
        analysis = {
            "argument": argument,
            "total_claims": len(sentences),
            "grounded_claims": 0,
            "ungrounded_claims": 0,
            "overall_grounding": 0.0,
            "claims": [],
        }
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:
                continue
            
            claim_analysis = self.check_claim(sentence)
            analysis["claims"].append(claim_analysis)
            
            if claim_analysis["grounding_score"] > 0.5:
                analysis["grounded_claims"] += 1
            else:
                analysis["ungrounded_claims"] += 1
        
        # Calculate overall grounding
        if analysis["total_claims"] > 0:
            analysis["overall_grounding"] = (
                analysis["grounded_claims"] / analysis["total_claims"]
            )
        
        return analysis
    
    def get_judge_signals(self, model_a_arg: str, model_b_arg: str) -> Dict[str, Any]:
        """Generate signals for the judge"""
        
        analysis_a = self.analyze_debate_side(model_a_arg)
        analysis_b = self.analyze_debate_side(model_b_arg)
        
        signals = {
            "model_a_grounding": analysis_a["overall_grounding"],
            "model_b_grounding": analysis_b["overall_grounding"],
            "recommendation": self._recommend(analysis_a, analysis_b),
            "confidence": max(
                analysis_a["overall_grounding"],
                analysis_b["overall_grounding"]
            ),
            "analysis": {
                "model_a": analysis_a,
                "model_b": analysis_b,
            }
        }
        
        return signals
    
    def _recommend(self, analysis_a: Dict, analysis_b: Dict) -> str:
        """Recommend based on grounding"""
        
        grounding_a = analysis_a["overall_grounding"]
        grounding_b = analysis_b["overall_grounding"]
        
        if grounding_a > grounding_b + 0.2:
            return "Model A more grounded"
        elif grounding_b > grounding_a + 0.2:
            return "Model B more grounded"
        else:
            return "Comparable grounding"


# Initialize bot
fact_bot = FactBot()


if __name__ == "__main__":
    # Test
    claim = "Python was created by Guido van Rossum in 1991"
    result = fact_bot.check_claim(claim)
    print(f"Claim: {claim}")
    print(f"Grounding score: {result['grounding_score']}")
    print(f"Sources: {result['sources']}")
