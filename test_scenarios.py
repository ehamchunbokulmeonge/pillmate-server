"""
AI 약사 필메이트 - 다양한 시나리오 테스트

OpenAI API를 사용하여 다양한 질문에 대한 응답을 테스트합니다.
"""

import asyncio
from app.routes.chat import get_ai_response


# 테스트 케이스들
test_cases = [
    # 1. 이름 관련 질문
    {
        "category": "이름 확인",
        "questions": [
            "이름이 뭐야?",
            "너 누구야?",
            "당신의 이름은?",
        ]
    },
    
    # 2. 약 관련 질문 (정상)
    {
        "category": "약 복용 상담",
        "questions": [
            "두통이 있는데 어떤 약을 먹어야 하나요?",
            "타이레놀과 게보린을 같이 먹어도 되나요?",
            "아스피린은 언제 복용하는 게 좋나요?",
            "감기약과 진통제를 함께 복용해도 괜찮을까요?",
        ]
    },
    
    # 3. 의학적 진단 질문
    {
        "category": "의학적 진단 (전문가 상담 권유 필요)",
        "questions": [
            "배가 계속 아픈데 무슨 병인가요?",
            "열이 39도인데 병원 가야 하나요?",
        ]
    },
    
    # 4. 약과 무관한 질문
    {
        "category": "약 외 질문 (거부 응답 필요)",
        "questions": [
            "날씨가 어때?",
            "저녁 메뉴 추천해줘",
            "파이썬 코딩 알려줘",
        ]
    },
    
    # 5. 불명확한 질문
    {
        "category": "불명확한 질문 (재질문 필요)",
        "questions": [
            "약",
            "이거 먹어도 돼?",
        ]
    },
]


async def run_tests():
    """모든 테스트 케이스 실행"""
    print("=" * 80)
    print("🏥 AI 약사 필메이트 - 시나리오 테스트")
    print("=" * 80)
    
    for test_group in test_cases:
        category = test_group["category"]
        questions = test_group["questions"]
        
        print(f"\n\n{'='*80}")
        print(f"📋 카테고리: {category}")
        print(f"{'='*80}\n")
        
        for i, question in enumerate(questions, 1):
            print(f"\n[테스트 {i}/{len(questions)}]")
            print(f"👤 질문: {question}")
            print("💭 처리 중...", end="", flush=True)
            
            try:
                response, metadata = await get_ai_response(question)
                print("\r" + " " * 20 + "\r", end="")  # 'Processing...' 지우기
                print(f"🤖 필메이트:\n{response}")
                
                # 응답 분석
                print(f"\n📊 분석:")
                print(f"  - 존댓말 사용: {'✅' if any(word in response for word in ['입니다', '습니다', '세요', '드립']) else '❌'}")
                print(f"  - 이모티콘 없음: {'✅' if not any(char in response for char in '😊😄🎉👍💊') else '❌'}")
                print(f"  - 답변 길이: {len(response)} 글자")
                print(f"  - 모델: {metadata.get('model', 'N/A')}")
                print(f"  - 토큰 사용: {metadata.get('tokens_used', 'N/A')}")
                
            except Exception as e:
                print(f"\n❌ 오류: {e}")
            
            print("-" * 80)
        
        # 각 카테고리 사이에 대기
        await asyncio.sleep(1)
    
    print("\n\n" + "=" * 80)
    print("✅ 모든 테스트 완료!")
    print("=" * 80)


async def test_conversation_flow():
    """대화 흐름 테스트 (이력 기반)"""
    print("\n\n" + "=" * 80)
    print("💬 대화 흐름 테스트 (이력 기반 응답)")
    print("=" * 80 + "\n")
    
    conversation = [
        "두통약 추천해주세요",
        "그럼 타이레놀은 하루에 몇 번 먹어야 하나요?",
        "식후에 먹어야 하나요?",
        "감사합니다",
    ]
    
    history = []
    
    for i, message in enumerate(conversation, 1):
        print(f"\n[대화 {i}]")
        print(f"👤 사용자: {message}")
        print("💬 처리 중...", end="", flush=True)
        
        response, metadata = await get_ai_response(message, history)
        print("\r" + " " * 20 + "\r", end="")
        print(f"🤖 필메이트: {response}")
        
        # 대화 이력에 추가
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        
        print("-" * 80)
        await asyncio.sleep(1)


async def main():
    """메인 테스트 함수"""
    # 기본 시나리오 테스트
    await run_tests()
    
    # 대화 흐름 테스트
    await test_conversation_flow()
    
    print("\n\n🎉 모든 테스트가 완료되었습니다!")


if __name__ == "__main__":
    asyncio.run(main())
