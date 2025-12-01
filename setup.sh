#!/bin/bash

echo "🚀 PillMate 서버 설치 시작..."

# 1. Python 가상환경 생성
echo "📦 가상환경 생성 중..."
python3 -m venv venv

# 2. 가상환경 활성화
echo "✅ 가상환경 활성화..."
source venv/bin/activate

# 3. pip 업그레이드
echo "⬆️  pip 업그레이드..."
pip install --upgrade pip

# 4. 의존성 설치
echo "📚 의존성 패키지 설치 중..."
pip install -r requirements.txt

# 5. uploads 디렉토리 생성
echo "📁 uploads 디렉토리 생성..."
mkdir -p uploads

# 6. 완료 메시지
echo ""
echo "✨ 설치 완료!"
echo ""
echo "다음 단계:"
echo "1. PostgreSQL 데이터베이스를 생성하세요:"
echo "   createdb pillmate_db"
echo ""
echo "2. .env 파일을 확인하고 필요한 설정을 수정하세요"
echo ""
echo "3. 데이터베이스 마이그레이션을 실행하세요:"
echo "   alembic revision --autogenerate -m 'Initial migration'"
echo "   alembic upgrade head"
echo ""
echo "4. 서버를 실행하세요:"
echo "   uvicorn app.main:app --reload"
echo ""
