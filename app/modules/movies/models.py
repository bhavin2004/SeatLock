from app.database.base import Base
import uuid
from datetime import date,datetime
from sqlalchemy import Uuid,String,Date,Text,Integer,CheckConstraint,Enum,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column
import enum


class MovieCertification(enum.Enum):  
    U = "U"
    UA_7_PLUS = "UA 7+"
    UA_13_PLUS = "UA 13+"
    UA_16_PLUS = "UA 16+"
    A = "A"


class MovieStatus(enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"	
    ARCHIVED = "ARCHIVED"


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        CheckConstraint(
            "duration_minutes > 0",
            name="ck_movies_duration_positive"
        ),
    )

    id : Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    poster_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    certification: Mapped[MovieCertification | None] = mapped_column(
        Enum(
        MovieCertification,
        name="movies_certification",
        values_callable=lambda enum_cls: [item.value for item in enum_cls]
        ),
        nullable=True
    )

    status: Mapped[MovieStatus] = mapped_column(
        Enum(
            MovieStatus,
            name="movie_status",
            values_callable = lambda enum_cls: [item.value for item in enum_cls]
        ),
        nullable=False,
        default=MovieStatus.DRAFT
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )