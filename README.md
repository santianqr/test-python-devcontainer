# WhatsApp AI Assistant

FastAPI application with LangChain + OpenAI for WhatsApp message responses with PostgreSQL + pgvector for conversational memory and vector search.

## Features

- FastAPI REST API
- LangChain + OpenAI integration
- PostgreSQL + pgvector for persistence and vector search
- Conversational memory per chat
- Business knowledge base with embeddings
- Custom tools for property management

## Quick Start

### 1. Start PostgreSQL
```bash
docker-compose up -d
```

### 2. Install dependencies
```bash
pip install uv
uv sync --extra dev --extra ds
```

### 3. Configure environment
```bash
cp env_example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Initialize database
```bash
uv run python init_db.py
```

### 5. Run application
```bash
uv run python main.py
```

Visit: http://localhost:8000/docs

## Database

- **Host**: localhost:5432
- **User**: postgres
- **Password**: postgres123
- **Database**: whatsapp_ai

## API Endpoints

- `GET /` - API info
- `POST /chat` - Send message to AI
- `GET /health` - Health check
- `GET /test` - Test endpoint

## Development

```bash
# Check database connection
uv run python -c "from database import test_connection; print(test_connection())"

# Linting
uv run ruff check .
uv run black .
uv run mypy .
```