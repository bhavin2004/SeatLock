from app.database.base import Base
import uuid
from datetime import datetime
from sqlalchemy import Uuid,String,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column


class Theater(Base):

    __tablename__ = "theaters"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        String(500), 
        nullable=False 
        )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False
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