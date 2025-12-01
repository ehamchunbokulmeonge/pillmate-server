from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from app.database import get_db
from app.models.schedule import Schedule
from app.models.medicine import Medicine
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, TodayScheduleResponse

router = APIRouter()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


@router.get(
    "/today",
    response_model=List[TodayScheduleResponse],
    summary="오늘의 복용 스케줄",
)
async def get_today_schedules(
    db: Session = Depends(get_db)
):
    """오늘 복용 스케줄 조회"""
    today = datetime.now()
    
    schedules = db.query(Schedule).filter(
        Schedule.user_id == MVP_USER_ID,
        Schedule.is_active == True,
        Schedule.start_date <= today,
        Schedule.end_date >= today
    ).all()
    
    return schedules


@router.get(
    "/",
    response_model=List[ScheduleResponse],
    summary="전체 복용 스케줄 조회",
)
async def get_schedules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """스케줄 목록 조회"""
    schedules = db.query(Schedule).filter(
        Schedule.user_id == MVP_USER_ID,
        Schedule.is_active == True
    ).offset(skip).limit(limit).all()
    
    return schedules


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="스케줄 상세 정보",
)
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """스케줄 상세 조회"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == MVP_USER_ID
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    return schedule


@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="복용 스케줄 등록",
    description="약이름, 개수, 복용시간, 복용기간을 입력하여 스케줄을 등록합니다."
)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """스케줄 등록"""
    # Verify medicine exists and belongs to user
    medicine = db.query(Medicine).filter(
        Medicine.id == schedule_data.medicine_id,
        Medicine.user_id == MVP_USER_ID
    ).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    db_schedule = Schedule(
        **schedule_data.model_dump(),
        user_id=MVP_USER_ID
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.put("/{schedule_id}",
            response_model=ScheduleResponse,
            summary="스케줄 수정"
)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """스케줄 수정"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == MVP_USER_ID
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Update fields
    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.delete("/{schedule_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="스케줄 삭제"
)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """스케줄 삭제"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == MVP_USER_ID
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    schedule.is_active = False
    db.commit()
    
    return None
