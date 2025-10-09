from sqlalchemy import Column, String, Integer, Float, ForeignKey
from .base import Base

class UserMetrics(Base):
    __tablename__ = "user_metrics"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    active_cases = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    revenue_generated = Column(Float, default=0.0)
    ai_queries_today = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    time_saved_per_case = Column(Float, default=0.0)
    citation_verification_rate = Column(Float, default=0.0)