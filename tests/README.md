# 테스트 스크립트

이 폴더에는 API 테스트 및 데모 스크립트가 포함되어 있습니다.

## 파일 목록

### 데이터 초기화
- `insert_test_data.py` - 테스트용 약물 및 스케줄 데이터 삽입

### API 테스트
- `test_scan_analysis.py` - 약 스캔 분석 API 테스트
- `test_timing_scan.py` - 타이밍정 이미지 스캔 테스트
- `test_ocr.py` - OCR 텍스트 인식 테스트
- `test_chat.py` - AI 채팅 API 테스트
- `test_scenarios.py` - 전체 시나리오 테스트

### 데모
- `demo_scan_analysis.py` - 약 스캔 분석 데모

## 사용 방법

```bash
# 가상환경 활성화
source venv/bin/activate

# 테스트 데이터 삽입
python tests/insert_test_data.py

# 약 스캔 테스트
python tests/test_timing_scan.py

# AI 채팅 테스트
python tests/test_chat.py
```
