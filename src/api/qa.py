"""
Q&A Module for Cora RAG System
Answers questions directly using retrieved context from the knowledge base.
"""

import ollama
from src.rag.retriever import get_retriever
from typing import Dict, Optional


# Initialize retriever (lazy loading)
_retriever = None


def get_qa_retriever():
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        try:
            _retriever = get_retriever()
            print("✓ Q&A retriever initialized")
        except Exception as e:
            print(f"⚠️  Q&A retriever failed to initialize: {e}")
            _retriever = None
    return _retriever


def get_qa_prompt() -> str:
    """
    Get the Q&A system prompt.

    Returns:
        Q&A system prompt string
    """
    return """You are a helpful customer support assistant for Rayied telecommunications company.

Your role is to answer customer questions accurately based on the provided context from our knowledge base.

### INSTRUCTIONS:
1. Answer questions directly and concisely
2. Use ONLY information from the RETRIEVED CONTEXT below
3. If the context doesn't contain the answer, say "I don't have enough information to answer that question. Please contact our support team."
4. Provide step-by-step instructions when applicable
5. Be friendly and professional
6. Support multiple languages: English, Arabic, and Kurdish
7. Match the language of the user's question in your response

### RESPONSE FORMAT:
- Start with a direct answer
- Provide relevant details or steps
- Include helpful tips if applicable
- Keep responses clear and concise
"""


def answer_question(
    question: str,
    language: Optional[str] = None,
    app_name: Optional[str] = None,
    model_name: str = "qwen2.5:1.5b",
) -> Dict:
    """
    Answer a question using RAG-retrieved context.

    Args:
        question: User's question
        language: Optional language filter (en, ar, ku)
        app_name: Optional app name filter
        model_name: Ollama model to use

    Returns:
        Dictionary with answer and metadata
    """

    # Get retriever
    retriever = get_qa_retriever()
    if not retriever:
        return {
            "error": "Q&A system not available",
            "answer": "I'm currently unable to answer questions. Please try again later.",
        }

    try:
        # Retrieve relevant context
        retrieved_docs = retriever.retrieve(
            query=question, language=language, app_name=app_name
        )

        if not retrieved_docs:
            return {
                "answer": "I don't have enough information to answer that question. Please contact our support team for assistance.",
                "sources": [],
                "confidence": "low",
            }

        # Format context for the prompt
        context = "\n### RETRIEVED CONTEXT:\n\n"
        sources = []

        for idx, doc_info in enumerate(retrieved_docs, 1):
            doc = doc_info["document"]
            metadata = doc_info["metadata"]
            similarity = doc_info["similarity"]

            # Add to context
            context += f"[Source {idx}]\n"
            if metadata.get("source_type") == "article":
                context += f"Article ID: {metadata.get('article_id')}\n"
                context += f"App: {metadata.get('app_name')}\n"
                context += f"Title: {metadata.get('title')}\n"

                # Track sources
                sources.append(
                    {
                        "type": "article",
                        "article_id": metadata.get("article_id"),
                        "title": metadata.get("title"),
                        "app": metadata.get("app_name"),
                        "similarity": round(similarity, 3),
                    }
                )
            else:
                context += f"PDF: {metadata.get('source_file')}\n"

                sources.append(
                    {
                        "type": "pdf",
                        "file": metadata.get("source_file"),
                        "similarity": round(similarity, 3),
                    }
                )

            context += f"Content:\n{doc}\n"
            context += "-" * 80 + "\n\n"

        # Build full prompt
        system_prompt = get_qa_prompt() + context

        # Ensure model is available
        ollama.pull(model_name)

        # Generate answer
        response = ollama.generate(
            model=model_name,
            system=system_prompt,
            prompt=f"Question: {question}\n\nPlease provide a helpful answer based on the context above.",
            options={
                "temperature": 0.3,  # Some creativity for natural responses
                "top_p": 0.9,
                "num_predict": 500,  # Limit response length
            },
        )

        answer = response["response"].strip()

        # Determine confidence based on similarity scores
        avg_similarity = sum(s["similarity"] for s in sources) / len(sources)
        if avg_similarity > 0.8:
            confidence = "high"
        elif avg_similarity > 0.6:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "retrieved_docs": len(retrieved_docs),
        }

    except Exception as e:
        return {
            "error": f"Failed to generate answer: {str(e)}",
            "answer": "I encountered an error while processing your question. Please try again.",
        }
