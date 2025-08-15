import os
from uuid import UUID
from datetime import datetime
from typing import Optional

from httpx import AsyncClient

from .models import Link as LinkModel, Integration as IntegrationModel
from ..general.dataclasses import ResolvableModel, ResolvableCompanyModel
from ..resolve_clients import ResolveClient


class Integration(ResolvableModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    icon: str
    type: str
    tag: Optional[str]
    enabled: bool
    description: str

    @staticmethod
    async def resolve_object(object_id: UUID) -> "Integration | None":
        result = await ResolveClient.integrations().get(f"integrations/{object_id}")

        if result.status_code != 200:
            return None

        return Integration(**result.json())

    @classmethod
    def from_model(cls: "Integration", model: IntegrationModel) -> "Integration":
        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            icon=model.icon,
            type=model.type,
            tag=model.tag,
            enabled=model.enabled,
            description=model.description,
        )


class Link(ResolvableCompanyModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    integration: Integration

    @staticmethod
    async def resolve_object(object_id: UUID, organization_id: UUID) -> "Link | None":
        result = await ResolveClient.integrations().get(f"links/{object_id}", headers={"X-Organization-ID": organization_id})

        if result.status_code != 200:
            return None

        return Link(**result.json())

    @classmethod
    async def from_model(cls: "Link", model: LinkModel) -> "Link | None":
        integration = await Integration.resolve_object(model.integration_id)

        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            status=model.status,
            integration=integration,
        )
