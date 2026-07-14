# 🚀 QUICK START GUIDE - EXAM RAG PORTAL

## ⚡ 30-Second Setup

```bash
cd c:\Users\ACER\Downloads\my-content\testing-rag
docker-compose up -d
```

**Wait 30 seconds for containers to start...**

Then open:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Qdrant:** http://localhost:6333/dashboard

---

## 📋 5-Minute Quickstart

### 1. Register & Login
```
1. Go to http://localhost:3000
2. Click "Register"
3. Enter email, username, password
4. Click "Login"
```

### 2. Upload Document
```
1. Click "Generate New Exam" on dashboard
2. Drag & drop a PDF/TXT/DOCX file
3. Select the document from list
```

### 3. Generate Exam
```
1. Enter topic: "Machine Learning"
2. Keep default settings or customize:
   - Number of questions: 5
   - Type: MCQ
   - Difficulty: Medium
3. LLM: Ollama (free, no API key needed)
4. Click "Generate Exam"
```

### 4. View Results
```
1. See questions appear with:
   - Question text
   - MCQ options (correct answer highlighted in green)
   - Explanation
   - Related concepts
2. Click "Back to Dashboard" to save
```

---

## 🎨 FEATURES AT A GLANCE

| Feature | Where | How |
|---------|-------|-----|
| **Upload Files** | Dashboard → Generate Exam | Drag & drop or browse |
| **Manage Docs** | Dashboard | View, delete documents |
| **View Exams** | Dashboard | Click "View" button |
| **Generate Exams** | Exam Generator Page | Fill form + click generate |
| **Choose LLM** | Exam Generator Form | Select provider (Ollama/OpenAI/etc) |
| **Add Custom Instructions** | Exam Generator Form | Optional text field |
| **Delete Items** | Dashboard | Click delete with confirmation |

---

## 🔑 AUTHENTICATION

**Default Login:**
- No default users - you must register first

**Storage:**
- JWT tokens stored in localStorage
- Expires automatically

**Options:**
- Email/username-based
- Password hashing with bcrypt
- Refresh token support

---

## 📄 SUPPORTED FORMATS

| Format | Example | Status |
|--------|---------|--------|
| PDF | document.pdf | ✅ Full support |
| TXT | notes.txt | ✅ Full support |
| DOCX | report.docx | ✅ Full support |
| XLSX | data.xlsx | ✅ Full support |

---

## 🧠 LLM PROVIDERS

| Provider | Free | Setup | Speed | Quality |
|----------|------|-------|-------|---------|
| **Ollama** | ✅ | Local | ⚡⚡⚡ | ⭐⭐⭐ |
| **OpenAI** | ❌ (paid) | API key | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| **Cohere** | ❌ (free tier) | API key | ⚡⚡ | ⭐⭐⭐⭐ |
| **HuggingFace** | ❌ (free tier) | API key | ⚡ | ⭐⭐⭐ |

---

## 🌐 INTERNET SOURCES

System can scrape:
- 🔍 Google search results
- 📚 Wikipedia articles
- 📄 ArXiv papers
- 💻 GitHub repositories

Set "Source Preference" to "Internet" or "Both" in exam generator

---

## 🆘 TROUBLESHOOTING

### Issue: Can't connect to http://localhost:3000
**Solution:** 
```bash
# Check if frontend is running
docker-compose ps

# If not running, restart
docker-compose restart frontend
```

### Issue: "No documents found"
**Solution:** 
1. Upload a document first
2. Wait for processing to complete (check badge: "completed")
3. Then generate exam

### Issue: "API key required"
**Solution:** 
- For Ollama: No API key needed
- For OpenAI/Cohere/HF: Provide valid API key from their websites

### Issue: Exam generation fails
**Solution:** 
1. Make sure documents are uploaded and processed
2. Check LLM provider has valid API key (if not Ollama)
3. Try with fewer questions first (start with 3)

---

## 📊 DATABASE SCHEMA

### Key Tables
- **users** - User accounts and profiles
- **documents** - Uploaded files metadata
- **document_chunks** - Text chunks with embeddings
- **exams** - Generated exams
- **exam_questions** - Individual questions
- **user_settings** - API keys and preferences

---

## 🔄 DATA FLOW

```
Upload Document
    ↓
Extract Text (PDF/DOCX/TXT parsing)
    ↓
Clean & Split into Chunks (500 tokens each)
    ↓
Generate Embeddings (sentence-transformers)
    ↓
Store in Qdrant (vector database)
    ↓
Save metadata in PostgreSQL
    ↓
Ready for exam generation!
    ↓
User requests exam
    ↓
Retrieve relevant chunks from Qdrant
    ↓
Build prompt with context
    ↓
Call LLM (OpenAI/Ollama/etc)
    ↓
Parse JSON questions
    ↓
Display to user
    ↓
Save exam to database
```

---

## 💾 FILES TO CUSTOMIZE

### Environment Variables (.env)
```bash
# Rename .env.example to .env
cp .env.example .env

# Edit with your settings
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
HUGGINGFACE_API_KEY=...
```

### LLM Model Selection
See Exam Generator form for options:
- Ollama: `llama2`, `mistral`, etc.
- OpenAI: `gpt-3.5-turbo`, `gpt-4`, etc.
- Cohere: `command-large`, etc.

---

## 📈 PERFORMANCE TIPS

1. **Use smaller documents first** (< 1MB) while testing
2. **Keep max tokens around 2000** (default)
3. **Start with 5 questions** before generating 50
4. **Ollama is faster** but lower quality
5. **OpenAI is better quality** but needs API key

---

## 🚀 SCALING READY

Current setup handles:
- ✅ Multiple users
- ✅ Hundreds of documents
- ✅ Thousands of questions
- ✅ Concurrent requests

For production, add:
- AWS RDS (managed PostgreSQL)
- AWS S3 (document storage)
- Redis caching
- Load balancer
- CDN for frontend

---

## 📚 LEARN MORE

- **Architecture:** See `PROJECT_PLAN.md`
- **Development:** See `DEVELOPMENT.md`  
- **API Testing:** See `API_TESTING_GUIDE.md`
- **Services:** See `SERVICES_GUIDE.md`
- **Implementation:** See `IMPLEMENTATION_COMPLETE.md`

---

## 🎯 SUPPORT

**If something doesn't work:**

1. **Check logs:**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs postgres
   ```

2. **Restart containers:**
   ```bash
   docker-compose restart
   ```

3. **Check connectivity:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Review documentation:**
   - API_TESTING_GUIDE.md
   - DEVELOPMENT.md
   - README.md

---

## ✅ WHAT'S WORKING

- ✅ User registration & authentication
- ✅ Document upload & processing
- ✅ Text extraction from 4 formats
- ✅ Embedding generation (local)
- ✅ Vector storage in Qdrant
- ✅ Exam generation with RAG
- ✅ Multi-provider LLM support
- ✅ Dashboard with stats
- ✅ Complete UI (all pages)
- ✅ Internet scraping ready

---

## 🎓 EXAMPLE COMMANDS

### Test Exam Generation (cURL)
```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"pass123"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass123"}'
# Copy the access_token from response

# 3. Generate Exam
curl -X POST http://localhost:8000/api/v1/exams/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python",
    "num_questions": 3,
    "question_type": "MCQ",
    "difficulty_level": "medium",
    "llm_config": {
      "provider": "ollama",
      "model": "llama2",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }'
```

---

## 🎉 YOU'RE READY!

**Everything is set up and ready to use.**

Start with simple tests and explore features.

Have fun! 🚀
