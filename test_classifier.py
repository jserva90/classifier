#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import json

with patch('settings.settings') as mock_settings:
    mock_settings.OPENAI_API_KEY = 'dummy_api_key'
    mock_settings.DEFAULT_MODEL = 'gpt-4.1'
    mock_settings.DEFAULT_CLAUSE_TYPES = ["Termination", "Confidentiality", "Governing Law"]
    
    from classifier import (
        classify_clauses
    )
    from classifier.api_classification import create_classification_prompt
    from classifier.text_processing import split_into_clauses
    from classifier.pattern_matching import calibrate_confidence_scores, summarize_document

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
    
    def test_calibrate_confidence_scores(self):
        """Test the confidence score calibration function"""
        results = [
            {"label": "Type A", "confidence": 0.95},
            {"label": "Type B", "confidence": 0.75},
            {"label": "Type C", "confidence": 0.55},
            {"label": "Type D", "confidence": 0.35},
            {"label": "Type E", "confidence": 0.15},
            {"label": "Type F", "confidence": 1.2},  # Above 1.0
            {"label": "Type G", "confidence": -0.1},  # Below 0.0
        ]
        
        calibrated = calibrate_confidence_scores(results)
        
        self.assertEqual(calibrated[5]["confidence"], 1.0)
        self.assertEqual(calibrated[6]["confidence"], 0.0)
        
        self.assertEqual(calibrated[0]["confidence_level"], "Very High")
        self.assertEqual(calibrated[1]["confidence_level"], "High")
        self.assertEqual(calibrated[2]["confidence_level"], "Moderate")
        self.assertEqual(calibrated[3]["confidence_level"], "Low")
        self.assertEqual(calibrated[4]["confidence_level"], "Very Low")
    
    def test_summarize_document(self):
        """Test the document summarization function"""
        results = [
            {"label": "Termination", "confidence": 0.9},
            {"label": "Termination", "confidence": 0.8},
            {"label": "Confidentiality", "confidence": 0.7},
        ]
        
        summary = summarize_document(results)
        
        self.assertIn("2 Termination clauses", summary)
        self.assertIn("1 Confidentiality clause", summary)
        
        summary = summarize_document([])
        self.assertEqual(summary, "No clauses found to summarize.")

    @patch('classifier.api_classification.OpenAI')
    def test_classify_clauses_integration(self, mock_openai):
        """Integration test for the classify_clauses function (using mocks)"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps({
            "results": [
                {
                    "clause": "This agreement shall terminate upon 30 days written notice.",
                    "label": "Termination",
                    "confidence": 0.95,
                    "summary": "Either party can end the agreement with 30 days notice."
                }
            ]
        })
        mock_client.chat.completions.create.return_value = mock_completion
        
        result = classify_clauses("This agreement shall terminate upon 30 days written notice.")
        
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["label"], "Termination")
        self.assertEqual(result["results"][0]["confidence"], 0.95)

if __name__ == "__main__":
    unittest.main()