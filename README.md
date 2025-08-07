# RAG LLM-Based Chatbot

A sophisticated RAG (Retrieval-Augmented Generation) chatbot system built with FastAPI, MCP (Model Context Protocol), LangChain, and PostgreSQL. This system provides a complete pipeline for query processing, answer generation, and conversation logging with a beautiful dashboard for monitoring.

## 🏗️ Architecture

The system consists of several microservices:

- **FastAPI Backend**: Main API server with async endpoints
- **MCP Server**: Provides FAQ resources and prompt templates
- **PostgreSQL**: Database for logging conversations
- **pgAdmin**: Database administration interface
- **Frontend Dashboard**: Vanilla HTML/CSS/JS monitoring interface

## 🌟 Features

- **Query Processing Pipeline**: 
  1. User query + conversation history → Query generation endpoint
  2. Refined query + FAQ content → Answer generation endpoint
- **MCP Integration**: Centralized resource and prompt management
- **LangChain Integration**: OpenAI LLM integration for query and answer generation
- **PostgreSQL Logging**: Complete conversation logging with timestamps
- **Real-time Dashboard**: Monitor conversations with filtering and search
- **Docker Compose**: Complete containerized deployment
- **Async Architecture**: High-performance async endpoints

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.11+ (for local development)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd rag-chatbot
```

### 2. Environment Configuration

Copy the example environment file and configure your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Start the System

```bash
docker-compose up --build
```

This will start all services:
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:3000
- **pgAdmin**: http://localhost:5050
- **PostgreSQL**: localhost:5432

### 4. Access the Services

- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **pgAdmin**: http://localhost:5050 (admin@example.com / admin)

## 📁 Project Structure

```
rag-chatbot/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # Main FastAPI app
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── database.py     # Database connection
│   │   └── services/       # Business logic services
│   ├── requirements.txt
│   └── Dockerfile
├── mcp_server/             # MCP server
│   ├── server.py          # MCP server implementation
│   ├── resources/
│   │   └── faq.txt        # FAQ content
│   ├── prompts/           # Prompt templates
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # Dashboard
│   ├── index.html        # Main HTML
│   ├── style.css         # Styling
│   ├── script.js         # JavaScript functionality
│   ├── nginx.conf        # Nginx configuration
│   └── Dockerfile
├── docker-compose.yml    # Complete system orchestration
├── init.sql             # Database initialization
├── .env.example         # Environment template
└── README.md           # This file
```

## 🔄 API Endpoints

### Core Endpoints

#### POST `/query_generate`
Generate refined query from user input and conversation history.

```json
{
  "user_query": "How do I reset my password?",
  "conversation_history": [
    {
      "role": "user",
      "content": "I'm having trouble logging in",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### POST `/answer_generate`
Generate answer from refined query and FAQ content.

```json
{
  "refined_query": "How can I reset my account password?",
  "original_query": "How do I reset my password?",
  "conversation_history": []
}
```

#### POST `/chat`
Complete pipeline: query generation + answer generation + logging.

```json
{
  "user_query": "What are your business hours?",
  "conversation_history": []
}
```

### Monitoring Endpoints

#### GET `/messages`
Retrieve logged messages with filtering options.

Query parameters:
- `limit`: Number of messages (default: 100)
- `offset`: Pagination offset (default: 0)
- `conversation_id`: Filter by conversation ID

#### GET `/messages/count`
Get total count of logged messages.

#### GET `/health`
Health check endpoint.

## 🎨 Dashboard Features

The frontend dashboard provides:

- **Real-time Statistics**: Total messages, today's messages, active conversations
- **Message History Table**: Sortable and filterable conversation logs
- **Search Functionality**: Search across queries and answers
- **Conversation Filtering**: Filter by conversation ID or date
- **Message Details Modal**: View complete message information
- **Responsive Design**: Works on desktop and mobile devices

## 🗄️ Database Schema

### `message_logs` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `user_query` | TEXT | Original user question |
| `refined_query` | TEXT | LLM-refined query |
| `answer` | TEXT | Generated answer |
| `conversation_id` | VARCHAR(100) | Conversation identifier |
| `timestamp` | TIMESTAMP | Message timestamp |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DATABASE_URL` | PostgreSQL connection string | See docker-compose.yml |
| `MCP_SERVER_URL` | MCP server URL | http://mcp_server:8001 |

### Customizing FAQ Content

Edit `mcp_server/resources/faq.txt` to customize the FAQ content for your use case.

### Customizing Prompts

Edit the prompt templates in `mcp_server/prompts/`:
- `query_generate.txt`: Query refinement prompt
- `answer_generate.txt`: Answer generation prompt

## 🔨 Development

### Local Development Setup

1. **Backend Development**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **MCP Server Development**:
```bash
cd mcp_server
pip install -r requirements.txt
python server.py
```

3. **Frontend Development**:
Serve the frontend directory with any static file server.

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
# Open index.html in browser for manual testing
```

## 📊 Monitoring and Logging

- **Application Logs**: Check Docker logs for each service
- **Database Monitoring**: Use pgAdmin interface
- **API Monitoring**: Built-in FastAPI documentation at `/docs`
- **Health Checks**: Use `/health` endpoint for service monitoring

## 🔒 Security Considerations

- Change default passwords in production
- Configure proper CORS origins
- Use HTTPS in production
- Secure OpenAI API key storage
- Implement proper authentication for production use

## 🚀 Production Deployment

For production deployment:

1. **Update Environment Variables**:
   - Use strong, unique passwords
   - Configure proper database credentials
   - Set production CORS origins

2. **SSL/TLS Configuration**:
   - Configure HTTPS for all services
   - Use proper SSL certificates

3. **Scaling Considerations**:
   - Use managed PostgreSQL service
   - Configure load balancer for backend
   - Use CDN for frontend assets

4. **Monitoring**:
   - Set up application monitoring
   - Configure log aggregation
   - Set up alerts for service health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Ensure `OPENAI_API_KEY` is set in your `.env` file

**"Database connection failed"**
- Wait for PostgreSQL to fully start (check `docker-compose logs postgres`)
- Verify database credentials in docker-compose.yml

**"MCP server not responding"**
- Check MCP server logs: `docker-compose logs mcp_server`
- Ensure MCP server container is running

**"Frontend can't connect to backend"**
- Verify backend is running on port 8000
- Check CORS configuration in FastAPI

### Getting Help

1. Check the logs: `docker-compose logs [service_name]`
2. Verify all services are running: `docker-compose ps`
3. Check the health endpoints
4. Review the configuration files

---

Built with ❤️ using FastAPI, MCP, LangChain, and PostgreSQL.