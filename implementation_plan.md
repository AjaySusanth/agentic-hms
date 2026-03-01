# Implementation Plan: Agentic Hospital Management System

## Architecture Overview

### Design Philosophy: Hybrid Router (LangGraph-Style Pattern)

The system uses a **custom agent framework inspired by LangGraph's Graph pattern**, without depending on the LangGraph library. This gives us:

- **Deterministic steps** for safety-critical healthcare workflows (patient registration, queue management)
- **LLM-powered routing** for conversational flexibility (intent detection, pivot handling)
- **Zero external AI framework dependencies** (no LangChain/LangGraph library; pure Python + FastAPI)

### Why Custom over LangGraph Library

| Factor | LangGraph Library | Custom (LangGraph Pattern) |
|:---|:---|:---|
| **Latency** | Abstraction overhead (~50-100ms) | Direct Python calls (~0ms overhead) |
| **LLM Cost** | May trigger extra reasoning loops | Surgical: LLM only at routing decisions |
| **Persistence** | Opinionated checkpointer | Fits our existing `AgentSessionService` + PostgreSQL |
| **Stability** | Frequent breaking API changes | Plain Python — never breaks |
| **Resume Value** | "Used a library" | "Built the pattern from scratch" |

### Architecture Diagram

```
User Message
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              CHATBOT ORCHESTRATOR                    │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │  LLM Router  │───▶│  Deterministic Step Logic │   │
│  │ (should_pivot)│    │  (State Machine Engine)   │   │
│  └──────────────┘    └──────────────────────────┘   │
│         │                       │                    │
│    ┌────▼────┐            ┌────▼─────┐              │
│    │  EXIT   │            │  NORMAL  │              │
│    │  PIVOT  │            │  FLOW    │              │
│    │  HELP   │            │          │              │
│    └─────────┘            └──────────┘              │
└─────────────────────────────────────────────────────┘
     │
     ▼ (HTTP Proxy)
┌─────────────────┐
│ Registration    │
│ Agent           │
│ (Hospital-Scoped)│
└─────────────────┘
```

### Agent Communication Pattern

- **Chatbot ↔ Registration Agent**: HTTP Proxy via `HospitalClient`
- **Registration ↔ Queue Agent**: Internal function call (`handoff_to_queue_agent`)
- **Future**: Standardized Agent Protocol for external systems (Hotel Booking, etc.)

---

## Component Breakdown

### 1. Chatbot Orchestrator (`agents/chatbot/`)

| File | Purpose |
|:---|:---|
| `state.py` | `ChatbotOrchestratorState` — Pydantic model with step tracking, intent, hospital selection, proxy state |
| `agent.py` | `ChatbotOrchestratorAgent` — State machine with LLM Router for pivot detection |
| `intent_detector.py` | `detect_intent()` — LLM classifies user message into medical/hotel/general. `should_pivot()` — LLM checks if user is deviating from expected flow |
| `hospital_client.py` | `HospitalClient` — HTTP client to proxy messages to Registration Agent |
| `router.py` | FastAPI endpoints: `/session`, `/session/{id}/message`, `/session/{id}` |

### 2. Registration Agent (`agents/registration/`)

Hospital-scoped, deterministic registration workflow:
`COLLECT_PHONE → PATIENT_LOOKUP → COLLECT_DETAILS → COLLECT_SYMPTOMS → RESOLVE_DEPARTMENT → SELECT_DOCTOR → CREATE_VISIT → HANDOFF`

### 3. Multi-Tenancy Foundation

- `Hospital` model with `hospital_id` foreign key on all core models
- `HospitalService` for CRUD and search (by department, location)
- Data isolation enforced at the query level

---

## LLM Usage Strategy (Cost Optimization)

| LLM Call | When | Model | Est. Tokens |
|:---|:---|:---|:---|
| `detect_intent()` | Once per session (Step 3) | Llama 3.1-8B (Groq) | ~300 |
| `should_pivot()` | Before each step handler (if input is non-numeric/non-structured) | Llama 3.1-8B (Groq) | ~200 |
| `summarize_symptoms()` | Once during registration | Llama 3.1-8B (Groq) | ~200 |
| `resolve_department()` | Once during registration | Llama 3.1-8B (Groq) | ~150 |

**Total per full session**: ~850 tokens (~$0.0001 on Groq free tier)

---

## Scaling Roadmap

| Stage | Trigger | Architecture |
|:---|:---|:---|
| **Current (MVP)** | 1-5 hospitals | Monolith + HTTP Proxy |
| **Stage 2** | 10+ hospitals | Containerized per-hospital services |
| **Stage 3** | Async workflows (insurance, lab) | Event-driven with Redis/RabbitMQ |
| **Stage 4** | 50+ hospitals | API Gateway + Service Mesh (K8s) |
| **Stage 5** | SaaS / Multi-region | Federated Agent Protocol |

