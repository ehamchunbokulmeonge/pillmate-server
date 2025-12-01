# PillMate Server (MVP - Hackathon)

약 복용 관리 및 AI 약사 상담 서비스 백엔드 API

> 🚀 **해커톤용 MVP 버전** - 인증 없이 바로 사용 가능합니다!

## 주요 기능

- 📅 **오늘 복용 스케줄**: 일일 약 복용 일정 관리
- 💊 **내 약 관리**: 등록된 약 조회/수정/삭제
- 📸 **OCR 약 인식**: 카메라로 약 정보 자동 인식
- 🔍 **약 성분 분석**: 중복 성분 감지 및 위험도 분석
- 🤖 **AI 약사 상담**: 챗봇 기반 약 관련 상담

## ⚡ MVP 특징

- ✅ **인증 불필요**: 회원가입/로그인 없이 바로 사용
- ✅ **간편한 테스트**: 모든 API를 즉시 테스트 가능
- ✅ **샘플 데이터**: 초기 데이터 자동 생성
- ✅ **AI 약사 챗봇**: OpenAI GPT-4 기반 전문 상담 (필메이트)

## 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **OCR**: Tesseract, OpenCV
- **AI**: OpenAI GPT API

## 프로젝트 구조

```
pillmate/
├── app/
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   ├── database.py      # Database configuration
│   └── main.py          # Application entry point
├── alembic/             # Database migrations
├── uploads/             # File uploads directory
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\\Scripts\\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 필요한 값들을 설정하세요
```

### 4. 데이터베이스 설정

PostgreSQL 데이터베이스를 생성하고 초기 데이터를 생성하세요:

```bash
# 데이터베이스 생성
createdb pillmate_db

# 초기 데이터 생성 (MVP 사용자 및 샘플 데이터)
python init_data.py
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 주소에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤖 AI 약사 테스트

### 빠른 테스트
```bash
./test_api.sh
```

### 대화형 테스트
```bash
python test_chat.py
```

### 전체 시나리오 테스트
```bash
python test_scenarios.py
```

자세한 내용은 [AI_CHAT_GUIDE.md](AI_CHAT_GUIDE.md)를 참고하세요.

## API 엔드포인트

> 💡 **MVP 버전에서는 인증이 필요 없습니다!** 모든 엔드포인트를 바로 호출할 수 있습니다.

### 약 관리
- `GET /api/v1/medicines` - 내 약 목록 조회
- `POST /api/v1/medicines` - 약 등록
- `GET /api/v1/medicines/{id}` - 약 상세 조회
- `PUT /api/v1/medicines/{id}` - 약 정보 수정
- `DELETE /api/v1/medicines/{id}` - 약 삭제

### 복용 스케줄
- `GET /api/v1/schedules/today` - 오늘 복용 스케줄
- `POST /api/v1/schedules` - 스케줄 등록
- `PUT /api/v1/schedules/{id}` - 스케줄 수정

### OCR
- `POST /api/v1/ocr/recognize` - 약 이미지 인식

### 성분 분석
- `POST /api/v1/analysis/detect-duplicate` - 중복 성분 감지

### AI 상담
- `POST /api/v1/chat` - AI 약사 상담

## 개발

### 데이터베이스 마이그레이션 생성

```bash
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

### 테스트 실행

```bash
pytest
```

## 라이센스

MIT
