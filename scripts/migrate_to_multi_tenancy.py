"""
Migration script to:
- Create a Default Hospital if not exists
- Assign all existing departments, doctors, patients, and visits to the Default Hospital
"""

import os
import sys
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Update this with your actual DB URL or use env var
DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydb"


def main():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # 1. Create Default Hospital if not exists
        default_hospital_code = "DEFAULT"
        default_hospital_id = None
        result = session.execute(
            text("SELECT id FROM hospitals WHERE code = :code"),
            {"code": default_hospital_code},
        )
        row = result.fetchone()
        if row:
            default_hospital_id = row[0]
        else:
            default_hospital_id = str(uuid.uuid4())
            session.execute(
                text(
                    """
                INSERT INTO hospitals (id, name, code, location, address, contact_number, is_active)
                VALUES (:id, :name, :code, :location, :address, :contact_number, true)
            """
                ),
                {
                    "id": default_hospital_id,
                    "name": "Default Hospital",
                    "code": default_hospital_code,
                    "location": "Default City",
                    "address": "123 Default St",
                    "contact_number": "0000000000",
                },
            )
            session.commit()
        print(f"Default Hospital ID: {default_hospital_id}")

        # 2. Update all departments
        session.execute(
            text("UPDATE departments SET hospital_id = :hid WHERE hospital_id IS NULL"),
            {"hid": default_hospital_id},
        )
        # 3. Update all doctors
        session.execute(
            text("UPDATE doctors SET hospital_id = :hid WHERE hospital_id IS NULL"),
            {"hid": default_hospital_id},
        )
        # 4. Update all patients
        session.execute(
            text("UPDATE patients SET hospital_id = :hid WHERE hospital_id IS NULL"),
            {"hid": default_hospital_id},
        )
        # 5. Update all visits
        session.execute(
            text("UPDATE visits SET hospital_id = :hid WHERE hospital_id IS NULL"),
            {"hid": default_hospital_id},
        )
        session.commit()
        print("All existing data assigned to Default Hospital.")
    except Exception as e:
        print(f"Migration failed: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
