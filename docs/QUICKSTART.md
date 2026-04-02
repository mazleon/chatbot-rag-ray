# Quick Start Guide

Get up and running in 5 minutes!

---

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (for LLM and embeddings)

---

## Step 1: Get Your API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (you won't see it again!)

---

## Step 2: Start the Application

```bash
# Clone and navigate to project
cd ray-works

# Copy environment template
cp .env.docker .env

# Edit .env with your API key (use any text editor)
# Find OPENAI_API_KEY and replace with your key

# Start all services
docker-compose up --build
```

Wait for all containers to start (about 2-3 minutes on first run).

---

## Step 3: Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Step 4: Test the Application

### 1. Ask a question
Type in the chat: "What is term life insurance?"

### 2. Upload a document
1. Click the upload button in the sidebar
2. Select a PDF, DOCX, or TXT file
3. Wait for "X chunks added" confirmation

### 3. Ask about your document
Type: "What does my document say about life insurance?"

---

## Common Questions

### Q: Why am I getting "API key not found" errors?
A: Make sure you added your OpenAI API key to the `.env` file and restarted Docker.

### Q: Why isn't RAG working?
A: You need to upload documents first before asking questions about them.

### Q: How do I stop the application?
A: Press `Ctrl+C` or run `docker-compose down`

---

## Next Steps

- Read the [API Documentation](API.md) for detailed endpoint info
- Read the [Technical Documentation](TECHNICAL.md) for architecture deep-dive
- Customize the agent prompts in `app/agents/graph.py`
