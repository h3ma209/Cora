"""
Q&A Module for Cora RAG System
Answers questions directly using retrieved context from the knowledge base.
"""

import ollama
from src.rag.retriever import get_retriever
from src.api.utils import call_mt_api
from typing import Dict, Optional


# Initialize retriever (lazy loading)
_retriever = None


def get_qa_retriever():
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        try:
            _retriever = get_retriever()
            print("Q&A retriever initialized")
        except Exception as e:
            print(f"Q&A retriever failed to initialize: {e}")
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

INSTRUCTIONS:
1. Answer questions directly and concisely
2. Base your answer on the RETRIEVED CONTEXT below.
3. BE HELPFUL: If the context contains troubleshooting steps, general advice, or related concepts that could apply to the user's situation, USE THEM, even if the context title doesn't exactly match the question.
4. Only say "I don't have enough information..." if the context is ABSOLUTELY IRRELEVANT (e.g. asking about billing but context is technical).
5. Provide step-by-step instructions when applicable
6. Be friendly and professional
7. Support multiple languages: English, Arabic, and Kurdish
8. Match the language of the user's question in your response
9. Do not reveal sensitive information
10. Keep a formal tone and language
10. Make sure the answers are human-like and natural as possible you can so the user doesn't feel like he's talking to a bot
11. If user said hello or hi or any greeting, respond with a greeting and ask him how can i help you
12. Don't recommend competition products or services
13. Recommendations and suggestions should always lead back to the company
14. If a question is unclear or ambiguous, politely ask for clarification before providing an answer
15. When providing technical instructions, use simple language and avoid jargon unless necessary
16. If multiple solutions exist, present the simplest or most commonly used option first
17. Always verify that pricing, plans, or promotional information exists in the context before sharing it
18. For billing or account-specific questions, guide users to appropriate channels rather than making assumptions
19. Maintain consistency in terminology (use the same terms for services/products throughout the conversation)
20. If the user expresses frustration or dissatisfaction, acknowledge their feelings with empathy before addressing the issue
21. Never make promises or commitments that aren't explicitly stated in the retrieved context
22. When explaining policies or terms, present them in a customer-friendly manner while remaining accurate
23. If discussing troubleshooting steps, ask if the previous step worked before moving to the next one
24. End responses with an offer to help further when appropriate (e.g., "Is there anything else I can help you with?")

RESPONSE FORMAT:
* Greeting if needed
* Start with a direct answer
* Provide relevant details or steps
* Include helpful tips if applicable
* Keep responses clear and concise
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
        # 1. Translate question to English (and detect language) if needed
        processing_question = question
        detected_lang = language or "auto"

        # Only translate if not explicitly English
        if detected_lang.lower() not in ["en", "english"]:
            print(f"Translating question (source={detected_lang}) to English...")
            mt_response = call_mt_api(question, source=detected_lang, target="en")

            processing_question = mt_response.get("translated_text", question)
            detected_lang = mt_response.get("source_lang", detected_lang)

            print(f"Detected: {detected_lang}, Translated: {processing_question}")

        # Retrieve relevant context using English question
        retrieved_docs = retriever.retrieve(
            query=processing_question, language=None, app_name=app_name
        )

        if not retrieved_docs:
            original_no_info = "I don't have enough information to answer that question. Please contact our support team for assistance."
            final_answer = original_no_info

            # Translate failure message back if needed
            if detected_lang and detected_lang.lower() not in ["en", "english", "auto"]:
                mt_resp = call_mt_api(
                    original_no_info, source="en", target=detected_lang
                )
                final_answer = mt_resp.get("translated_text", original_no_info)

            return {
                "answer": final_answer,
                "sources": [],
                # "confidence": "low",
            }

        # Format context for the prompt (using retriever's unified formatting)
        context = retriever.format_context(retrieved_docs)

        # Build sources list for API response
        sources = []
        seen_articles = set()

        for doc_info in retrieved_docs:
            metadata = doc_info["metadata"]
            similarity = doc_info["similarity"]

            if metadata.get("source_type") == "article":
                article_id = metadata.get("article_id")
                # Deduplicate by article_id
                if article_id and article_id in seen_articles:
                    continue
                if article_id:
                    seen_articles.add(article_id)

                sources.append(
                    {
                        "type": "article",
                        "article_id": article_id,
                        "title": metadata.get("title"),
                        "app": metadata.get("app_name"),
                        "similarity": round(similarity, 3),
                    }
                )
            else:
                sources.append(
                    {
                        "type": "pdf",
                        "file": metadata.get("source_file"),
                        "similarity": round(similarity, 3),
                    }
                )

        # Build full prompt
        system_prompt = get_qa_prompt() + context

        # Generate answer in English
        response = ollama.generate(
            model=model_name,
            system=system_prompt,
            prompt=f"Question: {processing_question}\n\nPlease provide a helpful answer based on the context above. Answer in English.",
            options={
                # you can set temperature to 0 for deterministic output
                "temperature": 0.1,
                "top_p": 0.85,
                "num_predict": 100,
            },
        )

        english_answer = response["response"].strip()
        final_answer = english_answer

        # Translate answer back to user language if needed
        if detected_lang and detected_lang.lower() not in ["en", "english", "auto"]:
            print(f"Translating answer from English to {detected_lang}...")
            mt_resp = call_mt_api(english_answer, source="en", target=detected_lang)
            final_answer = mt_resp.get("translated_text", english_answer)

        # Determine confidence based on similarity scores
        avg_similarity = sum(s["similarity"] for s in sources) / len(sources)
        if avg_similarity > 0.8:
            confidence = "high"
        elif avg_similarity > 0.6:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "answer": final_answer,
            "sources": sources,
            "confidence": confidence,
            "original_answer_en": english_answer
            if final_answer != english_answer
            else None,
            "retrieved_docs": len(retrieved_docs),
        }

    except Exception as e:
        return {
            "error": f"Failed to generate answer: {str(e)}",
            "answer": "I encountered an error while processing your question. Please try again.",
        }
