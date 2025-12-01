# 🔐 환경 변수 설정 가이드

## 중요! 시작하기 전에

`.env` 파일에는 **민감한 정보**가 포함되어 있습니다:
- OpenAI API 키
- 데이터베이스 비밀번호
- JWT Secret Key

**절대로 `.env` 파일을 Git에 커밋하지 마세요!**

## 설정 방법

### 1단계: .env 파일 생성

```bash
cp .env.example .env
```

### 2단계: .env 파일 수정

`.env` 파일을 열고 다음 값들을 수정하세요:

#### OpenAI API 키 (필수 - AI 약사 기능)
```bash
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

OpenAI API 키 발급: https://platform.openai.com/api-keys

#### 데이터베이스 설정
```bash
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/pillmate_db
DB_USER=postgres
DB_PASSWORD=your_password
```

#### JWT Secret Key (프로덕션 배포 시)
```bash
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
```

Secret Key 생성:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Git 안전 확인

### .env 파일이 제외되었는지 확인

```bash
git status
```

`.env` 파일이 **보이지 않아야** 합니다! ✅

만약 `.env`가 보인다면:
```bash
git rm --cached .env
git add .gitignore
```

## 팀원과 공유하는 방법

❌ **하지 말 것:**
- `.env` 파일을 Git에 커밋
- API 키를 메신저/이메일로 전송
- 스크린샷에 API 키 노출

✅ **올바른 방법:**
1. `.env.example` 파일만 Git에 포함
2. 팀원에게 별도로 안전한 방법으로 API 키 전달
   - 비밀번호 관리자 (1Password, LastPass 등)
   - 암호화된 메시지
   - 대면 전달

## 현재 프로젝트 설정

### Git에 포함되는 파일 ✅
- `app/` - 소스 코드
- `alembic/` - 마이그레이션 설정
- `*.py` - Python 스크립트
- `*.sh` - 실행 스크립트
- `*.md` - 문서
- `requirements.txt` - 의존성
- `.env.example` - 환경 변수 예시
- `.gitignore` - Git 제외 목록

### Git에서 제외되는 파일 ❌
- `.env` - **실제 환경 변수 (API 키 포함!)**
- `venv/` - 가상환경
- `__pycache__/` - Python 캐시
- `uploads/` - 업로드된 파일
- `*.log` - 로그 파일
- `.DS_Store` - macOS 파일

## 문제 해결

### "Import Error: module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Database connection error"
`.env` 파일에서 `DATABASE_URL` 확인

### "OpenAI API Error"
`.env` 파일에서 `OPENAI_API_KEY` 확인

## 프로덕션 배포 시 주의사항

### 1. DEBUG 모드 비활성화
```bash
DEBUG=False
```

### 2. 강력한 SECRET_KEY 사용
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 3. CORS 설정
```bash
ALLOWED_ORIGINS=https://yourdomain.com
```

### 4. 환경 변수 관리 서비스 사용
- AWS Secrets Manager
- Google Cloud Secret Manager
- Azure Key Vault
- Heroku Config Vars
- Vercel Environment Variables

## 체크리스트

배포 전 확인사항:

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는가?
- [ ] `git status`에 `.env`가 보이지 않는가?
- [ ] `.env.example`은 민감한 정보가 없는가?
- [ ] OpenAI API 키가 올바르게 설정되었는가?
- [ ] 데이터베이스 연결이 정상인가?
- [ ] SECRET_KEY가 프로덕션용으로 변경되었는가?
