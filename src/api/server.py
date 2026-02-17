from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from src.api import cora, qa
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cora API",
    description="AI Classification and Q&A Engine for Rayied Customer Support",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"],
)


class ClassificationRequest(BaseModel):
    text: str


class QuestionRequest(BaseModel):
    question: str
    language: Optional[str] = None  # en, ar, ku
    app_name: Optional[str] = None  # Filter by app
    session_id: Optional[str] = None  # For conversation context


@app.post("/classify")
async def classify_text(request: ClassificationRequest):
    """
    Classify customer support text into categories and recommend articles.

    Returns:
        - detected_language
        - category
        - issue_type
        - routing_department
        - recommended_article_ids
        - sentiment
        - summaries (multilingual)
    """
    try:
        # Check if text is provided
        if not request.text:
            raise HTTPException(status_code=400, detail="Text field cannot be empty")

        # Call the cora classification function
        result = cora.get_json_classification(request.text)

        # Check for error in result
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def answer_question(request: QuestionRequest):
    """
    Answer customer questions using RAG-retrieved context from knowledge base.
    Supports multi-turn conversations via session_id.

    Returns:
        - answer: Direct answer to the question
        - sources: List of source articles/documents used
        - confidence: Confidence level (high/medium/low)
        - retrieved_docs: Number of documents retrieved
        - session_id: Session ID for maintaining conversation context
    """
    try:
        # Check if question is provided
        if not request.question:
            raise HTTPException(
                status_code=400, detail="Question field cannot be empty"
            )

        # Call the Q&A function with session support
        result = qa.answer_question(
            question=request.question,
            language=request.language,
            app_name=request.app_name,
            session_id=request.session_id,
        )

        # Check for error in result
        if "error" in result and "answer" not in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/stream")
async def stream_question(request: QuestionRequest):
    """
    Stream the answer to a customer question.
    Supports multi-turn conversations via session_id.
    """
    from src.api.session import get_session_manager

    # Get or create session upfront to return ID in headers
    session_manager = get_session_manager()
    session = session_manager.get_session(request.session_id)

    return StreamingResponse(
        qa.stream_answer_question(
            question=request.question,
            language=request.language,
            app_name=request.app_name,
            session_id=session.session_id,
        ),
        media_type="text/event-stream",
        headers={"X-Session-ID": session.session_id},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Cora API",
        "version": "2.0.0",
        "endpoints": {
            "/classify": "POST - Classify support text",
            "/ask": "POST - Answer questions from knowledge base",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation (Swagger UI)",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Allow port configuration via environment variable
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
