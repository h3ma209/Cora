#!/usr/bin/env python3
"""
Cora RAG Indexer - Wrapper Script
Indexes knowledge base from data/ directory
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run indexer
from rag.indexer import main

if __name__ == "__main__":
    main()
