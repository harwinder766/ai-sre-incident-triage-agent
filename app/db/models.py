from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Incident information
    incident_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    error_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # Classification
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    severity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Investigation
    investigation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Root cause analysis
    root_cause: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Remediation
    remediation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Incident lifecycle
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="open",
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    