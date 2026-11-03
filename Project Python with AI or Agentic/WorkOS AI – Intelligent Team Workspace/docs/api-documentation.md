# WorkOS AI – REST & WebSocket API Specification

## 1. Overview & Conventions

- **Base URL**: `https://api.workos-ai.local/api/v1` (Development: `http://localhost:8000/api/v1`)
- **Protocol**: HTTPS / WSS
- **Content Type**: `application/json`
- **Authentication**: Bearer Token in HTTP Authorization Header:
  `Authorization: Bearer <access_token>`
- **Tenant Context**:
  `X-Workspace-ID: <workspace_uuid>` or via URL path parameter `/{workspace_id}`

---

## 2. Authentication & User Management

### 2.1 Register New User
- **Method**: `POST`
- **Endpoint**: `/auth/register`
- **Request Body**:
```json
{
  "email": "sarah.lead@company.com",
  "password": "SecurePassword123!",
  "full_name": "Sarah Connor"
}
```
- **Response (201 Created)**:
```json
{
  "user": {
    "id": "e2a149c4-0678-45a8-bcf9-42b3fe30485a",
    "email": "sarah.lead@company.com",
    "full_name": "Sarah Connor",
    "avatar_url": null,
    "created_at": "2026-11-02T14:40:00Z"
  },
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### 2.2 Login User
- **Method**: `POST`
- **Endpoint**: `/auth/login`
- **Request Body**:
```json
{
  "email": "sarah.lead@company.com",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK)**:
```json
{
  "user": {
    "id": "e2a149c4-0678-45a8-bcf9-42b3fe30485a",
    "email": "sarah.lead@company.com",
    "full_name": "Sarah Connor"
  },
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### 2.3 Get Current User Profile
- **Method**: `GET`
- **Endpoint**: `/auth/me`
- **Response (200 OK)**: Returns authenticated user profile and list of joined workspaces.

---

## 3. Workspace Management

### 3.1 List User Workspaces
- **Method**: `GET`
- **Endpoint**: `/workspaces`
- **Response (200 OK)**: List of workspaces where current user is a member.

### 3.2 Create Workspace
- **Method**: `POST`
- **Endpoint**: `/workspaces`
- **Request Body**:
```json
{
  "name": "Acme Engineering",
  "slug": "acme-eng"
}
```
- **Response (201 Created)**: Returns workspace object with creator assigned as `owner`.

### 3.3 Invite Member to Workspace
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/members/invite`
- **Request Body**:
```json
{
  "email": "engineer@company.com",
  "role": "member"
}
```

---

## 4. Projects & Tasks

### 4.1 List Workspace Projects
- **Method**: `GET`
- **Endpoint**: `/workspaces/{workspace_id}/projects`
- **Query Params**: `status` (optional), `page`, `page_size`

### 4.2 Create Project
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/projects`
- **Request Body**:
```json
{
  "name": "E-Commerce App Launch",
  "description": "8-week high velocity platform launch",
  "target_date": "2026-12-28",
  "lead_id": "e2a149c4-..."
}
```

### 4.3 List Project Tasks (Kanban / List)
- **Method**: `GET`
- **Endpoint**: `/workspaces/{workspace_id}/projects/{project_id}/tasks`
- **Response (200 OK)**: Tasks grouped by status (`todo`, `in_progress`, `review`, `completed`, `blocked`).

### 4.4 Create Task
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/projects/{project_id}/tasks`
- **Request Body**:
```json
{
  "title": "Design Database Schema & Models",
  "description": "Create PostgreSQL relational schema and initial migrations.",
  "status": "todo",
  "priority": "high",
  "assignee_id": "e2a149c4-...",
  "due_date": "2026-11-10",
  "estimated_hours": 16,
  "dependencies": ["4d5e6f..."]
}
```

### 4.5 Update Task Status (Drag-and-Drop)
- **Method**: `PATCH`
- **Endpoint**: `/workspaces/{workspace_id}/tasks/{task_id}/status`
- **Request Body**:
```json
{
  "status": "in_progress"
}
```

---

## 5. AI Planning & ReAct Agent

### 5.1 Generate Project Plan from Brief
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/ai/plan`
- **Request Body**:
```json
{
  "brief": "Build an e-commerce application within 8 weeks including Stripe payments, product catalog, cart, and authentication.",
  "target_weeks": 8
}
```
- **Response (200 OK)**:
```json
{
  "action_audit_id": "f8a42b10-...",
  "status": "pending_approval",
  "plan": {
    "project_name": "E-Commerce Platform",
    "summary": "Full-stack e-commerce application implementation",
    "milestones": [
      {
        "title": "Phase 1: Architecture & Foundation",
        "week_number": 1,
        "tasks": [
          {
            "temp_id": "t1",
            "title": "Database Schema & Auth Setup",
            "priority": "high",
            "estimated_hours": 24,
            "depends_on": []
          },
          {
            "temp_id": "t2",
            "title": "Stripe Integration Service",
            "priority": "urgent",
            "estimated_hours": 32,
            "depends_on": ["t1"]
          }
        ]
      }
    ],
    "identified_risks": [
      "Payment gateway compliance and webhook latency may impact checkout flow."
    ]
  }
}
```

### 5.2 Approve Staged AI Action
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/ai/actions/{action_audit_id}/approve`
- **Response (200 OK)**: Generates and commits all project entities to the database in an atomic transaction.

### 5.3 Workspace RAG Semantic Search
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/ai/rag/query`
- **Request Body**:
```json
{
  "query": "What are our current blockers in the backend infrastructure?"
}
```
- **Response (200 OK)**:
```json
{
  "answer": "The backend project currently has 2 critical blockers: (1) Stripe webhook testing is awaiting SSL certificate setup, and (2) Database migration script for Task #42 is failing due to foreign key deadlock.",
  "sources": [
    {
      "entity_type": "task",
      "entity_id": "3b2c1a...",
      "title": "Stripe Webhook Gateway",
      "snippet": "Status: blocked. Blocker reason: Missing SSL test domain."
    }
  ]
}
```

---

## 6. Meeting Intelligence

### 6.1 Create Meeting & Ingest Transcript
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/meetings`
- **Request Body**:
```json
{
  "title": "Sprint 3 Planning & Sync",
  "project_id": "5a4b3c...",
  "raw_transcript": "Sarah: Let's finalize the checkout flow by Friday. John, can you take care of the cart state bug? John: Yes, I will finish it before Thursday."
}
```

### 6.2 Extract Action Items & Key Decisions
- **Method**: `POST`
- **Endpoint**: `/workspaces/{workspace_id}/meetings/{meeting_id}/analyze`
- **Response (200 OK)**:
```json
{
  "summary": "Team aligned on finalizing checkout and fixing cart bug.",
  "decisions": [
    "Checkout flow completion deadline set to Friday."
  ],
  "suggested_tasks": [
    {
      "action_text": "Fix cart state synchronization bug",
      "suggested_due_date": "2026-11-06",
      "suggested_assignee": "John Doe",
      "confidence": 0.94
    }
  ]
}
```

---

## 7. Analytics & Project Risk Engine

### 7.1 Get Project Health & Risks
- **Method**: `GET`
- **Endpoint**: `/workspaces/{workspace_id}/projects/{project_id}/risks`
- **Response (200 OK)**:
```json
{
  "health_score": 78,
  "risk_level": "medium",
  "summary": "Project is 4 days behind schedule due to upstream payment gateway delays.",
  "delayed_tasks_count": 3,
  "blocked_tasks_count": 1,
  "critical_path_bottlenecks": [
    {
      "task_id": "4e5f6a...",
      "title": "Stripe Webhook Gateway",
      "impact": "Blocks 4 downstream tasks (Checkout UI, Order Email, Invoice Generation)"
    }
  ],
  "recommended_actions": [
    "Reallocate 1 backend engineer to resolve Stripe webhook endpoint by Nov 5."
  ]
}
```

---

## 8. Real-Time WebSockets

### Connection
- **Endpoint**: `ws://localhost:8000/api/v1/ws/{workspace_id}?token={access_token}`

### Inbound Events
```json
{
  "event": "presence.heartbeat",
  "data": {
    "active_page": "/projects/ecommerce/board"
  }
}
```

### Outbound Events
```json
{
  "event": "task.moved",
  "data": {
    "task_id": "8a7b6c...",
    "old_status": "todo",
    "new_status": "in_progress",
    "user_id": "e2a149c4...",
    "user_name": "Sarah Connor",
    "timestamp": "2026-11-02T14:45:00Z"
  }
}
```

