"""
Inference module for running local LLM using llama-cpp-python.
Loads a GGUF model and provides text generation capabilities.
"""

import logging
from pathlib import Path
from llama_cpp import Llama
import config

# Setup logging
logger = logging.getLogger(__name__)

# Global model instance (loaded once)
_llm = None


def _get_llm():
    """
    Lazy-load the LLM model. Loads only once and reuses the instance.
    
    Returns:
        Llama: The loaded LLM model instance
        
    Raises:
        FileNotFoundError: If the model file doesn't exist
        RuntimeError: If model loading fails
    """
    global _llm
    if _llm is None:
        try:
            # Verify model file exists
            model_path = Path(config.MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Model file not found: {config.MODEL_PATH}\n"
                    f"Please ensure the model is downloaded to the correct location."
                )
            
            logger.info(f"Loading model from: {config.MODEL_PATH}")
            logger.info(f"Model config: n_ctx={config.N_CTX}, n_threads={config.N_THREADS}, n_gpu_layers={config.N_GPU_LAYERS}")
            
            _llm = Llama(
                model_path=config.MODEL_PATH,
                n_ctx=config.N_CTX,
                n_threads=config.N_THREADS,
                n_gpu_layers=config.N_GPU_LAYERS,
                verbose=False
            )
            logger.info("Model loaded successfully!")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e
            
    return _llm


def run_local_llm(prompt: str, max_tokens: int = 512) -> str:
    """
    Run the local LLM with the given prompt.
    
    Args:
        prompt: The input prompt text
        max_tokens: Maximum number of tokens to generate (default: 512)
    
    Returns:
        Generated text response from the model
        
    Raises:
        ValueError: If prompt is empty
        RuntimeError: If text generation fails
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    try:
        llm = _get_llm()
        
        # Format prompt for Mistral-7B-Instruct format
        formatted_prompt = f"[INST] {prompt} [/INST]"
        
        logger.debug(f"Generating response for prompt (length: {len(prompt)} chars)")
        
        # Generate response with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = llm(
                    formatted_prompt,
                    max_tokens=max_tokens,
                    temperature=config.TEMPERATURE,
                    top_p=config.TOP_P,
                    stop=["[INST]", "</s>"],
                    echo=False
                )
                
                generated_text = response['choices'][0]['text'].strip()
                logger.debug(f"Generated response (length: {len(generated_text)} chars)")
                return generated_text
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Generation attempt {attempt + 1} failed: {e}. Retrying...")
                    continue
                else:
                    raise
                    
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise RuntimeError(f"Failed to generate text: {e}") from e


if __name__ == "__main__":
    test_prompt = "Summarize the following meeting."
    result = run_local_llm(test_prompt, max_tokens=100)
    print("Test result:")
    print(result)
