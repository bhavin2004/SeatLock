from pydantic import BaseModel,Field,HttpUrl,ConfigDict
from uuid import UUID

from app.modules.seats.models import SeatTypeEnum

class SeatCreate(BaseModel):

    row_label: str = Field(min_length=1,max_length=10)
    seat_number: int = Field(gt=0)
    seat_type: SeatTypeEnum

class SeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    screen_id: UUID
    row_label: str
    seat_number: int
    seat_type: SeatTypeEnum

