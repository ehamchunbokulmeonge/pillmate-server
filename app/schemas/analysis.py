from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
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
