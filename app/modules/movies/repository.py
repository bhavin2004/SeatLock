from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.movies.models import Movie,MovieStatus


def create_movie(db: Session,movie: Movie)->Movie:
    db.add(movie)
    db.flush()
    return movie

def get_movie_by_id(db: Session, movie_id: UUID) -> Movie | None:
    return db.get(Movie,movie_id)

def list_movies(db: Session, limit: int, offset: int) -> list[Movie]:
    stmt = (
        select(Movie).where(Movie.status == MovieStatus.PUBLISHED)
        .order_by(Movie.created_at.desc(), Movie.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())


def update_movie(db:Session , movie: Movie, update_data: dict) -> Movie:
    for key,val in update_data.items():
        setattr(movie,key,val)
    db.flush()
    return movie


def list_all_movies_for_admin(db: Session) -> list[Movie]:
    stmt = (
        select(Movie)
        .order_by(Movie.created_at.desc(), Movie.id)
    )

    return list(db.scalars(stmt).all())