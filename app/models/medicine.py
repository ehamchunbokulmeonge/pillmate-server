from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 약 기본 정보
    name = Column(String(255), nullable=False)
    product_code = Column(String(100))  # 품목기준코드
    company = Column(String(255))  # 제조사
    
    # 약 설명
    description = Column(Text)
    efficacy = Column(Text)  # 효능효과
    dosage = Column(Text)  # 용법용량
    
    # 성분 정보
    ingredients = Column(Text)  # JSON 형태로 저장
    
    # 경고 및 주의사항
    warnings = Column(Text)
    side_effects = Column(Text)
    
    # 이미지
    image_url = Column(String(500))
    
    # 복용 정보
    dosage_per_time = Column(Float)  # 1회 복용량
    dosage_unit = Column(String(50))  # 단위 (정, ml, g 등)
    
    # 메타 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="medicines")
    schedules = relationship("Schedule", back_populates="medicine", cascade="all, delete-orphan")
