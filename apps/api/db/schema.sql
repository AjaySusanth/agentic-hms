
-- Hospitals table
CREATE TABLE hospitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    location TEXT NOT NULL,
    address TEXT NOT NULL,
    contact_number TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);


CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    hospital_id UUID NOT NULL REFERENCES hospitals(id)
);

CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    department_id UUID NOT NULL REFERENCES departments(id),
    specialization TEXT,
    is_available BOOLEAN DEFAULT true,
    hospital_id UUID NOT NULL REFERENCES hospitals(id)
);

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    full_name TEXT NOT NULL,
    age INT,
    contact_number TEXT NOT NULL,
    abha_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id),
    CONSTRAINT uq_patient_phone_hospital UNIQUE (contact_number, hospital_id),
    CONSTRAINT uq_patient_abha_hospital UNIQUE (abha_id, hospital_id)
);



CREATE TABLE visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES doctors(id),
    symptoms_summary TEXT,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT now(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id)
);

-- Insert a default hospital for migration
INSERT INTO hospitals (id, name, code, location, address, contact_number, is_active)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'Default Hospital',
    'DEFAULT',
    'Default City',
    '123 Default St',
    '0000000000',
    true
) ON CONFLICT (code) DO NOTHING;



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
    hospital_id UUID NOT NULL REFERENCES hospitals(id),
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
    hospital_id UUID NOT NULL REFERENCES hospitals(id),

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

INSERT INTO departments (id, name, description, hospital_id) VALUES
(gen_random_uuid(), 'General Medicine', 'Common illnesses, fever, cold, general health', '00000000-0000-0000-0000-000000000000'),
(gen_random_uuid(), 'Cardiology', 'Heart-related conditions and chest pain', '00000000-0000-0000-0000-000000000000'),
(gen_random_uuid(), 'Orthopedics', 'Bone, joint, and muscle issues', '00000000-0000-0000-0000-000000000000'),
(gen_random_uuid(), 'Pediatrics', 'Healthcare for children under 18', '00000000-0000-0000-0000-000000000000');


INSERT INTO doctors (id, name, specialization, department_id, is_available, hospital_id)
SELECT
    gen_random_uuid(),
    'Dr. Alice Sharma',
    'Cardiologist',
    d.id,
    true,
    '00000000-0000-0000-0000-000000000000'
FROM departments d
WHERE d.name = 'Cardiology';

INSERT INTO doctors (id, name, specialization, department_id, is_available, hospital_id)
SELECT
    gen_random_uuid(),
    'Dr. Bob Varma',
    'General Physician',
    d.id,
    true,
    '00000000-0000-0000-0000-000000000000'
FROM departments d
WHERE d.name = 'General Medicine';

INSERT INTO doctors (id, name, specialization, department_id, is_available, hospital_id)
SELECT 
    gen_random_uuid(), 
    'Dr. Charlie Day', 
    'Orthopedic Surgeon', 
    d.id,            
    true,
    '00000000-0000-0000-0000-000000000000'
FROM departments d   
WHERE d.name = 'Orthopedics';




CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL UNIQUE REFERENCES visits(id),

    doctor_id UUID NOT NULL,
    patient_id UUID NOT NULL,

    notes TEXT,

    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL REFERENCES visits(id),

    status TEXT DEFAULT 'pending', 
    -- pending, sent_to_pharmacy, fulfilled

    created_at TIMESTAMPTZ DEFAULT now()
);


CREATE TABLE prescription_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id),

    medicine_name TEXT NOT NULL,
    dosage TEXT,
    frequency TEXT,
    duration_days INT,
    instructions TEXT,

    availability_status TEXT DEFAULT 'unknown'
    -- unknown, in_stock, out_of_stock (future)

);

CREATE TABLE lab_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL REFERENCES visits(id),

    test_name TEXT NOT NULL,
    priority TEXT DEFAULT 'routine', 
    -- routine, urgent

    status TEXT DEFAULT 'ordered',
    -- ordered, scheduled, completed

    created_at TIMESTAMPTZ DEFAULT now()
);
