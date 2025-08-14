from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RawCandidate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    hashed_email: str
    cv: str
    motivation_letter: str
    linked_in: str


class Candidate(RawCandidate):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID


class RawApplication(BaseModel):
    status: str
    source: str
    candidate_id: str
    vacancy_id: str


class Application(RawApplication):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID
