import os
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    model_a_id: str
    model_b_id: str
    judge_id: str
    fast_judge_id: str
    heavy_judge_id: str
    model_a_label: str
    model_b_label: str
    judge_label: str


def get_model_config() -> ModelConfig:
    if load_dotenv:
        load_dotenv()

    model_a_id = os.getenv("MODEL_A_ID", "llama3.2")
    model_b_id = os.getenv("MODEL_B_ID", "qwen3-vl:4b")
    judge_id = os.getenv("JUDGE_MODEL_ID", "llama3.1:8b")

    fast_judge_id = os.getenv("FAST_JUDGE_ID", judge_id)
    heavy_judge_id = os.getenv("HEAVY_JUDGE_ID", judge_id)

    model_a_label = os.getenv("MODEL_A_LABEL", "LLaMA 3.2")
    model_b_label = os.getenv("MODEL_B_LABEL", "Qwen 3 VL 4B")
    judge_label = os.getenv("JUDGE_LABEL", "LLaMA 3.1 8B")

    return ModelConfig(
        model_a_id=model_a_id,
        model_b_id=model_b_id,
        judge_id=judge_id,
        fast_judge_id=fast_judge_id,
        heavy_judge_id=heavy_judge_id,
        model_a_label=model_a_label,
        model_b_label=model_b_label,
        judge_label=judge_label,
    )
