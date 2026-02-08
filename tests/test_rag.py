#!/usr/bin/env python3
"""
Quick test script for RAG functionality
Tests retrieval without full classification
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.rag.retriever import get_retriever
from src.rag.vector_store import get_vector_store


def test_vector_store():
    """Test vector store connection and stats."""
    print("=" * 60)
    print("Testing Vector Store")
    print("=" * 60)

    try:
        vs = get_vector_store()
        stats = vs.get_collection_stats()

        print("\nVector Store Connected")
        print(f"   Collection: {stats['collection_name']}")
        print(f"   Documents: {stats['document_count']}")
        print(f"   Location: {stats['persist_directory']}")

        if stats["document_count"] == 0:
            print("\nNo documents indexed yet!")
            print("   Run: python3 indexer.py")
            return False

        return True
    except Exception as e:
        print(f"\nVector Store Error: {e}")
        return False


def test_retrieval(query="password reset"):
    """Test retrieval functionality."""
    print("\n" + "=" * 60)
    print("Testing Retrieval")
    print("=" * 60)

    try:
        retriever = get_retriever()

        print(f"\nQuery: '{query}'")
        print("\nRetrieving relevant documents...")

        docs = retriever.retrieve(query=query, language=None, app_name=None)

        if not docs:
            print("\nNo documents retrieved")
            print("   Try a different query or check similarity threshold")
            return False

        print(f"\nRetrieved {len(docs)} documents\n")

        for idx, doc in enumerate(docs, 1):
            print(f"--- Document {idx} ---")
            print(f"Similarity: {doc['similarity']:.3f}")
            print(f"Distance: {doc['distance']:.3f}")

            metadata = doc["metadata"]
            if metadata.get("source_type") == "article":
                print("Type: Article")
                print(f"ID: {metadata.get('article_id')}")
                print(f"App: {metadata.get('app_name')}")
                print(f"Title: {metadata.get('title')}")
                print(f"Language: {metadata.get('language')}")
            else:
                print("Type: PDF")
                print(f"File: {metadata.get('source_file')}")
                print(f"Chunk: {metadata.get('chunk_index')}")

            print(f"Content Preview: {doc['document'][:200]}...")
            print()

        return True
    except Exception as e:
        print(f"\nRetrieval Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_formatted_context(query="password reset"):
    """Test formatted context generation."""
    print("\n" + "=" * 60)
    print("Testing Context Formatting")
    print("=" * 60)

    try:
        retriever = get_retriever()
        context = retriever.retrieve_and_format(query=query)

        if not context:
            print("\nNo context generated")
            return False

        print(f"\nGenerated {len(context)} characters of context\n")
        print("--- Formatted Context ---")
        print(context[:1000])
        if len(context) > 1000:
            print(f"\n... ({len(context) - 1000} more characters)")

        return True
    except Exception as e:
        print(f"\nContext Formatting Error: {e}")
        return False


def test_article_recommendations(query="internet slow"):
    """Test article recommendation functionality."""
    print("\n" + "=" * 60)
    print("Testing Article Recommendations")
    print("=" * 60)

    try:
        retriever = get_retriever()

        print(f"\nQuery: '{query}'")
        print("\nGetting article recommendations...")

        article_ids = retriever.get_article_recommendations(
            query=query, language=None, n_results=5
        )

        if not article_ids:
            print("\nNo articles recommended")
            return False

        print(f"\nRecommended {len(article_ids)} articles")
        print(f"Article IDs: {article_ids}")

        return True
    except Exception as e:
        print(f"\nRecommendation Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Cora RAG System Test Suite")
    print("=" * 60)

    # Test 1: Vector Store
    if not test_vector_store():
        print("\nVector store test failed. Please run indexer first.")
        print("   Command: python3 indexer.py")
        sys.exit(1)

    # Test 2: Basic Retrieval
    test_queries = [
        "password reset",
        "كيف أعيد تعيين كلمة المرور",  # Arabic
        "internet slow",
    ]

    for query in test_queries:
        if not test_retrieval(query):
            print(f"\nRetrieval test failed for: {query}")

    # Test 3: Context Formatting
    test_formatted_context("how to reset password")

    # Test 4: Article Recommendations
    test_article_recommendations("internet connection problem")

    # Summary
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
    print("\nYour RAG system is working!")
    print("\nNext steps:")
    print("1. Test with real queries: python3 cora.py")
    print("2. Start the API: python3 server.py")
    print("3. Deploy with Docker: docker-compose up -d")


if __name__ == "__main__":
    main()
