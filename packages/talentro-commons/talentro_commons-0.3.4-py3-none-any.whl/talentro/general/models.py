from uuid import UUID, uuid4

from typing import Optional

from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {"onupdate": lambda: datetime.now(timezone.utc)}
    )


# App specific models
## Integrations
class IntegrationsModel(BaseModel):
    pass


class IntegrationsOrganizationModel(IntegrationsModel):
    organization: UUID = Field(index=True)


## Vacancies
class VacanciesModel(BaseModel):
    pass


class VacanciesOrganizationModel(VacanciesModel):
    organization: UUID = Field(index=True)


## Campaigns
class CampaignsModel(BaseModel):
    pass


class CampaignsOrganizationModel(CampaignsModel):
    organization: UUID = Field(index=True)



## Billing
class BillingModel(BaseModel):
    pass


class BillingOrganizationModel(BillingModel):
    organization: UUID = Field(index=True)


## IAM
class IAMModel(BaseModel):
    pass


class IAMOrganizationModel(BaseModel):
    organization: UUID = Field(index=True)
