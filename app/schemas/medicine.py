from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MedicineBase(BaseModel):
    name: str
    product_code: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    efficacy: Optional[str] = None
    dosage: Optional[str] = None
    ingredients: Optional[str] = None
    warnings: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None
    dosage_per_time: Optional[float] = None
    dosage_unit: Optional[str] = None


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    product_code: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    efficacy: Optional[str] = None
    dosage: Optional[str] = None
    ingredients: Optional[str] = None
    warnings: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None
    dosage_per_time: Optional[float] = None
    dosage_unit: Optional[str] = None
    is_active: Optional[bool] = None


class MedicineResponse(MedicineBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
