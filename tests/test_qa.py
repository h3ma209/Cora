#!/usr/bin/env python3
"""
Test Q&A Functionality
Tests the question answering system with sample questions.
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.api.qa import answer_question
import json


def test_qa():
    """Test Q&A with various questions."""

    print("=" * 70)
    print("🧪 Cora Q&A System Test")
    print("=" * 70)

    # Test questions in different languages
    test_questions = [
        {"question": "How do I reset my password?", "language": None, "app_name": None},
        {"question": "كيف أعيد تعيين كلمة المرور؟", "language": "ar", "app_name": None},
        {
            "question": "What should I do if my internet is slow?",
            "language": "en",
            "app_name": None,
        },
        {
            "question": "How can I download the Hakki app?",
            "language": "en",
            "app_name": "hakki",
        },
        {
            "question": "كيف أرسل نقاط في تطبيق الرعاية الذاتية؟",
            "language": "ar",
            "app_name": "self-care",
        },
        {"question": "What is HD Call?", "language": "en", "app_name": None},
    ]

    for idx, test in enumerate(test_questions, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {idx}/{len(test_questions)}")
        print(f"{'=' * 70}")
        print(f"Question: {test['question']}")
        if test["language"]:
            print(f"Language Filter: {test['language']}")
        if test["app_name"]:
            print(f"App Filter: {test['app_name']}")
        print()

        # Get answer
        result = answer_question(
            question=test["question"],
            language=test["language"],
            app_name=test["app_name"],
        )

        # Display result
        if "error" in result and "answer" not in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📝 Answer:")
            print(f"{result['answer']}")
            print()
            print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"📚 Sources Retrieved: {result.get('retrieved_docs', 0)}")

            if result.get("sources"):
                print(f"\n📖 Sources:")
                for source in result["sources"]:
                    if source["type"] == "article":
                        print(f"  • Article #{source['article_id']}: {source['title']}")
                        print(
                            f"    App: {source['app']} | Similarity: {source['similarity']}"
                        )
                    else:
                        print(f"  • PDF: {source['file']}")
                        print(f"    Similarity: {source['similarity']}")

        print()

    print("=" * 70)
    print("✅ Q&A Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    test_qa()
