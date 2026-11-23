from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.modules.movies.schemas import MovieCreate,MovieUpdate
from app.modules.movies.models import Movie,MovieStatus
from app.modules.movies import repository


def create_movie(db: Session,data: MovieCreate) -> Movie:
    try:
        movie = Movie(
        title=data.title,
        duration_minutes=data.duration_minutes,
        release_date=data.release_date,
        description=data.description,
        poster_url=str(data.poster_url) if data.poster_url else None,
        certification=data.certification
    )
        created_movie = repository.create_movie(db,movie=movie)
        db.commit()
        db.refresh(created_movie)
        return created_movie
    except Exception:
        db.rollback()
        raise

def get_movie_by_id(db: Session, movie_id: UUID) -> Movie:
    movie = repository.get_movie_by_id(db=db,movie_id=movie_id)
    
    if movie is None:
        raise HTTPException(status_code=404,detail="Movie Not Found")

    return movie

def list_movies(db: Session, limit: int, offset: int) -> list[Movie]:
    return repository.list_movies(db,limit,offset)

def update_movie(db: Session, movie_id: UUID, data: MovieUpdate) -> Movie:
    try:
        movie = get_movie_by_id(db=db,movie_id=movie_id)

        update_data= data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=422,
                detail="No fields provided for update"
            )
        for field in ("title","duration_minutes"):
            if field in update_data and update_data[field] is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} cannot be null"
                )

        if "poster_url" in update_data and update_data["poster_url"] is not None:
            update_data["poster_url"] = str(update_data["poster_url"])
            

        movie = repository.update_movie(db=db,movie=movie,update_data=update_data)
        db.commit()
        db.refresh(movie)
        return movie
    except Exception:
        db.rollback()
        raise


def publish_movie(db: Session, movie_id: UUID) -> Movie:
    try:
        movie: Movie = get_movie_by_id(db=db,movie_id=movie_id)
        if movie.status != MovieStatus.DRAFT:
            raise HTTPException(
                status_code=409,
                detail="Only draft movies can be published"
            )
        movie.status = MovieStatus.PUBLISHED
        db.commit()
        db.refresh(movie)
        return movie
    except Exception:
        db.rollback()
        raise

def archive_movie(db: Session, movie_id: UUID) -> Movie:
    try:
        movie: Movie = get_movie_by_id(db=db,movie_id=movie_id)
        if movie.status != MovieStatus.PUBLISHED:
            raise HTTPException(
                status_code=409,
                detail="Only published movies can be archived"
            )
        movie.status = MovieStatus.ARCHIVED
        db.commit()
        db.refresh(movie)
        return movie
    except Exception:
        db.rollback()
        raise

def get_published_movie_by_id(db: Session, movie_id: UUID) -> Movie:
    movie = get_movie_by_id(db=db,movie_id=movie_id)
    if movie.status != MovieStatus.PUBLISHED:
        raise HTTPException(
            status_code=404,
            detail="Movie Not Found"
        )
    return movie

def list_all_movies_for_admin(db: Session) -> list[Movie]:
    return repository.list_all_movies_for_admin(db=db)