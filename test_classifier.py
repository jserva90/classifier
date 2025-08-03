#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
from types import ModuleType

class MockSettings:
    OPENAI_API_KEY = 'dummy_api_key'
    DEFAULT_MODEL = 'gpt-4.1'
    DEFAULT_CLAUSE_TYPES = ["Termination", "Confidentiality", "Governing Law"]
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1000

mock_settings_module = ModuleType('settings')
setattr(mock_settings_module, 'settings', MockSettings())

mock_openai_module = ModuleType('openai')
setattr(mock_openai_module, 'OpenAI', MagicMock)

sys.modules['settings'] = mock_settings_module
sys.modules['openai'] = mock_openai_module

from classifier import (
    classify_clauses
)
from classifier.api_classification import create_classification_prompt, generate_document_summary
from classifier.text_processing import split_into_clauses

class TestClauseClassifier(unittest.TestCase):
    """Unit tests for the clause classifier functions"""
    
    def test_split_into_clauses(self):
        """Test the clause splitting function"""
        text = "This is the first clause. This is the second clause."
        clauses = split_into_clauses(text)
        self.assertEqual(len(clauses), 2)
        self.assertEqual(clauses[0], "This is the first clause.")
        self.assertEqual(clauses[1], "This is the second clause.")
        
        text = "This is the first clause; this is the second clause."
        clauses = split_into_clauses(text)
        self.assertEqual(len(clauses), 2)
        self.assertEqual(clauses[0], "This is the first clause")
        self.assertEqual(clauses[1], "this is the second clause.")
        
        text = ""
        clauses = split_into_clauses(text)
        self.assertEqual(len(clauses), 0)
    
    def test_create_classification_prompt(self):
        """Test the prompt creation function"""
        clauses = ["Clause 1", "Clause 2"]
        clause_types = ["Type A", "Type B"]
        
        prompt = create_classification_prompt(clauses, clause_types)
        
        self.assertIn("Type A, Type B", prompt)
        
        self.assertIn("1. Clause 1", prompt)
        self.assertIn("2. Clause 2", prompt)
        
        self.assertIn("JSON", prompt)
        self.assertIn("confidence", prompt)
    
    def test_confidence_level_assignment(self):
        """Test the confidence level assignment logic"""
        
        results = [
            {"label": "Type A", "confidence": 0.95},
            {"label": "Type B", "confidence": 0.75},
            {"label": "Type C", "confidence": 0.55},
            {"label": "Type D", "confidence": 0.35},
            {"label": "Type E", "confidence": 0.15},
            {"label": "Type F", "confidence": 1.2},  # Above 1.0
            {"label": "Type G", "confidence": -0.1},  # Below 0.0
        ]
        
        for result in results:
            result["confidence"] = max(0.0, min(1.0, result["confidence"]))
            
            result["confidence"] = round(result["confidence"], 2)
            
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
        
        self.assertEqual(results[5]["confidence"], 1.0)
        self.assertEqual(results[6]["confidence"], 0.0)
        
        self.assertEqual(results[0]["confidence_level"], "Very High")
        self.assertEqual(results[1]["confidence_level"], "High")
        self.assertEqual(results[2]["confidence_level"], "Moderate")
        self.assertEqual(results[3]["confidence_level"], "Low")
        self.assertEqual(results[4]["confidence_level"], "Very Low")
    
    def test_generate_document_summary(self):
        """Test the document summary generation function"""
        results = [
            {"label": "Termination", "confidence": 0.9},
            {"label": "Termination", "confidence": 0.8},
            {"label": "Confidentiality", "confidence": 0.7},
        ]
        
        summary = generate_document_summary(results)
        
        self.assertIn("2 Termination clauses", summary)
        self.assertIn("1 Confidentiality clause", summary)
        
        summary = generate_document_summary([])
        self.assertEqual(summary, "No clauses found to summarize.")

    @patch('classifier.core.classify_with_openai')
    def test_classify_clauses_integration(self, mock_classify_with_openai):
        """Integration test for the classify_clauses function (using mocks)"""
        # Set up the mock to return a predefined result
        expected_result = {
            "results": [
                {
                    "clause": "This agreement shall terminate upon 30 days written notice.",
                    "label": "Termination",
                    "confidence": 0.95,
                    "confidence_level": "Very High",
                    "summary": "Either party can end the agreement with 30 days notice."
                }
            ],
            "document_summary": "This document contains 1 Termination clause.",
            "metadata": {
                "model": "gpt-4.1",
                "clause_count": 1,
                "clause_types": ["Termination", "Confidentiality", "Governing Law"]
            }
        }
        mock_classify_with_openai.return_value = expected_result
        
        result = classify_clauses("This agreement shall terminate upon 30 days written notice.")
        
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["label"], "Termination")
        self.assertEqual(result["results"][0]["confidence"], 0.95)

if __name__ == "__main__":
    unittest.main()