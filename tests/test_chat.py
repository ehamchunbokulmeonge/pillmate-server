"""
AI 약사 필메이트 챗봇 테스트 스크립트

사용법:
    python test_chat.py "두통이 있어요"
    python test_chat.py "타이레놀과 게보린을 같이 먹어도 되나요?"
"""

import asyncio
import sys
from app.database import SessionLocal
from app.routes.chat import get_ai_response
from app.config import get_settings

settings = get_settings()


async def test_chat(message: str):
    """채팅 테스트"""
    print(f"\n👤 사용자: {message}")
    print("💬 필메이트가 답변 중...")
    
    response, metadata = await get_ai_response(message)
    
    print(f"\n🤖 필메이트: {response}")
    print(f"\n📊 메타데이터:")
    print(f"  - 모델: {metadata.get('model', 'N/A')}")
    print(f"  - 사용 토큰: {metadata.get('tokens_used', 'N/A')}")
    print()


async def interactive_chat():
    """대화형 채팅 테스트"""
    print("=" * 60)
    print("🏥 AI 약사 필메이트 챗봇 테스트")
    print("=" * 60)
    print("종료하려면 'exit' 또는 'quit'를 입력하세요.\n")
    
    chat_history = []
    
    while True:
        try:
            user_input = input("👤 질문: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', '종료']:
                print("\n👋 채팅을 종료합니다. 건강하세요!")
                break
            
            print("💬 필메이트가 답변 중...\n")
            
            # AI 응답 생성
            response, metadata = await get_ai_response(user_input, chat_history)
            
            print(f"🤖 필메이트: {response}\n")
            
            # 대화 이력 저장
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\n👋 채팅을 종료합니다. 건강하세요!")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}\n")


def main():
    if len(sys.argv) > 1:
        # 명령행 인자로 메시지를 받은 경우
        message = " ".join(sys.argv[1:])
        asyncio.run(test_chat(message))
    else:
        # 대화형 모드
        asyncio.run(interactive_chat())


if __name__ == "__main__":
    main()
