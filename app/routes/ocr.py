from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import base64
import io
import json
from typing import List
from PIL import Image
from rapidfuzz import fuzz
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
    이미지에서 텍스트 추출
    
    1순위: Google Cloud Vision API (설정된 경우)
    2순위: Tesseract OCR (로컬)
    """
    try:
        # Google Cloud Vision API 사용 (GOOGLE_APPLICATION_CREDENTIALS 설정 시)
        import os
        google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if google_creds:
            print(f"🔑 Google Vision API 키 파일: {google_creds}")
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=base64.b64decode(image_base64))
            response = client.text_detection(image=image)
            if response.text_annotations:
                text = response.text_annotations[0].description
                print(f"✅ Google Vision API 텍스트 추출 성공: {len(text)} 글자")
                return text
            else:
                print("⚠️ Google Vision API: 텍스트를 찾지 못함")
        else:
            print("⚠️ GOOGLE_APPLICATION_CREDENTIALS 환경 변수 없음")
    except Exception as e:
        print(f"❌ Google Vision API 사용 실패: {e}")
    
    # Fallback: pytesseract (간단한 OCR)
    try:
        print("🔄 Tesseract OCR로 대체...")
        import pytesseract
        from PIL import ImageEnhance, ImageFilter
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 이미지 전처리 (OCR 성능 향상)
        image = image.convert('L')  # 흑백 변환
        image = ImageEnhance.Contrast(image).enhance(2.0)  # 대비 증가
        image = image.filter(ImageFilter.SHARPEN)  # 선명도 증가
        
        text = pytesseract.image_to_string(image, lang='kor+eng')
        print(f"✅ Tesseract OCR 완료: {len(text.strip())} 글자")
        return text.strip()
    except Exception as e:
        print(f"❌ Tesseract OCR 실패: {e}")
        return ""


def calculate_match_score(extracted_text: str, med_data: dict) -> float:
    """
    추출된 텍스트와 약 데이터 간의 매칭 점수 계산 (개선된 알고리즘)
    """
    score = 0.0
    text_lower = extracted_text.lower()
    text_tokens = set(filter(None, [t.strip() for t in extracted_text.replace('\n', ' ').split()]))
    
    # 1. 약 이름 매칭 (60점) - 가중치 증가 + 퍼지 매칭
    drug_name = med_data.get("dl_name", "")
    drug_name_clean = drug_name.split("/")[0].strip()  # "타이밍정 50mg/PTP" → "타이밍정 50mg"
    drug_name_base = drug_name_clean.split()[0] if drug_name_clean else ""  # "타이밍정"
    
    # 정확한 매칭
    if drug_name_clean and drug_name_clean in extracted_text:
        score += 60
    # 기본 약 이름만 매칭 (타이밍정)
    elif drug_name_base and drug_name_base in extracted_text:
        score += 55
        # 용량도 매칭되면 보너스 (숫자만 추출해서 비교)
        import re
        dose_numbers_in_text = set(re.findall(r'\d+', extracted_text))
        dose_numbers_in_name = set(re.findall(r'\d+', drug_name_clean))
        if dose_numbers_in_text & dose_numbers_in_name:  # 교집합이 있으면
            score += 20  # 용량 매칭 보너스
    # 퍼지 매칭 (타이밍찜 vs 타이밍정)
    else:
        for token in text_tokens:
            if len(token) >= 2:  # 2글자 이상만 비교
                ratio = fuzz.ratio(token, drug_name_base)
                if ratio >= 80:  # 80% 이상 유사도
                    score += 50 * (ratio / 100.0)
                    break
    
    # 영문명 매칭
    drug_name_en = (med_data.get("dl_name_en") or "").lower()
    if drug_name_en:
        for token in text_tokens:
            if fuzz.ratio(token.lower(), drug_name_en) >= 85:
                score += 35
                break
    
    # 2. 각인 정보 매칭 (25점)
    print_front = (med_data.get("print_front") or "").strip()
    print_back = (med_data.get("print_back") or "").strip()
    
    if print_front and print_front.lower() != "마크" and print_front in extracted_text:
        score += 12.5
    if print_back and print_back in extracted_text:
        score += 12.5
    
    # 3. 제조사 매칭 (10점) - 가중치 감소
    company = med_data.get("dl_company", "")
    company_en = (med_data.get("dl_company_en") or "").lower()
    
    if company and company in extracted_text:
        score += 10
    elif company_en:
        for token in text_tokens:
            if fuzz.ratio(token.lower(), company_en) >= 85:
                score += 8
                break
    
    # 4. 성분명 매칭 (5점) - 가중치 크게 감소
    ingredients = med_data.get("dl_material", "")
    if ingredients:
        for ingredient in ingredients.split("|"):
            ingredient = ingredient.strip()
            if ingredient and ingredient in extracted_text:
                score += 5
                break
            # 퍼지 매칭
            for token in text_tokens:
                if len(token) >= 3 and fuzz.ratio(token, ingredient) >= 85:
                    score += 4
                    break
    
    return min(score / 100.0, 1.0)  # 0.0 ~ 1.0 사이로 정규화


def search_medicine_in_aihub_data(extracted_text: str) -> List[MedicineMatch]:
    """
    추출된 텍스트로 AI Hub 데이터셋에서 약 검색
    
    다중 검색 전략:
    1. 약 이름으로 검색 (dl_name, dl_name_en)
    2. 각인 정보로 검색 (print_front, print_back)
    3. 제조사로 검색 (dl_company)
    4. 매칭 점수 계산 후 정렬
    """
    loader = get_aihub_loader()
    
    if not loader.loaded:
        print("⚠️ AI Hub 데이터가 로드되지 않았습니다.")
        return []
    
    # 다중 검색 전략
    all_results = set()
    
    # 1. 약 이름 검색 - 개선된 토큰 검색
    # 줄바꿈으로 분리된 텍스트를 각각 검색
    search_tokens = extracted_text.replace('\n', ' ').split()
    print(f"🔍 검색 토큰: {search_tokens}")
    
    for token in search_tokens:
        if len(token) >= 2:  # 2글자 이상
            name_results = loader.search_by_name(token, limit=20)
            print(f"  '{token}' 검색 결과: {len(name_results)}개")
            for result in name_results:
                all_results.add(result.get("item_seq"))
    
    # 2. 각인 정보 추출 및 검색 (숫자, 영문 조합)
    import re
    tokens = re.findall(r'[A-Za-z0-9]+', extracted_text)
    for token in tokens:
        if len(token) >= 2:  # 2글자 이상만
            print_results = loader.search_by_print(token, limit=10)
            for result in print_results:
                all_results.add(result.get("item_seq"))
    
    print(f"✅ 총 {len(all_results)}개 약 후보 발견")
    
    # 3. item_seq 기반으로 실제 데이터 가져오기 및 점수 계산
    scored_matches = []
    for item_seq in all_results:
        med_data = loader.get_medicine_by_item_seq(item_seq)
        if med_data:
            score = calculate_match_score(extracted_text, med_data)
            if score > 0:  # 점수가 있는 것만
                drug_name = med_data.get("dl_name", "")
                print(f"  {drug_name}: {score*100:.1f}점")
                scored_matches.append((score, med_data))
    
    # 점수순 정렬
    scored_matches.sort(reverse=True, key=lambda x: x[0])
    
    # MedicineMatch 객체로 변환
    matches = []
    for score, med_data in scored_matches[:10]:  # 상위 10개만
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
            confidence=round(score, 2)
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
