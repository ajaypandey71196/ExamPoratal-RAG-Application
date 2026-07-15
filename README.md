# Exam RAG Portal Backend



## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment   Variables
Create `.env` file:
```
DATABASE_URL=postgresql://rag_user:rag_password_dev@localhost:5432/rag_db
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_key_here
ENVIRONMENT=development
```

### 3. Run with Docker Compose
```bash
docker-compose up -d
```

### 4. Check Services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant UI: http://localhost:6333/dashboard

### 5. Run Migrations
```bash
docker-compose exec backend alembic upgrade head
```

## Project Structure
```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── models.py      # Database models
│   ├── database.py    # Database config
│   ├── config.py      # Settings
│   ├── main.py        # FastAPI app
│   └── utils/         # Utilities
├── tests/             # Tests
└── requirements.txt   # Dependencies
```

## Development

### Run Backend Only
```bash
cd backend
uvicorn app.main:app --reload
```

### Run Tests
```bash
pytest
```
