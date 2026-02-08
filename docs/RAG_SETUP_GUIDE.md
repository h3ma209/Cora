# RAG Setup Guide for Cora AI

## 🎯 Overview

Your Cora AI now has a complete RAG (Retrieval-Augmented Generation) system! This allows the model to dynamically retrieve relevant context from your knowledge base before making classifications.

## 📦 What Was Created

### Core RAG Components

1. **`vector_store.py`** - ChromaDB vector database manager
2. **`indexer.py`** - Knowledge base indexer (JSON + PDF)
3. **`retriever.py`** - Context retrieval and formatting
4. **`cora.py`** (updated) - RAG-enhanced classification
5. **`docker-compose.yaml`** (updated) - ChromaDB persistence
6. **`requirements.txt`** (updated) - RAG dependencies

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/hema/Desktop/Drift/Cora
pip install -r requirements.txt
```

This will install:

- `chromadb` - Vector database
- `sentence-transformers` - Multilingual embeddings
- `langchain-text-splitters` - Text chunking utilities

### Step 2: Index Your Knowledge Base

```bash
# Index all files in the data directory
python3 indexer.py

# Or reset and reindex
python3 indexer.py --reset

# Check statistics
python3 indexer.py --stats
```

**What happens:**

- Scans `data/jsons/` for JSON files
- Scans `data/pdfs/` for PDF files
- Extracts content from all files
- Generates embeddings using multilingual model
- Stores in ChromaDB at `./chroma_db/`

**Expected output:**

```
============================================================
🚀 Cora Knowledge Base Indexer
============================================================

📁 Indexing directory: ./data
  Found 1 JSON files and 1 PDF files

📄 Processing JSON: data/jsons/articles.json
  ✓ Indexed 39 article variants

📄 Processing PDF: data/pdfs/app-docs/Rayied-Rayied Application Documentation.pdf
  Pages: 25
  ✓ Indexed 45 chunks

💾 Committing 84 documents to vector store...
Loading embedding model: paraphrase-multilingual-mpnet-base-v2
✓ Embedding model loaded
✓ Added 84 documents to vector store
✅ Indexing complete!

📊 Final Statistics:
  Total documents indexed: 84
  Total in vector store: 84
  Location: ./chroma_db
```

### Step 3: Test RAG Retrieval

```bash
# Test the classification with RAG
python3 cora.py
```

Or test via API:

```bash
curl -X POST http://localhost:8001/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "how do I reset my password in ana app?"}'
```

### Step 4: Deploy with Docker

```bash
# Rebuild with new dependencies
docker-compose build

# Start services
docker-compose up -d

# Index knowledge base inside container
docker-compose exec cora-api python3 indexer.py

# Check logs
docker-compose logs -f cora-api
```

## 🔧 How It Works

### Architecture Flow

```
User Query
    ↓
1. Detect Language
    ↓
2. Generate Query Embedding
    ↓
3. Search Vector Store (ChromaDB)
    ↓
4. Retrieve Top 3 Similar Documents
    ↓
5. Format Context
    ↓
6. Enhance System Prompt with Context
    ↓
7. Send to Ollama (Qwen2.5:1.5b)
    ↓
8. Return JSON Classification
```

### Embedding Model

**Model**: `paraphrase-multilingual-mpnet-base-v2`

- Supports 50+ languages including Arabic and Kurdish
- 768-dimensional embeddings
- Trained on 1B+ sentence pairs
- Optimized for semantic similarity

### Vector Database

**ChromaDB** - Lightweight, embedded vector database

- Persistent storage in `./chroma_db/`
- Fast similarity search using HNSW algorithm
- Metadata filtering (by language, app_name, etc.)

## 📊 Configuration

### Retriever Settings

Edit `retriever.py` to customize:

```python
RAGRetriever(
    n_results=3,              # Number of documents to retrieve
    similarity_threshold=0.5   # Minimum similarity score (0-1)
)
```

### Indexer Settings

Edit `indexer.py` to customize:

```python
index_pdf_file(
    file_path,
    chunk_size=1000  # Characters per chunk
)
```

### Vector Store Settings

Edit `vector_store.py` to customize:

```python
VectorStore(
    persist_directory="./chroma_db",
    collection_name="rayied_knowledge_base",
    embedding_model="paraphrase-multilingual-mpnet-base-v2"
)
```

## 🎯 Usage Examples

### Example 1: Basic Classification with RAG

```python
from cora import get_json_classification

# With RAG (default)
result = get_json_classification("كيف أعيد تعيين كلمتي السرية؟")

# Without RAG
result = get_json_classification("how to reset password", use_rag=False)
```

### Example 2: Custom Retrieval

```python
from retriever import get_retriever

retriever = get_retriever()

# Retrieve with language filter
docs = retriever.retrieve(
    query="password reset",
    language="en",
    app_name="ana"
)

# Get article recommendations
article_ids = retriever.get_article_recommendations(
    query="internet slow",
    language="ar",
    n_results=5
)
```

### Example 3: Re-indexing After Updates

```bash
# After adding new articles to articles.json
python3 indexer.py

# Or reset and reindex everything
python3 indexer.py --reset
```

## 📈 Performance Metrics

### Expected Performance

| Metric | Value |
|--------|-------|
| Indexing Time | ~2-5 min (first time) |
| Query Time | ~200-500ms |
| Embedding Generation | ~50-100ms per query |
| Vector Search | ~10-50ms |
| Total Latency | +300-600ms vs non-RAG |

### Memory Usage

- Embedding Model: ~400MB RAM
- ChromaDB: ~50MB + (documents × 3KB)
- Total: ~500-800MB additional RAM

## 🔍 Monitoring & Debugging

### Check Vector Store Stats

```bash
python3 indexer.py --stats
```

Output:

```
📊 Vector Store Statistics:
  Collection: rayied_knowledge_base
  Documents: 84
  Location: ./chroma_db
```

### Test Retrieval

```python
from retriever import get_retriever

retriever = get_retriever()
context = retriever.retrieve_and_format("password reset")
print(context)
```

### View Retrieved Context

The system prints RAG activity:

```
✓ RAG retriever initialized
✓ RAG: Retrieved 1247 chars of context
```

## ⚠️ Important Notes

### 1. First-Time Setup

The first time you run the indexer:

- Downloads embedding model (~400MB)
- Takes 2-5 minutes to index
- Subsequent runs are much faster

### 2. Docker Persistence

ChromaDB data is persisted in a Docker volume:

```bash
# View volumes
docker volume ls | grep chroma

# Backup volume
docker run --rm -v cora_chroma_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma_backup.tar.gz /data
```

### 3. Re-indexing

When you update articles or PDFs:

```bash
# Option 1: Incremental (adds new docs)
python3 indexer.py

# Option 2: Full reset (recommended for major changes)
python3 indexer.py --reset
```

### 4. Multilingual Support

The system automatically:

- Indexes all language variants (EN, AR, KU)
- Searches across all languages
- Returns best matches regardless of language
- Formats context with language labels

## 🐛 Troubleshooting

### Issue: "No module named 'chromadb'"

**Solution:**

```bash
pip install chromadb sentence-transformers
```

### Issue: "Embedding model download failed"

**Solution:**

```bash
# Pre-download the model
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"
```

### Issue: "Collection not found"

**Solution:**

```bash
# Reindex the knowledge base
python3 indexer.py
```

### Issue: "RAG retriever failed to initialize"

**Solution:**
The system automatically falls back to non-RAG mode. Check:

1. ChromaDB is installed
2. Knowledge base is indexed
3. Permissions on `./chroma_db/` directory

### Issue: "Slow performance"

**Solutions:**

1. Reduce `n_results` in retriever (3 → 2)
2. Increase `similarity_threshold` (0.5 → 0.7)
3. Use smaller embedding model
4. Cache frequent queries

## 🎓 Advanced Features

### Custom Metadata Filtering

```python
# Search only in specific app
docs = retriever.retrieve(
    query="login issue",
    app_name="hakki"
)

# Search only in specific language
docs = retriever.retrieve(
    query="مشكلة الدخول",
    language="ar"
)
```

### Article Recommendations

```python
# Get recommended article IDs
article_ids = retriever.get_article_recommendations(
    query="slow internet",
    n_results=5
)
# Returns: ['8', '4', '15', ...]
```

### Similarity Scores

```python
docs = retriever.retrieve(query="password")
for doc in docs:
    print(f"Similarity: {doc['similarity']:.2f}")
    print(f"Content: {doc['document'][:100]}...")
```

## 📚 Next Steps

### Immediate

1. ✅ Index your knowledge base
2. ✅ Test RAG retrieval
3. ✅ Deploy with Docker

### Short-term

1. Monitor performance metrics
2. Tune retrieval parameters
3. Add more documents to knowledge base

### Long-term

1. Implement caching for frequent queries
2. Add re-ranking for better relevance
3. Set up automated re-indexing
4. Track user feedback on recommendations

## 🆘 Support

If you encounter issues:

1. **Check logs**: `docker-compose logs cora-api`
2. **Verify indexing**: `python3 indexer.py --stats`
3. **Test retrieval**: Run `python3 cora.py`
4. **Rebuild**: `docker-compose build --no-cache`

## ✅ Summary

You now have a production-ready RAG system that:

- ✅ Indexes JSON articles and PDF documents
- ✅ Generates multilingual embeddings
- ✅ Retrieves relevant context dynamically
- ✅ Enhances classifications with domain knowledge
- ✅ Persists data across restarts
- ✅ Falls back gracefully if RAG fails

**Ready to use!** Just run:

```bash
python3 indexer.py
```
