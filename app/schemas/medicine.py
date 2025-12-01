from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.analysis import MedicationAnalysisResponse


class MedicineBase(BaseModel):
    name: str
    ingredient: Optional[str] = None  # 주성분명
    amount: Optional[str] = None  # 함량


class MedicineCreate(MedicineBase):
    """약 등록 시 스캔 보고서 포함"""
    scan_report: Optional[dict] = None  # MedicationAnalysisResponse JSON


class MedicineResponse(MedicineBase):
    """약 정보 응답 (목록용 - 간단한 정보만)"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicineDetailResponse(MedicineResponse):
    """약 상세 정보 (스캔 보고서 포함)"""
    scan_report: Optional[dict] = None  # MedicationAnalysisResponse JSON

    class Config:
        from_attributes = True
