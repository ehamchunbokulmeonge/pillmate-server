from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import base64
from datetime import datetime
from app.database import get_db
from app.models.medicine import Medicine
from app.models.analysis import AnalysisResult, RiskLevel
from app.models.schedule import Schedule
from app.schemas.analysis import (
    AnalysisRequest, 
    AnalysisResponse, 
    ScanAnalysisRequest, 
    MedicationAnalysisResponse,
    ScannedMedication,
    RiskItem,
    CommentSection
)
from app.config import get_settings
from app.services.rag_service import search_all_safety_info

router = APIRouter()
settings = get_settings()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


# 기존 엔드포인트들은 /api/v1/analysis/scan으로 통합됨


async def analyze_with_ai(scanned_med: dict, user_medicines: List[dict], medical_conditions: List[str] = None) -> dict:
    """
    OpenAI를 사용한 약물 상호작용 분석 (RAG 통합)
    
    Args:
        scanned_med: 촬영한 약물 정보 (name, ingredient, amount)
        user_medicines: 사용자의 현재 복용 중인 약물 목록
        medical_conditions: 사용자의 지병 목록
    
    Returns:
        dict: 분석 결과 (overallRiskScore, riskLevel, riskItems, warnings)
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # RAG: 스캔한 약과 복용 중인 약들의 DUR 안전 정보 검색
        all_drug_names = [scanned_med['ingredient']]
        for med in user_medicines:
            if 'ingredient' in med:
                all_drug_names.append(med['ingredient'])
        
        try:
            rag_safety_info = search_all_safety_info(all_drug_names)
            
            # RAG 컨텍스트 생성
            rag_context = "\n\n**참고할 의약품 안전 정보 (DUR 데이터):**\n"
            
            # 병용금기
            if rag_safety_info['contraindications']:
                rag_context += "\n[병용금기 정보]\n"
                for i, item in enumerate(rag_safety_info['contraindications'][:3], 1):
                    rag_context += f"{i}. {item['drug_a']} + {item['drug_b']}: {item['detail']}\n"
            
            # 연령금기
            if rag_safety_info['age_restrictions']:
                rag_context += "\n[연령금기 정보]\n"
                for i, item in enumerate(rag_safety_info['age_restrictions'][:2], 1):
                    rag_context += f"{i}. {item['drug']}: {item['detail']}\n"
            
            # 임부금기
            if rag_safety_info['pregnancy_restrictions']:
                rag_context += "\n[임부금기 정보]\n"
                for i, item in enumerate(rag_safety_info['pregnancy_restrictions'][:2], 1):
                    rag_context += f"{i}. {item['drug']}: {item['detail']}\n"
            
            # 노인주의
            if rag_safety_info['elderly_cautions']:
                rag_context += "\n[노인주의 정보]\n"
                for i, item in enumerate(rag_safety_info['elderly_cautions'][:2], 1):
                    rag_context += f"{i}. {item['drug']}: {item['detail']}\n"
        
        except Exception as e:
            print(f"RAG 검색 오류 (무시하고 계속): {e}")
            rag_context = ""
        
        # 지병 정보 추가
        medical_conditions_text = ""
        if medical_conditions:
            medical_conditions_text = f"\n\n**중요: 사용자의 지병**\n사용자는 다음 질환을 앓고 있습니다: {', '.join(medical_conditions)}\n이 지병들을 고려하여 약물의 적합성과 위험성을 평가하세요."
        
        # AI 분석을 위한 프롬프트
        system_prompt = f"""당신은 약물 상호작용 분석 전문가입니다.
촬영한 약물과 사용자가 현재 복용 중인 약물들을 비교하여 위험성을 분석하세요.{medical_conditions_text}

**중요**: 위에 제공된 "참고할 의약품 안전 정보 (DUR 데이터)"를 우선적으로 참고하여 정확한 분석을 수행하세요.

다음 3가지 위험 유형을 확인하세요:
1. duplicate: 성분 중복 (같은 성분이 여러 약에 포함)
2. interaction: 약물 상호작용 (특정 약 조합 시 부작용 발생 가능)
3. timing: 복용 시간 충돌 (같은 시간에 복용하면 안 되는 약)

분석 결과는 다음 JSON 형식으로 반환하세요:
{{"overallRiskScore": 0-10 사이 정수 (0=안전, 10=매우 위험),
  "riskLevel": "low" | "medium" | "high",
  "riskItems": [
    {{"id": "고유ID (예: duplicate-1, interaction-1)",
      "type": "duplicate | interaction | timing",
      "severity": "low | medium | high",
      "title": "위험 항목 제목",
      "description": "상세 설명 (DUR 데이터 기반)",
      "percentage": 0-100 사이 정수
    }}
  ],
  "warnings": ["경고 메시지 배열"],
  "summary": "분석 결과 요약 (강조할 부분은 **텍스트** 형식으로)",
  "sections": [
    {{"icon": "Ionicons 아이콘 이름 (time, alert-circle, swap-horizontal, flask, fitness, restaurant, water, moon 등)",
      "title": "섹션 제목",
      "content": "섹션 본문 (강조: **텍스트**, 줄바꿈: \\n으로 구분, 목록 형식 권장)"
    }}
  ]
}}

**중요 규칙:**
- sections 배열은 최소 1개 이상 (권장: 복용 방법, 주의사항, 대체 방안 등)
- summary와 sections[].content에서 강조할 부분은 **텍스트** 형식 사용
- 모든 텍스트는 한글로 제공
- icon은 유효한 Ionicons 이름 사용 (time, alert-circle, swap-horizontal, flask, fitness, restaurant, water, moon)
- content는 줄바꿈(\\n)과 목록 형식(• 또는 숫자)으로 작성
- DUR 데이터를 참고하여 더 정확하고 전문적인 분석 제공

반드시 위 JSON 형식만 출력하고, 다른 텍스트는 포함하지 마세요."""

        user_message = f"""촬영한 약물:
- 이름: {scanned_med['name']}
- 성분: {scanned_med['ingredient']}
- 함량: {scanned_med['amount']}

현재 복용 중인 약물:
{json.dumps(user_medicines, ensure_ascii=False, indent=2)}
{rag_context if rag_context else ""}

위험성을 분석해주세요."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,  # 낮은 온도로 일관된 분석
            max_tokens=1500,  # summary와 sections 추가로 토큰 증가
            response_format={"type": "json_object"}  # JSON 모드
        )
        
        # JSON 파싱
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        # 오류 시 기본 안전 응답
        return {
            "overallRiskScore": 0,
            "riskLevel": "low",
            "riskItems": [],
            "warnings": ["AI 분석 중 오류가 발생했습니다. 약사와 상담을 권장합니다."],
            "summary": "분석을 완료할 수 없습니다. 약사와 상담하시기 바랍니다.",
            "sections": [
                {
                    "icon": "alert-circle",
                    "title": "안내",
                    "content": "일시적인 오류로 정확한 분석이 어렵습니다.\n약사 또는 의사와 상담하시기 바랍니다."
                }
            ]
        }


@router.post(
    "/scan",
    response_model=MedicationAnalysisResponse,
    summary="약 사진 스캔 및 위험성 분석"
)
async def analyze_scanned_medication(
    request: ScanAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    약 사진을 OCR로 인식하고 사용자의 현재 복용 약과 비교 분석
    
    1. 이미지에서 OCR로 약물명 추출
    2. 데이터베이스에서 약물 정보 매칭
    3. 사용자의 현재 복용 중인 약물 조회
    4. AI로 성분 중복, 약물 상호작용, 복용 시간 충돌 분석
    5. 위험도 점수 및 경고 메시지 반환
    """
    
    # 1. OCR 처리 - OCR 라우터의 함수 재사용
    from app.routes.ocr import extract_text_from_image, search_medicine_in_aihub_data
    from app.utils.aihub_loader import get_aihub_loader
    
    try:
        # OCR로 텍스트 추출
        extracted_text = extract_text_from_image(request.image_base64)
        
        if not extracted_text or len(extracted_text.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="약물 텍스트를 인식할 수 없습니다. 더 선명한 사진으로 다시 시도해주세요."
            )
        
        # AI Hub 데이터셋에서 약 검색
        matched_medicines = search_medicine_in_aihub_data(extracted_text)
        
        if not matched_medicines:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="매칭되는 약물을 찾을 수 없습니다."
            )
        
        # 가장 높은 매칭 점수의 약물 선택 (MedicineMatch 객체)
        best_match = matched_medicines[0]
        med_name = best_match.drug_name  # 객체 속성으로 접근
        
        # 2. AI Hub 데이터셋에서 약물 상세 정보 조회
        loader = get_aihub_loader()
        
        scanned_medicine_data = next(
            (m for m in loader.medicine_data if m.get("dl_name") == med_name),
            None
        )
        
        if not scanned_medicine_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="약물 상세 정보를 찾을 수 없습니다."
            )
        
        # 3. 사용자 정보 및 지병 조회
        from app.models.user import User
        user = db.query(User).filter(User.id == request.user_id).first()
        user_medical_conditions = user.medical_conditions if user and user.medical_conditions else []
        
        # 4. 사용자의 현재 복용 약물 조회
        user_medicines = db.query(Medicine).filter(
            Medicine.user_id == request.user_id
        ).all()
        
        # 약물 스케줄도 조회하여 복용 시간 정보 포함
        user_med_with_schedule = []
        for med in user_medicines:
            schedules = db.query(Schedule).filter(
                Schedule.medicine_id == med.id
            ).all()
            
            user_med_with_schedule.append({
                "id": med.id,
                "name": med.name,
                "ingredient": med.ingredient or "정보 없음",
                "amount": med.amount or "정보 없음",
                "schedules": [
                    {
                        "time": s.dose_time.strftime("%H:%M") if s.dose_time else None,
                        "dose_count": s.dose_count
                    }
                    for s in schedules
                ]
            })
        
        # 4. 촬영한 약물 정보 구성
        scanned_med = {
            "name": scanned_medicine_data.get("dl_name", ""),
            "ingredient": scanned_medicine_data.get("dl_material", "정보 없음"),
            "amount": scanned_medicine_data.get("dl_name", "").split()[-1] if scanned_medicine_data.get("dl_name") else "정보 없음"
        }
        
        # 5. AI 분석 수행 (지병 정보 포함)
        ai_result = await analyze_with_ai(scanned_med, user_med_with_schedule, user_medical_conditions)
        
        # 6. 응답 구성
        return MedicationAnalysisResponse(
            scannedMedication=ScannedMedication(
                name=scanned_med["name"],
                ingredient=scanned_med["ingredient"],
                amount=scanned_med["amount"]
            ),
            overallRiskScore=ai_result.get("overallRiskScore", 0),
            riskLevel=ai_result.get("riskLevel", "low"),
            riskItems=[
                RiskItem(
                    id=item["id"],
                    type=item["type"],
                    severity=item["severity"],
                    title=item["title"],
                    description=item["description"],
                    percentage=item["percentage"]
                )
                for item in ai_result.get("riskItems", [])
            ],
            warnings=ai_result.get("warnings", []),
            summary=ai_result.get("summary", "분석이 완료되었습니다."),
            sections=[
                CommentSection(
                    icon=section["icon"],
                    title=section["title"],
                    content=section["content"]
                )
                for section in ai_result.get("sections", [])
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Scan Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"약물 분석 중 오류가 발생했습니다: {str(e)}"
        )
