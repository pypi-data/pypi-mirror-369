from datetime import datetime
from typing import Optional
from uuid import UUID

from ..campaigns.models import ChannelType, CampaignGoal
from ..general.models import BaseModel
from ..integrations.dataclasses import Integration


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
    channel: Integration
    channel_type: ChannelType
    campaign_goal: Optional[CampaignGoal]
