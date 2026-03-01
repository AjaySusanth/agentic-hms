# Future Scope: Agentic HMS Platform Architecture

This document outlines the two architectural approaches for the HMS Chatbot system, their use cases, scaling strategies, and the recommended evolution path.

---

## Table of Contents

1. [Current Architecture (Option A: Chatbot Agent)](#option-a-chatbot-agent-only)
2. [Future Architecture (Option B: Full Agentic Platform)](#option-b-full-agentic-platform)
3. [Chatbot Orchestration Patterns](#chatbot-orchestration-patterns)
4. [Infrastructure Scaling Roadmap](#infrastructure-scaling-roadmap)
5. [Customer Use Cases & Comparison](#customer-use-cases)
6. [Migration Path: A → B](#migration-path)

---

## Option A: Chatbot Agent Only

> "A smart chatbot that works with OUR hospital system."

### Architecture

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

### Design: Hybrid Router (LangGraph-Style Pattern)

Uses a **custom agent framework inspired by LangGraph's Graph pattern**, without depending on the LangGraph library:

- **Deterministic steps** for safety-critical healthcare workflows (patient registration, queue management)
- **LLM-powered routing** for conversational flexibility (intent detection, pivot handling)
- **Zero external AI framework dependencies** (no LangChain/LangGraph; pure Python + FastAPI)

### Why Custom Pattern over LangGraph Library

| Factor | LangGraph Library | Custom (LangGraph Pattern) |
|:---|:---|:---|
| **Latency** | Abstraction overhead (~50-100ms) | Direct Python calls (~0ms overhead) |
| **LLM Cost** | May trigger extra reasoning loops | Surgical: LLM only at routing decisions |
| **Persistence** | Opinionated checkpointer | Fits existing `AgentSessionService` + PostgreSQL |
| **Stability** | Frequent breaking API changes | Plain Python — never breaks |
| **Resume Value** | "Used a library" | "Built the pattern from scratch" |

### LLM Usage Strategy (Cost Optimization)

| LLM Call | When | Model | Est. Tokens |
|:---|:---|:---|:---|
| `detect_intent()` | Once per session (Step 3) | Llama 3.1-8B (Groq) | ~300 |
| `should_pivot()` | Before step handler (if input is non-structured) | Llama 3.1-8B (Groq) | ~200 |
| `summarize_symptoms()` | Once during registration | Llama 3.1-8B (Groq) | ~200 |
| `resolve_department()` | Once during registration | Llama 3.1-8B (Groq) | ~150 |

**Total per full session**: ~850 tokens (~$0.0001 on Groq free tier)

### Development Effort

| Item | Effort |
|:---|:---:|
| State machine orchestrator | 2-3 days |
| Intent detection (LLM) | 1 day |
| Hospital discovery + proxy | 2 days |
| Hybrid Router (pivot detection) | 1 day |
| Web chat UI | 2-3 days |
| **Total** | **~10 days** |

### When to Use Option A

- Single hospital or small group (1-5 branches)
- You control the backend system
- Fixed workflow (registration → queue → doctor)
- Budget-conscious deployment

---

## Option B: Full Agentic Platform

> "A platform that ANY hospital/hotel/service can plug into with zero code."

### Architecture

```
┌──────────────────────────────────────────────────────┐
│                  TEMPLATE LAYER                       │
│  Pre-built workflow templates for common patterns:    │
│  • medical_registration_template                      │
│  • hotel_booking_template                             │
│  • appointment_scheduling_template                    │
│  • general_inquiry_template (RAG-powered)             │
└──────────────┬───────────────────────────────────────┘
               │ parameterized by
┌──────────────▼───────────────────────────────────────┐
│                  CONFIG LAYER                         │
│  Per-client YAML that fills in the template:          │
│  • base_url, auth_headers                             │
│  • field_mappings (their "patient_name" = our "name") │
│  • endpoint_paths                                     │
│  • custom validation rules                            │
│  • branding (hospital name, greeting text)             │
└──────────────┬───────────────────────────────────────┘
               │ executed by
┌──────────────▼───────────────────────────────────────┐
│               DETERMINISTIC ENGINE                    │
│  State machine runs the template.                     │
│  LLM only used for: intent detection, pivots, FAQ     │
└──────────────┬───────────────────────────────────────┘
               │ answers info queries via
┌──────────────▼───────────────────────────────────────┐
│                  RAG PIPELINE                         │
│  Per-client document embeddings (FAISS/ChromaDB)      │
│  Answers: policies, FAQs, general information         │
└──────────────────────────────────────────────────────┘
```

### The Three Pillars

| Pillar | Role | Example |
|:---|:---|:---|
| **LLM Router** (smart) | Decides *what to do* | "User wants to book a hotel" |
| **Workflow Template** (deterministic) | Decides *how to do it* | Step 1 → Step 2 → Step 3 |
| **Config File** (customizable) | Decides *where to do it* | Hotel Sunrise API at `api.hotelsunrise.com` |

### Example: Onboarding "Hotel Sunrise"

Developer writes **ZERO Python code**. Creates one config file:

```yaml
# configs/integrations/hotel_sunrise.yaml
service_name: "Hotel Sunrise"
service_type: "hotel_booking"          # ← picks the workflow template
base_url: "https://api.hotelsunrise.com/v1"
auth:
  type: "api_key"
  header: "X-API-Key"
  value_env: "HOTEL_SUNRISE_API_KEY"   # ← from .env, never in config

field_mappings:
  check_in_date: "arrival_date"        # their field name → our standard name
  check_out_date: "departure_date"
  guest_name: "full_name"
  room_type: "category"

endpoints:
  search_rooms: "GET /rooms/available"
  book_room: "POST /reservations"
  cancel_booking: "DELETE /reservations/{id}"

rag_documents:                          # ← for informational queries
  - "docs/hotel_sunrise_faq.md"
  - "docs/hotel_sunrise_policies.md"
```

**Runtime flow:**
1. User says "I need a hotel near the hospital"
2. LLM Router detects `hotel_booking` intent → loads `hotel_booking` **template**
3. Template knows the workflow: `collect_dates → search_rooms → select_room → collect_details → confirm`
4. At each step, the **config** tells the engine which endpoint to hit and how to map fields
5. If user asks "What's the cancellation policy?" → RAG pipeline answers from `hotel_sunrise_policies.md`

### Why NOT Pure Config-Driven Tool Calling

A common temptation is to skip templates and let the LLM dynamically pick API endpoints from a config. Here's why that fails:

| Problem | Why It Fails |
|:---|:---|
| **Workflows ≠ Single API Calls** | Real integrations are multi-step (search → select → confirm → pay). A flat list of endpoints can't encode flow, dependencies, or branches. |
| **LLM Tool Selection is Unreliable** | Llama 3.1-8B accuracy drops with 5+ tools. Even GPT-4 achieves ~85%. In healthcare, 85% = 1 in 7 patients gets the wrong action. |
| **Security Nightmare** | LLM constructing HTTP requests to arbitrary APIs = prompt injection risk, data leakage, URL manipulation. |
| **Error Handling** | Config can't capture error semantics. Templates have explicit error handlers per step. |

### RAG + Tools: The Correct Split

| Query Type | Mechanism | Example |
|:---|:---|:---|
| **Informational** | RAG Pipeline | "What's the cancellation policy?" "Do you have pediatricians?" |
| **Transactional** | Workflow Template + Config | "Book an appointment" "Cancel my reservation" |

Never let a RAG pipeline execute a transaction. Never use tool calling for FAQ answers.

### Development Effort (Additional over Option A)

| Item | Effort |
|:---|:---:|
| Template Engine (load YAML → run workflow) | 3-4 days |
| 2-3 Workflow Templates (medical, hotel, inquiry) | 2 days each |
| RAG Pipeline (embed docs → vector search → LLM answer) | 3-4 days |
| Config validation + dynamic field mapping | 2 days |
| Admin panel for onboarding (optional) | 3-4 days |
| **Total additional** | **~15-20 days** |
| **Grand total (A + B)** | **~25-30 days** |

### When to Use Option B

- Hospital chains with 10+ branches
- Multi-service integration (hospitals + hotels + labs + pharmacies)
- SaaS/platform business model
- Onboarding new clients without developer involvement

---

## Chatbot Orchestration Patterns

### Comparison of All Approaches

| Pattern | How It Works | Determinism | Cost/Message | Healthcare Safety |
|:---|:---|:---:|:---:|:---:|
| **Custom State Machine** | `if/elif` step dispatch | ⭐⭐⭐⭐⭐ | Free | ⭐⭐⭐⭐⭐ |
| **LangGraph** | Graph of nodes + conditional edges | ⭐⭐⭐⭐ | Low (LLM at branches) | ⭐⭐⭐⭐ |
| **LangChain Agent** | LLM picks tools autonomously | ⭐⭐ | High (LLM every step) | ⭐⭐ |
| **CrewAI / AutoGen** | Multiple LLM agents "discuss" | ⭐ | Very High | ⭐ |
| **Hybrid Router (Ours)** | State Machine + LLM at routing points | ⭐⭐⭐⭐⭐ | Minimal | ⭐⭐⭐⭐⭐ |

### When to Migrate Between Patterns

| Trigger | Migrate From → To |
|:---|:---|
| >15 steps, parallel branches, retry loops | Custom State Machine → **LangGraph** |
| >50 intents, RAG integration, open-ended Q&A | LangGraph → **LangGraph + LangChain Tools** |
| Multi-agent reasoning, conflicting constraints | Any → **CrewAI** (rare for HMS) |

### Our Choice: Hybrid Router

We use the **logic** of a graph (Nodes → Edges → Router) but the **runtime** of a standard web app:
- **Deterministic Engine** handles the database and step transitions (safe)
- **LLM Steering** handles "Wait," "Thanks," "Change topic" messages (friendly)
- Best of both worlds without a library dependency

---

## Infrastructure Scaling Roadmap

### Stage 1: Monolith + HTTP Proxy (Current)

```
User → FastAPI → Orchestrator → HTTP self-call → Registration Agent → Same DB
```
- **Fits:** 1-5 hospitals, ~500 concurrent users, single server
- **Migration effort to next stage:** Low (just change URLs)

### Stage 2: Containerized Per-Hospital Services

```
User → API Gateway → Orchestrator Service
                        ├── Hospital A Service (Container A)
                        ├── Hospital B Service (Container B)
                        └── Hospital C Service (Container C)
```
- **Trigger:** 10+ hospitals, hospital-specific customization, uptime SLA differences, data residency requirements
- **Migration effort:** Low — `HospitalClient` already uses HTTP; just change `localhost` to container hostname

### Stage 3: Event-Driven with Message Queue

```
User → Orchestrator → Redis/RabbitMQ ─┬─→ Registration Worker
                                       ├─→ Insurance Verification Worker
                                       ├─→ Lab Booking Worker
                                       └─→ Notification Worker
       WebSocket ←─── Result Queue ←───┘
```
- **Trigger:** Long-running background tasks (insurance pre-auth), notification system, rate-limiting external APIs
- **Migration effort:** Medium — add Redis/RabbitMQ, split handlers into workers, add WebSocket for real-time responses

### Stage 4: API Gateway + Service Mesh

```
User → Nginx/Kong → Service Mesh (Istio)
                        ├─→ Orchestrator (3 replicas)
                        ├─→ Hospital A Service (2 replicas)
                        ├─→ Queue Service (2 replicas)
                        └─→ Notification Service (1 replica)
```
- **Trigger:** 50+ hospitals, auto-scaling needs, multi-team development, traffic spikes
- **Migration effort:** High — requires Kubernetes, Helm charts, distributed tracing

### Stage 5: Federated / Multi-Region

```
Central Cloud                          Hospital A (On-Premise)
┌────────────────┐                    ┌──────────────────┐
│ Orchestrator   │◄── Agent Protocol ─►│ Registration API │
│ Hospital Index │                    │ Queue API        │
│ Patient Portal │                    │ Local DB         │
└────────────────┘                    └──────────────────┘
```
- **Trigger:** Hospitals own their infra, B2B SaaS model, cross-geography data laws
- **Migration effort:** Very high — standardized Agent Protocol, auth between systems, data sharing agreements

### Growth Timeline

```
    NOW                 1K users           10K users          100K users
     │                     │                   │                   │
┌────▼────┐         ┌──────▼──────┐     ┌──────▼──────┐    ┌──────▼──────┐
│Monolith │ ──────► │Containerized│ ──► │API Gateway  │ ─► │ Federated   │
│HTTP Proxy│        │Per-Hospital │     │Service Mesh │    │Multi-Region │
│Single DB │        │Separate DBs │     │Auto-Scale   │    │Agent Proto  │
└─────────┘         └─────────────┘     └─────────────┘    └─────────────┘
 5 hospitals         10-20 hospitals     50+ hospitals      Enterprise SaaS
```

---

## Customer Use Cases

### Customer Profile 1: Single Hospital

> "We just want patients to book appointments through chat."

| Factor | Option A (Chatbot Agent) | Option B (Full Platform) |
|:---|:---|:---|
| What they need | A chatbot for THEIR system | Same |
| Setup time | Deploy and connect to DB | Overkill |
| Maintenance | Low | Unnecessarily complex |
| **Verdict** | ✅ **Perfect fit** | ❌ Over-engineered |

### Customer Profile 2: Hospital Chain (e.g., 50+ branches)

> "One chatbot across all branches, each with different departments."

| Factor | Option A | Option B |
|:---|:---|:---|
| Setup per branch | Write code for each | Drop a YAML config |
| Maintenance | High (50 codebases) | Low (50 config files) |
| **Verdict** | ❌ Doesn't scale | ✅ **Perfect fit** |

### Customer Profile 3: Health-Tech Platform (e.g., Practo)

> "Integrate hospitals AND hotels AND pharmacies into one chatbot."

| Factor | Option A | Option B |
|:---|:---|:---|
| New service type | Write a new agent from scratch | Create a template + config |
| RAG needed? | No | Yes (FAQs, policies per partner) |
| Maintenance | Very High | Template updates only |
| **Verdict** | ❌ Unsustainable | ✅ **Only viable option** |

### Summary Matrix

```
                    Single Hospital    Hospital Chain    Health-Tech Platform
                    ───────────────    ──────────────    ────────────────────
Chatbot Only            ✅ Best            ⚠️ Works         ❌ Won't scale
Full Platform           ❌ Overkill        ✅ Best           ✅ Only option
```

---

## Migration Path

### The Recommended Strategy

**Build Option A first. Sell it. Evolve to Option B when you have paying customers.**

1. **Option A is a sellable product TODAY.** A hospital doesn't care about "config-driven templates." They care about "can patients book appointments through chat?"
2. **Option B is the PLATFORM play.** Build it when Hospital #3 or #4 says "we need this too" and writing custom code per client becomes unsustainable.
3. **The migration is natural.** The current state machine becomes the first "template." Hospital-specific data becomes the first "config." Nothing is thrown away.

### What Gets Reused

| Option A Component | Becomes in Option B |
|:---|:---|
| `ChatbotOrchestratorAgent` | Template Engine (runs templates instead of hardcoded steps) |
| `ChatbotOrchestratorState` | Generic `WorkflowState` with template-defined fields |
| `HospitalClient` | Generic `ExternalServiceClient` (reads URLs from config) |
| `intent_detector.py` | Same (intent detection is universal) |
| `should_pivot()` | Same (conversational routing is universal) |
| Multi-tenancy (`hospital_id`) | Becomes `tenant_id` (supports any service type) |
