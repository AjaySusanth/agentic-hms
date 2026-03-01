from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class HospitalCreate(BaseModel):
    name: str
    code: str
    location: str
    address: str
    contact_number: str


class HospitalLoginRequest(BaseModel):
    code: str


class HospitalOut(BaseModel):
    id: UUID
    name: str
    code: str
    location: str
    address: str
    contact_number: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
