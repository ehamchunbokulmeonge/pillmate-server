from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class RiskLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 분석 대상 약물들 (JSON 형태)
    medicine_ids = Column(Text)  # [1, 2, 3] 형태로 저장
    
    # 분석 결과
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    duplicate_ingredients = Column(Text)  # JSON 형태로 중복 성분 저장
    interactions = Column(Text)  # JSON 형태로 상호작용 정보 저장
    
    # 추가 정보
    warnings = Column(Text)
    recommendations = Column(Text)
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
