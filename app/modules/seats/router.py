from uuid import UUID

from fastapi import APIRouter,status,Depends,Query
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.seats.models import Seat
from app.modules.seats.schemas import SeatCreate, SeatResponse
from app.modules.seats import service
from app.modules.auth.dependencies import  require_admin


router = APIRouter(
    prefix="/seats",
    tags=["Seats"],
)

