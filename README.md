# Cora AI - RAG-Enhanced Classification Engine

> Multilingual AI classification system with Retrieval-Augmented Generation for Rayied customer support

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-latest-orange.svg)](https://www.trychroma.com/)

## 🎯 Overview

Cora is an intelligent AI system that combines classification and question-answering capabilities using RAG (Retrieval-Augmented Generation). It supports English, Arabic, and Kurdish languages.

### Key Features

- ✅ **RAG-Enhanced Classification** - Categorizes support tickets with context
- ✅ **Q&A System** - Answers customer questions directly from knowledge base
- ✅ **Multilingual Support** - English, Arabic, Kurdish (Sorani & Kurmanji)
- ✅ **Semantic Search** - Vector-based similarity search using ChromaDB
- ✅ **Article Recommendations** - Auto-suggests relevant help articles
- ✅ **Source Attribution** - Shows which articles were used for answers
- ✅ **REST API** - FastAPI-based HTTP interface with two endpoints
- ✅ **Docker Ready** - Production deployment included

### Two Powerful Endpoints

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/classify` | Categorize support tickets | Ticket routing, analytics |
| `/ask` | Answer questions directly | Customer self-service, chatbot |

## 📁 Project Structure

```
Cora/
├── src/                          # Source code
│   ├── api/                      # API components
│   │   ├── cora.py              # Classification engine
│   │   ├── server.py            # FastAPI server
│   │   └── utils.py             # Utilities
│   └── rag/                      # RAG components
│       ├── vector_store.py      # ChromaDB interface
│       ├── retriever.py         # Context retrieval
│       └── indexer.py           # Knowledge indexer
│
├── tests/                        # Test suite
│   └── test_rag.py              # RAG tests
│
├── scripts/                      # Utility scripts
│   ├── setup_rag.sh             # Automated setup
│   ├── quick_append.sh          # Quick knowledge append
│   └── append_knowledge.py      # Knowledge appender
│
├── config/                       # Configuration
│   └── prompt.txt               # System prompt
│
├── docs/                         # Documentation
│   ├── RAG_SETUP_GUIDE.md       # Complete setup guide
│   ├── ARCHITECTURE.md          # System architecture
│   └── ...                      # More docs
│
├── data/                         # Knowledge base
│   ├── jsons/                   # JSON articles
│   └── pdfs/                    # PDF documents
│
├── chroma_db/                    # Vector store (auto-created)
│
├── Wrapper Scripts (root)        # Backward compatibility
│   ├── indexer.py               # → src/rag/indexer.py
│   ├── cora.py                  # → src/api/cora.py
│   ├── server.py                # → src/api/server.py
│   └── test_rag.py              # → tests/test_rag.py
│
├── requirements.txt              # Python dependencies
├── docker-compose.yaml           # Docker configuration
├── Dockerfile                    # Docker image
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or navigate to project
cd /path/to/Cora

# Run automated setup
./scripts/setup_rag.sh
```

This will:

- Install dependencies
- Index your knowledge base
- Test the RAG system

### 2. Test

```bash
# Test RAG retrieval
python3 test_rag.py

# Test classification
python3 cora.py
```

### 3. Run API Server

```bash
# Start server
python3 server.py

# Test Classification Endpoint
curl -X POST http://localhost:8001/classify \
  -H 'Content-Type: application/json' \
  -d '{"text": "how to reset password"}'

# Test Q&A Endpoint (NEW!)
curl -X POST http://localhost:8001/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "How do I reset my password?"}'

# Interactive API Documentation
open http://localhost:8001/docs
```

### 4. Deploy with Docker

#### Option A: Using Makefile (Recommended)

```bash
# First time setup (build + start + index)
make dev

# Check health
make health

# View logs
make logs

# See all commands
make help
```

#### Option B: Using docker-compose

```bash
# Build and start
docker-compose up -d

# Index knowledge base
docker-compose exec cora-api python3 indexer.py

# Check logs
docker-compose logs -f cora-api
```

**See `MAKEFILE_QUICK_REF.md` for all Makefile commands**

## 📊 How It Works

### Architecture Flow

```
User Query
    ↓
Generate Embedding (768-dim)
    ↓
Search Vector Store (ChromaDB)
    ↓
Retrieve Top 3 Relevant Documents
    ↓
Enhance Prompt with Context
    ↓
Ollama (Qwen2.5:1.5b)
    ↓
JSON Classification Result
```

### Example Request/Response

**Request:**

```json
{
  "text": "how to reset password in ana app"
}
```

**Response:**

```json
{
  "detected_language": "en",
  "category": "Account Access",
  "issue_type": "Password Reset",
  "routing_department": "Customer Care",
  "recommended_article_ids": ["17", "16"],
  "sentiment": "Neutral",
  "summaries": {
    "en": "User needs to reset password in ana app",
    "ar": "المستخدم يحتاج إلى إعادة تعيين كلمة المرور",
    "ckb": "بەکارهێنەر پێویستی بە دووبارە دانانی وشەی نهێنی هەیە",
    "kmr": "Bikarhêner hewce dike ku şîfreyê ji nû ve saz bike"
  }
}
```

## 🔧 Configuration

### Embedding Model

Edit `src/rag/vector_store.py`:

```python
VectorStore(
    embedding_model="paraphrase-multilingual-mpnet-base-v2"
)
```

### Retrieval Settings

Edit `src/rag/retriever.py`:

```python
RAGRetriever(
    n_results=3,              # Number of documents to retrieve
    similarity_threshold=0.5   # Minimum similarity (0-1)
)
```

### System Prompt

Edit `config/prompt.txt` to customize the classification behavior.

## 📚 Documentation

- **[RAG Setup Guide](docs/RAG_SETUP_GUIDE.md)** - Complete setup and configuration
- **[Q&A System](docs/QA_SYSTEM.md)** - Question answering endpoint guide
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture diagrams
- **[Quick Start](docs/QUICK_START.md)** - Quick reference guide
- **[Folder Structure](docs/FOLDER_STRUCTURE.md)** - Project organization

## 🛠️ Development

### Adding New Knowledge

```bash
# Add articles to data/jsons/articles.json
# Add PDFs to data/pdfs/

# Reindex
python3 indexer.py
```

### Running Tests

```bash
# Full test suite
python3 test_rag.py

# Check vector store stats
python3 indexer.py --stats
```

### Project Commands

```bash
# Index knowledge base
python3 indexer.py

# Reset and reindex
python3 indexer.py --reset

# View statistics
python3 indexer.py --stats

# Test classification
python3 cora.py

# Start API server
python3 server.py

# Run tests
python3 test_rag.py
```

## 🐳 Docker

### Build

```bash
docker-compose build
```

### Run

```bash
docker-compose up -d
```

### Index in Container

```bash
docker-compose exec cora-api python3 indexer.py
```

### Logs

```bash
docker-compose logs -f cora-api
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Indexing Time | 2-5 min (first run) |
| Query Latency | +300-600ms vs non-RAG |
| Memory Usage | +500-800MB |
| Embedding Model | 400MB |
| Documents Indexed | 77 (current) |

## 🔍 Troubleshooting

### Issue: "No module named 'src'"

**Solution:** Run from project root, not from subdirectories.

### Issue: "No documents retrieved"

**Solution:** Lower similarity threshold in `src/rag/retriever.py`:

```python
similarity_threshold=0.3  # Lower from 0.5
```

### Issue: "ChromaDB not found"

**Solution:**

```bash
pip install chromadb sentence-transformers
```

### Issue: "Slow performance"

**Solutions:**

1. Reduce `n_results` from 3 to 2
2. Increase `similarity_threshold` from 0.5 to 0.7
3. Cache frequent queries

## 🤝 Contributing

1. Add new features in `src/`
2. Add tests in `tests/`
3. Update documentation in `docs/`
4. Run tests before committing

## 📝 License

Proprietary - Rayied Project

## 🆘 Support

- **Check logs**: `docker-compose logs cora-api`
- **View stats**: `python3 indexer.py --stats`
- **Test RAG**: `python3 test_rag.py`
- **Documentation**: See `docs/` directory

## ✨ Credits

- **Embedding Model**: [sentence-transformers](https://www.sbert.net/)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/)
- **LLM**: [Ollama](https://ollama.ai/) with Qwen2.5:1.5b
- **API Framework**: [FastAPI](https://fastapi.tiangolo.com/)

---

**Version**: 2.0.0 (RAG-Enhanced)  
**Last Updated**: 2026-02-08
