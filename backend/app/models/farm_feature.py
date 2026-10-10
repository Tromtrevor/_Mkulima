from datetime import date

from sqlalchemy import Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FarmFeature(Base):
    __tablename__ = "farm_features"

    feature_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    farm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id"),
        nullable=False
    )

    ndvi_mean: Mapped[float | None] = mapped_column(
        Numeric
    )

    ndvi_min: Mapped[float | None] = mapped_column(
        Numeric
    )

    ndvi_max: Mapped[float | None] = mapped_column(
        Numeric
    )

    rainfall_mm: Mapped[float | None] = mapped_column(
        Numeric
    )

    temperature: Mapped[float | None] = mapped_column(
        Numeric
    )

    pH: Mapped[float | None] = mapped_column(
        Numeric
    )

    nitrogen: Mapped[float | None] = mapped_column(
        Numeric
    )

    observation_date: Mapped[date | None] = mapped_column(
        Date
    )

    cycle_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("crop_cycles.cycle_id"),
    )

