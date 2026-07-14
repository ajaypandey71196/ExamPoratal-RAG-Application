# EXAM PORTAL + RAG APPLICATION - COMPLETE PROJECT PLAN

**Last Updated:** 2026-07-14
**Status:** Planning Phase - MVP Development
**Owner:** Personal Project (10 Testing Users)

---

## 1. PROJECT OVERVIEW

### 1.1 What is this project?
A **production-ready Exam Generation Portal** powered by **Retrieval-Augmented Generation (RAG)** that:
- Takes user input (topic/subject)
- Scrapes data from internet sources (blogs, websites, LinkedIn, books, interview experiences)
- Combines with user-uploaded documents
- Generates dynamic exams based on user requirements
- Allows users to customize LLM models and prompts

### 1.2 Core Purpose
Enable users to create customized exams and training materials by leveraging:
1. **Their own data** (uploaded documents)
2. **Internet resources** (open-source content)
3. **User-submitted experiences** (interviews, recruiter insights)
4. **LLM-powered generation** with full customization control

### 1.3 Target Users
- **Students** preparing for interviews/certifications
- **Recruiters** creating interview question banks
- **Content creators** building training materials
- **HR teams** designing assessment exams

### 1.4 Deployment Model
- **Self-hosted on AWS EC2** (user's responsibility)
- **10 testing users** initially
- **Link-based sharing** to other users
- **Future:** SaaS model possible after MVP validation

---

## 2. TECH STACK (100% OPEN SOURCE & FREE)

### 2.1 Backend
- **Framework:** FastAPI (Python 3.10+)
- **API Server:** Uvicorn
- **Async Processing:** Celery + Redis (optional, for future scaling)

### 2.2 Databases
- **Vector Database:** Qdrant (self-hosted, Docker)
  - Stores embeddings of all content chunks
  - Metadata storage for retrieval tracking
- **Metadata Database:** PostgreSQL
  - User data, documents, exams, questions, logs
  - Structured data storage
- **Cache:** Redis (optional, for API rate limiting and caching)

### 2.3 Embeddings & LLM
- **Embeddings Model:** sentence-transformers (local, free)
  - `all-MiniLM-L6-v2` (384 dimensions) - lightweight
  - Runs locally, no API costs
- **LLM Providers** (user selectable):
  - **Local:** Ollama (free, offline)
  - **API:** OpenAI (free tier), Cohere (free tier), HuggingFace (free tier)
  - **User control:** Change models and API keys anytime

### 2.4 Frontend
- **Framework:** React 18 (TypeScript recommended)
- **State Management:** Redux Toolkit or Zustand
- **UI Components:** Chakra UI or Material-UI (free)
- **HTTP Client:** Axios
- **Build Tool:** Vite (faster than Create React App)

### 2.5 Data Scraping & Processing
- **Web Scraping:** BeautifulSoup 4 + Requests
- **Advanced Scraping:** Selenium (for JavaScript-heavy sites like LinkedIn)
- **PDF Processing:** PyPDF2 + pdfplumber
- **Document Parsing:** python-docx, openpyxl
- **HTML Parsing:** LXML, html2text

### 2.6 Search & Retrieval
- **Full-text Search:** BM25 (keyword-based, built-in)
- **Semantic Search:** Qdrant (vector similarity)
- **Hybrid Search:** Combine BM25 + semantic results
- **Re-ranking:** Optional cross-encoder models

### 2.7 Infrastructure & Deployment
- **Containerization:** Docker + Docker Compose
- **Container Orchestration:** Kubernetes (optional, for future)
- **Cloud Provider:** AWS
  - EC2 (t3.small or t3.medium)
  - S3 (for file storage, optional)
  - RDS (PostgreSQL, optional - use EC2 local for MVP)
- **CI/CD:** GitHub Actions (free tier)
- **Monitoring:** OpenTelemetry + Self-hosted Prometheus (future)

---

## 3. SYSTEM ARCHITECTURE

### 3.1 High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (React)                   │
│  - Login/Register                                           │
│  - Document Upload                                          │
│  - Internet Search Configuration                            │
│  - Exam Generation Form with Follow-up Questions            │
│  - Prompt & LLM Model Selection                             │
│  - Generated Exam Display & Evaluation                      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              BACKEND API SERVER (FastAPI)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Authentication & Authorization (JWT)                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Document Processing Pipeline                         │  │
│  │  - File Upload Handler                              │  │
│  │  - PDF/Document Parser                              │  │
│  │  - Text Chunker                                      │  │
│  │  - Embedding Generator (local)                       │  │
│  │  - Qdrant Storage                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Internet Data Scraper                                │  │
│  │  - Google Search Query Builder                       │  │
│  │  - Website Scraper (BeautifulSoup)                   │  │
│  │  - LinkedIn Scraper (Selenium-based)                 │  │
│  │  - Multiple Source Aggregator                        │  │
│  │  - Content Deduplication                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ RAG Retrieval Engine                                 │  │
│  │  - Qdrant Vector Search                              │  │
│  │  - BM25 Keyword Search                               │  │
│  │  - Hybrid Search Orchestrator                        │  │
│  │  - Context Ranking & Selection                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ LLM Integration Layer                                │  │
│  │  - Provider Router (OpenAI/Cohere/HuggingFace/Ollama)│  │
│  │  - Prompt Template Manager                           │  │
│  │  - API Key Management (user-provided)                │  │
│  │  - Model Switching Logic                             │  │
│  │  - Response Processing                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Exam Generation Engine                               │  │
│  │  - Question Generation from Context                  │  │
│  │  - Answer Key Creation                               │  │
│  │  - Difficulty Calibration                            │  │
│  │  - Format Validation                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Database Interface Layer                             │  │
│  │  - PostgreSQL ORM (SQLAlchemy)                       │  │
│  │  - Qdrant Client                                     │  │
│  │  - Transaction Management                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────┬──────────────────┬──────────────────┬──────────────────┘
     │                  │                  │
┌────▼──────┐    ┌──────▼─────┐    ┌──────▼──────┐
│ PostgreSQL│    │   Qdrant   │    │    Redis    │
│ (Metadata)│    │  (Vectors) │    │   (Cache)   │
└───────────┘    └────────────┘    └─────────────┘

┌──────────────────────────────────────────────────────────────┐
│           EXTERNAL SERVICES (User-Provided)                  │
│  - OpenAI API (gpt-3.5-turbo, gpt-4)                         │
│  - Cohere API                                                │
│  - HuggingFace API                                           │
│  - Ollama (Local LLM)                                        │
│  - Internet Search (Google, DuckDuckGo, Wikipedia, Arxiv)    │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow for Exam Generation
```
USER INPUT
├── Topic/Subject
├── Document Uploads (optional)
├── Internet Search Scope
├── Follow-up Answers (exam format preferences)
│   ├── Question Type (MCQ, Short Answer, Essay, Coding)
│   ├── Difficulty Level (Beginner, Intermediate, Advanced)
│   ├── Number of Questions
│   └── Custom Requirements
└── LLM Configuration
    ├── Model Selection (OpenAI/Cohere/Ollama)
    ├── API Key (if using paid service)
    └── Custom Prompt (optional)
           │
           ▼
DATA RETRIEVAL PHASE
├── 1. Embed User's Documents (if uploaded)
│   └── Store in Qdrant with metadata
│
├── 2. Internet Data Collection
│   ├── Query: Google/DuckDuckGo with topic
│   ├── Scrape: Top 10-20 results
│   ├── Parse: Extract main content
│   └── Store: Add to Qdrant + temporary storage
│
└── 3. User-Submitted Resources (future)
    ├── Interview experiences
    ├── Recruiter insights
    └── Study materials
           │
           ▼
RETRIEVAL & RANKING PHASE
├── 1. Query: Generate search queries from topic + requirements
├── 2. Semantic Search: Query Qdrant with embeddings
├── 3. Keyword Search: BM25 search on stored documents
├── 4. Combine & Rank: Merge results, rank by relevance
└── 5. Context Selection: Pick top-K chunks for LLM context
           │
           ▼
LLM PROCESSING PHASE
├── 1. Build Prompt:
│   ├── System Prompt (from user's template or default)
│   ├── Context (retrieved chunks)
│   ├── Instructions (exam format requirements)
│   └── Examples (optional)
│
├── 2. Call LLM:
│   └── Send to selected provider (OpenAI/Cohere/Ollama)
│
└── 3. Parse Response:
    ├── Extract questions in JSON format
    ├── Validate structure
    └── Enrich with metadata
           │
           ▼
EXAM STORAGE & DELIVERY
├── 1. Save to PostgreSQL:
│   ├── Exam metadata
│   ├── Questions & answers
│   ├── Retrieved sources
│   └── Generation timestamp
│
└── 2. Return to User:
    ├── Display in UI
    ├── Generate shareable link
    └── Options to regenerate or refine
```

---

## 4. DETAILED FEATURE SPECIFICATION

### 4.1 Core Features (MVP)

#### 4.1.1 User Management
- **Registration & Login**
  - Email-based authentication
  - JWT tokens for session management
  - Password hashing (bcrypt)
  - Optional: Social login (Google, GitHub)

- **User Profile**
  - Custom API keys storage (encrypted)
  - LLM model preferences
  - Default prompt templates
  - Document quotas (for free tier)

#### 4.1.2 Document Management
- **Upload Capabilities**
  - Supported formats: PDF, DOCX, TXT, PPTX, XLSX, MD
  - File size limit: 50MB per file (configurable)
  - Bulk upload support
  - Drag & drop interface

- **Document Processing**
  - Automatic text extraction
  - Cleaning (remove noise, formatting)
  - Intelligent chunking:
    - Semantic chunking (keep paragraphs together)
    - Overlap strategy (20% overlap between chunks)
    - Dynamic chunk size (300-800 tokens based on content)
  - Metadata extraction (title, author, creation date if available)
  - Status tracking (processing, completed, failed)

- **Document Organization**
  - Folder/collection structure
  - Tags & categories
  - Search within documents
  - Version tracking (optional)

#### 4.1.3 Internet Data Collection
- **Search Capabilities**
  - Multiple sources:
    - **Google Search** (via DuckDuckGo API or scraping)
    - **Wikipedia** (structured knowledge)
    - **Arxiv** (research papers)
    - **GitHub** (code examples, documentation)
    - **LinkedIn** (via Selenium, scraping public profiles)
    - **Reddit** (discussion forums)
    - **Medium, Dev.to, Hashnode** (blogs)
    - **Stack Overflow** (Q&A)
    - **YouTube Transcripts** (optional, via youtube-transcript-api)

- **Content Aggregation**
  - Query builder (expand single topic to multiple queries)
  - Duplicate detection & removal
  - Content deduplication (exact match + semantic)
  - Quality scoring (prioritize trusted sources)

- **Source Tracking**
  - Store URL, domain, title, publication date
  - Reference links in generated questions
  - Compliance (respect robots.txt, rate limiting)

#### 4.1.4 Follow-Up Questions Module
User answers these questions before exam generation:

```
1. Question Type:
   - Multiple Choice (MCQ)
   - Short Answer
   - True/False
   - Fill in the Blanks
   - Coding/Practical
   - Essay Type
   - Mix of above

2. Difficulty Level:
   - Beginner (Foundation concepts)
   - Intermediate (Applied knowledge)
   - Advanced (Critical thinking)
   - Mixed

3. Number of Questions:
   - 5, 10, 15, 20, 50, 100 (custom input allowed)

4. Time Duration (optional):
   - 15 mins, 30 mins, 1 hour, 2 hours, untimed

5. Topic Focus:
   - Broad coverage
   - Deep dive into specific subtopics
   - Real-world scenarios
   - Theoretical concepts

6. Question Source Preference:
   - User's documents only
   - Internet sources only
   - Mix of both (default)

7. Custom Instructions:
   - "Include code examples"
   - "Focus on recent technologies"
   - "Include interview preparation tips"
   - Free-text field
```

#### 4.1.5 LLM Model & Prompt Management
- **Model Selection Interface**
  - Dropdown to select LLM provider:
    - OpenAI (gpt-3.5-turbo, gpt-4)
    - Cohere (command, command-light)
    - HuggingFace (inference API models)
    - Ollama (local models: llama2, mistral, etc.)
  
- **API Key Management**
  - User enters their own API keys
  - Encrypted storage in PostgreSQL
  - Key testing endpoint (verify key validity)
  - Option to use user's account or app's shared account

- **Prompt Template Management**
  - Default templates provided by system
  - User can create custom templates
  - Template variables:
    - `{context}` - Retrieved content
    - `{num_questions}` - Number of questions
    - `{question_type}` - Type of question
    - `{difficulty}` - Difficulty level
    - `{custom_instructions}` - User's custom requirements
  
- **Model Configuration**
  - Temperature (0.0 - 1.0): Creativity vs consistency
  - Max tokens: Response length control
  - Top-p (nucleus sampling): Diversity
  - Frequency penalty: Repetition control

#### 4.1.6 Exam Generation
- **Generation Workflow**
  1. User submits all inputs (topic, document, preferences)
  2. System triggers data collection (documents + internet)
  3. Embeddings created + stored
  4. Retrieval: Gather relevant content
  5. Prompt building: Combine context + instructions
  6. LLM call: Generate questions
  7. Validation: Check format, grammar, uniqueness
  8. Storage: Save to database
  9. Display: Show to user in UI

- **Output Format**
  ```json
  {
    "exam_id": "uuid",
    "title": "Machine Learning Fundamentals Interview Questions",
    "created_at": "2024-01-15T10:30:00Z",
    "topic": "Machine Learning",
    "metadata": {
      "question_type": "MCQ",
      "difficulty": "Intermediate",
      "num_questions": 10,
      "source_mix": "50% documents, 50% internet",
      "generated_by_model": "gpt-3.5-turbo"
    },
    "questions": [
      {
        "id": 1,
        "question_text": "What is the primary purpose of cross-validation?",
        "question_type": "MCQ",
        "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
        "correct_answer": "C",
        "explanation": "Cross-validation...",
        "difficulty": "Intermediate",
        "source": {
          "type": "internet",
          "url": "https://...",
          "title": "ML Best Practices"
        }
      },
      ...
    ]
  }
  ```

- **Regeneration**
  - User can regenerate specific questions
  - Adjust parameters (difficulty, type, count)
  - Keep questions user likes

#### 4.1.7 Exam Sharing & Collaboration
- **Sharing Options**
  - Generate unique shareable link
  - Set access permissions (public, private, link-only)
  - Expiration date (optional)
  - Password protection (optional)

- **Collaborative Editing** (future)
  - Multiple users contribute to exam
  - Version control
  - Comments on questions

### 4.2 Future Features (Phase 2+)

#### 4.2.1 Student Assessment
- **Answer Submission**
  - MCQ auto-grading
  - Short answer with AI evaluation
  - Essay evaluation with rubric
  
- **Performance Analytics**
  - Score tracking
  - Weakness identification
  - Improvement recommendations
  - Comparison with other students (anonymized)

#### 4.2.2 Adaptive Learning
- **Difficulty Adjustment**
  - Increase difficulty if student scores high
  - Decrease if struggling
  - Personalized question recommendation

#### 4.2.3 Training Module
- **Learning Paths**
  - Course structure
  - Spaced repetition
  - Study progress tracking

#### 4.2.4 Interview Preparation
- **Mock Interview Mode**
  - Audio/video recording (optional)
  - Real-time feedback
  - Comparison with expert answers

---

## 5. DATABASE SCHEMA

### 5.1 PostgreSQL Tables

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_picture_url VARCHAR(500),
    bio TEXT,
    role VARCHAR(50) DEFAULT 'user', -- 'user', 'admin', 'educator'
    subscription_tier VARCHAR(50) DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- User Settings & API Keys (Encrypted)
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    default_llm_provider VARCHAR(50), -- 'openai', 'cohere', 'huggingface', 'ollama'
    default_llm_model VARCHAR(100),
    openai_api_key_encrypted TEXT, -- Encrypted
    cohere_api_key_encrypted TEXT, -- Encrypted
    huggingface_api_key_encrypted TEXT, -- Encrypted
    ollama_endpoint VARCHAR(500),
    default_temperature FLOAT DEFAULT 0.7,
    default_max_tokens INT DEFAULT 1024,
    documents_quota_mb INT DEFAULT 500,
    monthly_api_calls_quota INT DEFAULT 10000,
    custom_prompt_template TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents (User Uploads)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000), -- S3 or local path
    file_type VARCHAR(20), -- 'pdf', 'docx', 'txt', 'pptx', 'xlsx'
    file_size_bytes BIGINT,
    title VARCHAR(500),
    description TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    total_chunks INT,
    embedding_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
    processed_at TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    tags VARCHAR(500), -- comma-separated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document Chunks (Metadata about embeddings in Qdrant)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    qdrant_vector_id UUID NOT NULL, -- Points to Qdrant
    chunk_start_page INT, -- For PDFs
    chunk_start_char INT,
    chunk_end_char INT,
    tokens_count INT,
    embedding_model VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

-- Internet Sources (Scraped Data)
CREATE TABLE internet_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50), -- 'google', 'wikipedia', 'arxiv', 'github', 'linkedin', 'blog', 'stackoverflow'
    source_url VARCHAR(1000) NOT NULL,
    source_title VARCHAR(500),
    source_domain VARCHAR(255),
    author VARCHAR(255),
    publication_date TIMESTAMP,
    content TEXT,
    content_summary TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    quality_score FLOAT, -- 0-1, based on source reputation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Internet Source Chunks (Embeddings in Qdrant)
CREATE TABLE internet_source_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    internet_source_id UUID NOT NULL REFERENCES internet_sources(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    qdrant_vector_id UUID NOT NULL,
    tokens_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(internet_source_id, chunk_index)
);

-- Exams Generated
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Generation Config
    question_type VARCHAR(100), -- 'MCQ', 'short_answer', 'essay', 'mixed'
    difficulty_level VARCHAR(50), -- 'beginner', 'intermediate', 'advanced', 'mixed'
    num_questions INT NOT NULL,
    time_duration_minutes INT,
    
    -- Source Config
    source_preference VARCHAR(100), -- 'user_documents', 'internet', 'mixed'
    used_documents TEXT, -- JSON array of document IDs
    used_sources TEXT, -- JSON array of source IDs
    custom_instructions TEXT,
    
    -- Generation Info
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    generation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generation_duration_seconds INT,
    prompt_used TEXT, -- Store the actual prompt sent to LLM
    
    -- Metadata
    is_published BOOLEAN DEFAULT FALSE,
    is_shared BOOLEAN DEFAULT FALSE,
    shared_link_token VARCHAR(255) UNIQUE,
    shared_link_expiry TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exam Questions
CREATE TABLE exam_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    question_number INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50), -- 'MCQ', 'short_answer', 'essay', 'true_false', 'fill_blank', 'coding'
    difficulty_level VARCHAR(50),
    
    -- For MCQ
    options JSONB, -- ["Option A", "Option B", "Option C", "Option D"]
    correct_answer VARCHAR(50), -- "A", "B", "C", "D" OR full text
    
    -- Additional Info
    explanation TEXT,
    key_concepts VARCHAR(500), -- comma-separated
    difficulty_score FLOAT, -- 0-1
    
    -- Source Reference
    source_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    source_type VARCHAR(50), -- 'user_document', 'internet', 'hybrid'
    source_url VARCHAR(1000),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prompt Templates
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    template_name VARCHAR(255) NOT NULL,
    template_text TEXT NOT NULL,
    description TEXT,
    variables JSONB, -- ["context", "num_questions", "difficulty", "custom_instructions"]
    is_default BOOLEAN DEFAULT FALSE, -- System default or user custom
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Usage Logs (for future monetization/tracking)
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_type VARCHAR(100), -- 'document_upload', 'internet_search', 'exam_generation', 'llm_call'
    endpoint VARCHAR(255),
    model_used VARCHAR(100),
    tokens_used INT,
    cost_usd FLOAT,
    status_code INT,
    response_time_ms INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exam Submissions (for future - student responses)
CREATE TABLE exam_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_score FLOAT,
    total_possible_score FLOAT,
    percentage_score FLOAT,
    time_spent_seconds INT,
    is_completed BOOLEAN DEFAULT FALSE
);

-- Student Answers (for future)
CREATE TABLE student_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES exam_submissions(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES exam_questions(id) ON DELETE CASCADE,
    student_answer TEXT NOT NULL,
    is_correct BOOLEAN,
    points_earned FLOAT,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 Qdrant Vector Database Schema

**Collection: `document_embeddings`**
```json
{
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  },
  "payload_schema": {
    "chunk_id": {"type": "keyword"},
    "source_type": {"type": "keyword"}, // "user_document" or "internet"
    "source_id": {"type": "keyword"}, // document_id or internet_source_id
    "user_id": {"type": "keyword"},
    "chunk_index": {"type": "integer"},
    "chunk_text": {"type": "text"},
    "source_url": {"type": "keyword"},
    "source_title": {"type": "text"},
    "quality_score": {"type": "float"},
    "timestamp": {"type": "datetime"}
  }
}
```

---

## 6. API ENDPOINTS SPECIFICATION

### 6.1 Authentication Endpoints

```
POST /api/v1/auth/register
  Body: {email, username, password, first_name, last_name}
  Response: {user_id, email, message}

POST /api/v1/auth/login
  Body: {email, password}
  Response: {access_token, refresh_token, user_id}

POST /api/v1/auth/logout
  Headers: Authorization: Bearer {token}
  Response: {message}

POST /api/v1/auth/refresh
  Body: {refresh_token}
  Response: {access_token}

POST /api/v1/auth/forgot-password
  Body: {email}
  Response: {message}

POST /api/v1/auth/reset-password
  Body: {token, new_password}
  Response: {message}
```

### 6.2 User Settings Endpoints

```
GET /api/v1/user/profile
  Headers: Authorization: Bearer {token}
  Response: {user_data}

PUT /api/v1/user/profile
  Headers: Authorization: Bearer {token}
  Body: {first_name, last_name, bio, profile_picture_url}
  Response: {user_data}

GET /api/v1/user/settings
  Headers: Authorization: Bearer {token}
  Response: {settings}

PUT /api/v1/user/settings
  Headers: Authorization: Bearer {token}
  Body: {default_llm_provider, default_temperature, custom_prompt, ...}
  Response: {settings}

POST /api/v1/user/api-keys/validate
  Headers: Authorization: Bearer {token}
  Body: {api_key, provider}
  Response: {is_valid, message}
```

### 6.3 Document Management Endpoints

```
POST /api/v1/documents/upload
  Headers: Authorization: Bearer {token}, Content-Type: multipart/form-data
  Body: {file, title, description, tags}
  Response: {document_id, processing_status}

GET /api/v1/documents
  Headers: Authorization: Bearer {token}
  Query: {page, limit, search, tag, status}
  Response: {documents_list, total_count}

GET /api/v1/documents/{document_id}
  Headers: Authorization: Bearer {token}
  Response: {document_details, chunks_count, processing_status}

PUT /api/v1/documents/{document_id}
  Headers: Authorization: Bearer {token}
  Body: {title, description, tags, is_public}
  Response: {document}

DELETE /api/v1/documents/{document_id}
  Headers: Authorization: Bearer {token}
  Response: {message}

GET /api/v1/documents/{document_id}/chunks
  Headers: Authorization: Bearer {token}
  Query: {page, limit}
  Response: {chunks_list}
```

### 6.4 Internet Search Endpoints

```
POST /api/v1/internet/search
  Headers: Authorization: Bearer {token}
  Body: {query, num_results, source_types, language}
  Response: {sources_list, status, processing_id}

GET /api/v1/internet/search/{processing_id}
  Headers: Authorization: Bearer {token}
  Response: {status, results, progress_percentage}

GET /api/v1/internet/sources
  Headers: Authorization: Bearer {token}
  Query: {page, limit, search, source_type, date_from, date_to}
  Response: {sources_list, total_count}

DELETE /api/v1/internet/sources/{source_id}
  Headers: Authorization: Bearer {token}
  Response: {message}
```

### 6.5 Exam Generation Endpoints

```
POST /api/v1/exam/follow-up-questions
  Headers: Authorization: Bearer {token}
  Body: {topic}
  Response: {follow_up_questions} // Returns the form with default values

POST /api/v1/exam/generate
  Headers: Authorization: Bearer {token}
  Body: {
    topic,
    title,
    document_ids: [],
    internet_search: {enabled, search_terms},
    follow_up_answers: {
      question_type,
      difficulty_level,
      num_questions,
      time_duration,
      topic_focus,
      source_preference,
      custom_instructions
    },
    llm_config: {
      provider,
      model,
      temperature,
      max_tokens,
      custom_prompt
    }
  }
  Response: {exam_id, generation_status, estimated_wait_time}

GET /api/v1/exam/{exam_id}
  Headers: Authorization: Bearer {token}
  Response: {exam_details, questions_list}

GET /api/v1/exam/{exam_id}/generation-status
  Headers: Authorization: Bearer {token}
  Response: {status, progress_percentage, estimated_remaining_time}

PUT /api/v1/exam/{exam_id}
  Headers: Authorization: Bearer {token}
  Body: {title, description, is_published}
  Response: {exam}

DELETE /api/v1/exam/{exam_id}
  Headers: Authorization: Bearer {token}
  Response: {message}

GET /api/v1/exams
  Headers: Authorization: Bearer {token}
  Query: {page, limit, search, topic, date_from, date_to}
  Response: {exams_list, total_count}

POST /api/v1/exam/{exam_id}/regenerate
  Headers: Authorization: Bearer {token}
  Body: {question_numbers, new_config}
  Response: {exam_id, generation_status}

POST /api/v1/exam/{exam_id}/share
  Headers: Authorization: Bearer {token}
  Body: {is_public, expiry_days, password}
  Response: {shared_link, expiry_date}

GET /api/v1/exam/shared/{shared_token}
  Response: {exam_details, questions_list} // No auth required
```

### 6.6 Prompt Template Endpoints

```
GET /api/v1/prompts
  Headers: Authorization: Bearer {token}
  Response: {templates_list}

POST /api/v1/prompts
  Headers: Authorization: Bearer {token}
  Body: {template_name, template_text, description}
  Response: {template_id}

PUT /api/v1/prompts/{template_id}
  Headers: Authorization: Bearer {token}
  Body: {template_name, template_text, description}
  Response: {template}

DELETE /api/v1/prompts/{template_id}
  Headers: Authorization: Bearer {token}
  Response: {message}

GET /api/v1/prompts/default
  Response: {default_templates_list}
```

### 6.7 LLM Configuration Endpoints

```
GET /api/v1/llm/available-models
  Headers: Authorization: Bearer {token}
  Query: {provider}
  Response: {models_list}

POST /api/v1/llm/test
  Headers: Authorization: Bearer {token}
  Body: {provider, model, api_key, test_prompt}
  Response: {is_working, response_time, sample_output}

GET /api/v1/llm/pricing
  Response: {pricing_info}
```

### 6.8 Analytics Endpoints (Future)

```
GET /api/v1/analytics/dashboard
  Headers: Authorization: Bearer {token}
  Response: {total_exams, total_questions, api_calls, data_processed_mb}

GET /api/v1/analytics/usage
  Headers: Authorization: Bearer {token}
  Query: {date_from, date_to}
  Response: {usage_stats}
```

---

## 7. DATA SOURCES FOR INTERNET SCRAPING

### 7.1 Primary Sources (Priority Order)

1. **Google Search Results**
   - Method: DuckDuckGo scraping or Google Custom Search API
   - Content: Web pages, blogs, articles
   - Frequency: On-demand
   - Rate limit: Respect robots.txt

2. **Wikipedia**
   - Method: Official Wikipedia API
   - Content: General knowledge, definitions, overviews
   - Frequency: On-demand
   - Rate limit: 1 request per second (official recommendation)

3. **ArXiv** (Research Papers)
   - Method: Official ArXiv API
   - Content: Research papers, technical documentation
   - Frequency: On-demand
   - Rate limit: 3 requests per second

4. **GitHub**
   - Method: GitHub API (requires token)
   - Content: Code, documentation, README files
   - Frequency: On-demand
   - Rate limit: 60 requests/hour (unauthenticated), 5000/hour (authenticated)

5. **LinkedIn** (Public profiles, recruiter insights)
   - Method: Selenium-based scraping (no official API)
   - Content: Professional profiles, job descriptions, company info
   - Frequency: Scheduled/limited
   - Rate limit: Aggressive rate limiting, use proxies
   - Compliance: Respect LinkedIn ToS

6. **Medium, Dev.to, Hashnode** (Technical Blogs)
   - Method: RSS feeds or API
   - Content: Technical articles, tutorials
   - Frequency: Regular scraping
   - Rate limit: Reasonable per-site limits

7. **Stack Overflow** (Q&A)
   - Method: Official Stack Overflow API
   - Content: Questions, answers, discussion
   - Frequency: On-demand
   - Rate limit: 300 requests per day (unauthenticated)

8. **Reddit**
   - Method: PRAW (Python Reddit API Wrapper)
   - Content: Community discussions, tips
   - Frequency: On-demand
   - Rate limit: Respectful rate limiting

9. **YouTube Transcripts** (Optional)
   - Method: youtube-transcript-api library
   - Content: Video transcripts, educational content
   - Frequency: On-demand
   - Rate limit: Per-video

### 7.2 Content Quality Scoring

For each source, calculate quality score:
```
quality_score = (authority_score * 0.4) + (freshness_score * 0.3) + (relevance_score * 0.3)

Where:
- authority_score: Based on source domain reputation
- freshness_score: Based on publication date (recent = higher)
- relevance_score: Based on keyword matching with user's topic
```

### 7.3 Rate Limiting & Compliance

- Implement request queuing per source
- Respect `robots.txt` and `sitemap.xml`
- Add User-Agent headers
- Implement exponential backoff for retries
- Cache results to avoid repeated requests
- Compress duplicate content

---

## 8. INTERVIEW EXPERIENCE SUBMISSIONS (Future)

Users can submit:
- Mock interview transcripts
- Recruiter insights & feedback
- Study materials they used
- Common question collections

This becomes a community-driven knowledge base:
```
/api/v1/community/submit-experience
  Body: {
    topic,
    experience_type, // 'interview', 'hiring_practice', 'study_resource'
    content,
    difficulty_level,
    source_company, // optional
    is_anonymous
  }
```

---

## 9. DEVELOPMENT PHASES & TIMELINE

### Phase 1: MVP (4-6 weeks)
**Goal:** Functional core product with basic features

**COMPLETED ✅ (Phase 1 - Core Infrastructure):**
- [x] Backend setup (FastAPI, PostgreSQL, Qdrant) - ✅ Docker & docker-compose config, FastAPI app, DB models, health endpoint
- [x] User authentication system - ✅ JWT tokens, password hashing, login/register/refresh, user profile endpoints
- [x] Frontend (React) - basic UI - ✅ React Router, Chakra UI, all pages scaffolded, navigation component
- [x] Document processor service - ✅ PDF/DOCX/TXT/XLSX extraction, text cleaning, intelligent chunking
- [x] Embeddings service - ✅ sentence-transformers local model, batch processing (no API costs)
- [x] Qdrant vector DB service - ✅ Client, collection management, search/upsert/delete operations
- [x] LLM provider service - ✅ OpenAI, Cohere, HuggingFace, Ollama support with unified interface
- [x] RAG Retrieval Engine - ✅ Context retrieval, semantic search, hybrid search ready, source tracking
- [x] Exam Generation Service - ✅ Complete exam generation pipeline with prompt building and parsing
- [x] Configuration management - ✅ Environment variables, database ORM setup
- [x] Documentation - ✅ PROJECT_PLAN.md, DEVELOPMENT.md, README.md

**COMPLETED ✅ (Phase 1.5 - API Implementation):**
- [x] Document upload & processing API - ✅ Full endpoint with multipart upload, text extraction, chunking, embedding, vector storage
- [x] Exam generation API - ✅ Complete endpoint with RAG retrieval, LLM integration, parsing, database storage
- [x] Document listing & retrieval - ✅ List, get, delete endpoints with user authorization
- [x] Exam listing & retrieval - ✅ List, get, delete endpoints with full question display
- [x] DocumentProcessor BytesIO support - ✅ Updated to handle file uploads with proper type detection
- [x] TextChunker improvements - ✅ Returns metadata (tokens) with chunks for accurate tracking

**COMPLETED ✅ (Phase 2.0 - Frontend Dashboard & Exam Generator UI):**
- [x] Dashboard page - ✅ Shows documents, exams, stats, delete functionality
- [x] ExamGenerator page - ✅ Complete form with drag-drop upload, LLM config, results display
- [x] ExamView page - ✅ Full exam viewing with all questions and explanations
- [x] Document upload in frontend - ✅ Drag-and-drop, progress tracking, error handling
- [x] Form validation - ✅ Client-side validation for required fields
- [x] Navigation routing - ✅ All pages connected with proper navigation

**IN PROGRESS / TODO:**
- [ ] Internet scraping service - ✅ IMPLEMENTED (Google, Wikipedia, ArXiv, GitHub)
- [ ] Scraper API endpoints - Integrate scraper into exam generation flow
- [ ] Testing & debugging - End-to-end testing with real documents
- [ ] Performance optimization - Caching, rate limiting
- [ ] Deployment to AWS EC2 - EC2 setup, Docker deployment, domain configuration

### Phase 2: Feature Enhancement (4-6 weeks)
**Goal:** Multi-provider LLM support, internet scraping, improved UX

**COMPLETED ✅ (Phase 2.0 - Frontend & Scraper):**
- [x] Dashboard UI - Shows user's documents and exams with stats
- [x] Exam Generator Frontend - Complete form with all options
- [x] File upload UI - Drag-and-drop support with progress
- [x] Exam results display - Full question viewing with explanations
- [x] Internet scraping service - Google, Wikipedia, ArXiv, GitHub integration
- [x] Multi-source search - Combined search across multiple platforms
- [x] Chunk extraction from scraped content - Ready for RAG integration

**IN PROGRESS / TODO:**
- [ ] Scraper API endpoints - Integrate scraper into exam generation
- [ ] Internet source selection - Allow users to choose sources
- [ ] Caching for scraped content - Redis caching for performance
- [ ] Rate limiting - API rate limiting for users
- [ ] Performance optimization - Query optimization, indexing
- [ ] Better error handling & logging - Comprehensive error tracking

### Phase 3: Advanced Features (4-6 weeks)
**Goal:** Assessment, analytics, community features

Tasks:
- [ ] Student answer submission & grading
- [ ] Performance analytics dashboard
- [ ] Community experience submissions
- [ ] Adaptive learning recommendations
- [ ] Caching (Redis) implementation
- [ ] Monitoring & alerting
- [ ] API documentation (Swagger)

### Phase 4: Production Hardening (2-3 weeks)
**Goal:** Security, compliance, scalability

Tasks:
- [ ] Security audit
- [ ] GDPR/compliance implementation
- [ ] Load testing
- [ ] Disaster recovery setup
- [ ] Comprehensive logging
- [ ] Multi-region deployment (optional)

---

## 10. DEPLOYMENT ARCHITECTURE

### 10.1 AWS Infrastructure

```
AWS Account
├── EC2 Instance (t3.medium)
│   ├── Docker Container 1: FastAPI Backend
│   ├── Docker Container 2: Qdrant Vector DB
│   ├── Docker Container 3: PostgreSQL
│   ├── Docker Container 4: Redis (optional)
│   └── Docker Container 5: Ollama (optional, local LLM)
│
├── S3 Bucket (optional)
│   └── User document storage
│
├── RDS PostgreSQL (optional, for production)
│   └── Managed database
│
├── CloudFront (optional)
│   └── CDN for frontend static files
│
├── Route 53
│   └── DNS management
│
└── Security Groups
    ├── Backend (ports: 8000)
    ├── Database (port: 5432)
    └── Vector DB (port: 6333)
```

### 10.2 Docker Compose Setup

```yaml
version: '3.9'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/rag_db
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - qdrant
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=rag_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

### 10.3 Deployment Commands

```bash
# Clone repository
git clone <repo-url>
cd <repo>

# Build and start containers
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Database migrations
docker-compose exec backend python -m alembic upgrade head

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Qdrant UI: http://localhost:6333/dashboard
```

---

## 11. SECURITY CONSIDERATIONS

### 11.1 Current (MVP Phase)
- JWT-based authentication
- Password hashing (bcrypt)
- HTTPS enforcement (AWS SSL)
- API rate limiting
- Input validation & sanitization

### 11.2 Future (Post-MVP)
- OAuth2 (Google, GitHub)
- Multi-factor authentication (MFA)
- Encrypted API key storage
- Data encryption at-rest & in-transit
- GDPR compliance (data deletion, export)
- HIPAA compliance (if needed)
- Audit logging
- Penetration testing
- Regular security updates

---

## 12. COST ANALYSIS (Zero Budget MVP)

### 12.1 Free Tier Usage

| Service | Free Tier | Status |
|---------|-----------|--------|
| **AWS EC2** | 750 hours/month t2.micro (first year) | Sufficient for MVP |
| **AWS RDS** | 750 hours/month (first year) | Optional, use local DB initially |
| **OpenAI API** | None (pay-as-you-go) | BUT free $5 credits for new accounts |
| **DuckDuckGo API** | Free | Use for search |
| **Wikipedia API** | Free | Unlimited |
| **ArXiv API** | Free | 3 requests/second |
| **GitHub API** | 60 requests/hour unauthenticated, 5000 authenticated | Free |
| **Stack Overflow API** | 300 requests/day | Free |
| **Sentence Transformers** | Free, open source | Local computation |
| **Qdrant** | Open source, self-hosted | Free |
| **PostgreSQL** | Open source | Free |
| **Redis** | Open source | Free |
| **FastAPI** | Free, open source | Free |
| **React** | Free, open source | Free |
| **Docker** | Free Community Edition | Free |

### 12.2 First Year Cost (if no AWS free tier)
- AWS EC2: ~$240/year (t3.small)
- Miscellaneous (domain, monitoring): ~$20/year
- **Total: ~$260/year** (negligible for MVP)

### 12.3 Monthly API Costs (After free tier)
If using OpenAI GPT-3.5-turbo:
- 10 users × 10 exams/month × 2000 tokens avg = 200K tokens/month
- Cost: ~$3-5/month (negligible)

---

## 13. MONITORING & LOGGING

### 13.1 Metrics to Track
- API response times
- Database query performance
- Vector search latency
- LLM API response times
- Error rates & types
- User engagement (exams created, questions generated)
- API quota usage
- System resource usage (CPU, memory, disk)

### 13.2 Logging Strategy
- Application logs: FastAPI logs to file + stdout
- Access logs: Nginx/API gateway logs
- Error tracking: Sentry (free tier available)
- Metrics: Prometheus + Grafana (self-hosted)

### 13.3 Monitoring Tools (Free/Open Source)
- **Prometheus**: Metrics collection
- **Grafana**: Visualization & dashboards
- **ELK Stack** (Elasticsearch, Logstash, Kibana): Centralized logging
- **Sentry**: Error tracking (free tier: 5K events/month)

---

## 14. KEY TECHNICAL DECISIONS & RATIONALE

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Backend** | FastAPI | Modern, async, fast, great for ML/AI workloads |
| **Vector DB** | Qdrant | Better performance than Weaviate for small scale, easier setup |
| **Embeddings** | sentence-transformers | Free, open source, no API costs |
| **Frontend** | React | Large ecosystem, component libraries, ease of development |
| **Deployment** | AWS EC2 + Docker | Familiar, scalable, free tier available |
| **LLM Integration** | User-provided API keys | No backend API costs, user controls their own spending |
| **Chunking** | Semantic + overlap | Better context preservation than simple text splitting |
| **Search** | Hybrid (semantic + BM25) | Better relevance than semantic-only or keyword-only |
| **Caching** | Redis | Improves performance, reduces API calls |
| **Authentication** | JWT | Stateless, scalable, secure |

---

## 15. FUTURE ENHANCEMENTS

### Phase 2+
- [ ] Mobile app (React Native)
- [ ] Offline mode (progressive web app)
- [ ] Custom model fine-tuning
- [ ] Advanced analytics (student performance, question difficulty calibration)
- [ ] Collaborative features (teams, shared resources)
- [ ] Marketplace (buy/sell exams, prompts)
- [ ] Integration with learning management systems (LMS)
- [ ] Video generation (create video lessons from exam content)
- [ ] Speech-to-text (voice-based exam input)

### Enterprise Features
- [ ] White-label solution
- [ ] On-premise deployment
- [ ] Multi-language support
- [ ] Advanced compliance (HIPAA, SOC2, ISO27001)
- [ ] Customer success team
- [ ] Premium support

---

## 16. SUCCESS METRICS

### MVP Success Criteria
1. **Functionality**: All core features working (document upload, internet search, exam generation)
2. **Performance**: Exam generation < 2 minutes for 10 questions
3. **Reliability**: 99.5% uptime
4. **User Satisfaction**: Positive feedback from 10 test users
5. **Code Quality**: 80%+ test coverage

### Future Success Metrics
1. **Adoption**: 100+ active users by month 6
2. **Usage**: 1000+ exams generated per month
3. **Revenue** (if monetized): $10K MRR by year 2
4. **Community**: 500+ community-submitted resources

---

## 17. REPOSITORY STRUCTURE

```
exam-rag-portal/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── exams.py
│   │   │   ├── internet_search.py
│   │   │   ├── llm.py
│   │   │   └── prompts.py
│   │   ├── models/
│   │   │   ├── database.py
│   │   │   ├── schemas.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── document_processor.py
│   │   │   ├── embeddings.py
│   │   │   ├── internet_scraper.py
│   │   │   ├── rag_engine.py
│   │   │   ├── llm_provider.py
│   │   │   └── exam_generator.py
│   │   ├── utils/
│   │   ├── config.py
│   │   └── dependencies.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── styles/
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .github/workflows/ (CI/CD)
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   └── DEPLOYMENT.md
├── PROJECT_PLAN.md (this file)
├── README.md
├── .gitignore
└── LICENSE
```

---

## 18. GETTING STARTED CHECKLIST

### Before Development
- [ ] Read this plan document thoroughly
- [ ] Understand the architecture
- [ ] Familiarize yourself with tech stack
- [ ] Set up development environment

### Phase 1 Setup
- [ ] Create GitHub repository
- [ ] Set up local Docker development environment
- [ ] Initialize FastAPI project structure
- [ ] Set up PostgreSQL locally
- [ ] Set up Qdrant locally
- [ ] Create initial database schema
- [ ] Implement basic user authentication
- [ ] Create API endpoint templates
- [ ] Set up React frontend boilerplate
- [ ] Implement CI/CD pipeline (GitHub Actions)
- [ ] Deploy to AWS (initial setup)

---

## 19. CONTACT & SUPPORT

For questions or clarifications about this plan:
- Refer to this document as the source of truth
- For technical implementation issues, use code comments
- For architectural changes, update this document

---

**Document Version:** 1.0
**Last Updated:** 2026-07-14
**Next Review Date:** 2026-08-14

