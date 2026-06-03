from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.core.config import settings

Path("data").mkdir(exist_ok=True)
engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class MemoryRow(Base):
    __tablename__ = "memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    key: Mapped[str] = mapped_column(String(200), index=True)
    payload: Mapped[str] = mapped_column(Text)
    tier: Mapped[str] = mapped_column(String(50), default="encrypted_operational")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def upsert_memory(memory_type: str, key: str, payload: dict, tier: str = "encrypted_operational") -> None:
    init_db()
    with SessionLocal() as session:
        row = session.query(MemoryRow).filter_by(type=memory_type, key=key).one_or_none()
        now = datetime.utcnow()
        if row:
            row.payload = json.dumps(payload, default=str)
            row.updated_at = now
            row.tier = tier
        else:
            row = MemoryRow(type=memory_type, key=key, payload=json.dumps(payload, default=str), tier=tier)
            session.add(row)
        session.commit()


def list_memories(memory_type: str | None = None) -> list[dict]:
    init_db()
    with SessionLocal() as session:
        query = session.query(MemoryRow)
        if memory_type:
            query = query.filter_by(type=memory_type)
        rows = query.order_by(MemoryRow.updated_at.desc()).all()
        return [
            {
                "id": row.id,
                "type": row.type,
                "key": row.key,
                "payload": json.loads(row.payload),
                "tier": row.tier,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat(),
            }
            for row in rows
        ]
