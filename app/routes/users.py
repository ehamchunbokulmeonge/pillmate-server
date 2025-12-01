"""
사용자 지병 관리 API (MVP)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User

router = APIRouter()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


@router.get(
    "/medical-conditions",
    response_model=List[str],
    summary="지병 정보 조회"
)
async def get_medical_conditions(db: Session = Depends(get_db)):
    """현재 사용자의 지병 정보 조회 (MVP)"""
    user = db.query(User).filter(User.id == MVP_USER_ID).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return user.medical_conditions or []


@router.put(
    "/medical-conditions",
    response_model=List[str],
    summary="지병 정보 업데이트"
)
async def update_medical_conditions(
    medical_conditions: List[str],
    db: Session = Depends(get_db)
):
    """
    지병 정보 업데이트 (MVP)
    
    예시:
    ```json
    ["고혈압", "당뇨병", "고지혈증"]
    ```
    """
    user = db.query(User).filter(User.id == MVP_USER_ID).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    user.medical_conditions = medical_conditions
    db.commit()
    db.refresh(user)
    
    return user.medical_conditions or []
