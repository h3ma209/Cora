# Cora RAG System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUERY                                   │
│              "how do I reset my password in ana app?"               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CORA.PY (Main Entry)                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. Receive user query                                         │  │
│  │ 2. Check if RAG is enabled (use_rag=True)                    │  │
│  │ 3. Call retriever if RAG enabled                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RETRIEVER.PY (Context Retrieval)                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. Generate query embedding (768 dimensions)                 │  │
│  │ 2. Search vector store for similar documents                 │  │
│  │ 3. Filter by similarity threshold (>0.5)                     │  │
│  │ 4. Return top 3 most relevant documents                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  VECTOR_STORE.PY (ChromaDB Interface)                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Embedding Model: paraphrase-multilingual-mpnet-base-v2       │  │
│  │ ┌────────────────────────────────────────────────────────┐   │  │
│  │ │ Collection: rayied_knowledge_base                       │   │  │
│  │ │ ┌────────────────────────────────────────────────────┐ │   │  │
│  │ │ │ Document 1: [Article #17] [ana] reset password    │ │   │  │
│  │ │ │ Embedding: [0.23, -0.45, 0.67, ... 768 dims]      │ │   │  │
│  │ │ │ Metadata: {app: ana, lang: en, type: article}     │ │   │  │
│  │ │ ├────────────────────────────────────────────────────┤ │   │  │
│  │ │ │ Document 2: [Article #17] [ana] reset password    │ │   │  │
│  │ │ │ Embedding: [0.12, -0.34, 0.56, ... 768 dims]      │ │   │  │
│  │ │ │ Metadata: {app: ana, lang: ar, type: article}     │ │   │  │
│  │ │ ├────────────────────────────────────────────────────┤ │   │  │
│  │ │ │ ... 82 more documents ...                          │ │   │  │
│  │ │ └────────────────────────────────────────────────────┘ │   │  │
│  │ └────────────────────────────────────────────────────────┘   │  │
│  │ Similarity Search: Cosine similarity / L2 distance            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RETRIEVED CONTEXT (Top 3)                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ [Source 1] [Article ID: 17] [App: ana] [Title: reset pwd]   │  │
│  │ Similarity: 0.92                                             │  │
│  │ Content: "Open the app's main interface. At the top..."      │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ [Source 2] [Article ID: 16] [App: self-care] [Title: ...]   │  │
│  │ Similarity: 0.78                                             │  │
│  │ Content: "Easily and securely change your password..."       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │ [Source 3] [Article ID: 21] [App: self-care] [Title: ...]   │  │
│  │ Similarity: 0.65                                             │  │
│  │ Content: "Through settings > Edit profile > Click..."        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ENHANCED PROMPT CONSTRUCTION                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ SYSTEM PROMPT (from prompt.txt)                              │  │
│  │ + RETRIEVED CONTEXT (formatted)                              │  │
│  │ = ENHANCED PROMPT                                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OLLAMA (llama3.1:8b)                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Input: Enhanced Prompt + User Query                          │  │
│  │ Model: llama3.1:8b (local)                                  │  │
│  │ Format: JSON (forced)                                        │  │
│  │ Temperature: 0.0 (deterministic)                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    JSON CLASSIFICATION RESULT                        │
│  {                                                                   │
│    "detected_language": "en",                                        │
│    "detected_dialect": "na",                                         │
│    "category": "Account Access",                                     │
│    "issue_type": "Password Reset",                                   │
│    "routing_department": "Customer Care",                            │
│    "recommended_article_ids": ["17", "16", "21"],                    │
│    "sentiment": "Neutral",                                           │
│    "summaries": {                                                    │
│      "en": "User needs to reset password in ana app",                │
│      "ar": "المستخدم يحتاج إلى إعادة تعيين كلمة المرور",             │
│      "ckb": "بەکارهێنەر پێویستی بە دووبارە دانانی وشەی نهێنی هەیە",  │
│      "kmr": "Bikarhêner hewce dike ku şîfreyê ji nû ve saz bike"     │
│    }                                                                 │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                        INDEXING WORKFLOW
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                         INDEXER.PY                                   │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────┐    ┌──────────────────┐
│  data/jsons/     │    │  data/pdfs/      │
│  articles.json   │    │  Rayied-Doc.pdf  │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│ Parse JSON      │    │ Extract PDF Text │
│ 13 articles     │    │ 25 pages         │
│ × 3 languages   │    │ → 45 chunks      │
│ = 39 variants   │    │                  │
└────────┬────────┘    └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │ Generate Embeddings  │
         │ (768 dimensions)     │
         │ Batch: 32 at a time  │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │ Store in ChromaDB    │
         │ Location: ./chroma_db│
         │ Total: 84 documents  │
         └──────────────────────┘


═══════════════════════════════════════════════════════════════════════
                        DATA FLOW SUMMARY
═══════════════════════════════════════════════════════════════════════

1. INDEXING (One-time):
   JSON/PDF Files → Indexer → Embeddings → ChromaDB

2. RETRIEVAL (Per Query):
   Query → Embedding → Vector Search → Top 3 Docs → Context

3. CLASSIFICATION (Per Query):
   Query + Context → Enhanced Prompt → Ollama → JSON Result

4. API (Production):
   HTTP Request → FastAPI → Classification → HTTP Response


═══════════════════════════════════════════════════════════════════════
                        FILE STRUCTURE
═══════════════════════════════════════════════════════════════════════

Cora/
├── Core RAG System
│   ├── vector_store.py      (5.3K) - ChromaDB interface
│   ├── indexer.py            (9.3K) - Knowledge indexer
│   ├── retriever.py          (5.6K) - Context retrieval
│   └── cora.py              (updated) - RAG integration
│
├── Testing & Setup
│   ├── test_rag.py           (5.3K) - Test suite
│   ├── setup_rag.sh          (2.9K) - Automated setup
│   └── indexer.py --stats           - Stats checker
│
├── Documentation
│   ├── RAG_IMPLEMENTATION_SUMMARY.md (8.0K) - This file
│   ├── RAG_SETUP_GUIDE.md            (9.2K) - Full guide
│   └── QUICK_START.md                       - Quick ref
│
├── Data & Storage
│   ├── data/
│   │   ├── jsons/articles.json
│   │   └── pdfs/app-docs/*.pdf
│   └── chroma_db/           (auto-created) - Vector store
│
└── Configuration
    ├── requirements.txt      (updated) - Dependencies
    ├── docker-compose.yaml   (updated) - Docker config
    └── prompt.txt                      - System prompt


═══════════════════════════════════════════════════════════════════════
                        QUICK COMMANDS
═══════════════════════════════════════════════════════════════════════

# Setup (one-time)
./setup_rag.sh

# Index knowledge base
python3 indexer.py

# Test RAG system
python3 test_rag.py

# Run classification
python3 cora.py

# Start API server
python3 server.py

# Deploy with Docker
docker-compose build
docker-compose up -d
docker-compose exec cora-api python3 indexer.py

# Check stats
python3 indexer.py --stats

# Reset and reindex
python3 indexer.py --reset
```
