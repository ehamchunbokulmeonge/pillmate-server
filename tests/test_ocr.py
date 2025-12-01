#!/usr/bin/env python3
"""
OCR API 테스트 스크립트

사용법:
1. 약 패키지 사진 준비
2. python test_ocr.py [이미지_경로]

예시:
python test_ocr.py tylenol.jpg
python test_ocr.py /path/to/medicine.png
"""

import sys
import base64
import requests
import json
from pathlib import Path


def encode_image_to_base64(image_path: str) -> str:
    """이미지 파일을 Base64로 인코딩"""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode('utf-8')


def test_ocr_recognize(image_path: str, api_url: str = "http://localhost:8000"):
    """OCR 인식 API 테스트"""
    print(f"📸 이미지 로드: {image_path}")
    
    # 이미지 Base64 인코딩
    try:
        image_base64 = encode_image_to_base64(image_path)
        print(f"✅ Base64 인코딩 완료 ({len(image_base64)} bytes)")
    except Exception as e:
        print(f"❌ 이미지 로드 실패: {e}")
        return
    
    # API 요청
    url = f"{api_url}/api/v1/ocr/recognize"
    payload = {
        "image_base64": image_base64
    }
    
    print(f"\n🚀 API 요청 중: {url}")
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print("\n" + "="*60)
        print("📊 OCR 인식 결과")
        print("="*60)
        
        # 추출된 텍스트
        print(f"\n📝 추출된 텍스트:")
        print(f"   {result.get('extracted_text', 'N/A')}")
        
        # 매칭된 약 정보
        medicines = result.get('detected_medicines', [])
        print(f"\n💊 매칭된 약: {len(medicines)}개\n")
        
        for i, med in enumerate(medicines[:5], 1):  # 상위 5개만
            print(f"{i}. {med['drug_name']}")
            print(f"   제조사: {med['company']}")
            print(f"   영문명: {med.get('drug_name_en', 'N/A')}")
            print(f"   각인: 앞면={med.get('print_front', '')}, 뒷면={med.get('print_back', '')}")
            print(f"   모양: {med.get('shape', 'N/A')}")
            print(f"   색상: {med.get('color', 'N/A')}")
            print(f"   신뢰도: {med.get('confidence', 0)*100:.1f}%")
            print()
        
        # 전체 결과 저장
        output_file = "ocr_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 전체 결과 저장: {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   응답: {e.response.text}")


def test_ocr_search(query: str, api_url: str = "http://localhost:8000"):
    """약 이름 검색 API 테스트"""
    url = f"{api_url}/api/v1/ocr/search"
    params = {"query": query}
    
    print(f"🔍 검색어: {query}")
    print(f"🚀 API 요청 중: {url}")
    
    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        medicines = result.get('results', [])
        
        print(f"\n💊 검색 결과: {len(medicines)}개\n")
        
        for i, med in enumerate(medicines[:5], 1):
            print(f"{i}. {med['drug_name']}")
            print(f"   제조사: {med['company']}")
            print(f"   각인: {med.get('print_front', '')} / {med.get('print_back', '')}")
            print(f"   신뢰도: {med.get('confidence', 0)*100:.1f}%")
            print()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {e}")


def main():
    if len(sys.argv) < 2:
        print("사용법:")
        print("  이미지 인식: python test_ocr.py [이미지_경로]")
        print("  약 검색:    python test_ocr.py --search [약_이름]")
        print("\n예시:")
        print("  python test_ocr.py medicine.jpg")
        print("  python test_ocr.py --search 타이레놀")
        sys.exit(1)
    
    if sys.argv[1] == "--search":
        if len(sys.argv) < 3:
            print("❌ 검색어를 입력하세요")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        test_ocr_search(query)
    else:
        image_path = sys.argv[1]
        if not Path(image_path).exists():
            print(f"❌ 파일이 없습니다: {image_path}")
            sys.exit(1)
        test_ocr_recognize(image_path)


if __name__ == "__main__":
    main()
