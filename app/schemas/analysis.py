from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from app.models.analysis import RiskLevel


class AnalysisRequest(BaseModel):
    medicine_ids: List[int]


class DuplicateIngredient(BaseModel):
    ingredient: str
    count: int
    medicine_ids: List[int]


class Interaction(BaseModel):
    medicine_1_id: int
    medicine_2_id: int
    severity: str
    description: str


class AnalysisResponse(BaseModel):
    risk_level: RiskLevel
    duplicate_ingredients: List[Dict[str, Any]]
    interactions: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]
    created_at: datetime


class AnalysisResultResponse(BaseModel):
    id: int
    user_id: int
    medicine_ids: str
    risk_level: RiskLevel
    duplicate_ingredients: str
    interactions: str
    warnings: Optional[str] = None
    recommendations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== OCR 스캔 약물 분석 스키마 =====

class ScannedMedication(BaseModel):
    """촬영한 약물 정보"""
    name: str = Field(..., description="약물명 (예: 타이레놀 500mg)")
    ingredient: str = Field(..., description="주성분명 (예: 아세트아미노펜)")
    amount: str = Field(..., description="함량 (예: 500mg)")


class RiskItem(BaseModel):
    """위험 항목"""
    id: str = Field(..., description="위험 항목 고유 ID")
    type: Literal["duplicate", "interaction", "timing"] = Field(
        ..., 
        description="위험 유형 (duplicate: 성분 중복, interaction: 상호작용, timing: 시간 충돌)"
    )
    severity: Literal["high", "medium", "low"] = Field(..., description="심각도")
    title: str = Field(..., description="위험 항목 제목")
    description: str = Field(..., description="위험 항목 상세 설명")
    percentage: int = Field(..., ge=0, le=100, description="위험도 퍼센트 (0-100)")


class CommentSection(BaseModel):
    """코멘트 섹션"""
    icon: str = Field(..., description="Ionicons 아이콘 이름 (예: time, alert-circle, swap-horizontal)")
    title: str = Field(..., description="섹션 제목")
    content: str = Field(..., description="섹션 본문 (강조: **텍스트**, 줄바꿈: \\n)")


class MedicationAnalysisResponse(BaseModel):
    """약물 분석 응답"""
    scannedMedication: ScannedMedication = Field(..., description="촬영한 약물 정보")
    overallRiskScore: int = Field(..., ge=0, le=10, description="전체 위험도 점수 (0-10)")
    riskLevel: Literal["high", "medium", "low"] = Field(..., description="위험 등급")
    riskItems: List[RiskItem] = Field(default=[], description="위험 항목 배열")
    warnings: List[str] = Field(default=[], description="약물 상호작용 경고 메시지 배열")
    summary: str = Field(..., description="분석 결과 요약 (강조: **텍스트**)")
    sections: List[CommentSection] = Field(..., min_length=1, description="가이드 섹션 배열 (최소 1개)")


class ScanAnalysisRequest(BaseModel):
    """약 스캔 분석 요청"""
    image_base64: str = Field(..., description="Base64로 인코딩된 약 이미지")
    user_id: int = Field(default=1, description="사용자 ID (MVP: 고정값 1)")

