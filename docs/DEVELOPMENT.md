# PillMate 개발 가이드

## 프로젝트 구조 상세

```
pillmate/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 환경 설정
│   ├── database.py          # DB 연결 설정
│   │
│   ├── models/              # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── user.py          # 사용자 모델
│   │   ├── medicine.py      # 약 모델
│   │   ├── schedule.py      # 복용 스케줄 모델
│   │   ├── chat_history.py  # 채팅 이력 모델
│   │   └── analysis.py      # 분석 결과 모델
│   │
│   ├── schemas/             # Pydantic 스키마 (요청/응답)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── medicine.py
│   │   ├── schedule.py
│   │   ├── chat.py
│   │   ├── analysis.py
│   │   └── ocr.py
│   │
│   ├── routes/              # API 라우터
│   │   ├── __init__.py
│   │   ├── medicines.py     # 약 관리
│   │   ├── schedules.py     # 복용 스케줄
│   │   ├── ocr.py           # OCR 약 인식
│   │   ├── analysis.py      # 성분 분석/중복 감지
│   │   └── chat.py          # AI 약사 상담
│   │
│   ├── services/            # 비즈니스 로직 (추후 확장용)
│   │   └── __init__.py
│   │
│   └── utils/               # 유틸리티 함수
│       ├── __init__.py
│       ├── helpers.py
│       ├── file_handler.py
│       └── image_processing.py
│
├── alembic/                 # 데이터베이스 마이그레이션
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── uploads/                 # 업로드 파일 저장소
├── .env                     # 환경 변수
├── .gitignore
├── alembic.ini              # Alembic 설정
├── requirements.txt         # Python 의존성
├── scripts/
│   ├── setup.sh             # 설치 스크립트
│   ├── run.sh               # 실행 스크립트
│   └── test_api.sh          # API 테스트
└── README.md
```

## 주요 기능별 구현 상태

### ✅ 완료된 기능

1. **프로젝트 기본 구조**
   - FastAPI 앱 초기화
   - PostgreSQL 연결 설정
   - 환경 설정 관리

2. **인증 시스템** (`/api/v1/auth`)
   - 회원가입: `POST /register`
   - 로그인: `POST /login` (JWT 토큰 발급)
   - 현재 사용자 정보: `GET /me`
   - Password hashing (bcrypt)
   - JWT 토큰 인증

3. **약 관리** (`/api/v1/medicines`)
   - 약 목록 조회: `GET /`
   - 약 상세 조회: `GET /{id}`
   - 약 등록: `POST /`
   - 약 수정: `PUT /{id}`
   - 약 삭제: `DELETE /{id}`

4. **복용 스케줄** (`/api/v1/schedules`)
   - 오늘 스케줄: `GET /today`
   - 스케줄 목록: `GET /`
   - 스케줄 등록: `POST /`
   - 스케줄 수정: `PUT /{id}`
   - 복용 완료: `POST /{id}/complete`
   - 스케줄 삭제: `DELETE /{id}`

5. **OCR 약 인식** (`/api/v1/ocr`)
   - 이미지 인식: `POST /recognize`
   - 약 검색: `POST /search`

6. **성분 분석** (`/api/v1/analysis`)
   - 중복 성분 감지: `POST /detect-duplicate`
   - 분석 이력: `GET /history`

7. **AI 약사 상담** (`/api/v1/chat`)
   - 채팅: `POST /`
   - 채팅 이력: `GET /history`
   - 세션 삭제: `DELETE /history/{session_id}`

## 데이터베이스 모델

### User (사용자)
- 이메일, 사용자명, 비밀번호
- 전화번호, 전체 이름
- 활성화 상태

### Medicine (약)
- 약 이름, 제조사, 품목기준코드
- 효능, 용법용량
- 성분 정보
- 경고사항, 부작용
- 이미지 URL
- 복용량 정보

### Schedule (복용 스케줄)
- 약 정보 참조
- 복용 시간 (아침/점심/저녁/밤)
- 복용 빈도 (매일/매주/매월/필요시)
- 시작일/종료일
- 알림 설정
- 복용 완료 여부

### ChatHistory (채팅 이력)
- 사용자 참조
- 메시지 역할 (user/assistant)
- 메시지 내용
- 세션 ID

### AnalysisResult (분석 결과)
- 분석 대상 약물 ID 목록
- 위험도 (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
- 중복 성분 정보
- 상호작용 정보
- 경고 및 권장사항

## API 인증

모든 보호된 엔드포인트는 JWT Bearer 토큰을 요구합니다:

```bash
# 1. 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 2. 응답에서 access_token 받기
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer"
# }

# 3. 토큰을 사용하여 API 호출
curl -X GET "http://localhost:8000/api/v1/medicines" \
  -H "Authorization: Bearer eyJ..."
```

## 환경 변수 설정

`.env` 파일에서 다음 설정들을 수정하세요:

### 필수 설정
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `SECRET_KEY`: JWT 토큰 서명용 비밀 키 (프로덕션에서 반드시 변경!)

### 선택 설정
- `OPENAI_API_KEY`: AI 약사 기능 사용 시 필요
- `TESSERACT_CMD`: Tesseract OCR 실행 파일 경로
- `ALLOWED_ORIGINS`: CORS 허용 오리진

## 다음 단계 구현 가이드

### 1. OCR 기능 개선
현재는 기본 Tesseract OCR만 구현되어 있습니다. 다음 기능 추가를 권장합니다:

```python
# app/services/medicine_api.py 생성
# 공공데이터포털 의약품개요정보 API 연동
async def search_medicine_by_name(name: str):
    # API 호출 로직
    pass
```

### 2. AI 약사 기능 개선
현재는 간단한 키워드 기반 응답입니다. OpenAI API 연동:

```python
# app/routes/chat.py 수정
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

async def get_ai_response(message: str, history: list):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 전문 약사입니다."},
            *history,
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content
```

### 3. 알림 기능 추가
- APNs (iOS) / FCM (Android) 연동
- 복용 시간 알림
- 약 재고 부족 알림

### 4. 파일 업로드 개선
현재는 Base64만 지원합니다. 멀티파트 폼 데이터 지원:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_medicine_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # 파일 저장 로직
    pass
```

### 5. 테스트 코드 작성
```bash
# tests/ 디렉토리 생성
mkdir tests
touch tests/__init__.py
touch tests/test_auth.py
touch tests/test_medicines.py

# pytest 실행
pytest
```

## 배포 가이드

### Docker 사용 (권장)

1. Dockerfile 생성
2. docker-compose.yml 생성 (PostgreSQL 포함)
3. 빌드 및 실행

### 일반 서버 배포

1. Gunicorn + Uvicorn worker 사용
2. Nginx 리버스 프록시 설정
3. Let's Encrypt SSL 인증서
4. systemd 서비스 등록

## 문제 해결

### 패키지 import 에러
현재 lint 에러는 패키지가 설치되지 않아서 발생합니다. 다음 명령으로 해결:

```bash
./setup.sh
# 또는
pip install -r requirements.txt
```

### Tesseract 설치
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-kor
```

### PostgreSQL 설치
```bash
# macOS
brew install postgresql
brew services start postgresql
createdb pillmate_db

# Ubuntu/Debian
sudo apt-get install postgresql
sudo systemctl start postgresql
sudo -u postgres createdb pillmate_db
```

## 유용한 명령어

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행 (개발 모드)
uvicorn app.main:app --reload

# 데이터베이스 마이그레이션 생성
alembic revision --autogenerate -m "migration message"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 되돌리기
alembic downgrade -1

# 의존성 추가 후 저장
pip freeze > requirements.txt

# 코드 포맷팅 (선택)
black app/
isort app/

# 타입 체크 (선택)
mypy app/
```

## 라이센스

MIT
