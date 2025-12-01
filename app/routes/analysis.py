from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
from app.database import get_db
from app.models.medicine import Medicine
from app.models.analysis import AnalysisResult, RiskLevel
from app.schemas.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter()

# MVP: 고정 사용자 ID (인증 없음)
MVP_USER_ID = 1


def analyze_duplicate_ingredients(medicines: List[Medicine]) -> dict:
    """중복 성분 분석"""
    ingredient_map = {}
    
    for medicine in medicines:
        if medicine.ingredients:
            # ingredients가 JSON 문자열이라고 가정
            try:
                ingredients = json.loads(medicine.ingredients)
                if isinstance(ingredients, list):
                    for ingredient in ingredients:
                        if ingredient not in ingredient_map:
                            ingredient_map[ingredient] = []
                        ingredient_map[ingredient].append(medicine.id)
            except:
                # JSON 파싱 실패 시 텍스트로 처리
                if medicine.ingredients not in ingredient_map:
                    ingredient_map[medicine.ingredients] = []
                ingredient_map[medicine.ingredients].append(medicine.id)
    
    # 중복된 성분만 필터링
    duplicates = [
        {
            "ingredient": ingredient,
            "count": len(medicine_ids),
            "medicine_ids": medicine_ids
        }
        for ingredient, medicine_ids in ingredient_map.items()
        if len(medicine_ids) > 1
    ]
    
    return duplicates


def calculate_risk_level(duplicates: list, interactions: list) -> RiskLevel:
    """위험도 계산"""
    if not duplicates and not interactions:
        return RiskLevel.SAFE
    
    if len(duplicates) >= 3 or len(interactions) >= 2:
        return RiskLevel.HIGH
    elif len(duplicates) >= 2 or len(interactions) >= 1:
        return RiskLevel.MEDIUM
    elif len(duplicates) >= 1:
        return RiskLevel.LOW
    
    return RiskLevel.SAFE


@router.post(
    "/detect-duplicate",
    response_model=AnalysisResponse,
    summary="중복 성분 및 위험도 분석"
)
async def detect_duplicate(
    analysis_data: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """중복 성분 감지 및 위험도 분석"""
    
    # 약 목록 조회
    medicines = db.query(Medicine).filter(
        Medicine.id.in_(analysis_data.medicine_ids),
        Medicine.user_id == MVP_USER_ID
    ).all()
    
    if len(medicines) != len(analysis_data.medicine_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some medicines not found"
        )
    
    # 중복 성분 분석
    duplicates = analyze_duplicate_ingredients(medicines)
    
    # TODO: 실제 상호작용 분석 로직 추가 (외부 API 또는 DB)
    interactions = []
    
    # 위험도 계산
    risk_level = calculate_risk_level(duplicates, interactions)
    
    # 경고 및 권장사항 생성
    warnings = []
    recommendations = []
    
    if duplicates:
        warnings.append("중복된 성분이 발견되었습니다. 과다 복용에 주의하세요.")
        recommendations.append("의사 또는 약사와 상담하시기 바랍니다.")
    
    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        warnings.append("높은 위험도가 감지되었습니다.")
        recommendations.append("즉시 전문가와 상담하세요.")
    
    # 분석 결과 저장
    analysis_result = AnalysisResult(
        user_id=MVP_USER_ID,
        medicine_ids=json.dumps(analysis_data.medicine_ids),
        risk_level=risk_level,
        duplicate_ingredients=json.dumps(duplicates),
        interactions=json.dumps(interactions),
        warnings=json.dumps(warnings),
        recommendations=json.dumps(recommendations)
    )
    
    db.add(analysis_result)
    db.commit()
    db.refresh(analysis_result)
    
    return AnalysisResponse(
        risk_level=risk_level,
        duplicate_ingredients=duplicates,
        interactions=interactions,
        warnings=warnings,
        recommendations=recommendations,
        created_at=datetime.now()
    )


@router.get("/history")
async def get_analysis_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """분석 이력 조회 (MVP)"""
    results = db.query(AnalysisResult).filter(
        AnalysisResult.user_id == MVP_USER_ID
    ).order_by(AnalysisResult.created_at.desc()).offset(skip).limit(limit).all()
    
    return results
