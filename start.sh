#!/bin/bash

# RAG Chatbot Startup Script

echo "🤖 Starting RAG Chatbot System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OPENAI_API_KEY before running again."
    echo "   Example: OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Please set your OPENAI_API_KEY in the .env file"
    echo "   Example: OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

echo "🔧 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "🎉 System started successfully!"
echo ""
echo "📋 Available Services:"
echo "   🌐 Frontend Dashboard: http://localhost:3000"
echo "   🔗 Backend API:        http://localhost:8000"
echo "   📚 API Documentation:  http://localhost:8000/docs"
echo "   🗃️  pgAdmin:           http://localhost:5050"
echo ""
echo "📊 pgAdmin Login:"
echo "   Email:    admin@example.com"
echo "   Password: admin"
echo ""
echo "📝 To view logs: docker-compose logs [service_name]"
echo "🛑 To stop:      docker-compose down"
echo ""
echo "🚀 Your RAG Chatbot is ready!"