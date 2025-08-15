import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from httpx import AsyncClient

from ..campaigns.models import ChannelType, CampaignGoal, Campaign as CampaignModel
from ..general.dataclasses import ResolvableCompanyModel
from ..integrations.dataclasses import Link


class Campaign(ResolvableCompanyModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID
    name: str
    external_id: Optional[str]
    status: str
    last_sync_date: datetime
    ad_count: int
    channel: Link
    channel_type: ChannelType
    campaign_goal: Optional[CampaignGoal]

    @staticmethod
    async def resolve_object(object_id: UUID, organization_id: UUID) -> "Campaign | None":
        result = await ResolveClient.campaigns().get(f"campaigns/{object_id}", headers={"X-Organization-ID": organization_id})

        if result.status_code != 200:
            return None

        return Campaign(**result.json())

    @classmethod
    async def from_model(cls: "Campaign", model: CampaignModel) -> 'Campaign':
        return Campaign(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            external_id=model.external_id,
            status=model.status,
            last_sync_date=model.last_sync_date,
            ad_count=model.ad_count,
            channel=channel,
            channel_type=model.channel_type,
            campaign_goal=model.campaign_goal,
        )
