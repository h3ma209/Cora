#!/bin/bash
# RAG Setup Automation Script for Cora AI

echo "============================================================"
echo "🚀 Cora RAG System Setup"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo "📋 Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"
echo ""

# Step 2: Install dependencies
echo "📦 Step 2: Installing dependencies..."
echo "This may take a few minutes (downloading ~500MB)..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 3: Check data directory
echo "📁 Step 3: Checking data directory..."
if [ ! -d "./data" ]; then
    echo -e "${YELLOW}⚠️  Data directory not found${NC}"
    echo "Creating data directory structure..."
    mkdir -p data/jsons data/pdfs
    echo -e "${GREEN}✓ Created data directories${NC}"
else
    echo -e "${GREEN}✓ Data directory exists${NC}"
fi
echo ""

# Step 4: Index knowledge base
echo "🔍 Step 4: Indexing knowledge base..."
echo "This will scan data/jsons and data/pdfs..."
echo ""

python3 indexer.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Knowledge base indexed${NC}"
else
    echo ""
    echo -e "${RED}❌ Indexing failed${NC}"
    echo "Check the error above and try again"
    exit 1
fi
echo ""

# Step 5: Test RAG system
echo "🧪 Step 5: Testing RAG system..."
echo ""

python3 test_rag.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ RAG system tests passed${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed, but you can still proceed${NC}"
fi
echo ""

# Step 6: Summary
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Your Cora RAG system is ready to use!"
echo ""
echo "Next steps:"
echo ""
echo "1. Test locally:"
echo "   python3 cora.py"
echo ""
echo "2. Start the API server:"
echo "   python3 server.py"
echo ""
echo "3. Deploy with Docker:"
echo "   docker-compose build"
echo "   docker-compose up -d"
echo "   docker-compose exec cora-api python3 indexer.py"
echo ""
echo "4. Test the API:"
echo "   curl -X POST http://localhost:8001/classify \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"how to reset password\"}'"
echo ""
echo "📚 Documentation:"
echo "   - RAG_SETUP_GUIDE.md - Complete setup guide"
echo "   - QUICK_START.md - Quick reference"
echo ""
echo "🆘 Need help?"
echo "   - Check logs: docker-compose logs cora-api"
echo "   - View stats: python3 indexer.py --stats"
echo "   - Test RAG: python3 test_rag.py"
echo ""
