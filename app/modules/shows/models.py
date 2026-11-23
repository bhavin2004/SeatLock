from app.database.base import Base
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Uuid,DateTime
from sqlalchemy.orm import Mapped,mapped_column



class Show(Base):

    __tablename__ = "shows"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    movie_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("movies.id"),
        nullable=False,
    )

    screen_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("screens.id"),
        nullable=False,
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )