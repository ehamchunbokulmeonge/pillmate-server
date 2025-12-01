from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from app.database import get_db
from app.models.chat_history import ChatHistory, MessageRole
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.config import get_settings
from app.services.rag_service import search_by_question

router = APIRouter()
settings = get_settings()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


async def get_ai_response(message: str, chat_history: List[dict] = None, user_medicines: List[dict] = None, medical_conditions: List[str] = None) -> tuple[str, dict]:
    """
    AI 약사 필메이트 응답 생성 (RAG 통합 + 사용자 정보)
    OpenAI GPT-4o API + DUR 데이터 검색 + 사용자 복용 약물 및 지병
    
    Args:
        message: 사용자 질문
        chat_history: 이전 대화 이력
        user_medicines: 사용자가 복용 중인 약물 목록
        medical_conditions: 사용자의 지병 목록
    
    Returns:
        tuple: (response_text, metadata)
            - response_text: AI 응답 텍스트
            - metadata: 토큰 사용량, 모델 정보 등
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # RAG: 사용자 질문과 관련된 DUR 안전 정보 검색
        try:
            rag_results = search_by_question(message, k=3)
            
            # RAG 컨텍스트 생성
            rag_context = ""
            if rag_results:
                rag_context = "\n\n**참고할 의약품 안전 정보 (DUR 데이터):**\n"
                for i, result in enumerate(rag_results, 1):
                    rag_context += f"\n{i}. {result['content']}\n"
        except Exception as e:
            print(f"RAG 검색 오류 (무시하고 계속): {e}")
            rag_context = ""
        
        # 사용자 정보 컨텍스트 생성
        user_context = ""
        
        if medical_conditions:
            user_context += f"\n\n**사용자의 지병**: {', '.join(medical_conditions)}"
        
        if user_medicines:
            user_context += "\n\n**사용자가 현재 복용 중인 약물**:\n"
            for med in user_medicines:
                user_context += f"- {med.get('name', '알 수 없음')} ({med.get('ingredient', '성분 미상')})\n"
        
        # 시스템 프롬프트: AI 약사 필메이트의 역할과 규칙
        system_prompt = """당신은 '필메이트'라는 이름의 AI 약사 챗봇입니다.

필수 규칙:

1. 항상 부드럽고 자연스러운 존댓말을 사용하세요. 약사와 환자가 대화하듯이 편안하게 답변하세요.

2. 이모티콘은 사용하지 마세요.

3. 이름을 묻는 질문에는 "저는 AI 약사 필메이트입니다."라고만 답변하세요.

4. 약과 복약, 성분, 복용 시 주의사항 등 의약품 관련 질문에만 답변하세요.

5. 의학적 진단이나 처방이 필요한 질문에는 "정확한 진단이 필요할 수 있으니 의료 전문가에게 상담받으시는 걸 권장드려요."라고 안내하세요.

6. 약과 관련 없는 질문에는 "죄송하지만, 저는 약과 복약 관련 질문에만 답변할 수 있어요."라고 정중히 안내하세요.

7. 욕설이나 부적절한 표현이 포함된 질문에는 "부적절한 표현은 사용하지 말아주세요."라고 답변하세요.

8. 질문이 불명확하면 구체적으로 어떤 부분이 궁금한지 자연스럽게 되물어보세요.

9. 답변은 간결하면서도 충분한 정보를 담아 제공하세요. 약국에서 약사가 설명하듯이 자연스럽게 답변하세요.

10. 단정적인 표현(반드시, 절대 등)은 피하고, "~할 수 있어요", "~하시는 게 좋아요" 같은 부드러운 표현을 사용하세요.

11. **중요**: DUR 데이터나 제공된 데이터의 존재 여부를 절대 언급하지 마세요. "제공된 데이터에 없으므로", "DUR 정보가 없습니다" 같은 표현을 사용하지 마세요.

12. 더 자세한 정보가 필요한 경우, "더 궁금하신 점이 있으시면 언제든지 저에게 물어보세요." 정도로 자연스럽게 마무리하세요.

13. 기계적이거나 형식적인 답변을 피하고, 실제 약국에서 약사가 환자에게 설명하듯이 친근하고 이해하기 쉽게 답변하세요.

14. **매우 중요**: "주의가 필요합니다", "영향을 미칠 수 있습니다" 같은 모호한 표현만 사용하지 마세요. 반드시 구체적인 이유와 예시를 함께 설명해주세요.
    - 나쁜 예: "주의가 필요합니다."
    - 좋은 예: "**간 기능에 부담**을 줄 수 있어서 주의가 필요해요. 예를 들어, 아세트아미노펜과 알코올을 함께 복용하면 **간 손상 위험이 높아질 수** 있거든요."
    
15. **사용자의 복용 약물과 지병을 반드시 고려**하여 답변하세요. 위에 제공된 사용자 정보를 활용해 맞춤형 조언을 제공하세요.

16. **답변 형식**: 중요한 키워드나 강조할 내용은 **별표**로 감싸서 표시하세요. 예: "**간 손상 위험**", "**혈당 조절**", "**약물 상호작용**" 등

**중요**: 위에 제공된 "참고할 의약품 안전 정보 (DUR 데이터)"가 있다면, 이를 자연스럽게 활용하여 답변하세요. 하지만 데이터 출처나 존재 여부는 절대 언급하지 마세요."""

        # 메시지 구성
        messages = [{"role": "system", "content": system_prompt}]
        
        # 이전 대화 이력 추가
        if chat_history:
            messages.extend(chat_history[-10:])  # 최근 10개만 사용
        
        # 현재 사용자 메시지 추가 (RAG 컨텍스트 + 사용자 정보 포함)
        user_message = message
        if rag_context or user_context:
            user_message = f"{message}\n{user_context}\n{rag_context}"
        
        messages.append({"role": "user", "content": user_message})
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
        
        # 메타데이터 추출
        metadata = {
            "model": response.model,
            "tokens_used": response.usage.total_tokens if response.usage else None,
            "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
            "completion_tokens": response.usage.completion_tokens if response.usage else None,
        }
        
        return response.choices[0].message.content, metadata
        
    except Exception as e:
        # API 오류 시 기본 응답
        print(f"OpenAI API Error: {e}")
        error_metadata = {
            "model": "error",
            "tokens_used": 0,
            "error": str(e)
        }
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.", error_metadata


@router.post(
    "/",
    response_model=ChatResponse,
    summary="AI 약사 상담",
)
async def chat(
    chat_data: ChatRequest,
    db: Session = Depends(get_db)
):
    """AI 약사 상담"""
    
    # 세션 ID 생성 (새로운 대화인 경우)
    session_id = chat_data.session_id or str(uuid.uuid4())
    
    # 이전 대화 이력 조회 (컨텍스트용)
    if chat_data.session_id:
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.user_id == MVP_USER_ID,
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.created_at).all()
        
        history_for_ai = [
            {"role": msg.role.value, "content": msg.content}
            for msg in chat_history
        ]
    else:
        history_for_ai = []
    
    # 사용자의 복용 중인 약물 및 지병 정보 조회
    from app.models.medicine import Medicine
    from app.models.user import User
    
    user = db.query(User).filter(User.id == MVP_USER_ID).first()
    medical_conditions = user.medical_conditions if user and user.medical_conditions else []
    
    medicines = db.query(Medicine).filter(
        Medicine.user_id == MVP_USER_ID,
        Medicine.is_active == True
    ).all()
    
    user_medicines = [
        {
            "name": med.name,
            "ingredient": med.ingredient,
            "amount": med.amount
        }
        for med in medicines
    ]
    
    # 사용자 메시지 저장
    user_message = ChatHistory(
        user_id=MVP_USER_ID,
        role=MessageRole.USER,
        content=chat_data.message,
        session_id=session_id
    )
    db.add(user_message)
    
    # AI 응답 생성 (사용자 정보 포함)
    ai_response_text, metadata = await get_ai_response(
        chat_data.message, 
        history_for_ai,
        user_medicines=user_medicines,
        medical_conditions=medical_conditions
    )
    
    # AI 응답 저장
    ai_message = ChatHistory(
        user_id=MVP_USER_ID,
        role=MessageRole.ASSISTANT,
        content=ai_response_text,
        session_id=session_id
    )
    db.add(ai_message)
    
    db.commit()
    db.refresh(ai_message)
    
    return ChatResponse(
        message=ai_response_text,
        session_id=session_id,
        created_at=ai_message.created_at,
        tokens_used=metadata.get("tokens_used"),
        model=metadata.get("model")
    )


@router.get("/history",
            response_model=List[ChatHistoryResponse],
            summary="채팅 이력 조회"
)
async def get_chat_history(
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """채팅 이력 조회 (MVP)"""
    query = db.query(ChatHistory).filter(ChatHistory.user_id == MVP_USER_ID)
    
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)
    
    history = query.order_by(ChatHistory.created_at).all()
    
    return history


@router.delete("/history/{session_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="채팅 이력 삭제"
)
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """특정 세션의 채팅 이력 삭제 (MVP)"""
    db.query(ChatHistory).filter(
        ChatHistory.user_id == MVP_USER_ID,
        ChatHistory.session_id == session_id
    ).delete()
    
    db.commit()
    
    return None
