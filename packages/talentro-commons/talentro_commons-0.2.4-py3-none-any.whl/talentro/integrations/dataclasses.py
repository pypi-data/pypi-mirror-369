from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .models import Link as LinkModel, Integration as IntegrationModel


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

    @classmethod
    def from_model(cls: "Integration", model: IntegrationModel) -> "Integration":
        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            icon=model.icon,
            type=model.type,
            tag=model.tag,
            enabled=model.enabled,
            description=model.description,
        )


class Link(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    integration: Integration

    @classmethod
    def from_model(cls: "Link", model: LinkModel, integration_model: IntegrationModel) -> "Link":
        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            status=model.status,
            integration=Integration.from_model(integration_model),
        )
