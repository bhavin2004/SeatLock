from uuid import UUID

from pydantic import BaseModel, ConfigDict,Field


class TheaterCreate(BaseModel):

    name: str = Field(max_length=100,min_length=3)
    address: str = Field(max_length=500,min_length=10)
    city: str = Field(max_length=100,min_length=3)
    timezone: str = Field(max_length=64, min_length=3)

class TheaterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) 

    id: UUID
    name: str
    address: str
    city: str
    timezone: str

