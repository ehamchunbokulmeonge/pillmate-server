from pydantic import BaseModel
from typing import Optional


class OCRRequest(BaseModel):
    image_base64: str  # Base64 인코딩된 이미지


class OCRResponse(BaseModel):
    text: str  # 인식된 텍스트
    medicine_info: Optional[dict] = None  # 약 정보 (있을 경우)
    confidence: Optional[float] = None  # 신뢰도


class MedicineSearchRequest(BaseModel):
    query: str


class MedicineSearchResponse(BaseModel):
    results: list  # 검색 결과 리스트
