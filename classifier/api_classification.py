import json
import re
from typing import Dict, List, Any, Optional
from loguru import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from settings import settings
from .models import ModelType, DEFAULT_CLAUSE_TYPES, FEW_SHOT_EXAMPLES
from .text_processing import split_into_clauses

def create_classification_prompt(clauses: List[str], clause_types: List[str]) -> str:
    """
    Create a prompt for classifying legal clauses.
    
    Args:
        clauses: List of clauses to classify
        clause_types: List of clause types to classify into
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
You are a legal assistant AI specialized in contract analysis. Classify each clause into one of the following categories:
{", ".join(clause_types)}

If a clause doesn't clearly fit any category, classify it as the closest match and adjust the confidence score accordingly.

For each clause, respond with a JSON object containing:
- clause: the original text of the clause
- label: the most appropriate category from the list above
- confidence: a float between 0 and 1 representing your confidence in this classification
  - 0.9-1.0: Very high confidence, clear and unambiguous classification
  - 0.7-0.9: High confidence, strong indicators of the category
  - 0.5-0.7: Moderate confidence, some indicators but potential ambiguity
  - 0.3-0.5: Low confidence, weak indicators or multiple possible categories
  - 0.0-0.3: Very low confidence, unclear or unusual clause
- summary: a concise explanation of the clause in plain English

Respond with a JSON array containing one object for each clause.

{FEW_SHOT_EXAMPLES}

Clauses to classify:
"""
    
    for i, clause in enumerate(clauses, 1):
        prompt += f"\n{i}. {clause}"
    
    return prompt

def classify_with_openai(
    text: str,
    clause_types: Optional[List[str]] = None,
    model: str = ModelType.GPT_4,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Classify legal clauses using the OpenAI API.
    
    Args:
        text: The legal text to classify
        clause_types: Optional list of clause types to classify into (uses defaults if None)
        model: The OpenAI model to use
        temperature: Temperature parameter for the model
        
    Returns:
        Dictionary with results and metadata
    """
    if not OPENAI_AVAILABLE:
        return {
            "error": "OpenAI API not available. Install with: pip install openai",
            "results": []
        }
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    clauses = split_into_clauses(text)
    
    if not clauses:
        return {"error": "No clauses detected", "results": []}
    
    prompt = create_classification_prompt(clauses, clause_types or DEFAULT_CLAUSE_TYPES)
    
    messages = [
        {"role": "system", "content": "You are an expert in legal contract analysis and clause classification."},
        {"role": "user", "content": prompt}
    ]

    logger.info(f"=== USING OPENAI API WITH MODEL: {model} ===")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        logger.info(f"=== RECEIVED OPENAI API RESPONSE ===")
        logger.info(f"Response ID: {response.id}")
        logger.info(f"Model used: {response.model}")
        logger.info(f"Completion tokens: {response.usage.completion_tokens}")
        logger.info(f"Prompt tokens: {response.usage.prompt_tokens}")
        logger.info(f"Total tokens: {response.usage.total_tokens}")
        logger.debug(f"Raw response from model: {result_text[:200]}...")
        
        results = []
        
        try:
            parsed_results = json.loads(result_text)
            
            if isinstance(parsed_results, dict) and "results" in parsed_results:
                results = parsed_results["results"]
            elif isinstance(parsed_results, list):
                results = parsed_results
            else:
                if isinstance(parsed_results, dict):
                    if "clause" in parsed_results and "label" in parsed_results:
                        results = [parsed_results]
                    else:
                        for key, value in parsed_results.items():
                            if isinstance(value, list) and len(value) > 0:
                                if all(isinstance(item, dict) for item in value):
                                    results = value
                                    break
                
                if len(results) == 0:
                    logger.warning(f"Could not parse results from model response")
                    
                    error_message = None
                    if isinstance(parsed_results, dict) and "error" in parsed_results:
                        error_message = parsed_results["error"]
                        logger.warning(f"Model returned error: {error_message}")
                    
                    logger.info("Creating simple result")
                    if len(text) > 200:
                        chunks = [text[i:i+200] for i in range(0, len(text), 200)]
                        for i, chunk in enumerate(chunks[:3]):
                            results.append({
                                "clause": chunk,
                                "label": "Unclassified Text",
                                "confidence": 0.5,
                                "confidence_level": "Moderate",
                                "summary": f"Part {i+1} of unclassified legal text"
                            })
                    else:
                        results.append({
                            "clause": text,
                            "label": "Unclassified Text",
                            "confidence": 0.5,
                            "confidence_level": "Moderate",
                            "summary": "Unclassified legal text"
                        })
        except json.JSONDecodeError as e:
            logger.exception(f"Error parsing JSON response: {e}")
            logger.debug(f"Response was: {result_text}")
            
            try:
                # This pattern allows for escaped quotes within the strings
                pattern = r'\{\s*"clause":\s*"((?:\\"|[^"])+)",\s*"label":\s*"((?:\\"|[^"])+)",\s*"confidence":\s*([\d\.]+),\s*"summary":\s*"((?:\\"|[^"])+)"\s*\}'
                matches = re.findall(pattern, result_text)
                
                if matches:
                    logger.info(f"Found {len(matches)} partial results")
                    results = []
                    for match in matches:
                        clause, label, confidence, summary = match
                        results.append({
                            "clause": clause,
                            "label": label,
                            "confidence": float(confidence),
                            "confidence_level": "High",
                            "summary": summary
                        })
                else:
                    results = [{
                        "clause": text[:1000] + "..." if len(text) > 1000 else text,
                        "label": "Legal Document",
                        "confidence": 0.7,
                        "confidence_level": "High",
                        "summary": "This is a legal document containing various clauses related to contracts, agreements, or legal matters."
                    }]
            except Exception as inner_e:
                logger.exception(f"Error extracting partial results: {inner_e}")
                results = [{
                    "clause": text[:1000] + "..." if len(text) > 1000 else text,
                    "label": "Legal Document",
                    "confidence": 0.7,
                    "confidence_level": "High",
                    "summary": "This is a legal document containing various clauses related to contracts, agreements, or legal matters."
                }]
            
        # Add confidence level based on confidence score
        for result in results:
            if "confidence" in result:
                # Clip confidence to [0, 1] range
                result["confidence"] = max(0.0, min(1.0, result["confidence"]))
                
                # Round to 2 decimal places for readability
                result["confidence"] = round(result["confidence"], 2)
                
                # Add confidence level explanation
                if result["confidence"] >= 0.9:
                    result["confidence_level"] = "Very High"
                elif result["confidence"] >= 0.7:
                    result["confidence_level"] = "High"
                elif result["confidence"] >= 0.5:
                    result["confidence_level"] = "Moderate"
                elif result["confidence"] >= 0.3:
                    result["confidence_level"] = "Low"
                else:
                    result["confidence_level"] = "Very Low"
        
        # Generate document summary
        document_summary = generate_document_summary(results)
        
        # Add metadata
        return {
            "results": results,
            "document_summary": document_summary,
            "metadata": {
                "model": model,
                "clause_count": len(clauses),
                "clause_types": clause_types or DEFAULT_CLAUSE_TYPES
            }
        }
        
    except Exception as e:
        logger.exception(f"=== OPENAI API ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"This indicates the OpenAI API call failed")
        
        # Re-raise the exception to be handled by the caller
        raise

def generate_document_summary(results):
    """
    Generate an overall summary of the document based on classified clauses.
    
    Args:
        results: List of classification results
        
    Returns:
        Document summary string
    """
    if not results:
        return "No clauses found to summarize."
    
    clause_counts = {}
    for result in results:
        label = result.get("label", "Unknown")
        clause_counts[label] = clause_counts.get(label, 0) + 1
    
    summary = "This document contains "
    summary += ", ".join([f"{count} {label} clause{'s' if count > 1 else ''}"
                         for label, count in clause_counts.items()])
    summary += "."
    
    return summary