from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cora
import os

app = FastAPI(title="Cora API", description="API for Rayeid AI Classification Engine")


class ClassificationRequest(BaseModel):
    text: str


@app.post("/classify")
async def classify_text(request: ClassificationRequest):
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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    # Allow port configuration via environment variable
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
