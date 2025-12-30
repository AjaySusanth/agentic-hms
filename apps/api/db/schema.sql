-- Run schema.sql once on your DB

CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    department_id UUID NOT NULL REFERENCES departments(id),
    specialization TEXT,
    is_available BOOLEAN DEFAULT true
);

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    full_name TEXT NOT NULL,
    age INT,
    contact_number TEXT UNIQUE NOT NULL,
    abha_id TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);



CREATE TABLE visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES doctors(id),
    symptoms_summary TEXT,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT now()
);



CREATE TABLE agent_sessions (
    session_id UUID PRIMARY KEY,
    agent_name TEXT NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE doctor_queues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    doctor_id UUID NOT NULL,
    queue_date DATE NOT NULL,

    -- Shift definition (MVP: one shift per day)
    shift_start_time TIME NOT NULL,
    shift_end_time TIME NOT NULL,

    -- Queue control
    queue_open BOOLEAN DEFAULT true,
    max_queue_size INT,
    avg_consult_time_minutes INT NOT NULL DEFAULT 10,

    -- Progress tracking
    current_token INT DEFAULT 0,
    current_visit_id UUID,

    -- Explainability & audit
    last_event_type TEXT,
    last_event_reason TEXT,
    last_updated_by TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT uq_doctor_queue UNIQUE (doctor_id, queue_date)
);

CREATE TABLE queue_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    queue_id UUID NOT NULL REFERENCES doctor_queues(id) ON DELETE CASCADE,
    visit_id UUID NOT NULL,

    token_number INT NOT NULL,
    position INT NOT NULL,

    status TEXT NOT NULL CHECK (
        status IN (
            'waiting',
            'present',
            'called',
            'in_consultation',
            'skipped',
            'completed'
        )
    ),

    check_in_time TIMESTAMPTZ,
    consultation_start_time TIMESTAMPTZ,
    consultation_end_time TIMESTAMPTZ,
    skipped_at TIMESTAMPTZ,
    skip_reason TEXT,
    skip_position_token INT,
    eligible_after_token INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT uq_queue_visit UNIQUE (queue_id, visit_id),
    CONSTRAINT uq_queue_token UNIQUE (queue_id, token_number)
);


--dummy data
INSERT INTO doctors (id, name, specialization, department_id, is_available)
SELECT
    gen_random_uuid(),
    'Dr. Alice Sharma',
    'Cardiologist',
    d.id,
    true
FROM departments d
WHERE d.name = 'Cardiology';

INSERT INTO doctors (id, name, specialization, department_id, is_available)
SELECT
    gen_random_uuid(),
    'Dr. Bob Varma',
    'General Physician',
    d.id,
    true
FROM departments d
WHERE d.name = 'General Medicine';

INSERT INTO doctors (id, name, specialization, department_id, is_available)
SELECT
    gen_random_uuid(),
    'Dr. Charlie Day',
    'Orthopedic Surgeon',
WHERE d.name = 'Orthopedics';

INSERT INTO departments (id, name, description) VALUES
(gen_random_uuid(), 'General Medicine', 'Common illnesses, fever, cold, general health'),
(gen_random_uuid(), 'Cardiology', 'Heart-related conditions and chest pain'),
(gen_random_uuid(), 'Orthopedics', 'Bone, joint, and muscle issues'),
(gen_random_uuid(), 'Pediatrics', 'Healthcare for children under 18');