# AI Hub 데이터셋 설정 가이드

## 1. AI Hub 데이터 다운로드

https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=576

위 링크에서 "의약품 이미지" 데이터셋을 다운로드하세요.

### 다운로드할 파일 (라벨링 데이터만)
`01.데이터/1.Training/라벨링데이터/` 폴더에서:

**경구약제조합 5000종** (8개 파일, 약 60MB):
- TL_1_조합.zip ~ TL_8_조합.zip

**단일경구약제 5000종** (81개 파일, 약 2GB):
- TL_1_단일.zip ~ TL_81_단일.zip

⚠️ **주의**: 원천데이터(TS_*.zip)는 이미지 파일로 용량이 매우 크니 다운로드하지 마세요. 라벨링 데이터(JSON)만 있으면 됩니다.

## 2. 데이터 파일 배치

```bash
# 1. 프로젝트 루트에 data 폴더 생성
cd /Users/tlsalsco/pillmate
mkdir -p data/aihub

# 2. 다운로드 폴더로 이동 (다운로드한 ZIP 파일 위치)
cd ~/Downloads

# 3. 압축 해제 (JSON 파일만 data/aihub/에 직접 저장됨)
for file in TL_*.zip; do 
    unzip -j "$file" '*.json' -d /Users/tlsalsco/pillmate/data/aihub/
done

# 또는 하나씩 압축 해제
unzip -j 'TL_1_조합.zip' '*.json' -d /Users/tlsalsco/pillmate/data/aihub/
```

**최종 구조**:
```
/Users/tlsalsco/pillmate/
└── data/
    └── aihub/
        ├── 파일1.json
        ├── 파일2.json
        ├── 파일3.json
        └── ... (JSON 파일들만 직접 위치)
```

⚠️ **중요**: `-j` 옵션으로 폴더 구조 없이 JSON 파일만 추출합니다!

## 3. 데이터 구조

AI Hub JSON 파일 구조:
```json
{
  "images": [
    {
      "dl_name": "비타비백정 100mg/병",
      "dl_name_en": "Vita B 100 Tab.",
      "dl_company": "(주)유한양행",
      "dl_material": "니코틴산아미드|피리독신염산염...",
      "print_front": "YH",
      "print_back": "V100",
      "drug_shape": "타원형",
      "color_class1": "빨강",
      "item_seq": 200802213,
      ...
    }
  ]
}
```

## 4. OCR API 사용

### 약 패키지 인식

```python
import base64
import requests

# 이미지를 Base64로 인코딩
with open("medicine.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

# API 호출
response = requests.post(
    "http://localhost:8000/api/v1/ocr/recognize",
    json={"image_base64": image_base64}
)

result = response.json()
print(f"추출 텍스트: {result['extracted_text']}")
print(f"매칭된 약: {result['detected_medicines']}")
```

### 약 이름으로 검색

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/search?query=타이레놀"
```

## 5. Google Cloud Vision 설정 (선택사항)

현재는 임시 텍스트를 반환하지만, 실제 OCR을 사용하려면:

1. Google Cloud Console에서 프로젝트 생성
2. Cloud Vision API 활성화
3. 서비스 계정 키 생성 (JSON)
4. 환경변수 설정:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

5. `requirements.txt`에 추가:
```
google-cloud-vision==3.4.5
```

6. `app/routes/ocr.py`의 `extract_text_from_image()` 함수 주석 해제

## 6. 데이터 로드 확인

```bash
# 1. JSON 파일 확인
ls -lh data/aihub/*.json | head -5

# 2. JSON 구조 확인 (첫 번째 파일의 구조 확인)
python3 -c "
import json
import glob
files = glob.glob('data/aihub/*.json')
if files:
    with open(files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        print('Keys:', list(data.keys()))
        if 'images' in data and data['images']:
            print('First item keys:', list(data['images'][0].keys()))
            print('Sample:', json.dumps(data['images'][0], ensure_ascii=False, indent=2))
else:
    print('JSON 파일이 없습니다.')
"

# 3. 데이터 로드 확인
python -c "from app.utils.aihub_loader import get_aihub_loader; loader = get_aihub_loader(); print(f'로드된 약 개수: {len(loader.medicine_data)}')"

# 4. 검색 테스트
python -c "from app.utils.aihub_loader import get_aihub_loader; loader = get_aihub_loader(); results = loader.search_by_name('타이레놀'); print(f'검색 결과: {len(results)}개'); print(results[0] if results else '결과 없음')"
```

## 7. 주의사항

- AI Hub 데이터는 용량이 크므로 `.gitignore`에 `data/` 폴더가 포함되어 있습니다
- 라벨링 데이터(TL_*.zip)만 다운로드하면 약 2GB 정도입니다
- 원천데이터(TS_*.zip)는 이미지 파일로 수백 GB이므로 다운로드 불필요
- 실제 배포 시에는 데이터베이스에 저장하거나 S3 등 클라우드 스토리지 사용 권장
- Google Cloud Vision API는 유료이므로 비용 확인 필요
