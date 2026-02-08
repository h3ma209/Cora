#!/usr/bin/env python3
"""
Quick Q&A Demo
Demonstrates the Q&A functionality with a simple example.
"""

import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.qa import answer_question


def demo():
    """Run a simple Q&A demo."""

    print("=" * 70)
    print("🤖 Cora Q&A System Demo")
    print("=" * 70)
    print()

    # Test question
    question = "How do I reset my password?"

    print(f"Question: {question}")
    print()
    print("Thinking...")
    print()

    # Get answer
    result = answer_question(question)

    # Display result
    if "error" in result and "answer" not in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("📝 Answer:")
        print(result["answer"])
        print()
        print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
        print(f"📚 Sources: {result.get('retrieved_docs', 0)} documents")

        if result.get("sources"):
            print()
            print("📖 Source Articles:")
            for source in result["sources"]:
                if source["type"] == "article":
                    print(f"  • Article #{source['article_id']}: {source['title']}")
                    print(f"    Similarity: {source['similarity']:.3f}")

    print()
    print("=" * 70)
    print("✅ Demo Complete!")
    print()
    print("Try the API:")
    print("  python3 server.py")
    print("  curl -X POST http://localhost:8001/ask \\")
    print("    -H 'Content-Type: application/json' \\")
    print('    -d \'{"question": "YOUR_QUESTION"}\'')
    print("=" * 70)


if __name__ == "__main__":
    demo()
