# API Endpoints Reference

Complete reference for all AgentOrchestra API endpoints with request parameters, response examples, and error codes.

---

## Table of Contents

- [Chat API](#chat-api)
  - [Send a Chat Message](#post-apiv1chat)
  - [Stream Chat Response](#get-apiv1chatstream)
  - [Get Conversation History](#get-apiv1chathistory)
- [Agent API](#agent-api)
  - [List All Agents](#get-apiv1agents)
  - [Get Agent Details](#get-apiv1agentsagent_id)
  - [Update Agent Configuration](#post-apiv1agentsagent_idconfig)
- [Task API](#task-api)
  - [Create a Task](#post-apiv1tasks)
  - [List All Tasks](#get-apiv1tasks)
  - [Get Task Details](#get-apiv1taskstask_id)
- [Health API](#health-api)
  - [Health Check](#get-health)
  - [Root Endpoint](#get-)

---

## Chat API

### `POST /api/v1/chat`

Send a chat message and receive a response from the multi-agent system.

**Summary:** Process a chat message through the full orchestration pipeline.

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | `string` | Yes | -- | The user's message content (min: 1 char) |
| `conversation_id` | `string` | No | Auto-generated | Conversation ID for continuing a conversation |
| `stream` | `boolean` | No | `false` | Whether to stream the response via SSE |
| `model_override` | `string` | No | `null` | Override the default LLM provider (`openai`, `anthropic`, `ollama`) |
| `agent_override` | `string` | No | `null` | Override agent routing (bypass orchestration) |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a REST API with FastAPI that manages a todo list",
    "model_override": "openai"
  }'
```

**Response (200 OK):**

```json
{
  "message": "I've created a comprehensive REST API for a todo management system using FastAPI. The API includes CRUD operations, input validation, and proper error handling.",
  "conversation_id": "a1b2c3d4e5f6",
  "agent_messages": [
    {
      "id": "msg_001",
      "agent_name": "planner",
      "agent_role": "planner",
      "content": "## Task Analysis\nBuild a REST API for todo management...\n\n## Execution Plan\n1. Define data models\n2. Implement CRUD endpoints\n3. Add validation\n4. Add error handling",
      "message_type": "plan",
      "timestamp": "2025-01-15T10:30:00Z",
      "execution_time_ms": 1523.4,
      "tools_used": [],
      "confidence": null,
      "metadata": {}
    },
    {
      "id": "msg_002",
      "agent_name": "researcher",
      "agent_role": "researcher",
      "content": "## Research Summary\nFastAPI best practices for REST APIs...",
      "message_type": "text",
      "timestamp": "2025-01-15T10:30:02Z",
      "execution_time_ms": 2100.0,
      "tools_used": ["search"],
      "confidence": null,
      "metadata": {}
    },
    {
      "id": "msg_003",
      "agent_name": "coder",
      "agent_role": "coder",
      "content": "## Implementation\n```python\nfrom fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass TodoItem(BaseModel):\n    id: int\n    title: str\n    completed: bool = False\n\n# ... endpoints ...\n```",
      "message_type": "code",
      "timestamp": "2025-01-15T10:30:05Z",
      "execution_time_ms": 3200.0,
      "tools_used": [],
      "confidence": null,
      "metadata": {}
    },
    {
      "id": "msg_004",
      "agent_name": "reviewer",
      "agent_role": "reviewer",
      "content": "## Review Summary\nCode quality: Good\n- Proper use of Pydantic models\n- Missing pagination on list endpoint\n- Consider adding authentication\n\n## Decision: APPROVED",
      "message_type": "review",
      "timestamp": "2025-01-15T10:30:08Z",
      "execution_time_ms": 1800.0,
      "tools_used": [],
      "confidence": null,
      "metadata": {}
    },
    {
      "id": "msg_005",
      "agent_name": "summarizer",
      "agent_role": "summarizer",
      "content": "## Summary\nSuccessfully created a FastAPI-based REST API for todo management...",
      "message_type": "summary",
      "timestamp": "2025-01-15T10:30:10Z",
      "execution_time_ms": 1200.0,
      "tools_used": [],
      "confidence": null,
      "metadata": {}
    }
  ],
  "task_result": {
    "id": "result_abc123",
    "task_id": "123456789",
    "summary": "Successfully created a FastAPI-based REST API...",
    "outputs": {
      "planner": "## Task Analysis...",
      "researcher": "## Research Summary...",
      "coder": "## Implementation...",
      "reviewer": "## Review Summary...",
      "summarizer": "## Summary..."
    },
    "code_artifacts": [],
    "status": "success",
    "total_execution_time_ms": 12543.2,
    "created_at": "2025-01-15T10:30:10Z"
  }
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `422` | Missing `message` field | `{"detail": [{"loc": ["body", "message"], "msg": "field required", "type": "value_error.missing"}]}` |
| `500` | Orchestration failed | `{"detail": "Processing failed: OpenAI API rate limit exceeded"}` |

---

### `GET /api/v1/chat/stream`

Stream a chat response via Server-Sent Events (SSE).

**Summary:** Send a message and receive real-time streaming output from each agent as they complete.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | `string` | Yes | -- | The user's message |
| `conversation_id` | `string` | No | Auto-generated | Conversation ID |
| `model_override` | `string` | No | `null` | LLM provider override |

**Example Request:**

```bash
curl -N http://localhost:8000/api/v1/chat/stream?message="Build%20a%20todo%20API"
```

**Response (200 OK):**

SSE stream with the following event types:

```
event: agent_complete
data: {"event": "agent_complete", "agent": "planner", "content": "## Task Analysis...", "timestamp": 1705312200.0}

event: agent_complete
data: {"event": "agent_complete", "agent": "researcher", "content": "## Research Summary...", "timestamp": 1705312202.0}

event: agent_complete
data: {"event": "agent_complete", "agent": "coder", "content": "## Implementation...", "timestamp": 1705312205.0}

event: agent_complete
data: {"event": "agent_complete", "agent": "reviewer", "content": "## Review...", "timestamp": 1705312208.0}

event: agent_complete
data: {"event": "agent_complete", "agent": "summarizer", "content": "## Summary...", "timestamp": 1705312210.0}

event: workflow_complete
data: {"event": "workflow_complete", "execution_time_ms": 12543.2, "timestamp": 1705312210.0}
```

**SSE Event Types:**

| Event | Description |
|-------|-------------|
| `agent_complete` | An agent has finished executing. Includes agent name and content. |
| `workflow_complete` | The entire workflow has finished. Includes total execution time. |
| `error` | An error occurred during execution. Includes error message. |

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `500` | Stream initialization failed | `{"detail": "Stream init failed: ..."}` |

---

### `GET /api/v1/chat/history`

Get conversation history.

**Summary:** Retrieve conversation history for a specific conversation or list all recent conversations.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `conversation_id` | `string` | No | `null` | Specific conversation ID. If omitted, returns all conversations. |
| `limit` | `int` | No | `20` | Maximum number of conversations to return |

**Example Request:**

```bash
# Get a specific conversation
curl http://localhost:8000/api/v1/chat/history?conversation_id=a1b2c3d4e5f6

# List all conversations
curl http://localhost:8000/api/v1/chat/history?limit=10
```

**Response - Single Conversation (200 OK):**

```json
{
  "conversation_id": "a1b2c3d4e5f6",
  "data": {
    "request": {
      "message": "Build a REST API with FastAPI",
      "conversation_id": "a1b2c3d4e5f6",
      "stream": false,
      "model_override": "openai",
      "agent_override": null
    },
    "response": {
      "message": "I've created a comprehensive REST API...",
      "conversation_id": "a1b2c3d4e5f6",
      "agent_messages": [...],
      "task_result": {...}
    }
  }
}
```

**Response - All Conversations (200 OK):**

```json
{
  "conversations": [
    {
      "conversation_id": "a1b2c3d4e5f6",
      "data": {
        "request": {...},
        "response": {...}
      }
    },
    {
      "conversation_id": "f6e5d4c3b2a1",
      "data": {
        "request": {...},
        "response": {...}
      }
    }
  ],
  "total": 2
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `404` | Conversation not found | `{"detail": "Conversation 'xyz' not found"}` |

---

## Agent API

### `GET /api/v1/agents`

List all registered agents.

**Summary:** Get information about all agents in the system, including their type, description, status, and available tools.

**Query Parameters:** None

**Example Request:**

```bash
curl http://localhost:8000/api/v1/agents
```

**Response (200 OK):**

```json
[
  {
    "name": "planner",
    "agent_type": "planner",
    "description": "Analyzes tasks and creates structured execution plans",
    "status": "idle",
    "tools": [],
    "execution_count": 0
  },
  {
    "name": "researcher",
    "agent_type": "researcher",
    "description": "Gathers relevant information and research context",
    "status": "idle",
    "tools": ["search"],
    "execution_count": 0
  },
  {
    "name": "coder",
    "agent_type": "coder",
    "description": "Generates code and technical solutions",
    "status": "idle",
    "tools": ["code_executor"],
    "execution_count": 0
  },
  {
    "name": "reviewer",
    "agent_type": "reviewer",
    "description": "Reviews code quality and provides feedback",
    "status": "idle",
    "tools": [],
    "execution_count": 0
  },
  {
    "name": "summarizer",
    "agent_type": "summarizer",
    "description": "Compiles comprehensive final summaries",
    "status": "idle",
    "tools": [],
    "execution_count": 0
  }
]
```

---

### `GET /api/v1/agents/{agent_id}`

Get detailed information about a specific agent.

**Summary:** Retrieve detailed information about a single agent by its name/identifier.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `string` | Yes | Agent name/identifier (e.g., `planner`, `coder`) |

**Example Request:**

```bash
curl http://localhost:8000/api/v1/agents/coder
```

**Response (200 OK):**

```json
{
  "name": "coder",
  "agent_type": "coder",
  "description": "Generates code and technical solutions based on plans and research",
  "status": "idle",
  "tools": ["code_executor"],
  "execution_count": 42
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `404` | Agent not found | `{"detail": "Agent 'unknown_agent' not found"}` |

---

### `POST /api/v1/agents/{agent_id}/config`

Update an agent's runtime configuration.

**Summary:** Dynamically update an agent's configuration including model, temperature, system prompt, and tools.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `string` | Yes | Agent name/identifier |

**Request Body:**

All fields are optional. Only provided fields will be updated.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `model` | `string` | No | -- | New LLM model name |
| `temperature` | `float` | No | `0.0 - 2.0` | New sampling temperature |
| `max_tokens` | `int` | No | `1 - 128000` | New max tokens per response |
| `system_prompt` | `string` | No | -- | New system prompt template |
| `tools` | `list[string]` | No | -- | New list of available tool names |
| `max_retries` | `int` | No | `0 - 10` | New maximum retry attempts |
| `timeout_seconds` | `int` | No | `10 - 600` | New execution timeout |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/agents/coder/config \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "temperature": 0.3,
    "max_tokens": 8192,
    "system_prompt": "You are an expert Python developer. Write clean, production-ready code."
  }'
```

**Response (200 OK):**

```json
{
  "agent_id": "coder",
  "updated_fields": ["model", "temperature", "max_tokens", "system_prompt"],
  "config": {
    "model": "gpt-4o",
    "temperature": 0.3,
    "max_tokens": 8192,
    "system_prompt": "You are an expert Python developer. Write clean, production-ready code."
  }
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `404` | Agent not found | `{"detail": "Agent 'unknown' not found"}` |
| `422` | Invalid field value | `{"detail": [{"loc": ["body", "temperature"], "msg": "ensure this value is less than or equal to 2.0"}]}` |
| `500` | Configuration update failed | `{"detail": "Configuration update failed: ..."}` |

---

## Task API

### `POST /api/v1/tasks`

Create and execute a new multi-agent task.

**Summary:** Create a task that runs through the full orchestration pipeline and returns the result.

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | `string` | Yes | -- | Task description (min: 1 char) |
| `model_override` | `string` | No | `null` | LLM provider override |
| `priority` | `string` | No | `medium` | Task priority (`low`, `medium`, `high`) |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the current trends in AI agent frameworks",
    "priority": "high"
  }'
```

**Response (201 Created):**

```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0",
  "message": "Analyze the current trends in AI agent frameworks",
  "status": "completed",
  "priority": "high",
  "result": {
    "id": "result_xyz789",
    "task_id": "123456789",
    "summary": "The analysis reveals several key trends in AI agent frameworks...",
    "outputs": {
      "planner": "## Analysis Plan\n1. Identify key frameworks\n2. Compare approaches\n3. Analyze trends",
      "researcher": "## Research Findings\n- LangGraph: Stateful workflows\n- AutoGen: Multi-agent conversations\n- CrewAI: Role-based agents",
      "coder": "## Analysis Data\n[Structured comparison of frameworks]",
      "reviewer": "## Review\nAnalysis is comprehensive and well-structured.",
      "summarizer": "## Summary\nKey trends include: stateful orchestration, multi-agent collaboration, and tool integration."
    },
    "code_artifacts": [],
    "status": "success",
    "total_execution_time_ms": 18500.0,
    "created_at": "2025-01-15T10:35:00Z"
  },
  "created_at": "2025-01-15T10:35:00Z",
  "completed_at": "2025-01-15T10:35:19Z"
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `422` | Missing `message` field | `{"detail": [{"loc": ["body", "message"], "msg": "field required", "type": "value_error.missing"}]}` |
| `500` | Task execution failed | `{"detail": "Task execution failed: ..."}` |

---

### `GET /api/v1/tasks`

List all tasks with optional filtering.

**Summary:** Retrieve a paginated list of all tasks, optionally filtered by status.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | `string` | No | `null` | Filter by status: `pending`, `processing`, `completed`, `failed` |
| `limit` | `int` | No | `50` | Maximum tasks to return |
| `offset` | `int` | No | `0` | Number of tasks to skip |

**Example Request:**

```bash
# List all tasks
curl http://localhost:8000/api/v1/tasks

# List only completed tasks
curl "http://localhost:8000/api/v1/tasks?status=completed&limit=10"

# Pagination
curl "http://localhost:8000/api/v1/tasks?offset=10&limit=10"
```

**Response (200 OK):**

```json
[
  {
    "id": "a1b2c3d4e5f6",
    "message": "Build a REST API with FastAPI",
    "status": "completed",
    "priority": "medium",
    "result": {
      "id": "result_abc",
      "task_id": "123456",
      "summary": "Successfully created a REST API...",
      "outputs": {...},
      "code_artifacts": [],
      "status": "success",
      "total_execution_time_ms": 12543.2,
      "created_at": "2025-01-15T10:30:10Z"
    },
    "created_at": "2025-01-15T10:30:00Z",
    "completed_at": "2025-01-15T10:30:15Z"
  },
  {
    "id": "f6e5d4c3b2a1",
    "message": "Analyze market trends",
    "status": "failed",
    "priority": "high",
    "result": null,
    "created_at": "2025-01-15T10:25:00Z",
    "completed_at": null
  }
]
```

---

### `GET /api/v1/tasks/{task_id}`

Get detailed information about a specific task.

**Summary:** Retrieve the full details and result of a specific task by its ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | `string` | Yes | Unique task identifier |

**Example Request:**

```bash
curl http://localhost:8000/api/v1/tasks/a1b2c3d4e5f6
```

**Response (200 OK):**

```json
{
  "id": "a1b2c3d4e5f6",
  "message": "Build a REST API with FastAPI",
  "status": "completed",
  "priority": "medium",
  "result": {
    "id": "result_abc123",
    "task_id": "123456789",
    "summary": "Successfully created a comprehensive REST API for todo management...",
    "outputs": {
      "planner": "## Task Analysis\n...",
      "researcher": "## Research Summary\n...",
      "coder": "## Implementation\n...",
      "reviewer": "## Review Summary\n...",
      "summarizer": "## Summary\n..."
    },
    "code_artifacts": [
      {
        "filename": "main.py",
        "language": "python",
        "content": "from fastapi import FastAPI..."
      }
    ],
    "status": "success",
    "total_execution_time_ms": 12543.2,
    "created_at": "2025-01-15T10:30:10Z"
  },
  "created_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:30:15Z"
}
```

**Error Responses:**

| Status | Condition | Response |
|--------|-----------|----------|
| `404` | Task not found | `{"detail": "Task 'nonexistent_id' not found"}` |

---

## Health API

### `GET /health`

Health check endpoint for monitoring and load balancers.

**Summary:** Returns the service health status, application name, and version.

**Example Request:**

```bash
curl http://localhost:8000/health
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "app": "AgentOrchestra",
  "version": "0.1.0"
}
```

---

### `GET /`

Root endpoint with API information.

**Summary:** Returns basic API information and links to documentation.

**Example Request:**

```bash
curl http://localhost:8000/
```

**Response (200 OK):**

```json
{
  "name": "AgentOrchestra",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```
