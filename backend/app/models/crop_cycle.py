from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    cycle_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    farm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id"),
        nullable=False
    )

    crop_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("crops.crop_id"),
        nullable=False
    )

    planting_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    harvest_date: Mapped[date | None] = mapped_column(
        Date
    )

    season: Mapped[str | None] = mapped_column(
        String
    )

    expected_yield: Mapped[Decimal | None] = mapped_column(
        Numeric
    )

    actual_yield: Mapped[Decimal | None] = mapped_column(
        Numeric
    )