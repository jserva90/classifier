"""
Model definitions, enums, and constants for the classifier package.
"""

from enum import Enum
from typing import List

from settings import settings

class ModelType(str, Enum):
    GPT_4 = settings.DEFAULT_MODEL
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini-2025-04-14"

DEFAULT_CLAUSE_TYPES = settings.DEFAULT_CLAUSE_TYPES

FEW_SHOT_EXAMPLES = """
Example 1:
Text: "This agreement shall terminate upon 30 days written notice by either party."
Classification: {
  "clause": "This agreement shall terminate upon 30 days written notice by either party.",
  "label": "Termination",
  "confidence": 0.95,
  "summary": "Either party can end the agreement with 30 days written notice."
}

Example 2:
Text: "All information shared during the course of this agreement shall be kept confidential for a period of 5 years."
Classification: {
  "clause": "All information shared during the course of this agreement shall be kept confidential for a period of 5 years.",
  "label": "Confidentiality",
  "confidence": 0.98,
  "summary": "Information shared must be kept secret for 5 years."
}

Example 3:
Text: "This agreement shall be governed by the laws of the State of California."
Classification: {
  "clause": "This agreement shall be governed by the laws of the State of California.",
  "label": "Governing Law",
  "confidence": 0.97,
  "summary": "California law applies to this agreement."
}
"""