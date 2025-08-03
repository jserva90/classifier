from typing import Dict, List, Any, Optional
from loguru import logger

from .models import ModelType, DEFAULT_CLAUSE_TYPES
from .api_classification import classify_with_openai

def classify_clauses(
    text: str,
    clause_types: Optional[List[str]] = None,
    model: str = ModelType.GPT_4,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Classify legal clauses using OpenAI API.
    
    Args:
        text: The legal text to classify
        clause_types: Optional list of clause types to classify into (uses defaults if None)
        model: The OpenAI model to use
        temperature: Temperature parameter for the model
        
    Returns:
        Dictionary with results and metadata
    """
    if not text.strip():
        logger.warning("Empty text provided for classification")
        return {"error": "Empty text provided", "results": []}
    
    if clause_types is None or len(clause_types) == 0:
        logger.debug(f"Using default clause types: {DEFAULT_CLAUSE_TYPES}")
        clause_types = DEFAULT_CLAUSE_TYPES
    else:
        logger.debug(f"Using custom clause types: {clause_types}")
    
    return classify_with_openai(text, clause_types, model, temperature)