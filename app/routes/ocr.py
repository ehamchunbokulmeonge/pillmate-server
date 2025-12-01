from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import base64
import io
import json
from typing import List
from PIL import Image
from app.database import get_db
from app.schemas.ocr import OCRRequest, OCRResponse, MedicineMatch
from app.config import get_settings
from app.utils.aihub_loader import get_aihub_loader

router = APIRouter()
settings = get_settings()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


def extract_text_from_image(image_base64: str) -> str:
    """
    Google Cloud Vision API를 사용하여 이미지에서 텍스트 추출
    
    TODO: Google Cloud Vision API 연동
    현재는 임시로 빈 문자열 반환
    """
    # 실제 구현 시:
    # from google.cloud import vision
    # client = vision.ImageAnnotatorClient()
    # image = vision.Image(content=base64.b64decode(image_base64))
    # response = client.text_detection(image=image)
    # texts = response.text_annotations
    # return texts[0].description if texts else ""
    
    return "임시 추출 텍스트"


def search_medicine_in_aihub_data(extracted_text: str) -> List[MedicineMatch]:
    """
    추출된 텍스트로 AI Hub 데이터셋에서 약 검색
    
    AI Hub 데이터 파일 (JSON)을 로드하여 매칭
    - 약 이름 (dl_name)
    - 각인 정보 (print_front, print_back)
    - 제조사 (dl_company)
    등으로 검색
    """
    loader = get_aihub_loader()
    
    if not loader.loaded:
        # AI Hub 데이터가 없을 경우 샘플 데이터 반환
        return [
            MedicineMatch(
                drug_name="비타비백정 100mg/병 (샘플)",
                drug_name_en="Vita B 100 Tab.",
                company="(주)유한양행",
                ingredients="니코틴산아미드|피리독신염산염97%과립|리보플라빈|티아민질산염",
                shape="타원형",
                color="빨강",
                print_front="YH",
                print_back="V100",
                item_seq="200802213",
                confidence=0.0
            )
        ]
    
    # 실제 검색
    results = loader.search_by_name(extracted_text, limit=5)
    
    matches = []
    for med_data in results:
        match = MedicineMatch(
            drug_name=med_data.get("dl_name", ""),
            drug_name_en=med_data.get("dl_name_en"),
            company=med_data.get("dl_company", ""),
            ingredients=med_data.get("dl_material", ""),
            shape=med_data.get("drug_shape"),
            color=med_data.get("color_class1"),
            print_front=med_data.get("print_front"),
            print_back=med_data.get("print_back"),
            image_url=med_data.get("img_key"),
            item_seq=str(med_data.get("item_seq", "")),
            confidence=0.8  # TODO: 실제 매칭 알고리즘으로 계산
        )
        matches.append(match)
    
    return matches


@router.post(
    "/recognize",
    response_model=OCRResponse,
    summary="약 패키지 OCR 인식",
    description="""
    약 패키지 이미지에서 텍스트를 추출하고 AI Hub 데이터셋과 매칭합니다.
    
    **기능:**
    - Google Cloud Vision API로 텍스트 추출
    - AI Hub 의약품 이미지 데이터셋 매칭
    - 약 이름, 제조사, 성분 정보 제공
    - 각인 정보 (앞면/뒷면) 매칭
    
    **사용 방법:**
    1. 약 패키지 사진 촬영
    2. Base64로 인코딩하여 전송
    3. 매칭된 약 정보 확인
    """
)
async def recognize_medicine_package(
    ocr_data: OCRRequest,
    db: Session = Depends(get_db)
):
    """약 패키지 이미지 인식 및 매칭"""
    try:
        # 1. Google Cloud Vision API로 텍스트 추출
        extracted_text = extract_text_from_image(ocr_data.image_base64)
        
        # 2. AI Hub 데이터셋에서 약 검색
        matched_medicines = search_medicine_in_aihub_data(extracted_text)
        
        return OCRResponse(
            extracted_text=extracted_text,
            detected_medicines=matched_medicines,
            success=True
        )
        
    except Exception as e:
        return OCRResponse(
            extracted_text="",
            detected_medicines=[],
            success=False,
            error_message=f"OCR 처리 실패: {str(e)}"
        )


@router.post(
    "/search",
    summary="약 이름으로 검색",
    description="""
    약 이름, 제조사, 각인 정보로 AI Hub 데이터셋에서 검색합니다.
    
    **검색 가능한 정보:**
    - 약 이름 (한글/영문)
    - 제조사명
    - 앞면/뒷면 각인 문자
    """
)
async def search_medicine_by_name(
    query: str,
    db: Session = Depends(get_db)
):
    """약 이름으로 AI Hub 데이터셋 검색"""
    try:
        # AI Hub 데이터셋에서 검색
        results = search_medicine_in_aihub_data(query)
        
        return {
            "query": query,
            "count": len(results),
            "results": [result.model_dump() for result in results]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"검색 실패: {str(e)}"
        )
