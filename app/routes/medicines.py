from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineResponse

router = APIRouter()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


@router.get("/", response_model=List[MedicineResponse])
async def get_medicines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """내 약 목록 조회 (MVP)"""
    medicines = db.query(Medicine).filter(
        Medicine.user_id == MVP_USER_ID,
        Medicine.is_active == True
    ).offset(skip).limit(limit).all()
    return medicines


@router.get("/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """약 상세 조회 (MVP)"""
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == MVP_USER_ID
    ).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    return medicine


@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine_data: MedicineCreate,
    db: Session = Depends(get_db)
):
    """약 등록 (MVP)"""
    db_medicine = Medicine(
        **medicine_data.model_dump(),
        user_id=MVP_USER_ID
    )
    
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    
    return db_medicine


@router.put("/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    db: Session = Depends(get_db)
):
    """약 정보 수정 (MVP)"""
    medicine = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == MVP_USER_ID
    ).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # Update fields
    update_data = medicine_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medicine, field, value)
    
    db.commit()
    db.refresh(medicine)
    
    return medicine


@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """약 삭제 (소프트 삭제) (MVP)"""
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
