from uuid import UUID
from fastapi import APIRouter,status,Depends,Query
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.movies import service
from app.modules.auth.dependencies import require_admin
from app.modules.movies.models import Movie
from app.modules.movies.schemas import MovieCreate,MovieResponse,MovieUpdate


router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
)


@router.post(
    "",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_movie(data: MovieCreate,db: Session= Depends(get_db)):
    return service.create_movie(db=db,data=data)

@router.get(
    "/list_all_movies_for_admin",
    response_model=list[MovieResponse],
    status_code=200,
    dependencies=[Depends(require_admin)]
)
def list_all_movies_for_admin(
    db: Session = Depends(get_db)
) -> list[Movie]:
    return service.list_all_movies_for_admin(db=db)


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    status_code=200
)
def get_movie_by_id(movie_id: UUID,db: Session = Depends(get_db)) -> Movie:
    return service.get_published_movie_by_id(db=db,movie_id=movie_id)


@router.get(
    "",
    response_model=list[MovieResponse],
    status_code=200
)
def list_movies(
    limit: int = Query(default=10,ge=1, le=100),
    offset: int = Query(default=0,ge=0),
    db: Session = Depends(get_db)
):  
    return service.list_movies(db=db, limit=limit, offset=offset)


@router.patch(
    "/{movie_id}",
    response_model=MovieResponse,
    status_code=200,
    dependencies=[Depends(require_admin)]
)
def update_movie(
    movie_id: UUID,
    data: MovieUpdate,
    db:Session = Depends(get_db)
) -> Movie:
    return service.update_movie(db=db,movie_id=movie_id,data=data)

@router.post(
    "/{movie_id}/publish",
    response_model=MovieResponse,
    status_code=200,
    dependencies=[Depends(require_admin)]
)
def publish_movie(
    movie_id: UUID,
    db:Session = Depends(get_db)
)-> Movie:
    return service.publish_movie(db,movie_id)

@router.post(
    "/{movie_id}/archive",
    response_model=MovieResponse,
    status_code=200,
    dependencies=[Depends(require_admin)]
)
def archive_movie(
    movie_id: UUID,
    db:Session = Depends(get_db)
)-> Movie:
    return service.archive_movie(db,movie_id)

