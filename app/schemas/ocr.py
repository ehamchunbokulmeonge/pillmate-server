from pydantic import BaseModel
from typing import Optional, List


class OCRRequest(BaseModel):
    image_base64: str  # Base64 인코딩된 약 패키지 이미지


class MedicineMatch(BaseModel):
    """AI Hub 데이터셋 매칭 결과"""
    drug_name: str  # 약 이름 (dl_name)
    drug_name_en: Optional[str] = None  # 영문 이름
    company: str  # 제조사
    ingredients: str  # 성분 (dl_material)
    shape: Optional[str] = None  # 모양
    color: Optional[str] = None  # 색상
    print_front: Optional[str] = None  # 앞면 각인
    print_back: Optional[str] = None  # 뒷면 각인
    image_url: Optional[str] = None  # 약 이미지
    item_seq: Optional[str] = None  # 품목기준코드
    confidence: float = 0.0  # 매칭 신뢰도


class OCRResponse(BaseModel):
    extracted_text: str  # Google Vision으로 추출한 텍스트
    detected_medicines: List[MedicineMatch] = []  # 매칭된 약 정보 리스트
    success: bool = True
    error_message: Optional[str] = None


class MedicineSearchRequest(BaseModel):
    query: str


class MedicineSearchResponse(BaseModel):
    results: list  # 검색 결과 리스트
