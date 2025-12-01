# 🚀 PillMate MVP 빠른 시작 가이드

해커톤용 MVP 버전 - 5분 안에 서버 실행하기!

## 1️⃣ 사전 준비

### 필수 설치
- Python 3.9+
- PostgreSQL

### PostgreSQL 설치 (macOS)
```bash
brew install postgresql
brew services start postgresql
```

## 2️⃣ 프로젝트 설정

### 1단계: 저장소 클론
```bash
git clone https://github.com/ehamchunbokulmeonge/pillmate-server.git
cd pillmate-server
```

### 2단계: 자동 설치 스크립트 실행
```bash
./setup.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- 가상환경 생성
- 의존성 패키지 설치
- uploads 디렉토리 생성

### 3단계: 데이터베이스 생성
```bash
createdb pillmate_db
```

### 4단계: 초기 데이터 생성
```bash
source venv/bin/activate
python init_data.py
```

다음이 생성됩니다:
- MVP 테스트 사용자 (ID: 1)
- 샘플 약 데이터 3개
- 샘플 복용 스케줄 2개

### 5단계: 서버 실행
```bash
./run.sh
# 또는
uvicorn app.main:app --reload
```

## 3️⃣ API 테스트

서버가 실행되면 브라우저에서 다음 주소로 접속:

### Swagger UI (추천)
```
http://localhost:8000/docs
```

여기서 모든 API를 바로 테스트할 수 있습니다!

### 주요 엔드포인트

#### 📋 약 목록 조회
```bash
curl http://localhost:8000/api/v1/medicines
```

#### 💊 약 등록
```bash
curl -X POST "http://localhost:8000/api/v1/medicines" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "아스피린",
    "company": "바이엘",
    "efficacy": "해열, 진통"
  }'
```

#### 📅 오늘의 스케줄
```bash
curl http://localhost:8000/api/v1/schedules/today
```

#### 🤖 AI 약사 상담
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "두통이 있을 때 어떤 약을 먹어야 하나요?"
  }'
```

## 4️⃣ MVP 주요 특징

### ✅ 인증 불필요
- 회원가입/로그인 없음
- 모든 데이터는 사용자 ID 1에 저장
- API 토큰 불필요

### ✅ 즉시 테스트 가능
- 샘플 데이터 자동 생성
- Swagger UI에서 즉시 테스트
- 복잡한 설정 없음

### ✅ 모든 기능 포함
- 약 관리 (CRUD)
- 복용 스케줄
- OCR 약 인식
- 성분 분석
- AI 상담

## 5️⃣ 문제 해결

### 포트 충돌
```bash
# 8000번 포트가 사용 중이면 다른 포트 사용
uvicorn app.main:app --reload --port 8001
```

### PostgreSQL 연결 오류
```bash
# .env 파일에서 DATABASE_URL 확인
# 기본값: postgresql://postgres:postgres@localhost:5432/pillmate_db
```

### 패키지 import 오류
```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

### 데이터베이스 초기화
```bash
# 데이터베이스 삭제 후 재생성
dropdb pillmate_db
createdb pillmate_db
python init_data.py
```

## 6️⃣ 다음 단계

### 기능 추가
- `app/routes/` - 새로운 API 엔드포인트 추가
- `app/models/` - 데이터베이스 모델 수정
- `app/schemas/` - 요청/응답 스키마 정의

### OCR 개선
- Tesseract OCR 설치 및 설정
- 한글 언어팩 설치

### AI 상담 개선
- OpenAI API 키 설정
- `.env` 파일에 `OPENAI_API_KEY` 추가

## 📚 추가 문서

- [README.md](README.md) - 전체 프로젝트 개요
- [DEVELOPMENT.md](DEVELOPMENT.md) - 상세 개발 가이드

## 🆘 도움이 필요하신가요?

- GitHub Issues: [여기서 문의](https://github.com/ehamchunbokulmeonge/pillmate-server/issues)
- Swagger UI: http://localhost:8000/docs

---

**해커톤 화이팅! 🚀**
