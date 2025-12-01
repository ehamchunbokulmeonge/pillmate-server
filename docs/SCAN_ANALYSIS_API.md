# 약 스캔 분석 API 가이드

## 개요

약 패키지를 촬영하면 OCR로 인식하고, 사용자의 현재 복용 중인 약물 목록과 비교하여 위험성을 분석합니다.

## 주요 기능

1. **OCR 인식**: Google Cloud Vision API로 약 패키지 이미지에서 텍스트 추출
2. **약물 매칭**: AI Hub 데이터셋(8,024개 약물)에서 가장 유사한 약물 검색
3. **위험성 분석**: OpenAI GPT-4o-mini를 사용하여 다음을 분석
   - **성분 중복** (duplicate): 같은 성분이 여러 약에 포함되어 있는지 확인
   - **약물 상호작용** (interaction): 특정 약물 조합 시 부작용 발생 가능성
   - **복용 시간 충돌** (timing): 같은 시간에 복용하면 안 되는 약물 조합

## API 엔드포인트

### POST /api/v1/analysis/scan

약 사진을 OCR로 인식하고 위험성 분석

#### 요청 (Request)

```json
{
  "image_base64": "base64로 인코딩된 이미지 문자열",
  "user_id": 1
}
```

**Parameters:**
- `image_base64` (string, required): 약 패키지 이미지를 Base64로 인코딩한 문자열
- `user_id` (integer, optional): 사용자 ID (기본값: 1, MVP에서는 고정값)

#### 응답 (Response)

```json
{
  "scannedMedication": {
    "name": "타이레놀정 500mg",
    "ingredient": "아세트아미노펜",
    "amount": "500mg"
  },
  "overallRiskScore": 7,
  "riskLevel": "medium",
  "riskItems": [
    {
      "id": "duplicate-1",
      "type": "duplicate",
      "severity": "high",
      "title": "성분 중복 감지",
      "description": "아세트아미노펜 성분이 게보린정과 중복됩니다. 하루 최대 권장량을 초과할 수 있습니다.",
      "percentage": 85
    },
    {
      "id": "timing-1",
      "type": "timing",
      "severity": "medium",
      "title": "복용 시간 충돌",
      "description": "아침 시간대에 복용하는 약이 3개 이상입니다. 시간 간격을 두고 복용하세요.",
      "percentage": 60
    }
  ],
  "warnings": [
    "아세트아미노펜 성분이 중복됩니다. 과다 복용에 주의하세요.",
    "같은 시간대에 복용하는 약이 많습니다. 약사와 상담을 권장합니다."
  ],
  "summary": "현재 복용 중인 약물들의 성분을 분석한 결과, **아세트아미노펜 성분이 중복**되어 있어 간 손상 위험이 있습니다.",
  "sections": [
    {
      "icon": "time",
      "title": "권장 복용 방법",
      "content": "• 타이레놀은 **아침 8시에 복용**\n• 이부프로펜이 포함된 약은 최소 **6시간 간격**을 두고 오후 2시 이후 복용\n• 하루 아세트아미노펜 총 섭취량이 **4000mg을 넘지 않도록** 주의"
    },
    {
      "icon": "alert-circle",
      "title": "주의사항",
      "content": "• 공복 복용 시 위장 장애가 발생할 수 있으니 **식후 30분 이내** 복용 권장\n• 음주 시 간 손상 위험이 증가하므로 복용 기간 중 **금주 필수**\n• **3일 이상** 증상이 지속되면 복용을 중단하고 의사와 상담하세요"
    },
    {
      "icon": "swap-horizontal",
      "title": "대체 방안",
      "content": "성분 중복을 피하고 싶다면 **아세트아미노펜이 없는 소염진통제**로 대체하거나, 약사와 상담하여 용량 조절을 고려해보세요."
    }
  ]
}
```

**Response Fields:**

- `scannedMedication`: 촬영한 약물 정보
  - `name`: 약물명
  - `ingredient`: 주성분명
  - `amount`: 함량

- `overallRiskScore`: 전체 위험도 점수 (0-10)
  - 0-3: 낮음 (low)
  - 4-6: 중간 (medium)
  - 7-10: 높음 (high)

- `riskLevel`: 위험 등급 ("low" | "medium" | "high")

- `riskItems`: 발견된 위험 항목 배열
  - `id`: 고유 ID
  - `type`: 위험 유형
    - `duplicate`: 성분 중복
    - `interaction`: 약물 상호작용
    - `timing`: 복용 시간 충돌
  - `severity`: 심각도 ("low" | "medium" | "high")
  - `title`: 위험 항목 제목
  - `description`: 상세 설명
  - `percentage`: 위험도 퍼센트 (0-100)

- `warnings`: 경고 메시지 배열

- `summary`: 분석 결과 요약 (강조: `**텍스트**`)

- `sections`: 가이드 섹션 배열 (최소 1개)
  - `icon`: Ionicons 아이콘 이름
    - `"time"`: 복용 시간 관련
    - `"alert-circle"`: 주의사항
    - `"swap-horizontal"`: 대체 방안
    - `"flask"`: 성분 관련
    - `"fitness"`: 건강 관련
    - `"restaurant"`: 식사 관련
    - `"water"`: 수분/음료 관련
    - `"moon"`: 수면 관련
  - `title`: 섹션 제목
  - `content`: 섹션 본문
    - 강조: `**텍스트**` 형식 사용
    - 줄바꿈: `\n`으로 구분
    - 목록 형식 권장 (`•` 또는 숫자)

## 사용 예시

### Python

```python
import requests
import base64

# 1. 이미지 파일을 Base64로 인코딩
with open("타이레놀.jpg", "rb") as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")

# 2. API 요청
url = "http://localhost:8000/api/v1/analysis/scan"
payload = {
    "image_base64": image_base64,
    "user_id": 1
}

response = requests.post(url, json=payload)
result = response.json()

# 3. 결과 확인
print(f"촬영한 약물: {result['scannedMedication']['name']}")
print(f"위험도 점수: {result['overallRiskScore']}/10")
print(f"위험 등급: {result['riskLevel']}")

for item in result['riskItems']:
    print(f"\n[{item['type']}] {item['title']}")
    print(f"  심각도: {item['severity']}")
    print(f"  설명: {item['description']}")
```

### cURL

```bash
# 이미지를 Base64로 인코딩
IMAGE_BASE64=$(base64 -i 타이레놀.jpg)

# API 요청
curl -X POST "http://localhost:8000/api/v1/analysis/scan" \
  -H "Content-Type: application/json" \
  -d "{
    \"image_base64\": \"$IMAGE_BASE64\",
    \"user_id\": 1
  }"
```

### 테스트 스크립트 사용

```bash
# 기본 사용
python test_scan_analysis.py 타이레놀.jpg

# 테스트용 약물 추가 후 실행 (성분 중복 테스트)
python test_scan_analysis.py 타이밍정.jpg --add-test-med
```

## 분석 로직

### 1. OCR 처리
- Google Cloud Vision API로 이미지에서 텍스트 추출
- Tesseract OCR 폴백 (Google API 실패 시)

### 2. 약물 매칭
- AI Hub 데이터셋에서 fuzzy matching
- 점수 계산 로직:
  - 약물명 매칭: 60점 (용량 일치 시 +20점)
  - 각인 정보 매칭: 25점
  - 제조사 매칭: 10점
  - 성분 매칭: 5점
- 80% 이상 유사도로 매칭

### 3. AI 분석
OpenAI GPT-4o-mini를 사용하여 다음을 분석:

#### 성분 중복 (duplicate)
- 촬영한 약물의 주성분이 현재 복용 중인 약에 포함되어 있는지 확인
- 예시: 아세트아미노펜이 타이레놀과 게보린에 모두 포함

#### 약물 상호작용 (interaction)
- 특정 약물 조합 시 부작용 발생 가능성
- 예시:
  - 이부프로펜 + 아스피린 → 위장 출혈 위험
  - 카페인 함유 약물 다량 복용 → 불면, 심계항진

#### 복용 시간 충돌 (timing)
- 같은 시간대에 복용하는 약물이 너무 많은 경우
- 예시: 아침 시간대에 5개 이상의 약물 복용

## 에러 처리

### 400 Bad Request
```json
{
  "detail": "약물 텍스트를 인식할 수 없습니다. 더 선명한 사진으로 다시 시도해주세요."
}
```

OCR에서 텍스트를 추출할 수 없는 경우

### 404 Not Found
```json
{
  "detail": "매칭되는 약물을 찾을 수 없습니다."
}
```

AI Hub 데이터셋에서 약물을 찾을 수 없는 경우

### 500 Internal Server Error
```json
{
  "detail": "약물 분석 중 오류가 발생했습니다: <오류 메시지>"
}
```

서버 내부 오류 발생 시

## 주의사항

1. **이미지 품질**: 약 패키지 텍스트가 선명하게 보이는 사진을 사용하세요
2. **조명**: 밝은 곳에서 촬영하여 글씨가 잘 보이도록 하세요
3. **각도**: 정면에서 촬영하여 텍스트가 왜곡되지 않도록 하세요
4. **파일 크기**: Base64 인코딩 시 약 10MB 이하 권장

## 환경 변수 설정

```bash
# .env 파일
OPENAI_API_KEY=sk-...  # OpenAI API 키 (필수)
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-vision-key.json  # Google Cloud Vision API 키 경로 (필수)
```

## 관련 API

- `POST /api/v1/ocr/recognize`: 약 패키지 OCR만 수행 (분석 없음)
- `POST /api/v1/analysis/detect-duplicate`: 약물 ID 목록으로 중복 성분 분석
- `GET /api/v1/medicines`: 사용자의 복용 약물 목록 조회
- `POST /api/v1/medicines`: 새로운 약물 추가

## 버전 히스토리

- **v1.0.0** (2024-01-XX)
  - 초기 릴리스
  - OCR 인식 및 AI 분석 기능
  - 성분 중복, 약물 상호작용, 복용 시간 충돌 감지
