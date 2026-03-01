# Development Plan Checklist: Multi-Hospital HMS Chatbot

## Architecture: Hybrid Router (LangGraph-Style Pattern)
> Custom agent framework using deterministic state machines + LLM-powered routing.
> See `implementation_plan.md` for full architecture details.

---

## Phase 1: Multi-Tenancy Foundation ✅
- [x] Implement `Hospital` Model and `hospital_id` in core models (Doctor, Dept, Patient, Visit)
- [x] Add `hospital_id` to Queue models (DoctorQueue, QueueEntry)
- [x] Set up Database Migrations for `hospital_id` isolation
- [x] Create `HospitalService` and `HospitalRouter` (Admin CRUD)
- [x] **STOP: Verify DB integrity and Hospital CRUD API** ✅
- [x] Refactor Registration Agent to support `hospital_id` scoping
- [x] **STOP: Verify existing Registration flow works with hospital scoping** ✅
- [x] Verify Hospital data isolation in existing agent flows

## Phase 2: Unified Chatbot Gateway
- [x] Implement `ChatbotOrchestratorAgent` (State, Steps, Handler)
- [x] Implement Intent Detection via LLM (Groq)
- [x] Implement Hospital Discovery with doctor availability
- [x] Implement Proxy Mode to Registration Agent
- [x] Create Chatbot API endpoints (`/session`, `/session/{id}/message`)
- [x] Fix proxy response parsing (nested `response`/`state` extraction)
- [x] Fix step-aware input mapping (`symptoms`, `confirm`, `doctor_id`)
- [x] **STOP: Verify Chatbot end-to-end flow via Postman** ✅

## Phase 2.5: Hybrid Router Upgrade (LangGraph-Style) ✅
- [x] Add `should_pivot()` LLM function to `intent_detector.py`
  - Detects: `continue` | `exit` | `pivot` | `help`
- [x] Add `last_bot_message` to `ChatbotOrchestratorState` for context
- [x] Implement **Symptom Merging** logic (append new symptoms to history on pivot)
- [x] Implement **CONFIRM_BOOKING** step (ask before showing hospital list)
- [x] Wire LLM Router into `agent.py` `handle()` interceptor
- [x] Fix: `general_query` intent now transitions to `COLLECT_SYMPTOMS` (no more stuck loop)
- [x] **STOP: Verify conversational flexibility via Postman** ✅
  - [x] Test: Mid-flow exit ("No thanks, goodbye")
  - [x] Test: Mid-flow pivot ("Actually my ear hurts too")
  - [x] Test: Mid-flow help ("What is Cardiology?")

## Phase 3: Web Chatbot Frontend
- [ ] Create `ChatbotPage` UI component with message thread
- [ ] Implement dynamic option buttons for hospital/doctor selection
- [ ] Update `App.jsx` with `/chat` route
- [ ] Extend `api.js` with Chatbot-specific service calls
- [ ] **STOP: Manual E2E Walkthrough (Start Chat → Select Hospital → Complete Registration)**

## Phase 4: External System Integration
- [ ] Define `AgentProtocol` standard interface
- [ ] Implement `HotelBooking` external system adapter (Mock/Stub for MVP)
- [ ] Connect Chatbot Orchestrator to External handoff flow
- [ ] **STOP: Verify External Handoff (Chatbot → Hotel Agent transition)**

## Final Polish & Deployment
- [ ] Add structured JSON logging and agent telemetry middleware
- [ ] Add Prometheus `/metrics` endpoint (API latency, LLM response time)
- [ ] Run Full Integration test suite (Positive + Critical Negatives)
- [ ] Final UI/UX polish (Animations, glassmorphism refinement)
- [ ] Deployment Readiness Check
