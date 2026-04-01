#!/bin/bash
set -e

echo "Setting up Life Insurance Agent..."

# Check for .env file
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"
    else
        echo "Creating default .env..."
        cat > .env << 'EOF'
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=
DEBUG=true
LOG_LEVEL=INFO
EOF
        echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"
    fi
fi

# Python setup
if command -v python3 &> /dev/null; then
    echo "Setting up Python environment..."
    if command -v uv &> /dev/null; then
        echo "Using uv to sync dependencies..."
        uv sync
    else
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        source .venv/bin/activate
        pip install -r requirements.txt
    fi
fi

# Frontend setup
if [ -d "frontend" ]; then
    echo "Setting up frontend..."
    cd frontend
    if command -v npm &> /dev/null; then
        npm install
    else
        echo "⚠️  npm not found, skipping frontend setup"
    fi
    cd ..
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the backend:"
echo "  uv run uvicorn main:app --reload"
echo ""
echo "To run the frontend (in separate terminal):"
echo "  cd frontend && npm run dev"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"