from datetime import datetime
from typing import Optional
from uuid import UUID

from ..campaigns.models import ChannelType, CampaignGoal, Campaign as CampaignModel
from ..general.models import BaseModel
from ..integrations.dataclasses import Link


class Campaign(BaseModel):
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

    @classmethod
    def from_model(cls: "Campaign", model: CampaignModel, channel: Link) -> 'Campaign':
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
            channel_type=channel.channel_type,
            campaign_goal=channel.campaign_goal,
        )
