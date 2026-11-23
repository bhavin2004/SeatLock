from uuid import UUID

from fastapi import APIRouter,status,Depends,Query
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.theaters import service
from app.modules.auth.dependencies import  require_admin
from app.modules.theaters.schemas import TheaterCreate, TheaterResponse


router = APIRouter(
    prefix="/theaters",
    tags=["Theaters"],
)


@router.post(
    "",
    response_model=TheaterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def add_theater(
    data: TheaterCreate,
    db: Session = Depends(get_db)
):
    return service.create_theater(db=db, data=data)