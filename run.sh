#!/bin/bash

echo "🚀 PillMate 서버 시작..."

# 가상환경 활성화
source venv/bin/activate

# Google Cloud Vision API 설정
export GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-vision-key.json

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
