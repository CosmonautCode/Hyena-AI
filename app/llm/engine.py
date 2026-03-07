
from llama_cpp import Llama
from pathlib import Path

MODEL_PATH = Path("app/models/Hyena3-4B-Instruct-2507.Q2_K.gguf")

def load_instances(num_instances=1):
    """Load LLM instances."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    instances = []
    for _ in range(num_instances):
        llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=8192,  # Full capacity - only loading 1 instance total
            n_threads=8,
            n_gpu_layers=-1,
            verbose=False,
            chat_format="chatml",
            encoding="utf-8"  # Explicit UTF-8 encoding
        )
        instances.append(llm)
    
    return instances

