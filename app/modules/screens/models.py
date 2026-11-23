from app.database.base import Base
import uuid
from sqlalchemy import Uuid,String,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column


class Screen(Base):

    __tablename__ = "screens"
    
    __table_args__ = (
        UniqueConstraint(
            "theater_id",
            "name",
            name="uq_screens_theater_name"
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    theater_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("theaters.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

