#!/bin/bash

echo "🧶 Starting Yarn Master - AI-Powered Crochet Pattern Generator"
echo "=================================================="

# Check if Python virtual environment exists
if [ ! -d "fastapi-template/.venv310" ]; then
    echo "❌ Python virtual environment not found. Please set up the backend first."
    echo "Run: cd fastapi-template && python -m venv .venv310 && source .venv310/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if Node modules exist
if [ ! -d "crochet-decoder/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd crochet-decoder
    npm install
    cd ..
fi

echo "🚀 Starting backend server..."
cd fastapi-template
source .venv310/bin/activate
export GEMINI_API_KEY=$(cat ../.env | grep GEMINI_API_KEY | cut -d'=' -f2)
uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🎨 Starting frontend server..."
cd crochet-decoder
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Yarn Master is now running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "👋 Yarn Master stopped. Happy crocheting!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait