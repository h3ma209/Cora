# ✅ **Both Endpoints Work on the Same Server!**

## 🎉 **Confirmed: Single Server, Two Endpoints**

Your Cora API server now runs **both** the classification and Q&A endpoints on the **same server** at `http://localhost:8001`.

### **Server Status:**

```
✅ Server Running: http://localhost:8001
✅ Version: 2.0.0
✅ Both Endpoints Active
```

---

## 📡 **Available Endpoints**

### **1. Root - API Information**

```bash
curl http://localhost:8001/
```

**Response:**

```json
{
  "name": "Cora API",
  "version": "2.0.0",
  "endpoints": {
    "/classify": "POST - Classify support text",
    "/ask": "POST - Answer questions from knowledge base",
    "/health": "GET - Health check",
    "/docs": "GET - API documentation (Swagger UI)"
  }
}
```

---

### **2. Classification Endpoint** `/classify`

**Purpose**: Categorize support tickets for routing

**Request:**

```bash
curl -X POST http://localhost:8001/classify \
  -H 'Content-Type: application/json' \
  -d '{"text": "I cannot login to my account"}'
```

**Response:**

```json
{
  "detected_language": "en",
  "category": "Account Access",
  "issue_type": "Login Problem",
  "routing_department": "Technical Support",
  "recommended_article_ids": ["17", "16"],
  "sentiment": "Negative"
}
```

---

### **3. Q&A Endpoint** `/ask` (NEW!)

**Purpose**: Answer customer questions directly

**Request:**

```bash
curl -X POST http://localhost:8001/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "How do I reset my password?"}'
```

**Response:**

```json
{
  "answer": "To reset your password:\n\n1. Open the app's main interface\n2. At the top of the screen, tap the options button\n3. Select 'Change Password' from the menu\n4. Enter a new password (can include numbers and letters)\n5. Tap 'Confirm' to save\n\nYour password will be updated immediately.",
  "sources": [
    {
      "type": "article",
      "article_id": "17",
      "title": "reset password",
      "app": "ana",
      "similarity": 0.923
    }
  ],
  "confidence": "high",
  "retrieved_docs": 3
}
```

---

### **4. Health Check** `/health`

```bash
curl http://localhost:8001/health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

---

### **5. Interactive API Docs** `/docs`

Open in browser:

```
http://localhost:8001/docs
```

This provides:

- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

---

## 🎯 **Why Same Server?**

### **Advantages:**

1. ✅ **Shared Resources**
   - Same RAG knowledge base
   - Same vector store (ChromaDB)
   - Same embedding model
   - Efficient memory usage

2. ✅ **Simplified Deployment**
   - Single Docker container
   - One port to manage (8001)
   - Easier to scale

3. ✅ **Consistent Performance**
   - Shared connection pooling
   - Single Ollama instance
   - Unified monitoring

4. ✅ **Easy Integration**
   - One base URL for all endpoints
   - Consistent authentication (if added)
   - Single API documentation

---

## 🔧 **When to Separate?**

You might want separate servers if:

- **Heavy Load**: Different scaling needs for each endpoint
- **Different SLAs**: Q&A needs faster response than classification
- **Security**: Different access controls for each endpoint
- **Team Structure**: Different teams manage each service

### **How to Separate (if needed):**

1. Create two separate FastAPI apps:

   ```python
   # classify_server.py
   app = FastAPI()
   @app.post("/classify")
   async def classify(...)
   
   # qa_server.py
   app = FastAPI()
   @app.post("/ask")
   async def ask(...)
   ```

2. Run on different ports:

   ```bash
   python3 classify_server.py  # Port 8001
   python3 qa_server.py         # Port 8002
   ```

3. Use a reverse proxy (nginx) to route:

   ```
   /classify → localhost:8001
   /ask      → localhost:8002
   ```

---

## 📊 **Current Architecture**

```
┌─────────────────────────────────────────┐
│     Cora API Server (Port 8001)         │
│                                         │
│  ┌─────────────┐    ┌──────────────┐   │
│  │  /classify  │    │    /ask      │   │
│  │  endpoint   │    │  endpoint    │   │
│  └──────┬──────┘    └──────┬───────┘   │
│         │                  │           │
│         └──────┬───────────┘           │
│                │                       │
│         ┌──────▼──────┐                │
│         │  RAG System │                │
│         │  (Shared)   │                │
│         └──────┬──────┘                │
│                │                       │
│         ┌──────▼──────┐                │
│         │  ChromaDB   │                │
│         │ Vector Store│                │
│         └──────┬──────┘                │
│                │                       │
│         ┌──────▼──────┐                │
│         │   Ollama    │                │
│         │ Qwen2.5:1.5b│                │
│         └─────────────┘                │
└─────────────────────────────────────────┘
```

---

## 🚀 **Quick Test Commands**

### Test Classification

```bash
curl -X POST http://localhost:8001/classify \
  -H 'Content-Type: application/json' \
  -d '{"text": "my internet is very slow"}'
```

### Test Q&A

```bash
curl -X POST http://localhost:8001/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "How do I reset my password?"}'
```

### Test Q&A with Filters

```bash
# Arabic question
curl -X POST http://localhost:8001/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "كيف أعيد تعيين كلمة المرور؟",
    "language": "ar"
  }'

# App-specific
curl -X POST http://localhost:8001/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "How do I send points?",
    "app_name": "self-care"
  }'
```

---

## ✅ **Summary**

**YES, both endpoints work on the same server!**

- ✅ **Single Server**: Port 8001
- ✅ **Two Endpoints**: `/classify` and `/ask`
- ✅ **Shared RAG**: Same knowledge base
- ✅ **Production Ready**: Fully functional
- ✅ **Easy to Use**: One API, multiple capabilities

**No need to separate unless you have specific scaling or security requirements!**

---

## 📚 **Next Steps**

1. **Test Both Endpoints**: Use the curl commands above
2. **View API Docs**: <http://localhost:8001/docs>
3. **Integrate**: Use in your frontend/mobile app
4. **Monitor**: Track usage and performance
5. **Scale**: Add load balancing if needed

**Your unified API is ready to use!** 🎉
