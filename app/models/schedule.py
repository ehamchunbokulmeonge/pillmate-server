from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class FrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"


class TimeOfDay(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    BEFORE_MEAL = "before_meal"
    AFTER_MEAL = "after_meal"


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    
    # 약 이름 (중복 저장 - 빠른 조회용)
    medicine_name = Column(String(255), nullable=False)
    
    # 약 개수 (1회 복용량)
    dose_count = Column(Integer, nullable=False, default=1)  # 예: 2정
    
    # 복용 시간
    dose_time = Column(Time, nullable=False)  # 복용 시간 (예: 08:00)
    
    # 복용 기간
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # 메타 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="schedules")
    medicine = relationship("Medicine", back_populates="schedules")
