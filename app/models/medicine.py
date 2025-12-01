from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 약 기본 정보 (스캔 보고서에서 가져옴)
    name = Column(String(255), nullable=False)  # 약물명
    ingredient = Column(String(255))  # 주성분명
    amount = Column(String(100))  # 함량 (예: 500mg)
    
    # 스캔 분석 보고서 (JSON 형태로 저장)
    scan_report = Column(Text)  # MedicationAnalysisResponse 전체 JSON
    
    # 메타 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="medicines")
    schedules = relationship("Schedule", back_populates="medicine", cascade="all, delete-orphan")
