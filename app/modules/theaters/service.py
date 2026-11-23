from sqlalchemy.orm import Session
from app.modules.theaters.models import Theater
from app.modules.theaters.schemas import TheaterCreate
from app.modules.theaters import repository as theater_repository

def create_theater(db: Session, *, data: TheaterCreate) -> Theater:
    theater = Theater(
        name=data.name,
        address=data.address,
        city=data.city,
        timezone=data.timezone
    )
    try:
        theater_repository.add_theater(db, theater=theater)
        db.commit()

    except Exception:
        db.rollback()
        raise
    return theater
