from datetime import datetime

from pydantic import BaseModel,Field,field_validator
from uuid import UUID

from app.modules.bookings.models import BookingStatusEnum



class BookingCreate(BaseModel):


    show_id: UUID
    seat_ids: list[UUID] = Field(min_length=1)
    @field_validator("seat_ids")
    @classmethod
    def seat_ids_must_be_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("seat_ids must be unique")
        return value

class BookingResponse(BaseModel):
    id: UUID
    show_id: UUID
    seat_ids: list[UUID]
    status: BookingStatusEnum
    expires_at: datetime

