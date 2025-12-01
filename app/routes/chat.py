from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from app.database import get_db
from app.models.chat_history import ChatHistory, MessageRole
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


async def get_ai_response(message: str, chat_history: List[dict] = None) -> tuple[str, dict]:
    """
    AI 약사 필메이트 응답 생성
    OpenAI GPT-4 API 사용
    
    Returns:
        tuple: (response_text, metadata)
            - response_text: AI 응답 텍스트
            - metadata: 토큰 사용량, 모델 정보 등
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # 시스템 프롬프트: AI 약사 필메이트의 역할과 규칙
        system_prompt = """당신은 '필메이트'라는 이름의 AI 약사 챗봇입니다.

필수 규칙:

1. 항상 부드럽고 공손한 존댓말을 사용해야 합니다. 반말은 절대 사용하지 마세요.

2. 이모티콘은 사용하지 마세요.

3. 이름을 묻는 질문에는 "저는 AI 약사 필메이트입니다."라고만 답변하세요.

4. 약과 복약, 성분, 복용 시 주의사항 등 의약품 관련 질문에만 답변하세요.

5. 의학적 진단이나 처방이 필요한 질문에는
   "정확한 진단이 필요할 수 있으니 의료 전문가에게 상담을 권장드립니다."라고 안내하세요.

6. 약과 관련 없는 질문에는
   "죄송하지만, 저는 약과 복약 관련 질문에만 답변할 수 있습니다."라고 정중히 안내하세요.

7. 욕설이나 부적절한 표현이 포함된 질문에는
   "부적절한 표현은 사용하지 말아주세요."라고 답변하세요.

8. 질문이 불명확하면 구체적으로 어떤 부분이 궁금한지 정중하게 되물어보세요.

9. 답변은 간결하면서도 충분한 정보를 담아 제공하세요.

10. 단정적인 표현(반드시, 절대 등)은 피하고, 가능성이나 주의 중심으로 설명하세요."""

        # 메시지 구성
        messages = [{"role": "system", "content": system_prompt}]
        
        # 이전 대화 이력 추가
        if chat_history:
            messages.extend(chat_history[-10:])  # 최근 10개만 사용
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": message})
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
    
    # 사용자 메시지 저장
    user_message = ChatHistory(
        user_id=MVP_USER_ID,
        role=MessageRole.USER,
        content=chat_data.message,
        session_id=session_id
    )
    db.add(user_message)
    
    # AI 응답 생성
    ai_response_text, metadata = await get_ai_response(chat_data.message, history_for_ai)
    
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
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """채팅 이력 조회 (MVP)"""
    query = db.query(ChatHistory).filter(ChatHistory.user_id == MVP_USER_ID)
    
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)
    
    history = query.order_by(ChatHistory.created_at).offset(skip).limit(limit).all()
    
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
