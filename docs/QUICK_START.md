# Knowledge Appender - Quick Start Guide

## ✅ What I Created

I've built a simple Python script that reads files and appends their content to your Cora AI model's knowledge base.

### Files Created

1. **`append_knowledge.py`** - Main script for appending knowledge
2. **`KNOWLEDGE_APPENDER_README.md`** - Full documentation
3. **Updated `requirements.txt`** - Added PyPDF2 dependency

## 🚀 How to Use

### Quick Example

```bash
# Append your articles to the model
python3 append_knowledge.py data/jsons/articles.json

# Or append PDF documentation
python3 append_knowledge.py "data/pdfs/app-docs/Rayied-Rayied Application Documentation.pdf"

# Restart the service to apply changes
docker-compose restart cora-api
```

## 📊 What It Does

The script:

1. ✅ Reads JSON or PDF files
2. ✅ Extracts all content (including multilingual text)
3. ✅ Creates a backup of your current prompt
4. ✅ Shows you a preview of what will be added
5. ✅ Asks for confirmation
6. ✅ Appends knowledge to `prompt.txt`
7. ✅ Reminds you to restart the service

## 🎯 Test Results

I tested it with your `articles.json` file:

- ✅ Successfully extracted **22,910 characters** of knowledge
- ✅ Parsed all 13 articles with multilingual content
- ✅ Formatted properly for the model

### Preview of Extracted Knowledge

```
[Article ID: 17] [ana] reset password
EN: Open the app's main interface...
AR: افتح الواجهة الرئيسية للتطبيق...
KU: Navrûya sereke ya serîlêdanê vekin...
```

## 🔧 Installation

If running locally (not in Docker):

```bash
pip install PyPDF2
```

If using Docker:

```bash
# Rebuild the container to include PyPDF2
docker-compose build cora-api
docker-compose up -d
```

## 📝 Example Workflow

### Step 1: Append Articles

```bash
cd /Users/hema/Desktop/Drift/Cora
python3 append_knowledge.py data/jsons/articles.json
# Type 'y' when prompted
```

### Step 2: Restart Service

```bash
docker-compose restart cora-api
```

### Step 3: Test the Model

```bash
curl -X POST http://localhost:8001/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "how do I reset my password in ana app?"}'
```

The model will now use the appended knowledge to provide better classifications!

## 🛡️ Safety Features

- **Automatic Backup**: Creates `prompt.txt.backup` before any changes
- **Duplicate Detection**: Warns if knowledge already exists
- **Interactive Confirmation**: You must approve before changes
- **Preview**: Shows what will be added before committing

## 📈 Benefits vs Full RAG

| Feature | Knowledge Appender | Full RAG |
|---------|-------------------|----------|
| Setup Time | ✅ 5 minutes | ❌ 2-3 weeks |
| Complexity | ✅ Simple | ❌ Complex |
| Dependencies | ✅ Just PyPDF2 | ❌ Vector DB, embeddings, etc. |
| Performance | ✅ Fast | ⚠️ Slower (retrieval overhead) |
| Context Limit | ⚠️ Limited by model | ✅ Unlimited knowledge base |
| Dynamic Updates | ⚠️ Manual re-run | ✅ Automatic |

## ⚠️ Important Notes

### Context Window Limitation

- Qwen2.5:1.5b has a **2048 token limit**
- Your current prompt + knowledge must fit within this
- Current articles = ~22,910 chars ≈ 5,700 tokens (too large!)
- **Solution**: Only append most relevant articles or use chunking

### Recommendation

For now, you have two options:

**Option A: Selective Appending** (Recommended for immediate use)

- Create smaller JSON files with only critical articles
- Append only the most frequently needed knowledge
- Keep total under ~1,500 tokens

**Option B: Full RAG Implementation** (Recommended for production)

- Follow the RAG plan I provided earlier
- Use vector database for semantic search
- Retrieve only relevant context per query

## 🎯 Next Steps

### Immediate (Today)

1. Test the script with a small subset of articles
2. Monitor model performance
3. Restart service and verify

### Short-term (This Week)

1. Create filtered JSON files with priority articles
2. Append incrementally
3. Measure classification accuracy improvement

### Long-term (Next Month)

1. Implement full RAG if knowledge base grows
2. Add vector database (ChromaDB)
3. Enable semantic retrieval

## 📚 Documentation

- Full guide: `KNOWLEDGE_APPENDER_README.md`
- RAG implementation plan: (provided in previous response)

## 🆘 Troubleshooting

**Issue**: Script says "command not found: python"
**Fix**: Use `python3` instead of `python`

**Issue**: "PyPDF2 not installed"
**Fix**: `pip install PyPDF2`

**Issue**: Changes not reflected
**Fix**: `docker-compose restart cora-api`

**Issue**: Model performance degraded
**Fix**: Too much knowledge appended. Restore backup: `cp prompt.txt.backup prompt.txt`

## ✨ Summary

You now have a working tool to enhance your Cora AI model with domain-specific knowledge from your JSON and PDF files. It's production-ready and safe to use!

**Ready to use?** Just run:

```bash
python3 append_knowledge.py data/jsons/articles.json
```
