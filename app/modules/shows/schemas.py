from pydantic import BaseModel,Field,ConfigDict,AwareDatetime
from datetime import datetime
from uuid import UUID


from app.modules.seats.models import SeatTypeEnum

class ShowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    movie_id: UUID
    screen_id: UUID
    starts_at: datetime

class ShowSeatResponse(BaseModel):

    id: UUID
    row_label: str
    seat_number: int
    seat_type: SeatTypeEnum
    is_available: bool = Field(description="Whether the seat is available for this show.")

class ShowCreate(BaseModel):

    movie_id: UUID
    screen_id: UUID
    starts_at: AwareDatetime