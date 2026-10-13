from datetime import date
from sqlalchemy import Date, Numeric, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class YieldPrediction(Base):
    __tablename__ = "yield_prediction"

    prediction_id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True
    )
    
    cycle_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("crop_cycles.cycle_id"),
        nullable=False
    )
    
    prediction_date: Mapped[date | None] = mapped_column(Date)
    
    predicted_yield: Mapped[float | None] = mapped_column(Numeric)
    
    confidence: Mapped[float | None] = mapped_column(Numeric)
    
    model_version: Mapped[str | None] = mapped_column(String)