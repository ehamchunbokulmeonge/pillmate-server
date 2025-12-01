from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from app.database import get_db
from app.models.chat_history import ChatHistory, MessageRole
from app.models.chat_session import ChatSession
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
        system_prompt = """당신은 '필메이트'라는 이름의 AI 약사 챗봇입니다. 약국에서 약사가 간단명료하게 설명하듯이 답변하세요.

핵심 규칙:

1. **간결하게 답변**: 서론 없이 바로 핵심만 전달하세요.

2. **구체적으로 설명**: "주의가 필요합니다" 같은 모호한 표현 금지. 왜 주의해야 하는지 구체적 이유를 바로 말하세요.
   - 나쁜 예: "주의가 필요합니다."
   - 좋은 예: "**간에 부담**을 줄 수 있어요. 특히 알코올과 함께 복용하면 **간 손상** 위험이 높아집니다."

3. **중요 내용 강조**: 핵심 키워드는 **별표**로 표시하세요. 예: **약물 상호작용**, **혈당 조절**, **복용 시간**

4. **사용자 맞춤 답변**: 제공된 복용 약물과 지병 정보를 반드시 고려하세요.

5. **자연스러운 존댓말**: 친근하게 "~해요", "~거든요" 같은 표현 사용.

6. 이모티콘 사용 금지.

7. 데이터 출처 언급 금지 ("제공된 데이터", "DUR 정보" 등 언급 안 됨).

8. 약 관련 질문만 답변. 다른 질문은 "약과 복약 관련 질문에만 답변할 수 있어요."

9. 진단/처방 질문은 "의료 전문가 상담을 권장드려요."

10. 추가 질문 유도: "더 궁금한 점 있으시면 물어보세요."

11. 결론에서 복용법 요약 제공: 결론은 "요약하자면," 다음에 ^^캐럿^^로 표시하세요. 예: "요약하자면, ^^...^^ 더 궁금한 점 있으시면 물어보세요."

"""

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
            max_tokens=300,  # 더 간결한 답변을 위해 제한
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


async def generate_chat_title(messages: List[dict], db: Session) -> str:
    """
    대화 내용을 바탕으로 제목 생성 (GPT-4o 사용)
    
    Args:
        messages: 대화 메시지 리스트 (최근 3개 정도)
        db: Database session
    
    Returns:
        str: 생성된 제목 (최대 30자)
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # 대화 내용 요약을 위한 프롬프트
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages[:3]  # 처음 3개 메시지만 사용
        ])
        
        prompt = f"""다음 약물 상담 대화의 제목을 30자 이내로 지어주세요.
        
대화 내용:
{conversation_text}

제목 규칙:
- 핵심 키워드만 간결하게
- "타이레놀 복용법", "게보린 주의사항" 같은 형식
- 존댓말 사용 안 함
- 30자 이내
- 이모티콘 사용 안 함

제목:"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        title = response.choices[0].message.content.strip()
        return title[:30]  # 최대 30자로 제한
        
    except Exception as e:
        print(f"제목 생성 오류: {e}")
        # 기본 제목 반환
        return f"약물 상담 {datetime.now().strftime('%m/%d %H:%M')}"


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
    
    # 새 세션인 경우 제목 자동 생성
    if not chat_data.session_id:
        # ChatSession 생성
        chat_session = ChatSession(
            user_id=MVP_USER_ID,
            session_id=session_id
        )
        db.add(chat_session)
        db.commit()
        
        # 제목 생성 (비동기로 첫 대화 기반)
        title = await generate_chat_title([
            {"role": "user", "content": chat_data.message},
            {"role": "assistant", "content": ai_response_text}
        ], db)
        
        chat_session.title = title
        db.commit()
    
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


@router.get("/sessions",
            summary="대화 세션 목록 조회"
)
async def get_chat_sessions(
    db: Session = Depends(get_db)
):
    """사용자의 모든 대화 세션 목록 조회 (제목 포함)"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == MVP_USER_ID
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return [
        {
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }
        for session in sessions
    ]

