from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Integration(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    icon: str
    type: str
    tag: str
    enabled: bool
    description: str
    code_reference: str
    setup_config: dict
    order: int


class Link(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    auth_config: dict
    integration_id: UUID
