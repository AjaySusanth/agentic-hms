# Development Plan Checklist: Multi-Hospital HMS Chatbot

## Phase 1: Multi-Tenancy Foundation ✅
- [x] Implement `Hospital` Model and `hospital_id` in core models (Doctor, Dept, Patient, Visit)
- [x] Add `hospital_id` to Queue models (DoctorQueue, QueueEntry)
- [x] Set up Database Migrations for `hospital_id` isolation
- [x] Create `HospitalService` and `HospitalRouter` (Admin CRUD)
- [x] **STOP: Verify DB integrity and Hospital CRUD API** ✅
- [x] Refactor Registration Agent to support `hospital_id` scoping
- [x] **STOP: Verify existing Registration flow works with hospital scoping** ✅
- [x] Verify Hospital data isolation in existing agent flows

## Phase 2: Unified Chatbot Gateway ✅
- [x] Implement `ChatbotOrchestratorAgent` (State, Steps, Handler)
- [x] Implement Intent Detection via LLM (Groq)
- [x] Implement Hospital Discovery with doctor availability
- [x] Implement Proxy Mode to Registration Agent
- [x] Create Chatbot API endpoints (`/session`, `/session/{id}/message`)
- [x] **STOP: Verify Chatbot end-to-end flow via Postman** ✅

## Phase 3: Web Chatbot Frontend
- [ ] Create `ChatbotPage` UI component with message thread
- [ ] Implement dynamic option buttons for hospital/doctor selection
- [ ] Update `App.jsx` with `/chat` route
- [ ] Extend `api.js` with Chatbot-specific service calls
- [ ] **STOP: Manual E2E Walkthrough (Start Chat ➔ Select Hospital ➔ Complete Registration)**

## Phase 4: External System Integration
- [ ] Define `AgentProtocol` standard interface
- [ ] Implement `HotelBooking` external system adapter (Mock/Stub for MVP)
- [ ] Connect Chatbot Orchestrator to External handoff flow
- [ ] **STOP: Verify External Handoff (Chatbot ➔ Hotel Agent transition)**

## Final Polish & Deployment
- [ ] Run Full Integration test suite (Positive + Critical Negatives)
- [ ] Final UI/UX polish (Animations, glassmorphism refinement)
- [ ] Deployment Readiness Check
