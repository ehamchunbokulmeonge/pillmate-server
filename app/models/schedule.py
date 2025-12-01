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
    
    # 복용 시간
    time_of_day = Column(SQLEnum(TimeOfDay), nullable=False)
    specific_time = Column(Time)  # 특정 시간 (예: 08:00)
    
    # 복용 빈도
    frequency_type = Column(SQLEnum(FrequencyType), default=FrequencyType.DAILY)
    frequency_value = Column(Integer, default=1)  # 빈도 값 (예: 하루 3번이면 3)
    
    # 복용 기간
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # 알림 설정
    notification_enabled = Column(Boolean, default=True)
    
    # 복용 완료 여부
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    # 메타 정보
    notes = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="schedules")
    medicine = relationship("Medicine", back_populates="schedules")
