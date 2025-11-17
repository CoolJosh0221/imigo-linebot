# IMIGO API Documentation

Base URL: `https://api.imigo.tw`

## Authentication

Currently, the API does not require authentication for most endpoints. The LINE webhook endpoint validates signatures from LINE platform.

## Available Endpoints

### Root & Health Check

#### GET /
Get basic service information

**Response:**
```json
{
  "status": "running",
  "bot": "IMIGO",
  "language": "id",
  "country": "Indonesia"
}
```

#### GET /health
Simple health check

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Chat API

### POST /api/chat/message
Send a message to the AI bot and receive a response.

**Request Body:**
```json
{
  "user_id": "string",
  "message": "string",
  "language": "id"
}
```

**Parameters:**
- `user_id` (required): Unique identifier for the user
- `message` (required): The message text
- `language` (optional): Language code (default: "id")
  - `id`: Indonesian (Bahasa Indonesia)
  - `zh`: Traditional Chinese (繁體中文)
  - `en`: English
  - `vi`: Vietnamese (Tiếng Việt)
  - `th`: Thai (ภาษาไทย)
  - `fil`: Tagalog (Filipino)

**Response:**
```json
{
  "user_id": "string",
  "message": "string",
  "response": "string",
  "language": "id"
}
```

**Example:**
```bash
curl -X POST https://api.imigo.tw/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Saya butuh bantuan dengan visa kerja",
    "language": "id"
  }'
```

### POST /api/chat/clear
Clear conversation history for a specific user.

**Request Body:**
```json
{
  "user_id": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation cleared"
}
```

**Example:**
```bash
curl -X POST https://api.imigo.tw/api/chat/clear \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

### GET /api/chat/history/{user_id}
Get conversation history for a user.

**Parameters:**
- `user_id` (path, required): User identifier
- `limit` (query, optional): Maximum messages to return (default: 10)

**Response:**
```json
{
  "user_id": "string",
  "history": [
    {
      "role": "user",
      "content": "string",
      "timestamp": "2025-01-17T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "string",
      "timestamp": "2025-01-17T12:00:01Z"
    }
  ],
  "count": 2
}
```

**Example:**
```bash
curl https://api.imigo.tw/api/chat/history/user123?limit=20
```

---

## Translation API

### POST /api/translate/
Translate text between supported languages.

**Request Body:**
```json
{
  "text": "string",
  "target_language": "string",
  "source_language": "auto"
}
```

**Parameters:**
- `text` (required): Text to translate
- `target_language` (required): Target language code
- `source_language` (optional): Source language code or "auto" for auto-detection (default: "auto")

**Response:**
```json
{
  "original_text": "string",
  "translated_text": "string",
  "source_language": "string",
  "target_language": "string"
}
```

**Example:**
```bash
curl -X POST https://api.imigo.tw/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how can I help you?",
    "target_language": "id",
    "source_language": "en"
  }'
```

**Response:**
```json
{
  "original_text": "Hello, how can I help you?",
  "translated_text": "Halo, bagaimana saya bisa membantu Anda?",
  "source_language": "en",
  "target_language": "id"
}
```

### GET /api/translate/languages
Get list of supported languages.

**Response:**
```json
{
  "languages": {
    "id": "Indonesian (Bahasa Indonesia)",
    "zh": "Traditional Chinese (繁體中文)",
    "en": "English",
    "vi": "Vietnamese (Tiếng Việt)",
    "th": "Thai (ภาษาไทย)",
    "fil": "Tagalog (Filipino)"
  }
}
```

**Example:**
```bash
curl https://api.imigo.tw/api/translate/languages
```

---

## System API

### GET /api/system/health
Detailed health check with timestamp.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T12:00:00.000000",
  "service": "imigo-linebot"
}
```

### GET /api/system/info
Get system and bot information.

**Response:**
```json
{
  "bot": {
    "name": "IMIGO",
    "language": "id",
    "country": "Indonesia"
  },
  "version": "1.0.0",
  "timestamp": "2025-01-17T12:00:00.000000"
}
```

### GET /api/system/stats
Get service statistics.

**Response:**
```json
{
  "status": "operational",
  "timestamp": "2025-01-17T12:00:00.000000"
}
```

---

## LINE Webhook

### POST /webhook
LINE Bot webhook endpoint for receiving events from LINE platform.

**Headers:**
- `X-Line-Signature`: Signature for request validation

This endpoint is used internally by LINE platform and should not be called directly.

---

## Interactive API Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: https://api.imigo.tw/api/docs
- **ReDoc**: https://api.imigo.tw/api/redoc

---

## Rate Limiting

The API implements rate limiting:
- **Average**: 100 requests per minute
- **Burst**: 50 requests

If you exceed the rate limit, you'll receive a `429 Too Many Requests` response.

---

## CORS

The API allows Cross-Origin Resource Sharing (CORS) from all origins. In production, this should be restricted to specific domains.

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## SDKs and Libraries

### JavaScript/TypeScript

```javascript
// Example: Send a chat message
async function sendMessage(userId, message, language = 'id') {
  const response = await fetch('https://api.imigo.tw/api/chat/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      message: message,
      language: language,
    }),
  });

  return await response.json();
}

// Usage
const result = await sendMessage('user123', 'Bagaimana cara apply visa?', 'id');
console.log(result.response);
```

### Python

```python
import requests

def send_message(user_id: str, message: str, language: str = "id"):
    response = requests.post(
        "https://api.imigo.tw/api/chat/message",
        json={
            "user_id": user_id,
            "message": message,
            "language": language,
        }
    )
    return response.json()

# Usage
result = send_message("user123", "Bagaimana cara apply visa?", "id")
print(result["response"])
```

### cURL

```bash
# Send a message
curl -X POST https://api.imigo.tw/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Saya butuh bantuan",
    "language": "id"
  }'

# Translate text
curl -X POST https://api.imigo.tw/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Good morning",
    "target_language": "id"
  }'
```

---

## Support

For issues or questions:
- Check the interactive documentation at https://api.imigo.tw/api/docs
- Review the deployment guide in DEPLOYMENT.md
- Check service logs: `docker-compose logs -f backend`
