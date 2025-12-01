#!/usr/bin/env python3
"""
약 스캔 분석 API 테스트
"""
import requests
import base64
import json
from pathlib import Path

# API 설정
BASE_URL = "http://localhost:8000/api/v1"

def test_scan_analysis(image_path: str):
    """약 스캔 분석 테스트"""
    
    # 1. 이미지를 Base64로 인코딩
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
    
    print(f"\n{'='*60}")
    print(f"테스트 이미지: {image_path}")
    print(f"{'='*60}\n")
    
    # 2. 약 스캔 분석 API 호출
    url = f"{BASE_URL}/analysis/scan"
    payload = {
        "image_base64": image_base64,
        "user_id": 1
    }
    
    print(f"API 호출: POST {url}")
    print(f"사용자 ID: 1")
    print("\n분석 중...\n")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ 분석 성공!\n")
            
            # 촬영한 약물 정보
            scanned = result["scannedMedication"]
            print(f"📦 촬영한 약물:")
            print(f"  - 이름: {scanned['name']}")
            print(f"  - 성분: {scanned['ingredient']}")
            print(f"  - 함량: {scanned['amount']}")
            print()
            
            # 위험도 점수
            print(f"⚠️  전체 위험도 점수: {result['overallRiskScore']}/10")
            print(f"📊 위험 등급: {result['riskLevel'].upper()}")
            print()
            
            # 위험 항목
            if result["riskItems"]:
                print(f"🚨 발견된 위험 항목 ({len(result['riskItems'])}개):")
                for i, item in enumerate(result["riskItems"], 1):
                    print(f"\n  [{i}] {item['title']}")
                    print(f"      유형: {item['type']}")
                    print(f"      심각도: {item['severity']}")
                    print(f"      위험도: {item['percentage']}%")
                    print(f"      설명: {item['description']}")
            else:
                print("✅ 발견된 위험 항목 없음")
            
            print()
            
            # 경고 메시지
            if result["warnings"]:
                print(f"⚠️  경고 메시지:")
                for warning in result["warnings"]:
                    print(f"  - {warning}")
            else:
                print("✅ 경고 메시지 없음")
            
            print(f"\n{'='*60}\n")
            
            # 전체 JSON 출력
            print("📄 전체 응답 JSON:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
        else:
            print(f"❌ 오류 발생 (HTTP {response.status_code})")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()


def test_add_test_medicine():
    """테스트용 약물 추가"""
    url = f"{BASE_URL}/medicines"
    
    # 카페인 포함 약물 추가 (타이밍정과 성분 중복 테스트)
    test_medicine = {
        "name": "게보린정",
        "ingredient": "카페인무수물",
        "amount": "50mg",
        "description": "두통약",
        "morning": True,
        "afternoon": False,
        "evening": False
    }
    
    print(f"\n{'='*60}")
    print(f"테스트용 약물 추가: {test_medicine['name']}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, json=test_medicine)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 약물 추가 성공!")
            print(f"ID: {result['id']}")
            print(f"이름: {result['name']}")
            print(f"성분: {result.get('ingredient', '없음')}")
            print(f"함량: {result.get('amount', '없음')}")
        else:
            print(f"❌ 약물 추가 실패 (HTTP {response.status_code})")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")


def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python test_scan_analysis.py <이미지_경로> [--add-test-med]")
        print("\n예시:")
        print("  python test_scan_analysis.py 타이밍정.jpg")
        print("  python test_scan_analysis.py 타이레놀.jpeg --add-test-med")
        return
    
    image_path = sys.argv[1]
    
    # 테스트 약물 추가 옵션
    if "--add-test-med" in sys.argv:
        test_add_test_medicine()
        print("\n대기 중...\n")
        import time
        time.sleep(1)
    
    # 이미지 파일 존재 확인
    if not Path(image_path).exists():
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
        return
    
    # 분석 테스트 실행
    test_scan_analysis(image_path)


if __name__ == "__main__":
    main()
