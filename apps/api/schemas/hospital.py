from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class HospitalCreate(BaseModel):
    name: str
    code: str
    location: str
    address: str
    contact_number: str


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
