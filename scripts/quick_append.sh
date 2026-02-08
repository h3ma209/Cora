#!/bin/bash
# Quick helper script to append knowledge and restart service

echo "🚀 Cora Knowledge Appender Helper"
echo "=================================="
echo ""

# Check if file argument provided
if [ $# -eq 0 ]; then
    echo "Usage: ./quick_append.sh <file_path>"
    echo ""
    echo "Examples:"
    echo "  ./quick_append.sh data/jsons/articles.json"
    echo "  ./quick_append.sh 'data/pdfs/app-docs/Rayied-Rayied Application Documentation.pdf'"
    exit 1
fi

FILE_PATH="$1"

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "❌ Error: File not found - $FILE_PATH"
    exit 1
fi

echo "📄 File: $FILE_PATH"
echo ""

# Run the Python script
python3 append_knowledge.py "$FILE_PATH"

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🔄 Restarting Cora service..."
    docker-compose restart cora-api
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ All done! Your model now has the new knowledge."
        echo ""
        echo "Test it with:"
        echo "  curl -X POST http://localhost:8001/classify -H 'Content-Type: application/json' -d '{\"text\": \"your test query\"}'"
    else
        echo "⚠️  Warning: Failed to restart service. Run manually:"
        echo "  docker-compose restart cora-api"
    fi
else
    echo ""
    echo "❌ Failed to append knowledge. Check the error above."
fi
