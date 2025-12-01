from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from app.database import get_db
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineResponse, MedicineDetailResponse

router = APIRouter()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


@router.get(
    "/",
    response_model=List[MedicineResponse],
    summary="내 약 목록 조회"
)
async def get_medicines(
    db: Session = Depends(get_db)
):
    """내 약 목록 조회"""
    medicines = db.query(Medicine).filter(
        Medicine.user_id == MVP_USER_ID,
        Medicine.is_active == True
    ).all()
    return medicines


@router.get(
    "/{medicine_id}",
    response_model=MedicineDetailResponse,
    summary="약 상세 정보 조회",
    description="약 스캔 시 생성된 분석 보고서를 그대로 반환합니다."
)
async def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """약 상세 조회 - 스캔 보고서 포함"""
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == MVP_USER_ID
    ).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # scan_report를 JSON으로 파싱
    response_data = {
        "id": medicine.id,
        "user_id": medicine.user_id,
        "name": medicine.name,
        "ingredient": medicine.ingredient,
        "amount": medicine.amount,
        "scan_report": json.loads(medicine.scan_report) if medicine.scan_report else None,
        "is_active": medicine.is_active,
        "created_at": medicine.created_at,
        "updated_at": medicine.updated_at
    }
    
    return response_data


@router.post(
    "/",
    response_model=MedicineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새 약 등록",
    description="약 스캔 후 분석 보고서와 함께 약을 등록합니다."
)
async def create_medicine(
    medicine_data: MedicineCreate,
    db: Session = Depends(get_db)
):
    """약 등록"""
    # scan_report를 JSON 문자열로 변환
    scan_report_json = json.dumps(medicine_data.scan_report) if medicine_data.scan_report else None
    
    db_medicine = Medicine(
        name=medicine_data.name,
        ingredient=medicine_data.ingredient,
        amount=medicine_data.amount,
        scan_report=scan_report_json,
        user_id=MVP_USER_ID
    )
    
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    
    return db_medicine


@router.delete(
    "/{medicine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="약 삭제",
    description="등록된 약을 삭제합니다. 실제로는 is_active를 False로 변경하는 소프트 삭제입니다."
)
async def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """약 삭제 (소프트 삭제)"""
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == MVP_USER_ID
    ).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    medicine.is_active = False
    db.commit()
    
    return None
