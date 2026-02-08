#!/usr/bin/env python3
"""
Cora RAG Test Suite - Wrapper Script
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run tests
from tests.test_rag import main

if __name__ == "__main__":
    main()
