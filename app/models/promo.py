from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric
from app.database import Base


class Promo(Base):
    __tablename__ = "promos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, nullable=False)
    discount_amount = Column(Numeric(12, 2))
    min_transaction = Column(Numeric(12, 2), default=0)
    max_discount = Column(Numeric(12, 2))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)

