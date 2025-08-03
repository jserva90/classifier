#!/usr/bin/env python3

from flask import Flask, request, Response
import base64
from typing import Any

from classifier import (
    classify_clauses,
    extract_text_from_pdf,
    ModelType,
    DEFAULT_CLAUSE_TYPES,
    PDF_SUPPORT
)
from classifier.api_models import ClassifyRequest, ClassifyResponse, HealthResponse
from settings import settings

app = Flask(__name__)

def pydantic_to_response(model: Any) -> Response:
    return Response(
        model.model_dump_json(),
        mimetype='application/json'
    )

@app.route('/classify', methods=['POST'])
def classify_endpoint():
    if not request.is_json:
        response = ClassifyResponse(error="Request must be JSON")
        return pydantic_to_response(response), 400
    
    try:
        data = request.get_json()
        classify_request = ClassifyRequest(**data)
        
        if not classify_request.text and not classify_request.pdf_base64:
            response = ClassifyResponse(error="Missing 'text' or 'pdf_base64' field in request")
            return pydantic_to_response(response), 400
        
        if classify_request.pdf_base64:
            if not PDF_SUPPORT:
                response = ClassifyResponse(error="PDF support requires unstructured library")
                return pydantic_to_response(response), 400
            
            try:
                pdf_data = base64.b64decode(classify_request.pdf_base64)
                text = extract_text_from_pdf(pdf_data)
            except Exception as e:
                response = ClassifyResponse(error=f"PDF processing error: {str(e)}")
                return pydantic_to_response(response), 400
        else:
            text = classify_request.text
        
        if classify_request.model not in [m.value for m in ModelType]:
            response = ClassifyResponse(
                error=f"Invalid model. Choose from: {[m.value for m in ModelType]}"
            )
            return pydantic_to_response(response), 400
        
        try:
            if text is None:
                text = ""
                
            results_dict = classify_clauses(
                text=text,
                clause_types=classify_request.clause_types,
                model=classify_request.model
            )
            
            response = ClassifyResponse(**results_dict)
            return pydantic_to_response(response)
        except Exception as e:
            response = ClassifyResponse(error=str(e))
            return pydantic_to_response(response), 500
    except Exception as e:
        response = ClassifyResponse(error=f"Invalid request: {str(e)}")
        return pydantic_to_response(response), 400

@app.route('/health', methods=['GET'])
def health_check():
    response = HealthResponse(
        status="ok",
        version="0.3.0",
        supported_models=[m.value for m in ModelType],
        default_clause_types=DEFAULT_CLAUSE_TYPES,
        pdf_support=PDF_SUPPORT
    )
    return pydantic_to_response(response)

if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)