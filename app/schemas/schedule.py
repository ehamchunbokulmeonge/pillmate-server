from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional


class ScheduleBase(BaseModel):
    medicine_id: int
    medicine_name: str  # 약 이름
    dose_count: int = 1  # 약 개수 (1회 복용량)
    dose_time: time  # 복용 시간
    start_date: datetime  # 복용 시작일
    end_date: datetime  # 복용 종료일


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    medicine_name: Optional[str] = None
    dose_count: Optional[int] = None
    dose_time: Optional[time] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodayScheduleResponse(BaseModel):
    """오늘의 복용 스케줄"""
    id: int
    medicine_id: int
    medicine_name: str
    dose_count: int
    dose_time: time
    
    class Config:
        from_attributes = True