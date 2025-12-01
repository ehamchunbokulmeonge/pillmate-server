#!/bin/bash

# ngrok 고정 도메인으로 실행
# 사용법: ./start_ngrok.sh

# 여기에 ngrok 대시보드에서 생성한 도메인을 입력하세요
NGROK_DOMAIN="your-domain.ngrok-free.app"

echo "🚀 ngrok 시작 중..."
echo "도메인: $NGROK_DOMAIN"

# 기존 ngrok 프로세스 종료
pkill -f ngrok

# 고정 도메인으로 ngrok 시작
nohup ngrok http --domain=$NGROK_DOMAIN 8000 > ngrok.log 2>&1 &

sleep 3

# URL 확인
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('tunnels'):
        url = data['tunnels'][0]['public_url']
        print(f'\n✅ ngrok 시작 완료!')
        print(f'🌐 고정 URL: {url}')
        print(f'📄 API 문서: {url}/docs')
    else:
        print('❌ ngrok 터널을 찾을 수 없습니다.')
except:
    print('❌ ngrok이 시작되지 않았습니다. ngrok.log를 확인하세요.')
"
