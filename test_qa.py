#!/usr/bin/env python3
"""
Test Q&A System - Wrapper Script
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run
if __name__ == "__main__":
    from tests.test_qa import test_qa

    test_qa()
