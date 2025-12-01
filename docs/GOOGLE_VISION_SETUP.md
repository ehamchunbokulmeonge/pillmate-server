# Google Cloud Vision API 설정 가이드

## 1. Google Cloud 프로젝트 생성

1. https://console.cloud.google.com 접속
2. 우측 상단 프로젝트 선택 → "새 프로젝트" 클릭
3. 프로젝트 이름 입력 (예: `pillmate-ocr`)
4. "만들기" 클릭

## 2. Cloud Vision API 활성화

1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. "Cloud Vision API" 검색
3. "사용 설정" 클릭

## 3. 서비스 계정 생성 및 키 다운로드

### 3.1 서비스 계정 생성
1. 좌측 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. 상단 "+ 사용자 인증 정보 만들기" → "서비스 계정" 선택
3. 서비스 계정 세부정보 입력:
   - **서비스 계정 이름**: `pillmate-vision-ocr`
   - **서비스 계정 ID**: 자동 생성됨
   - **설명**: "PillMate OCR 서비스"
4. "만들기 및 계속하기" 클릭

### 3.2 역할 부여
5. "역할 선택" 드롭다운에서:
   - "Cloud Vision" → "Cloud Vision API 사용자" 선택
   - 또는 "기본" → "편집자" (개발 환경용)
6. "계속" 클릭
7. "완료" 클릭

### 3.3 키 다운로드
8. 생성된 서비스 계정 목록에서 방금 만든 계정 클릭
9. 상단 탭 중 "키" 선택
10. "키 추가" → "새 키 만들기"
11. 키 유형: **JSON** 선택
12. "만들기" 클릭
13. JSON 파일이 자동으로 다운로드됩니다

## 4. 프로젝트에 키 파일 설정

### 4.1 키 파일 저장
다운로드한 JSON 키 파일을 프로젝트의 `credentials/` 폴더에 저장:

```bash
# 프로젝트 루트에서
mkdir -p credentials
mv ~/Downloads/pillmate-ocr-*.json credentials/google-vision-key.json
```

### 4.2 환경 변수 설정
`.env` 파일이 이미 설정되어 있습니다:
```
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-vision-key.json
```

## 5. 테스트

### 5.1 서버 재시작
```bash
./scripts/run.sh
```

### 5.2 OCR 테스트
```bash
# 이미지로 테스트
python test_ocr.py ~/Downloads/타이레놀.jpeg

# 또는 API로 테스트
curl -X POST "http://localhost:8000/api/ocr/recognize" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANS..."
  }'
```

## 6. 요금 정보

### 무료 할당량 (매월)
- **OCR 요청**: 첫 1,000건 무료
- **추가 요금**: 1,000건당 $1.50

### 비용 절감 팁
1. 개발 중에는 테스트 이미지를 캐싱하여 재사용
2. 배치 처리 사용 (한 번에 여러 이미지)
3. 불필요한 기능 비활성화 (`TEXT_DETECTION`만 사용)

## 7. 보안 주의사항

⚠️ **중요**: JSON 키 파일은 절대 Git에 커밋하지 마세요!

- `credentials/` 폴더는 `.gitignore`에 추가되어 있습니다
- JSON 키는 서버 관리자 권한을 가집니다
- 프로덕션 환경에서는 환경 변수로 키 내용 전체를 설정하는 것을 권장합니다

## 8. 프로덕션 배포 시

### 환경 변수로 직접 설정 (권장)
```bash
# JSON 파일 내용을 환경 변수로
export GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type": "service_account", ...}'
```

### 또는 서버에 파일 업로드
```bash
# 서버에 안전하게 파일 복사
scp credentials/google-vision-key.json user@server:/app/credentials/
```

## 문제 해결

### "Could not load credentials" 오류
```bash
# 파일 경로 확인
ls -la credentials/google-vision-key.json

# 파일 권한 확인
chmod 600 credentials/google-vision-key.json
```

### API가 활성화되지 않음
- Google Cloud Console에서 "Cloud Vision API"가 사용 설정되어 있는지 확인
- 프로젝트가 올바르게 선택되어 있는지 확인

### 요금 한도 초과
- Google Cloud Console → "결제" → "할당량" 확인
- 필요 시 일일 한도 설정

## 참고 링크

- [Cloud Vision API 공식 문서](https://cloud.google.com/vision/docs)
- [가격 책정](https://cloud.google.com/vision/pricing)
- [Python 클라이언트 라이브러리](https://googleapis.dev/python/vision/latest/index.html)
