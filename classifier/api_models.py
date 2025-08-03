from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ClassifyRequest(BaseModel):
    text: Optional[str] = Field(None, description="Text to classify")
    pdf_base64: Optional[str] = Field(None, description="Base64-encoded PDF content")
    model: Optional[str] = Field("gpt-4.1", description="Model to use for classification")
    clause_types: Optional[List[str]] = Field(None, description="Custom clause types to classify")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "This agreement shall terminate upon 30 days written notice by either party.",
                "model": "gpt-4.1"
            }
        }
    }

class ClauseResult(BaseModel):
    """
    Model for a single clause classification result.
    """
    clause: str = Field(..., description="The text of the clause")
    label: str = Field(..., description="The classification label")
    confidence: float = Field(..., description="Confidence score (0-1)")
    confidence_level: str = Field(..., description="Confidence level (Very Low, Low, Moderate, High, Very High)")
    summary: str = Field(..., description="Plain English summary of the clause")

class ClassifyResponse(BaseModel):
    """
    Response model for the /classify endpoint.
    """
    results: List[ClauseResult] = Field(default_factory=list, description="Classification results")
    document_summary: Optional[str] = Field(None, description="Summary of the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata about the classification")
    error: Optional[str] = Field(None, description="Error message if classification failed")

class HealthResponse(BaseModel):
    """
    Response model for the /health endpoint.
    """
    status: str = Field(..., description="Status of the API")
    version: str = Field(..., description="API version")
    supported_models: List[str] = Field(..., description="List of supported models")
    default_clause_types: List[str] = Field(..., description="Default clause types")
    pdf_support: bool = Field(..., description="Whether PDF support is available")