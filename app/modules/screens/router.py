from uuid import UUID

from fastapi import APIRouter,status,Depends,Query
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.screens.models import Screen
from app.modules.seats.models import Seat
from app.modules.seats.schemas import SeatCreate, SeatResponse
from app.modules.screens.schemas import ScreenCreate, ScreenResponse
from app.modules.screens import service
from app.modules.seats import service as seat_service
from app.modules.auth.dependencies import  require_admin


router = APIRouter(
    prefix="/screens",
    tags=["Screens"],
)

@router.post(
    "",
    response_model=ScreenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_screen(
    data: ScreenCreate,
    db: Session = Depends(get_db)
) -> Screen:
    return service.create_screen(db=db, data=data)


@router.post(
    "/{screen_id}/seats",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def add_seat_to_screen(
    screen_id: UUID,
    data: SeatCreate,
    db: Session = Depends(get_db)
) -> Seat:
    return seat_service.create_seat(db=db, screen_id=screen_id, data=data)
