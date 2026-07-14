# API Testing Guide - Complete Workflow

## 🚀 Quick Start

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Verify Services Running
```bash
docker-compose ps
```

### 3. Access API Documentation
```
http://localhost:8000/docs
```

---

## 📋 Complete Testing Workflow

### Step 1: Register User

**Via Swagger UI:** http://localhost:8000/docs → Servers → POST `/api/v1/auth/register`

**Via cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "username": "testuser",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "id": "user-uuid-here",
  "email": "user@test.com",
  "username": "testuser",
  "message": "User registered successfully"
}
```

---

### Step 2: Login and Get Tokens

**Via cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**⚠️ Save the `access_token` for next steps!**

---

### Step 3: Get User Profile

**Via cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": "user-uuid",
  "email": "user@test.com",
  "username": "testuser",
  "first_name": null,
  "last_name": null,
  "bio": null,
  "created_at": "2026-07-14T12:00:00"
}
```

---

### Step 4: Upload Document (CRITICAL TEST)

**Create a test document:**
```bash
# Option A: Use existing PDF
# Option B: Create test TXT file
echo "Machine Learning is a subset of artificial intelligence that focuses on enabling computers to learn from data without being explicitly programmed. It involves algorithms that improve through experience. Common applications include image recognition, natural language processing, and recommendation systems." > test_doc.txt
```

**Upload via cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@test_doc.txt"
```

**Expected Response:**
```json
{
  "document_id": "doc-uuid-here",
  "file_name": "test_doc.txt",
  "processing_status": "completed",
  "total_chunks": 3,
  "file_size_bytes": 280,
  "message": "Document uploaded and processed successfully"
}
```

**⚠️ Save the `document_id` for exam generation!**

---

### Step 5: List Documents

**Via cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/documents/list \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "documents": [
    {
      "id": "doc-uuid",
      "file_name": "test_doc.txt",
      "title": "test_doc",
      "file_type": "txt",
      "file_size_bytes": 280,
      "processing_status": "completed",
      "total_chunks": 3,
      "upload_date": "2026-07-14T12:00:00",
      "processed_at": "2026-07-14T12:00:01"
    }
  ],
  "total": 1
}
```

---

### Step 6: Get Document Details

**Via cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/documents/DOC_UUID_HERE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": "doc-uuid",
  "file_name": "test_doc.txt",
  "title": "test_doc",
  "description": null,
  "file_type": "txt",
  "file_size_bytes": 280,
  "processing_status": "completed",
  "total_chunks": 3,
  "upload_date": "2026-07-14T12:00:00",
  "processed_at": "2026-07-14T12:00:01",
  "error_message": null
}
```

---

### Step 7: Generate Exam (MAIN FEATURE!)

**Via cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/exams/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning",
    "num_questions": 5,
    "question_type": "MCQ",
    "difficulty_level": "medium",
    "document_ids": ["DOC_UUID_HERE"],
    "custom_instructions": "Focus on practical applications and real-world use cases",
    "llm_config": {
      "provider": "ollama",
      "model": "llama2",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "source_preference": "documents"
  }'
```

**Alternative - Using OpenAI:**
```bash
curl -X POST http://localhost:8000/api/v1/exams/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning",
    "num_questions": 5,
    "question_type": "MCQ",
    "difficulty_level": "medium",
    "document_ids": ["DOC_UUID_HERE"],
    "custom_instructions": "Create comprehensive exam questions",
    "llm_config": {
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "api_key": "sk-...",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "source_preference": "documents"
  }'
```

**Expected Response:**
```json
{
  "exam_id": "exam-uuid",
  "title": "Exam: Machine Learning",
  "topic": "Machine Learning",
  "num_questions": 5,
  "question_type": "MCQ",
  "difficulty_level": "medium",
  "questions": [
    {
      "question_number": 1,
      "question_text": "What is machine learning?",
      "question_type": "MCQ",
      "difficulty_level": "easy",
      "options": {
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      },
      "correct_answer": "A",
      "explanation": "Machine learning is...",
      "key_concepts": "Definition, AI"
    },
    ...
  ],
  "sources": [
    {
      "id": "doc-uuid",
      "chunks": 3
    }
  ],
  "generation_duration_seconds": 8.5,
  "status": "completed"
}
```

**⚠️ Save the `exam_id` for retrieval!**

---

### Step 8: Get Exam Details

**Via cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/exams/EXAM_UUID_HERE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "id": "exam-uuid",
  "title": "Exam: Machine Learning",
  "topic": "Machine Learning",
  "description": null,
  "question_type": "MCQ",
  "difficulty_level": "medium",
  "num_questions": 5,
  "time_duration_minutes": null,
  "source_preference": "documents",
  "custom_instructions": "...",
  "llm_provider": "ollama",
  "llm_model": "llama2",
  "generation_duration_seconds": 8,
  "is_published": false,
  "is_shared": false,
  "created_at": "2026-07-14T12:00:00",
  "questions": [...]
}
```

---

### Step 9: List Exams

**Via cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/exams/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "exams": [
    {
      "id": "exam-uuid",
      "title": "Exam: Machine Learning",
      "topic": "Machine Learning",
      "num_questions": 5,
      "question_type": "MCQ",
      "difficulty_level": "medium",
      "is_published": false,
      "is_shared": false,
      "created_at": "2026-07-14T12:00:00",
      "generation_duration_seconds": 8
    }
  ],
  "total": 1
}
```

---

### Step 10: Delete Operations

**Delete Document:**
```bash
curl -X DELETE http://localhost:8000/api/v1/documents/DOC_UUID_HERE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Delete Exam:**
```bash
curl -X DELETE http://localhost:8000/api/v1/exams/EXAM_UUID_HERE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## 🔧 Testing Different File Types

### PDF Document
```bash
# Download a sample PDF or use existing one
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@sample.pdf"
```

### DOCX Document
```bash
# Requires: python-docx library
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@sample.docx"
```

### XLSX Document
```bash
# Requires: openpyxl library
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@sample.xlsx"
```

---

## 🧪 Troubleshooting

### Issue: "No text extracted from document"
**Solution:** Document might be scanned image-based PDF. Try TXT or DOCX format.

### Issue: "API key required for provider"
**Solution:** For Ollama (local), don't provide api_key. For OpenAI/Cohere/HF, provide valid key.

### Issue: "Document not found"
**Solution:** Make sure document_id is correct and document is fully processed (status: "completed")

### Issue: "No valid processed documents"
**Solution:** Upload document first and wait for processing to complete before generating exam.

### Check Logs
```bash
# Backend logs
docker-compose logs backend

# Database logs
docker-compose logs postgres

# Qdrant logs
docker-compose logs qdrant
```

---

## 📊 Performance Testing

### Test with Multiple Documents
```bash
# Create 3 test documents
for i in 1 2 3; do
  echo "Test content $i" > test_doc_$i.txt
  curl -X POST http://localhost:8000/api/v1/documents/upload \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
    -F "file=@test_doc_$i.txt"
done
```

### Generate Multiple Exams
```bash
# Generate exams on same topic
for i in 1 2 3; do
  curl -X POST http://localhost:8000/api/v1/exams/generate \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
    -H "Content-Type: application/json" \
    -d '{
      "topic": "Python Programming",
      "num_questions": 5,
      "question_type": "MCQ",
      "difficulty_level": "medium",
      "llm_config": {
        "provider": "ollama",
        "model": "llama2",
        "temperature": 0.7,
        "max_tokens": 2000
      }
    }'
done
```

---

## ✅ Success Criteria

- ✅ User registration works
- ✅ Login returns valid JWT tokens
- ✅ Document upload processes successfully
- ✅ Embeddings generated (stored in Qdrant)
- ✅ Exam generation retrieves context from documents
- ✅ Questions are properly formatted with MCQ options
- ✅ Exam can be retrieved with all questions
- ✅ Delete operations work

---

## 🎯 Next Steps

1. **Test with Swagger UI:** http://localhost:8000/docs
2. **Test with Postman:** Import `openapi.json` from `/api/v1/docs`
3. **Test Frontend:** Implement upload form in React
4. **Test Different LLM Providers:** Switch between Ollama, OpenAI, Cohere
5. **Performance Test:** Upload 10+ documents, generate multiple exams

---

**Generated:** 2026-07-14
**API Status:** 🟢 All endpoints implemented and ready
