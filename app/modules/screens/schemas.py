from uuid import UUID

from pydantic import BaseModel,Field,ConfigDict,AwareDatetime

class ScreenCreate(BaseModel):

    theater_id: UUID = Field(description="The ID of the theater to which this screen belongs.")
    name: str = Field(max_length=100,min_length=1)

class ScreenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    theater_id: UUID
    name: str