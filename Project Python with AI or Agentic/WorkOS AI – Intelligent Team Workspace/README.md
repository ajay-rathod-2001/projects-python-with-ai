# WorkOS AI – Intelligent Team Workspace

> **An AI-powered Operating System for Teams that converts unstructured workspace activity into structured project graphs, predicts delivery risks, performs semantic RAG retrieval, and executes human-in-the-loop AI actions.**

---

## 🌟 Overview & Architecture

WorkOS AI brings together project management (Jira), document workspace (Notion), and team collaboration (Lark) powered by an autonomous ReAct AI layer:
- **Intelligent Planning**: Turn natural-language project briefs into multi-phase milestone and task graphs with durations and cross-task dependencies.
- **Strict Multi-Tenant Isolation**: Enforced at the middleware, relational DB, and vector search layers.
- **Risk Detection Engine**: Continuously assesses critical paths, deadline slippage, and upstream blockers.
- **Meeting Intelligence**: Parses transcripts into key decisions, action items, and auto-generated tasks.
- **Workspace RAG**: Context-aware semantic search over project specs, meeting notes, and task comments using PostgreSQL `pgvector`.
- **Human-in-the-Loop AI**: Write actions are safely staged in `pending_approval` state until explicitly authorized by a human workspace administrator.

---

## 📁 Repository Structure

```plaintext
WorkOS-AI/
├── docs/                      # Architectural specs & API definitions
│   ├── architecture.md        # Deep-dive architecture & data models
│   └── api-documentation.md   # Complete REST & WebSocket specification
├── frontend/                  # React + TypeScript SPA
│   ├── public/                # Static assets & index.html
│   └── src/
│       ├── assets/            # SVG icons, illustrations
│       ├── components/        # Reusable UI & domain components
│       │   ├── common/        # Buttons, Modals, Badges, Search
│       │   ├── dashboard/     # Metric cards, Activity feeds
│       │   ├── projects/      # Project cards, Timelines
│       │   ├── tasks/         # Drag-and-drop Kanban board
│       │   ├── ai-assistant/  # Brief planner & RAG chat drawer
│       │   └── ui/            # Base primitives (Shadcn style)
│       ├── pages/             # Route views (Dashboard, Board, Meetings, Analytics)
│       ├── layouts/           # Sidebar & top navigation shell
│       ├── hooks/             # Custom React hooks (useWorkspace, useAuth, useWebSocket)
│       ├── services/          # Axios API clients & WebSocket connection handlers
│       ├── store/             # Zustand state stores (auth, workspace, tasks)
│       ├── types/             # TypeScript interfaces & enums
│       └── utils/             # Formatting, dates, error handlers
├── backend/                   # FastAPI + Python 3.11+
│   ├── app/
│   │   ├── api/               # API endpoints, dependencies, & WebSocket routers
│   │   │   ├── deps.py        # Auth & Tenant isolation dependencies
│   │   │   ├── v1/endpoints/  # Auth, Workspaces, Projects, Tasks, AI, Meetings, Risks
│   │   │   └── websockets/    # Real-time WebSocket connection manager & Redis bridge
│   │   ├── core/              # App config, JWT utilities, logging & exceptions
│   │   ├── database/          # Async SQLAlchemy engine & Redis client
│   │   ├── models/            # SQLAlchemy ORM models (Tenant-isolated)
│   │   ├── schemas/           # Pydantic schemas for request/response validation
│   │   ├── repositories/      # Data access layer with tenancy filters
│   │   ├── services/          # Core business logic
│   │   ├── agents/            # ReAct planning engine, RAG pipeline, and tools
│   │   ├── integrations/      # External adapters (GitHub OAuth & Webhooks)
│   │   └── workers/           # Celery async tasks & beat schedulers
│   ├── tests/                 # Pytest test suite
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container image
├── docker-compose.yml         # Full local orchestration (Postgres, Redis, Backend, Celery, Frontend)
├── .gitignore
└── README.md
```

---

## 📦 Single-File Standalone Windows Executable (.exe)

You can compile WorkOS AI into a **single, standalone `.exe` file (`WorkOS-AI.exe`)** to share with anyone on Windows. The recipient does not need Python, Node.js, or any database installed!

### How to Build the `.exe`:
1. Double-click [`build_exe.bat`](file:///c:/Users/ajayr/OneDrive/Docs/GitHub/Project%20Python%20with%20AI%20or%20Agentic/WorkOS%20AI%20–%20Intelligent%20Team%20Workspace/build_exe.bat) (or run `.\build_exe.bat` in your terminal).
2. PyInstaller packages the complete system into `WorkOS-AI.exe`.
3. Share the single `WorkOS-AI.exe` file with any Windows user!

---

## 🚀 Quickstart & How to Run (Single Command)

You only need **ONE** command to run everything:

```powershell
py main.py
```

This single master command presents a clean interactive menu to:
- **[1] Launch Web App**: Automatically boots FastAPI backend, React frontend, and opens [http://localhost:5173](http://localhost:5173) in your browser.
- **[2] Launch Desktop App**: Opens the native dark-mode Windows desktop GUI window.
- **[3] Launch Terminal CLI**: Opens the interactive terminal command center.
- **[4] Build Standalone .exe**: Compiles the entire system into a single `WorkOS-AI.exe` file.

You can also pass arguments directly:
```powershell
py main.py web        # Starts Web App + opens browser
py main.py desktop    # Starts Desktop GUI App
py main.py cli        # Starts Terminal CLI
py main.py build      # Compiles WorkOS-AI.exe
```

### Prerequisites
- Docker & Docker Compose **OR**
- Node.js 18+ & Python 3.11+
- PostgreSQL 16 with `pgvector` & Redis 7

### Running with Docker Compose (Recommended)

1. Clone the repository and copy the environment file:
   ```bash
   cp .env.example .env
   ```
2. Start all services:
   ```bash
   docker compose up --build
   ```
3. Access services:
   - **Frontend Web App**: [http://localhost:5173](http://localhost:5173)
   - **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **PostgreSQL**: `localhost:5432` (User: `workos`, DB: `workos_db`)
   - **Redis**: `localhost:6379`

---

## 🛡️ Multi-Tenant Security & Tenant Isolation

Every API request targeting workspace data is verified at the database access boundary:
- Request header `X-Workspace-ID` or path parameter is resolved by `get_current_workspace_member`.
- If the authenticated user does not have an active membership row in `workspace_members`, the request is halted with `403 Forbidden`.
- Vector embeddings and documents are indexed with compound tenant keys, preventing cross-tenant information disclosure during RAG context retrieval.

---

## 🤖 ReAct AI Agent Workflow

```
[User Brief] 
     │
     ▼
[ReAct Planner] ──► [Workspace Context Retrieval (RAG)]
     │
     ▼
[Structured Plan Generation] (Milestones, Tasks, Estimates, Dependencies)
     │
     ▼
[Pending Approval Stage] (Stored in AgentActionAudit)
     │
     ▼
[Human Confirmation by Workspace Admin] ──► [Atomic Commit to Postgres]
                                                    │
                                                    ▼
                                           [WebSocket Real-time Broadcast]
```

