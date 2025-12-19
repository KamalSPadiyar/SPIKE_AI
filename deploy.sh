#!/bin/bash

# SPIKE AI Backend Deployment Script
# Production-ready deployment for evaluator environments

set -e  # Exit on any error

echo "🚀 Starting SPIKE AI Backend Deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check Python version
print_step "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    print_error "Python not found. Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_status "Found Python $PYTHON_VERSION"

# Verify Python version is 3.8+
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ required. Found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
print_step "Creating virtual environment..."
if [ -d ".venv" ]; then
    print_warning "Virtual environment already exists. Removing and recreating..."
    rm -rf .venv
fi

$PYTHON_CMD -m venv .venv
print_status "Virtual environment created"

# Activate virtual environment
print_step "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash/MSYS)
    source .venv/Scripts/activate
else
    # Unix-like systems
    source .venv/bin/activate
fi
print_status "Virtual environment activated"

# Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip
print_status "Pip upgraded"

# Install dependencies
print_step "Installing dependencies..."
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please ensure you're in the correct directory."
    exit 1
fi

pip install -r requirements.txt
print_status "Dependencies installed successfully"

# Verify critical dependencies
print_step "Verifying critical dependencies..."
$PYTHON_CMD -c "import fastapi; print('FastAPI:', fastapi.__version__)" || {
    print_error "FastAPI not installed correctly"
    exit 1
}

$PYTHON_CMD -c "import google.analytics.data_v1beta; print('GA4 client: OK')" || {
    print_warning "GA4 client may not be available (check credentials later)"
}

$PYTHON_CMD -c "import litellm; print('LiteLLM:', litellm.__version__)" || {
    print_warning "LiteLLM may not be available (check API keys later)"
}

print_status "Dependency verification complete"

# Check for credentials file
print_step "Checking credentials..."
if [ ! -f "credentials.json" ]; then
    print_warning "credentials.json not found. Creating placeholder..."
    print_warning "⚠️  Replace with actual GA4 service account credentials before running!"
else
    # Basic JSON validation
    $PYTHON_CMD -c "import json; json.load(open('credentials.json'))" 2>/dev/null || {
        print_warning "credentials.json appears to be invalid JSON"
    }
    print_status "credentials.json found"
fi

# Check for optional SEO data
print_step "Checking optional files..."
if [ ! -f "screamingfrog.csv" ]; then
    print_warning "screamingfrog.csv not found. SEO agent will use sample data."
else
    print_status "SEO data file found"
fi

# Test application startup
print_step "Testing application startup..."
timeout 10 $PYTHON_CMD -c "
from app.main import app
from app.orchestrator import Orchestrator
print('✅ Application imports successful')
" || {
    print_error "Application startup test failed"
    exit 1
}
print_status "Application startup test passed"

# Set environment variables (if .env file exists)
if [ -f ".env" ]; then
    print_step "Loading environment variables from .env..."
    set -a
    source .env
    set +a
    print_status "Environment variables loaded"
else
    print_warning ".env file not found. Using default configuration."
fi

# Determine host and port
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-"8080"}

print_step "Starting SPIKE AI Backend server..."
print_status "🌐 Server will be available at: http://$HOST:$PORT"
print_status "📚 API Documentation: http://$HOST:$PORT/docs"
print_status "🔍 Health Check: http://$HOST:$PORT/health"
print_status ""
print_status "🚀 Starting server..."

# Start the server
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload &

# Store the server PID
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Test health endpoint
print_step "Testing server health..."
if command -v curl &> /dev/null; then
    if curl -f -s "http://$HOST:$PORT/health" > /dev/null; then
        print_status "✅ Server health check passed"
    else
        print_warning "❌ Server health check failed (server may still be starting)"
    fi
else
    print_warning "curl not available for health check"
fi

echo ""
print_status "🎉 SPIKE AI Backend deployment complete!"
echo ""
print_status "Next steps:"
echo "  1. Replace credentials.json with your actual GA4 service account file"
echo "  2. (Optional) Add screamingfrog.csv for SEO analysis"
echo "  3. Set OPENAI_API_KEY environment variable for LLM features"
echo "  4. Visit http://$HOST:$PORT/docs to explore the API"
echo ""
print_status "Example API call:"
echo '  curl -X POST http://'$HOST':'$PORT'/query \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '\''{"query": "Show me users from last week", "propertyId": "123456789"}'\'''
echo ""

# Keep server running
print_status "Server running with PID: $SERVER_PID"
print_status "Press Ctrl+C to stop the server"

# Wait for the server process
wait $SERVER_PID