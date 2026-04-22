from llama_cpp import Llama
from pathlib import Path
import logging
from app.utils.retry import retry, with_fallback

logger = logging.getLogger("hyena.llm.engine")

# Model path - now using Qwen 3.5-9B
MODEL_PATH = Path("app/models/Qwen3.5-9B.Q8_0.gguf")

@retry(max_attempts=3, delay=1.0, backoff=True)
def load_instances(num_instances=1):
    """Load LLM instances with the new Qwen model.
    
    Args:
        num_instances: Number of LLM instances to load
        
    Returns:
        list: List of loaded Llama instances
    """
    if not MODEL_PATH.exists():
        logger.error(f"Model file not found at {MODEL_PATH}")
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    logger.info(f"Loading {num_instances} instance(s) of {MODEL_PATH.name}")
    
    instances = []
    for i in range(num_instances):
        try:
            llm = Llama(
                model_path=str(MODEL_PATH),
                n_ctx=8192,  # Context window
                n_threads=8,  # CPU threads
                n_gpu_layers=-1,  # Use GPU if available
                verbose=False,
                chat_format="chatml",  # Chat message format
                encoding="utf-8"  # UTF-8 encoding
            )
            instances.append(llm)
            logger.info(f"Successfully loaded instance {i+1}/{num_instances}")
        except Exception as e:
            logger.error(f"Failed to load LLM instance {i+1}: {e}")
            raise
    
    logger.info(f"All {num_instances} LLM instance(s) loaded successfully")
    return instances

@with_fallback(fallback_value={"choices": [{"message": {"content": "I'm having difficulty processing your request. Please try again."}}]})
def create_completion_safe(llm, **kwargs):
    """Safe wrapper for LLM completion with fallback."""
    return llm.create_completion(**kwargs)

