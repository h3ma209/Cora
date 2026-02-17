# Knowledge Appender for Cora AI

## Overview

This script allows you to dynamically append knowledge from JSON and PDF files to your Cora AI model's prompt, enhancing its classification capabilities without requiring a full RAG infrastructure.

## Features

- ✅ Reads JSON files (like `articles.json`)
- ✅ Extracts text from PDF files
- ✅ Automatically backs up your `prompt.txt` before modifying
- ✅ Prevents duplicate knowledge entries
- ✅ Interactive confirmation before changes
- ✅ Supports multilingual content (English, Arabic, Kurdish)

## Installation

First, install the required dependency:

```bash
pip install PyPDF2
```

Or if using Docker, rebuild your container:

```bash
docker-compose build cora-api
```

## Usage

### Basic Syntax

```bash
python3 append_knowledge.py <file_path>
```

### Examples

#### 1. Append JSON Articles

```bash
python3 append_knowledge.py data/jsons/articles.json
```

This will:

- Parse all articles from the JSON file
- Extract ID, app_name, title, and content in all languages
- Format them for the model
- Append to `prompt.txt`

#### 2. Append PDF Documentation

```bash
python3 append_knowledge.py "data/pdfs/app-docs/Rayied-Rayied Application Documentation.pdf"
```

This will:

- Extract text from all PDF pages
- Format the content
- Append to `prompt.txt`

## How It Works

### Step-by-Step Process

1. **File Detection**: Script detects file type (.json or .pdf)
2. **Content Extraction**:
   - JSON: Parses articles with all language variants
   - PDF: Extracts text page by page
3. **Formatting**: Structures content for model consumption
4. **Backup**: Creates `prompt.txt.backup` before modifying
5. **Preview**: Shows first 500 characters of extracted knowledge
6. **Confirmation**: Asks for user confirmation
7. **Append**: Inserts knowledge into `prompt.txt` before closing `"""`
8. **Restart Reminder**: Prompts you to restart the service

### Example Output

```
Processing file: data/jsons/articles.json
File type: .json

✓ Extracted 25847 characters of knowledge

--- Preview (first 500 chars) ---

### KNOWLEDGE BASE FROM JSON:

[Article ID: 17] [ana] reset password
EN: Open the app's main interface.

At the top of the screen, tap the options button.

A menu will appear containing the option "Change Password." Select this option.
...

Append this knowledge to prompt.txt? (y/n): y
✓ Backup created: prompt.txt.backup
✓ Knowledge appended to prompt.txt

✅ Success! Knowledge has been appended to the model.
The model will now use this information for classification.

Note: Restart the server for changes to take effect:
  docker-compose restart cora-api
```

## Important Notes

### ⚠️ Backup & Recovery

The script automatically creates a backup before modifying `prompt.txt`:

- Backup file: `prompt.txt.backup`
- To restore: `cp prompt.txt.backup prompt.txt`

### 🔄 Restart Required

After appending knowledge, you **must** restart the service:

```bash
docker-compose restart cora-api
```

Or if running locally:

```bash
# Stop the server (Ctrl+C)
# Then restart
python3 server.py
```

### 📊 Knowledge Format

**JSON Articles** are formatted as:

```
[Article ID: 17] [ana] reset password
EN: <english content>
AR: <arabic content>
KU: <kurdish content>
--------------------------------------------------------------------------------
```

**PDF Content** is formatted as:

```
### KNOWLEDGE BASE FROM PDF:
Source: Rayied-Rayied Application Documentation.pdf

--- Page 1 ---
<page 1 text>

--- Page 2 ---
<page 2 text>
...
```

## Advanced Usage

### Append Multiple Files

You can run the script multiple times to append different sources:

```bash
# First, append articles
python3 append_knowledge.py data/jsons/articles.json

# Then, append PDF documentation
python3 append_knowledge.py "data/pdfs/app-docs/Rayied-Rayied Application Documentation.pdf"

# Restart service
docker-compose restart cora-api
```

### Check Current Knowledge

To see what knowledge is currently in the prompt:

```bash
grep -A 20 "### KNOWLEDGE BASE" prompt.txt
```

### Remove Appended Knowledge

To remove all appended knowledge and restore original prompt:

```bash
# Restore from backup
cp prompt.txt.backup prompt.txt

# Restart service
docker-compose restart cora-api
```

## Troubleshooting

### Issue: "PyPDF2 not installed"

**Solution:**

```bash
pip install PyPDF2
```

### Issue: "File not found"

**Solution:** Check the file path. Use quotes for paths with spaces:

```bash
python3 append_knowledge.py "data/pdfs/my file.pdf"
```

### Issue: "Existing knowledge base found"

**Solution:** The script detected previous knowledge. You can:

- Type `y` to append anyway (will add duplicate)
- Type `n` to abort
- Manually edit `prompt.txt` to remove old knowledge first

### Issue: Changes not reflected in model

**Solution:** Make sure to restart the service:

```bash
docker-compose restart cora-api
```

## Best Practices

1. **Start Small**: Test with one file first
2. **Check Preview**: Always review the preview before confirming
3. **Keep Backups**: Don't delete `prompt.txt.backup`
4. **Monitor Size**: Large prompts may slow down inference
5. **Restart Service**: Always restart after appending knowledge

## Limitations

- **Context Window**: qwen2.5:7b has a 2048 token limit. Don't append too much knowledge.
- **No Semantic Search**: This is not full RAG - all knowledge is in the prompt
- **Manual Updates**: You need to re-run the script when files change

## Next Steps

For production use, consider implementing full RAG with:

- Vector database (ChromaDB)
- Semantic search
- Dynamic retrieval
- See the RAG implementation plan for details

## Support

If you encounter issues:

1. Check the backup file exists: `ls -la prompt.txt.backup`
2. Verify file paths are correct
3. Ensure PyPDF2 is installed
4. Check Docker logs: `docker-compose logs cora-api`
