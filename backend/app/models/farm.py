from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    farm_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    farmer_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("farmers.farmer_id")
    )

    farm_name: Mapped[str | None] = mapped_column(String(100))

    area_ha: Mapped[float | None] = mapped_column(Numeric(10, 2))

    boundary = mapped_column(
        Geometry("POLYGON", srid=4326)
    )
    
    created_at: Mapped[DateTime | None] = mapped_column(DateTime)