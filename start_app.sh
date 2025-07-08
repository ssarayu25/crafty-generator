#!/bin/bash

echo "🧶 Starting Yarn Master Application..."

# Start the FastAPI backend
echo "🚀 Starting backend server..."
cd fastapi-template
python3 -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the React frontend
echo "🎨 Starting frontend server..."
cd ../crochet-decoder
npm start &
FRONTEND_PID=$!

echo "✨ Yarn Master is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8081"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Shutting down Yarn Master..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait