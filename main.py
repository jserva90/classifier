#!/usr/bin/env python3

import argparse
import json
import sys
from loguru import logger

from classifier import (
    classify_clauses,
    extract_text_from_pdf,
    ModelType,
)

def format_results(results, json_output=False):
    if json_output:
        return json.dumps(results, indent=2)
    
    output = []
    
    if "error" in results and results["error"]:
        output.append(f"Error: {results['error']}")
        return "\n".join(output)
    
    if "document_summary" in results:
        output.append(f"Document Summary: {results['document_summary']}")
        output.append("")
    
    if "metadata" in results:
        meta = results["metadata"]
        output.append(f"Model: {meta.get('model', 'unknown')}")
        output.append(f"Clause Types: {', '.join(meta.get('clause_types', []))}")
        output.append(f"Clauses Found: {meta.get('clause_count', 0)}")
        output.append("")
    
    if "results" in results and results["results"]:
        output.append("Classification Results:")
        for i, result in enumerate(results["results"], 1):
            output.append(f"\n[{i}] {result.get('label', 'Unknown')} (Confidence: {result.get('confidence', 'N/A')} - {result.get('confidence_level', 'N/A')})")
            output.append(f"Clause: \"{result.get('clause', 'N/A')}\"")
            output.append(f"Summary: {result.get('summary', 'N/A')}")
    else:
        output.append("No clauses were classified.")
    
    return "\n".join(output)

def read_file(file_path):
    try:
        if file_path.lower().endswith('.pdf'):
            try:
                logger.info(f"Processing PDF file: {file_path}")
                return extract_text_from_pdf(file_path, is_file_path=True)
            except ImportError as e:
                logger.exception(f"Error: {str(e)}")
                sys.exit(1)
            except Exception as e:
                logger.exception(f"Error processing PDF: {str(e)}")
                sys.exit(1)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.exception(f"Error reading file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Classify legal clauses in text")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", help="Text to classify")
    input_group.add_argument("--file", help="File containing text to classify (supports .txt and .pdf)")
    
    parser.add_argument("--model", choices=[m.value for m in ModelType],
                        default=ModelType.GPT_4, help="Model to use for classification")
    parser.add_argument("--clause-types", nargs="+", help="Custom clause types to classify")
    
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--output", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    if args.text:
        text = args.text
    else:
        text = read_file(args.file)
    
    try:
        results = classify_clauses(
            text=text,
            clause_types=args.clause_types,
            model=args.model
        )
    except Exception as e:
        logger.exception(f"Error during classification: {e}")
        sys.exit(1)
    
    output = format_results(results, args.json)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        except Exception as e:
            logger.exception(f"Error writing to output file: {e}")
            sys.exit(1)
    else:
        logger.info(output)

if __name__ == "__main__":
    main()
