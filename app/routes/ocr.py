from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import base64
import io
from PIL import Image
import pytesseract
from app.database import get_db
from app.schemas.ocr import OCRRequest, OCRResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


@router.post("/recognize", response_model=OCRResponse)
async def recognize_medicine(
    ocr_data: OCRRequest,
    db: Session = Depends(get_db)
):
    """
    약 이미지에서 텍스트 인식 (OCR) (MVP)
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(ocr_data.image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Set Tesseract path if configured
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        
        # Perform OCR
        # 한글 + 영어 인식을 위해 lang='kor+eng' 사용
        text = pytesseract.image_to_string(image, lang='kor+eng')
        
        # TODO: 인식된 텍스트로 약 정보 검색 로직 추가
        # 예: 공공데이터포털 의약품 안전나라 API 연동
        
        return OCRResponse(
            text=text.strip(),
            medicine_info=None,
            confidence=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.post("/search")
async def search_medicine(
    query: str,
    db: Session = Depends(get_db)
):
    """
    약 이름으로 검색 (MVP)
    TODO: 공공데이터 API 연동
    """
    # 실제로는 공공데이터포털의 의약품개요정보 API 등을 호출해야 함
    # 예시 응답
    return {
        "query": query,
        "results": [
            {
                "name": "타이레놀",
                "company": "한국얀센",
                "ingredients": "아세트아미노펜",
                "efficacy": "해열, 진통"
            }
        ]
    }
