"""
Debate prompts for TriLLM Arena.
"""


def opening_prompt(topic: str) -> str:
    """Generate opening argument prompt."""
    return f"""You are participating in a formal AI debate.

Topic:
"{topic}"

Rules:
- Be logically rigorous
- No hallucinations
- No emotional language
- Stay concise (max 200 words)

Give your opening argument for or against this topic."""


def rebuttal_prompt(topic: str, opponent_text: str) -> str:
    """Generate rebuttal prompt."""
    return f"""You are debating an AI opponent.

Topic:
"{topic}"

Opponent's Argument:
{opponent_text}

Task:
- Critically analyze opponent logic
- Point out flaws or assumptions
- Do NOT repeat their points
- Max 150 words

Provide your rebuttal."""


def defense_prompt(topic: str, opponent_rebuttal: str) -> str:
    """Generate defense prompt."""
    return f"""Topic:
"{topic}"

Opponent's Rebuttal:
{opponent_rebuttal}

Task:
- Defend your original position
- Clarify misunderstood points
- Avoid introducing new arguments
- Max 150 words

Provide your defense."""


def judge_prompt(topic: str, a_text: str, b_text: str) -> str:
    """Generate judge prompt for debate evaluation."""
    return f"""You are an impartial AI judge evaluating a debate.

Topic:
"{topic}"

Model A's Complete Argument:
{a_text}

Model B's Complete Argument:
{b_text}

Task: Evaluate strictly on:
1. Logical consistency
2. Factual accuracy
3. Depth of reasoning
4. Clarity of arguments
5. Risk of hallucination

Return ONLY valid JSON (no markdown, no explanation):

{{
  "winner": "Model A" or "Model B",
  "scores": {{
    "Model A": <float 0-10>,
    "Model B": <float 0-10>
  }},
  "reasoning": "<concise 1-2 sentence explanation>"
}}"""
