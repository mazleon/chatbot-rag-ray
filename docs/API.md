# API Documentation

## Base URL

```
Production: http://localhost:5173/api/v1
Development: http://localhost:8000/api/v1
```

---

## Authentication

Currently, no authentication is required. The API uses API keys for LLM services only.

---

## Endpoints

### 1. Health Check

Check if the API is running and healthy.

```http
GET /api/v1/health
```

**Example Request:**
```bash
curl -X GET http://localhost:5173/api/v1/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

---

### 2. Chat

Send a message and receive a response from the AI agent.

```http
POST /api/v1/chat
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | No | Unique session identifier. If not provided, a new session will be created. |
| `message` | string | Yes | The user's message/question |

**Example Request:**
```bash
curl -X POST http://localhost:5173/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "What is term life insurance?"
  }'
```

**Example Response:**
```json
{
  "session_id": "user-123",
  "message": "Term life insurance is a type of life insurance that provides coverage for a specific period or 'term'...",
  "intent": "policy_info",
  "sources": ["Reference 1: Life insurance provides financial protection..."]
}
```

---

### 3. Upload Document

Upload a document (PDF, DOCX, TXT) to be added to the knowledge base.

```http
POST /api/v1/upload
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | string | Yes | Name of the file (e.g., "policy.pdf") |
| `content` | string | Yes | Base64-encoded file content |
| `session_id` | string | No | Session identifier |

**Example Request:**
```bash
curl -X POST http://localhost:5173/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "my-policy.pdf",
    "content": "SGVsbG8gV29ybGQhIFRoaXMgaXMgYSB0ZXN0IGRvY3VtZW50Lg==",
    "session_id": "user-123"
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "chunks_created": 5,
  "message": "Successfully processed my-policy.pdf"
}
```

**File Upload in JavaScript:**
```javascript
async function uploadFile(file) {
  const reader = new FileReader();
  const base64 = await new Promise((resolve) => {
    reader.onload = () => {
      const result = reader.result.split(',')[1];
      resolve(result);
    };
    reader.readAsDataURL(file);
  });

  const response = await fetch('/api/v1/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: file.name,
      content: base64
    })
  });
  return response.json();
}
```

---

### 4. Get Session History

Retrieve the conversation history for a specific session.

```http
GET /api/v1/sessions/{session_id}/history
```

**Example Request:**
```bash
curl -X GET http://localhost:5173/api/v1/sessions/user-123/history
```

**Example Response:**
```json
{
  "session_id": "user-123",
  "messages": [
    {
      "role": "user",
      "content": "What is term life insurance?"
    },
    {
      "role": "assistant",
      "content": "Term life insurance is..."
    }
  ],
  "message_count": 2
}
```

---

### 5. Delete Session

Delete a session and its conversation history.

```http
DELETE /api/v1/sessions/{session_id}
```

**Example Request:**
```bash
curl -X DELETE http://localhost:5173/api/v1/sessions/user-123
```

**Example Response:**
```json
{
  "status": "deleted",
  "session_id": "user-123"
}
```

---

## Response Schemas

### ChatResponse

```typescript
interface ChatResponse {
  session_id: string;
  message: string;
  intent: "general" | "policy_info" | "claims" | "premium" | "benefits" | "eligibility" | "document_query" | "summarize" | "personal_info";
  sources: string[] | null;
}
```

### UploadResponse

```typescript
interface UploadResponse {
  status: "success" | "error";
  chunks_created: number;
  message: string;
}
```

### SessionHistoryResponse

```typescript
interface SessionHistoryResponse {
  session_id: string;
  messages: Array<{
    role: "user" | "assistant";
    content: string;
    intent?: string;
  }>;
  message_count: number;
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Status Code | Description |
|------------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 404 | Not Found - Endpoint not found |
| 422 | Validation Error - Invalid request body |
| 500 | Internal Server Error |

---

## Rate Limits

Currently, no rate limits are enforced. However, API calls are subject to the underlying LLM provider's rate limits.

---

## Postman Collection

A Postman collection is available in `api-collection.json` for easy import and testing.

```bash
# Import in Postman:
File > Import > Select api-collection.json
```
