"""타이밍정 스캔 테스트"""
import base64
import requests
import json

# 1. 이미지를 Base64로 변환
image_path = "/Users/tlsalsco/Downloads/타이밍정.jpg"
with open(image_path, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

print(f"✅ 이미지 로드 완료 (크기: {len(image_base64)} bytes)")

# 2. API 요청
url = "http://localhost:8000/api/v1/analysis/scan"
payload = {
    "image_base64": image_base64
}

print("\n📤 약 스캔 분석 API 요청 중...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()
    
    print("\n" + "="*70)
    print("✅ 약 스캔 분석 완료!")
    print("="*70)
    
    # 스캔된 약물 정보
    scanned = result['scannedMedication']
    print(f"\n💊 스캔된 약물:")
    print(f"  - 약물명: {scanned['name']}")
    print(f"  - 성분: {scanned['ingredient']}")
    print(f"  - 함량: {scanned['amount']}")
    
    # 위험도
    print(f"\n⚠️  위험도: {result['riskLevel'].upper()} (점수: {result['overallRiskScore']}/10)")
    
    # 위험 항목
    if result.get('riskItems'):
        print(f"\n🚨 발견된 위험 항목: {len(result['riskItems'])}개")
        for item in result['riskItems']:
            severity_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(item['severity'], "⚪")
            print(f"\n  {severity_icon} [{item['type'].upper()}] {item['title']}")
            print(f"     {item['description']}")
            print(f"     위험도: {item['percentage']}%")
    
    # 요약
    print(f"\n📝 요약:")
    print(f"  {result['summary']}")
    
    # 상세 섹션
    if result.get('sections'):
        print(f"\n📌 상세 가이드:")
        for section in result['sections']:
            print(f"\n  [{section['icon']}] {section['title']}")
            for line in section['content'].split('\n'):
                print(f"      {line}")
    
    # 경고사항
    if result.get('warnings'):
        print(f"\n⚠️  경고사항:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    print("\n" + "="*70)
    
else:
    print(f"\n❌ 에러 발생: {response.status_code}")
    print(response.text)
