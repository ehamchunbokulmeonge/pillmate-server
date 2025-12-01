#!/bin/bash

echo "🤖 AI 약사 필메이트 빠른 테스트"
echo "================================"
echo ""

# API 서버가 실행 중인지 확인
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ 서버가 실행되지 않았습니다."
    echo "먼저 서버를 실행하세요: ./run.sh"
    exit 1
fi

echo "✅ 서버 연결 확인 완료"
echo ""

# 테스트 질문들
questions=(
    "안녕하세요, 이름이 뭐예요?"
    "두통이 있는데 어떤 약을 먹어야 하나요?"
    "타이레놀과 게보린을 같이 먹어도 되나요?"
    "날씨가 어때요?"
)

for i in "${!questions[@]}"; do
    question="${questions[$i]}"
    num=$((i + 1))
    
    echo "📝 테스트 $num/${#questions[@]}"
    echo "👤 질문: $question"
    echo "💬 처리 중..."
    
    # API 호출
    response=$(curl -s -X POST "http://localhost:8000/api/v1/chat" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$question\"}" 2>/dev/null)
    
    # 응답 파싱 (jq 사용)
    if command -v jq &> /dev/null; then
        message=$(echo "$response" | jq -r '.message')
        echo "🤖 필메이트: $message"
    else
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # API 호출 간격
    sleep 1
done

echo "✅ 모든 테스트 완료!"
echo ""
echo "💡 더 자세한 테스트:"
echo "   python test_chat.py          # 대화형 테스트"
echo "   python test_scenarios.py     # 시나리오 테스트"
