# API Documentation

This document provides an overview of the AgentOrchestra REST API, including authentication, request/response formats, error handling, and rate limiting.

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Request Format](#request-format)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Interactive Documentation](#interactive-documentation)
- [API Versioning](#api-versioning)

---

## Overview

The AgentOrchestra API is a RESTful API built with FastAPI. It provides endpoints for:

| Domain | Description |
|--------|-------------|
| **Chat** | Send messages, stream responses, retrieve conversation history |
| **Agents** | List agents, get agent details, update agent configuration |
| **Tasks** | Create tasks, list tasks, get task details |
| **Health** | Service health check |

All API endpoints are prefixed with `/api/v1` and return JSON responses.

---

## Authentication

### Current Status

The current version (v0.1.0) does not enforce authentication. This is suitable for development and internal deployments.

### Planned Authentication

Future versions will support:

| Method | Description |
|--------|-------------|
| **API Key** | Simple API key passed via `Authorization: Bearer <key>` header |
| **OAuth 2.0** | Full OAuth 2.0 flow for third-party integrations |
| **JWT** | JSON Web Tokens for session-based authentication |

### Security Note

> **Warning:** In production, always deploy behind a reverse proxy (Nginx) with TLS termination and implement authentication. Never expose the API directly to the public internet without authentication.

---

## Base URL

| Environment | Base URL |
|-------------|----------|
| **Local Development** | `http://localhost:8000` |
| **Docker (Nginx)** | `http://localhost` |
| **Production** | `https://your-domain.com` |

All API endpoints are relative to the base URL:

```
{BASE_URL}/api/v1/{endpoint}
```

---

## Request Format

### Content Type

All `POST` and `PUT` requests must use `Content-Type: application/json`.

### Query Parameters

`GET` requests use standard URL query parameters:

```
GET /api/v1/chat/stream?message=Hello&conversation_id=abc123
```

### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes (POST/PUT) | `application/json` |
| `Accept` | No | `application/json` (default) |
| `Authorization` | No (planned) | `Bearer <token>` |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a REST API for a todo application",
    "stream": false,
    "model_override": "openai"
  }'
```

---

## Response Format

### Success Response

All successful responses follow a consistent JSON format:

```json
{
  "message": "Task completed successfully.",
  "conversation_id": "abc123def456",
  "agent_messages": [
    {
      "id": "msg_001",
      "agent_name": "planner",
      "agent_role": "planner",
      "content": "## Execution Plan\n1. ...",
      "message_type": "plan",
      "timestamp": "2025-01-15T10:30:00Z",
      "execution_time_ms": 1523.4
    }
  ],
  "task_result": {
    "id": "result_001",
    "task_id": "123456789",
    "summary": "Successfully created a REST API...",
    "outputs": {
      "planner": "...",
      "researcher": "...",
      "coder": "...",
      "reviewer": "...",
      "summarizer": "..."
    },
    "code_artifacts": [],
    "status": "success",
    "total_execution_time_ms": 12543.2,
    "created_at": "2025-01-15T10:30:15Z"
  }
}
```

### Response Headers

| Header | Description |
|--------|-------------|
| `Content-Type` | `application/json` |
| `X-Process-Time` | Request processing time in milliseconds |

### Pagination

List endpoints support pagination via query parameters:

```
GET /api/v1/tasks?limit=20&offset=0
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `50` | Maximum items per page (max: 100) |
| `offset` | `int` | `0` | Number of items to skip |

---

## Error Handling

### Error Response Format

All errors return a consistent JSON structure:

```json
{
  "detail": "Error description message"
}
```

For validation errors (HTTP 422), the response includes field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| `200 OK` | Success | Request completed successfully |
| `201 Created` | Created | Resource was created successfully |
| `400 Bad Request` | Invalid Request | Malformed request syntax or invalid parameters |
| `401 Unauthorized` | Unauthorized | Authentication required (planned) |
| `403 Forbidden` | Forbidden | Insufficient permissions (planned) |
| `404 Not Found` | Not Found | Requested resource does not exist |
| `422 Unprocessable Entity` | Validation Error | Request body failed validation |
| `429 Too Many Requests` | Rate Limited | Too many requests in a given time period |
| `500 Internal Server Error` | Server Error | Unexpected server-side error |

### Error Scenarios

| Scenario | Status Code | Example |
|----------|-------------|---------|
| Agent not found | `404` | `{"detail": "Agent 'unknown' not found"}` |
| Task not found | `404` | `{"detail": "Task 'abc123' not found"}` |
| Conversation not found | `404` | `{"detail": "Conversation 'xyz789' not found"}` |
| Missing required field | `422` | `{"detail": [{"loc": ["body", "message"], "msg": "field required"}]}` |
| Invalid field value | `422` | `{"detail": [{"loc": ["body", "temperature"], "msg": "ensure this value is less than or equal to 2.0"}]}` |
| LLM provider error | `500` | `{"detail": "Processing failed: OpenAI API rate limit exceeded"}` |
| Unknown LLM provider | `500` | `{"detail": "Processing failed: Unknown LLM provider: 'gemini'"}` |

---

## Rate Limiting

### Current Status

Rate limiting is not enforced in the current version (v0.1.0). It is planned for a future release.

### Planned Rate Limits

| Tier | Requests/Minute | Description |
|------|----------------|-------------|
| Free | 30 | Community / open-source users |
| Standard | 100 | Registered users |
| Premium | 500 | Paid subscribers |
| Enterprise | Custom | Contact sales |

Rate limit headers will be included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800
```

When rate limited, the API returns:

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after": 30
}
```

---

## Interactive Documentation

AgentOrchestra provides two auto-generated API documentation interfaces:

### Swagger UI

Access the interactive API explorer at:

```
http://localhost:8000/docs
```

Features:
- Try-it-out functionality for all endpoints
- Request/response schemas
- Example values
- Authentication support (when implemented)

### ReDoc

Access the alternative documentation view at:

```
http://localhost:8000/redoc
```

Features:
- Clean, readable layout
- Search functionality
- Code sample generation
- Schema visualization

---

## API Versioning

The API uses URL path versioning:

```
/api/v1/chat
/api/v2/chat  (future)
```

### Versioning Policy

| Policy | Description |
|--------|-------------|
| **Backward Compatibility** | Minor versions will not break existing clients |
| **Deprecation Period** | Deprecated endpoints will be supported for at least 2 minor versions |
| **Breaking Changes** | Only introduced in major version bumps |
| **Migration Guide** | Provided with every breaking change |

### Current Version

| Version | Status | Notes |
|---------|--------|-------|
| `v1` | Current | Initial API release |

---

## Next Steps

For the complete endpoint reference with request/response examples, see:

- [API Endpoints Reference](endpoints.md) -- Detailed documentation for every endpoint
