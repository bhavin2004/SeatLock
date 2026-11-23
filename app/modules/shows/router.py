from uuid import UUID

from fastapi import APIRouter,status,Depends,Query
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.shows.models import Show
from app.modules.shows.schemas import ShowCreate, ShowResponse, ShowSeatResponse
from app.modules.shows import service
from app.modules.auth.dependencies import  require_admin


router = APIRouter(
    prefix="/shows",
    tags=["Shows"],
)

@router.get(
    "",
    response_model=list[ShowResponse],
    status_code=status.HTTP_200_OK,
)
def list_upcoming_shows(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0,),
)-> list[Show]:
    return  service.list_upcoming_shows(db=db, limit=limit, offset=offset)
    


@router.get(
    "/{show_id}/seats",
    response_model=list[ShowSeatResponse],
    status_code=status.HTTP_200_OK,
)
def list_show_seats(
    show_id: UUID,
    db: Session = Depends(get_db),
) -> list[ShowSeatResponse]:
    return service.list_show_seats(db=db, show_id=show_id)

@router.post(
    "",
    response_model=ShowResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_show(
    data: ShowCreate,
    db: Session = Depends(get_db),
)-> Show:
    return service.create_show(db=db, data=data)