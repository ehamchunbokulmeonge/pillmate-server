from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional
from app.models.schedule import FrequencyType, TimeOfDay


class ScheduleBase(BaseModel):
    medicine_id: int
    time_of_day: TimeOfDay
    specific_time: Optional[time] = None
    frequency_type: FrequencyType = FrequencyType.DAILY
    frequency_value: int = 1
    start_date: datetime
    end_date: Optional[datetime] = None
    notification_enabled: bool = True
    notes: Optional[str] = None


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    medicine_id: Optional[int] = None
    time_of_day: Optional[TimeOfDay] = None
    specific_time: Optional[time] = None
    frequency_type: Optional[FrequencyType] = None
    frequency_value: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notification_enabled: Optional[bool] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodayScheduleResponse(BaseModel):
    schedule: ScheduleResponse
    medicine_name: str
    medicine_image_url: Optional[str] = None

    class Config:
        from_attributes = True
