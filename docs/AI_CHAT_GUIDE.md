# 🤖 AI 약사 필메이트 - 사용 가이드

## 개요

필메이트는 약과 복약에 관한 질문에 답변하는 AI 약사 챗봇입니다.

### 주요 특징
- ✅ 항상 존댓말 사용
- ✅ 이모티콘 없는 전문적인 답변
- ✅ 약물 관련 질문에만 응답
- ✅ 의학적 진단 필요 시 전문가 상담 권유
- ✅ 대화 이력 기반 맥락 이해

## 설정

### 1. OpenAI API 키 설정

`.env` 파일에 API 키를 설정하세요:

```bash
OPENAI_API_KEY=your-api-key-here
```

이미 설정되어 있습니다! ✅

### 2. 필요한 패키지 확인

```bash
pip install openai
```

## API 사용법

### 기본 사용

#### POST /api/v1/chat

**요청:**
```json
{
  "message": "두통이 있는데 어떤 약을 먹어야 하나요?",
  "session_id": null
}
```

**응답:**
```json
{
  "message": "두통의 경우 아세트아미노펜 성분의 진통제를 고려해 보실 수 있습니다...",
  "session_id": "uuid-generated",
  "created_at": "2025-12-01T10:00:00",
  "tokens_used": 245,
  "model": "gpt-4o-mini"
}
```

### 대화 이력 유지

같은 `session_id`를 사용하면 이전 대화 맥락을 기억합니다:

```json
{
  "message": "하루에 몇 번 먹어야 하나요?",
  "session_id": "previous-session-id"
}
```

## 테스트 스크립트

### 1. 대화형 테스트

```bash
python test_chat.py
```

실행 후:
```
🏥 AI 약사 필메이트 챗봇 테스트
============================================================
종료하려면 'exit' 또는 'quit'를 입력하세요.

👤 질문: 두통이 있어요
💬 필메이트가 답변 중...

🤖 필메이트: 두통이 있으시군요. 일반적으로 아세트아미노펜...
```

### 2. 단일 질문 테스트

```bash
python test_chat.py "타이레놀과 게보린을 같이 먹어도 되나요?"
```

### 3. 시나리오 테스트

다양한 케이스를 자동으로 테스트:

```bash
python test_scenarios.py
```

테스트 항목:
- ✅ 이름 확인
- ✅ 약 복용 상담
- ✅ 의학적 진단 (전문가 권유)
- ✅ 약 외 질문 (거부)
- ✅ 불명확한 질문 (재질문)
- ✅ 대화 흐름 테스트

## 필메이트 응답 규칙

### ✅ 정상 응답 케이스

#### 1. 이름 질문
**질문:** "이름이 뭐야?"
**응답:** "저는 AI 약사 필메이트입니다."

#### 2. 약 복용 상담
**질문:** "두통이 있는데 어떤 약을 먹어야 하나요?"
**응답:** 적절한 약물 정보와 복용 방법 안내

#### 3. 약물 상호작용
**질문:** "타이레놀과 게보린을 같이 먹어도 되나요?"
**응답:** 성분 중복 여부와 주의사항 안내

### ⚠️ 특수 케이스 응답

#### 1. 의학적 진단 필요
**질문:** "배가 계속 아픈데 무슨 병인가요?"
**응답:** "정확한 진단이 필요할 수 있으니 의료 전문가에게 상담을 권장드립니다."

#### 2. 약 외 질문
**질문:** "날씨가 어때?"
**응답:** "죄송하지만, 저는 약과 복약 관련 질문에만 답변할 수 있습니다."

#### 3. 부적절한 표현
**질문:** (욕설 포함)
**응답:** "부적절한 표현은 사용하지 말아주세요."

#### 4. 불명확한 질문
**질문:** "약"
**응답:** "구체적으로 어떤 부분이 궁금하신지 말씀해 주시겠어요?"

## API 엔드포인트

### 1. 새 대화 시작
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "두통약 추천해주세요"
  }'
```

### 2. 대화 이어가기
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "하루에 몇 번 먹어야 하나요?",
    "session_id": "받은-세션-아이디"
  }'
```

### 3. 대화 이력 조회
```bash
curl "http://localhost:8000/api/v1/chat/history?session_id=세션아이디"
```

### 4. 대화 이력 삭제
```bash
curl -X DELETE "http://localhost:8000/api/v1/chat/history/세션아이디"
```

## 모델 설정

### 현재 설정
- **모델:** gpt-4o-mini
- **Temperature:** 0.7 (창의성과 일관성 균형)
- **Max Tokens:** 500 (적절한 답변 길이)
- **Frequency Penalty:** 0.3 (반복 감소)
- **Presence Penalty:** 0.3 (다양성 증가)

### 모델 변경

더 고급 응답이 필요한 경우 `app/routes/chat.py`에서 변경:

```python
response = client.chat.completions.create(
    model="gpt-4o",  # 또는 "gpt-4-turbo"
    messages=messages,
    temperature=0.7,
    max_tokens=800,  # 더 긴 답변
    ...
)
```

## 대화 이력 관리

### 이력 저장
모든 대화는 `chat_histories` 테이블에 자동 저장됩니다:
- user_id
- role (user/assistant)
- content
- session_id
- created_at

### 이력 사용
- 최근 10개 메시지만 컨텍스트로 사용
- 토큰 사용량 최적화
- 대화 맥락 유지

## 비용 관리

### 토큰 사용량 확인

응답에 포함된 메타데이터 확인:
```json
{
  "tokens_used": 245,
  "model": "gpt-4o-mini"
}
```

### 예상 비용 (gpt-4o-mini)
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- 평균 대화 1회: ~300 tokens = $0.0001 미만

### 비용 절감 팁
1. `max_tokens` 제한 사용
2. 대화 이력을 최근 10개로 제한
3. gpt-4o-mini 사용 (gpt-4 대비 저렴)

## 문제 해결

### OpenAI API 오류

**증상:** "일시적인 오류가 발생했습니다"

**해결:**
1. API 키 확인
```bash
echo $OPENAI_API_KEY
```

2. 요금 한도 확인
https://platform.openai.com/account/billing/overview

3. API 상태 확인
https://status.openai.com/

### Import 오류

**증상:** `Import "openai" could not be resolved`

**해결:**
```bash
pip install openai --upgrade
```

### 응답 품질 개선

**방법:**
1. Temperature 조정 (0.5-0.9)
2. 시스템 프롬프트 개선
3. Few-shot 예시 추가

## 고급 기능

### 1. 사용자별 약물 정보 활용

```python
# 사용자의 등록된 약물 정보를 컨텍스트에 추가
user_medicines = db.query(Medicine).filter(
    Medicine.user_id == MVP_USER_ID
).all()

medicine_info = "\n".join([
    f"- {med.name}: {med.ingredients}"
    for med in user_medicines
])

system_prompt += f"\n\n사용자가 복용 중인 약물:\n{medicine_info}"
```

### 2. 스트리밍 응답

실시간으로 답변 표시:
```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 3. 함수 호출

약물 검색 등의 기능 통합:
```python
functions = [
    {
        "name": "search_medicine",
        "description": "약물 정보 검색",
        "parameters": {
            "type": "object",
            "properties": {
                "medicine_name": {"type": "string"}
            }
        }
    }
]
```

## 모범 사례

### 1. 적절한 질문 예시
✅ "타이레놀은 하루에 몇 번 먹어야 하나요?"
✅ "아스피린과 타이레놀을 같이 먹어도 되나요?"
✅ "임신 중에 두통약을 먹어도 안전한가요?"

### 2. 부적절한 질문 예시
❌ "코딩 도와줘"
❌ "날씨 알려줘"
❌ "저녁 메뉴 추천"

## 다음 단계

1. ✅ OpenAI API 연동 완료
2. ✅ 필메이트 규칙 적용 완료
3. ⬜ 실제 약물 데이터베이스 연동
4. ⬜ 약물 상호작용 체크 기능
5. ⬜ 음성 인식/합성 추가

---

**문의:** GitHub Issues
**문서:** README.md, DEVELOPMENT.md
