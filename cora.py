#!/usr/bin/env python3
"""
Cora Classification Engine - Wrapper Script
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run
from api.cora import get_json_classification
import json

if __name__ == "__main__":
    # Example usage
    english_payload = "how to reset password"

    result = get_json_classification(english_payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))
