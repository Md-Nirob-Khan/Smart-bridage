"""Database tables (SRS section 6)."""
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="viewer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    inspections: Mapped[list["Inspection"]] = relationship(back_populates="inspector")


class Bridge(Base):
    __tablename__ = "bridges"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    location: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    length_m: Mapped[float | None] = mapped_column(Float)
    construction_year: Mapped[int | None] = mapped_column(Integer)
    bridge_type: Mapped[str | None] = mapped_column(String(50))  # RCC, steel, prestressed...
    daily_traffic: Mapped[int | None] = mapped_column(Integer)
    last_inspection_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    inspections: Mapped[list["Inspection"]] = relationship(
        back_populates="bridge", cascade="all, delete-orphan"
    )


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True)
    bridge_id: Mapped[int] = mapped_column(ForeignKey("bridges.id"), index=True)
    inspector_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    damage_score: Mapped[float | None] = mapped_column(Float)
    risk_score: Mapped[float | None] = mapped_column(Float)
    priority: Mapped[str | None] = mapped_column(String(10))  # High / Medium / Low
    recommendation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bridge: Mapped[Bridge] = relationship(back_populates="inspections")
    inspector: Mapped[User] = relationship(back_populates="inspections")
    images: Mapped[list["InspectionImage"]] = relationship(
        back_populates="inspection", cascade="all, delete-orphan"
    )


class InspectionImage(Base):
    __tablename__ = "inspection_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), index=True)
    component: Mapped[str | None] = mapped_column(String(30))  # deck, girder, pier...
    original_path: Mapped[str] = mapped_column(String(500))
    annotated_path: Mapped[str | None] = mapped_column(String(500))
    defect_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="pending")  # or "No Damage Detected"

    inspection: Mapped[Inspection] = relationship(back_populates="images")
    defects: Mapped[list["Defect"]] = relationship(
        back_populates="image", cascade="all, delete-orphan"
    )


class Defect(Base):
    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("inspection_images.id"), index=True)
    damage_type: Mapped[str] = mapped_column(String(30))  # crack, spalling, corrosion...
    confidence: Mapped[float] = mapped_column(Float)
    bbox: Mapped[list | None] = mapped_column(JSON)  # [x1, y1, x2, y2]
    length_px: Mapped[float | None] = mapped_column(Float)
    max_width_px: Mapped[float | None] = mapped_column(Float)
    avg_width_px: Mapped[float | None] = mapped_column(Float)
    area_px: Mapped[float | None] = mapped_column(Float)
    area_percent: Mapped[float | None] = mapped_column(Float)
    length_mm: Mapped[float | None] = mapped_column(Float)
    width_mm: Mapped[float | None] = mapped_column(Float)
    severity: Mapped[str | None] = mapped_column(String(10))  # Low / Medium / High

    image: Mapped[InspectionImage] = relationship(back_populates="defects")
