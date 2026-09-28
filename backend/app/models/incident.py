from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    service: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH")
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    summary: Mapped[str] = mapped_column(Text)
    logs: Mapped[str] = mapped_column(Text, default="")
    metrics: Mapped[str] = mapped_column(Text, default="")
    deployment: Mapped[str] = mapped_column(String(120), default="")
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
