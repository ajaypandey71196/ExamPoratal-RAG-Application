# DEVELOPMENT GUIDE - Phase 1 Progress

## Current Status (2026-07-14)

### ✅ Completed Components

#### 1. **Backend Infrastructure**
- FastAPI application boilerplate
- Docker & docker-compose setup for all services
- PostgreSQL database with ORM models
- Configuration management system
- Health check endpoint

#### 2. **Authentication & Authorization**
- JWT token generation and validation
- User registration and login
- Password hashing with bcrypt
- User profile management

#### 3. **Database Models**
- User model with settings
- Document model with chunks
- Exam model with questions
- All relationships and constraints defined

#### 4. **Core Services (Ready to Use)**
- **DocumentProcessor**: Extract text from PDF, DOCX, TXT, XLSX files
- **TextChunker**: Split text into overlapping chunks
- **EmbeddingsService**: Generate embeddings using sentence-transformers (local, no API costs)
- **QdrantService**: Vector database client for storage and retrieval
- **LLMService**: Multi-provider LLM support (OpenAI, Cohere, HuggingFace, Ollama)
- **RAGEngine**: Retrieval-Augmented Generation for fetching relevant context
- **ExamGenerationService**: Generate exams using RAG + LLM

#### 5. **Frontend Scaffolding**
- React app with React Router
- Chakra UI components
- Pages: Home, Login, Register, Dashboard, ExamGenerator
- Navigation component with auth state management

### ⏳ Remaining Tasks for Phase 1

#### 1. **Document Upload API & Integration**
**File:** `backend/app/api/documents.py`
**Tasks:**
- Implement multipart file upload endpoint
- Integrate with DocumentProcessor
- Store file metadata in PostgreSQL
- Trigger embedding generation after upload
- Return processing status to frontend

**Example code:**
```python
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Save file
    # Extract text using DocumentProcessor
    # Chunk text using TextChunker
    # Generate embeddings
    # Store in Qdrant
    # Save metadata in PostgreSQL
```

#### 2. **Internet Scraping Service** 
**File:** `backend/app/services/internet_scraper.py` (TODO)
**Tasks:**
- Implement Google/DuckDuckGo search
- Wikipedia API integration
- ArXiv API for research papers
- GitHub API for code/docs
- Rate limiting and deduplication
- Store results in PostgreSQL

#### 3. **Exam Generation Endpoints**
**File:** `backend/app/api/exams.py`
**Tasks:**
- POST `/generate` - Trigger exam generation
- GET `/{exam_id}` - Retrieve generated exam
- POST `/regenerate` - Regenerate specific questions
- Include follow-up questions form

#### 4. **Frontend: Exam Generator Page**
**File:** `frontend/src/pages/ExamGenerator.jsx`
**Tasks:**
- Document upload UI with drag & drop
- Follow-up questions form with all options
- LLM configuration (model selection, API key input)
- Custom prompt editor
- Generation progress indicator
- Display generated exam

#### 5. **Testing & Debugging**
- Test all services in isolation
- Test end-to-end flow (upload → embed → retrieve → generate)
- Debug issues with Docker containers
- Set up logging and monitoring

### 📁 Project Structure Overview

```
exam-rag-portal/
├── backend/
│   ├── app/
│   │   ├── main.py                    # ✅ FastAPI app
│   │   ├── config.py                  # ✅ Settings
│   │   ├── database.py                # ✅ Database setup
│   │   ├── models.py                  # ✅ SQLAlchemy models
│   │   ├── api/
│   │   │   ├── auth.py                # ✅ Authentication endpoints
│   │   │   ├── users.py               # ✅ User management
│   │   │   ├── documents.py           # 🚧 TODO: Full implementation
│   │   │   └── exams.py               # 🚧 TODO: Full implementation
│   │   ├── services/
│   │   │   ├── document_processor.py  # ✅ Text extraction & chunking
│   │   │   ├── embeddings.py          # ✅ Embedding generation
│   │   │   ├── qdrant_service.py      # ✅ Vector DB client
│   │   │   ├── llm_service.py         # ✅ Multi-provider LLM
│   │   │   ├── rag_engine.py          # ✅ Retrieval engine
│   │   │   ├── exam_generator.py      # ✅ Exam generation
│   │   │   └── internet_scraper.py    # 🚧 TODO: Create
│   │   └── utils/
│   │       └── security.py            # ✅ JWT utilities
│   ├── requirements.txt               # ✅ Dependencies
│   └── Dockerfile                     # ✅ Docker config
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # ✅ Main app
│   │   ├── index.jsx                  # ✅ Entry point
│   │   ├── pages/
│   │   │   ├── Home.jsx               # ✅ Home page
│   │   │   ├── Login.jsx              # ✅ Login page
│   │   │   ├── Register.jsx           # ✅ Register page
│   │   │   ├── Dashboard.jsx          # 🚧 TODO: Implement
│   │   │   └── ExamGenerator.jsx      # 🚧 TODO: Implement
│   │   ├── components/
│   │   │   └── Navigation.jsx         # ✅ Navigation
│   │   └── services/                  # 🚧 TODO: API client services
│   ├── package.json                   # ✅ Dependencies
│   ├── Dockerfile                     # ✅ Docker config
│   └── vite.config.js                 # ✅ Vite config
│
├── docker-compose.yml                 # ✅ Multi-container setup
├── .env.example                       # ✅ Environment template
├── .gitignore                         # ✅ Git ignore
├── README.md                          # ✅ Setup guide
├── PROJECT_PLAN.md                    # ✅ Detailed plan
└── DEVELOPMENT.md                     # 📄 This file

```

### 🚀 How to Continue Development

#### **Step 1: Run Docker Containers**
```bash
cd /path/to/testing-rag
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Qdrant (port 6333, UI at 6333/dashboard)
- Redis (port 6379)
- FastAPI backend (port 8000, docs at /docs)
- React frontend (port 3000)

#### **Step 2: Check Services Health**
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### **Step 3: Test API**
```bash
# Health check
curl http://localhost:8000/health

# API docs (interactive)
http://localhost:8000/docs
```

#### **Step 4: Implement Missing Endpoints**

**Priority Order:**
1. **Document Upload** - Required for MVP
2. **Exam Generation** - Core feature
3. **Internet Scraping** - Enhance capability

### 🔧 Key Service Usage Examples

#### **Using DocumentProcessor**
```python
from app.services.document_processor import DocumentProcessor, TextChunker

# Extract text from file
text = DocumentProcessor.extract_text("/path/to/file.pdf")

# Chunk text
chunks = TextChunker.chunk_text(text, chunk_size=500, overlap=50)
```

#### **Using EmbeddingsService**
```python
from app.services.embeddings import get_embeddings_service

embeddings_svc = get_embeddings_service()

# Generate embedding for single text
embedding = embeddings_svc.embed_text("Your text here")

# Batch embeddings
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = embeddings_svc.embed_texts(texts)
```

#### **Using QdrantService**
```python
from app.services.qdrant_service import get_qdrant_service
from qdrant_client.models import PointStruct

qdrant = get_qdrant_service("http://localhost:6333")

# Create collection
qdrant.create_collection("documents", vector_size=384)

# Upsert vectors
points = [
    PointStruct(
        id="unique-id",
        vector=[0.1, 0.2, 0.3, ...],  # 384 dims
        payload={"text": "Your text", "source": "document1"}
    )
]
qdrant.upsert_vectors("documents", points)

# Search
results = qdrant.search_vectors("documents", query_vector, limit=5)
```

#### **Using LLMService**
```python
from app.services.llm_service import LLMService

# Initialize with OpenAI
llm = LLMService("openai", api_key="sk-...", model="gpt-3.5-turbo")

# Generate text
response = llm.generate(
    prompt="Generate 5 MCQ questions about machine learning",
    temperature=0.7,
    max_tokens=1024,
    system_message="You are an expert exam creator"
)
```

#### **Using RAGEngine**
```python
from app.services.rag_engine import RAGEngine

rag = RAGEngine(qdrant_service)

# Retrieve relevant context
results = rag.retrieve_context(
    query="What is machine learning?",
    top_k=5,
    user_id="user-123"
)

# Combine context
context, sources = rag.combine_context(results)
```

#### **Using ExamGenerationService**
```python
from app.services.exam_generator import ExamGenerationService

exam_gen = ExamGenerationService(rag_engine, llm_service)

exam = exam_gen.generate_exam(
    topic="Machine Learning Basics",
    user_id="user-123",
    question_type="MCQ",
    difficulty_level="intermediate",
    num_questions=10,
    custom_instructions="Include practical examples"
)
```

### 📊 Data Flow Diagram

```
User Upload
    ↓
DocumentProcessor (Extract Text)
    ↓
TextChunker (Split into chunks)
    ↓
EmbeddingsService (Generate vectors)
    ↓
Qdrant (Store vectors + metadata)
    ↓
PostgreSQL (Store document metadata)

---

User Exam Request
    ↓
RAGEngine (Retrieve relevant context)
    ├→ Qdrant Search (Semantic)
    └→ PostgreSQL Query (Metadata filtering)
    ↓
LLMService (Generate questions)
    ├→ OpenAI / Cohere / HuggingFace / Ollama
    ↓
ExamGenerationService (Parse & validate)
    ↓
Return to User
```

### 📝 Environment Variables Needed

Create a `.env` file in project root:
```
ENVIRONMENT=development
DATABASE_URL=postgresql://rag_user:rag_password_dev@postgres:5432/rag_db
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=dev-secret-key-change-in-prod
```

### 🧪 Testing Commands

```bash
# Test individual services
python -c "from app.services.embeddings import get_embeddings_service; svc = get_embeddings_service(); print('✅ Embeddings service working')"

# Run API tests
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"pass123"}'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'
```

### 🐛 Common Issues & Solutions

#### **Issue: "Connection refused" for Qdrant**
- **Solution:** Ensure Qdrant container is running: `docker-compose logs qdrant`
- Check if port 6333 is accessible

#### **Issue: "No module named" for libraries**
- **Solution:** Reinstall requirements: `pip install -r backend/requirements.txt`
- Rebuild Docker: `docker-compose build --no-cache`

#### **Issue: Embeddings service slow**
- **Solution:** It's downloading the model on first use (~350MB)
- Check GPU availability for faster processing

#### **Issue: LLM API errors**
- **Solution:** Verify API keys are correct
- Check rate limits on provider

### 📚 Next Steps After Phase 1

1. **Phase 2**: Multi-provider support, internet scraping, follow-up questions form
2. **Phase 3**: Student assessment, analytics, community features
3. **Phase 4**: Production hardening, security, compliance

---

**Last Updated:** 2026-07-14
**Status:** Phase 1 - Core Infrastructure Complete ✅

