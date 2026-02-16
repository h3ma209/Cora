# Cora AI - RAG-Enhanced Classification Engine

Cora is an intelligent AI system that combines classification and question-answering capabilities using Retrieval-Augmented Generation (RAG). It supports English, Arabic, and Kurdish languages.

## Key Features

- **RAG-Enhanced Classification**: Categorizes support tickets with context.
- **Q&A System**: Answers customer questions directly from the knowledge base.
- **Multilingual Support**: Optimized for English, Arabic, and Kurdish.
- **Semantic Search**: Vector-based similarity search using ChromaDB.
- **REST API**: FastAPI-based HTTP interface.
- **Docker Ready**: Production-ready deployment configuration.

## Project Structure

```text
Cora/
├── src/                  # Source code

│   ├── api/              # API and Q&A logic
│   └── rag/              # RAG components (Indexer, Retriever)
├── tests/                # Unit tests
├── data/                 # Knowledge base (JSONs, PDFs)
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── config/               # Configuration files
├── docker-compose.yaml   # Docker orchestration
├── Dockerfile            # API container definition
├── Makefile              # Build and management commands
└── requirements.txt      # Python dependencies
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)

### Deployment

To build and start the entire system (API + Database + Ollama):

```bash
make setup
```

This command will:

1. Build Docker images.
2. Start services in the background.
3. Index the knowledge base.

### API Usage

The API runs on port **8001** by default.

#### 1. Classification

Classify support text and get article recommendations.

```bash
curl -X POST http://localhost:8001/classify \
  -H 'Content-Type: application/json' \
  -d '{"text": "how to reset password"}'
```

#### 2. Q&A

Ask a question and get an answer based on the knowledge base.

```bash
curl -X POST http://localhost:8001/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "How do I reset my password?"}'
```

### Management Commands

Use `make help` to see all available commands.

- **Start Services**: `make up`
- **Stop Services**: `make down`
- **View Logs**: `make logs`
- **Reindex Knowledge Base**: `make index`
- **Run Tests**: `make test`

## Configuration

- **Embedding Model**: Configured in `src/rag/vector_store.py` (Default: `paraphrase-multilingual-mpnet-base-v2`).
- **Retrieval Settings**: Adjusted in `src/rag/retriever.py` (Thresholds, Top-K).
- **System Prompt**: Located in `config/prompt.txt`.

## Development

To run locally without Docker:

```bash
pip install -r requirements.txt
python3 -m uvicorn src.api.server:app --reload
```

## License

Proprietary - Rayied Project.


### Test streaming
```bash
http --stream POST localhost:9321/ask/stream question="Why my sim has such a low signal?" language=en
```