"""테스트 데이터 삽입 스크립트"""
import json
from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.medicine import Medicine
from app.models.schedule import Schedule

def insert_test_data():
    db = SessionLocal()
    
    try:
        # 1. 타이레놀 추가
        tylenol_report = {
            "medications": [
                {
                    "name": "타이레놀정 500mg",
                    "ingredient": "아세트아미노펜",
                    "amount": "500mg",
                    "company": "한국얀센",
                    "efficacy": "해열, 진통"
                }
            ],
            "risk_level": "low",
            "risk_score": 25,
            "summary": "타이레놀은 일반적으로 안전한 해열진통제입니다. 권장 용량을 지켜 복용하세요.",
            "sections": [
                {
                    "icon": "checkmark-circle",
                    "title": "안전성",
                    "content": "일반적으로 안전한 약물입니다."
                },
                {
                    "icon": "warning",
                    "title": "주의사항",
                    "content": "간 질환이 있는 경우 의사와 상담하세요."
                }
            ],
            "interactions": [],
            "warnings": ["하루 최대 4000mg을 넘지 마세요", "음주 시 복용을 피하세요"],
            "recommendations": ["식후 30분에 복용하세요", "충분한 물과 함께 복용하세요"]
        }
        
        tylenol = Medicine(
            user_id=1,
            name="타이레놀정 500mg",
            ingredient="아세트아미노펜",
            amount="500mg",
            scan_report=json.dumps(tylenol_report, ensure_ascii=False)
        )
        db.add(tylenol)
        db.flush()
        
        # 타이레놀 스케줄 (아침 8시, 오늘부터 7일간)
        tylenol_schedule = Schedule(
            user_id=1,
            medicine_id=tylenol.id,
            medicine_name="타이레놀정 500mg",
            dose_count=2,
            dose_time=time(8, 0),
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        db.add(tylenol_schedule)
        
        # 2. 지르텍 추가
        zyrtec_report = {
            "medications": [
                {
                    "name": "지르텍정 10mg",
                    "ingredient": "세티리진",
                    "amount": "10mg",
                    "company": "UCB 파마",
                    "efficacy": "알레르기성 비염, 두드러기"
                }
            ],
            "risk_level": "low",
            "risk_score": 20,
            "summary": "지르텍은 항히스타민제로 알레르기 증상 완화에 사용됩니다.",
            "sections": [
                {
                    "icon": "checkmark-circle",
                    "title": "안전성",
                    "content": "졸음이 적은 2세대 항히스타민제입니다."
                },
                {
                    "icon": "information-circle",
                    "title": "복용법",
                    "content": "1일 1회, 잠들기 전 복용을 권장합니다."
                }
            ],
            "interactions": [],
            "warnings": ["운전 전 복용 주의"],
            "recommendations": ["잠들기 2시간 전 복용하세요"]
        }
        
        zyrtec = Medicine(
            user_id=1,
            name="지르텍정 10mg",
            ingredient="세티리진",
            amount="10mg",
            scan_report=json.dumps(zyrtec_report, ensure_ascii=False)
        )
        db.add(zyrtec)
        db.flush()
        
        # 지르텍 스케줄 (밤 10시, 오늘부터 14일간)
        zyrtec_schedule = Schedule(
            user_id=1,
            medicine_id=zyrtec.id,
            medicine_name="지르텍정 10mg",
            dose_count=1,
            dose_time=time(22, 0),
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14)
        )
        db.add(zyrtec_schedule)
        
        # 3. 오메가3 추가
        omega3_report = {
            "medications": [
                {
                    "name": "오메가3",
                    "ingredient": "EPA, DHA",
                    "amount": "1000mg",
                    "company": "건강식품",
                    "efficacy": "혈행 개선, 기억력 개선"
                }
            ],
            "risk_level": "low",
            "risk_score": 10,
            "summary": "오메가3는 건강기능식품으로 안전합니다.",
            "sections": [
                {
                    "icon": "nutrition",
                    "title": "영양정보",
                    "content": "EPA와 DHA가 함유된 건강기능식품입니다."
                }
            ],
            "interactions": [],
            "warnings": [],
            "recommendations": ["식후 복용 시 흡수율이 높습니다"]
        }
        
        omega3 = Medicine(
            user_id=1,
            name="오메가3",
            ingredient="EPA, DHA",
            amount="1000mg",
            scan_report=json.dumps(omega3_report, ensure_ascii=False)
        )
        db.add(omega3)
        db.flush()
        
        # 오메가3 스케줄 (아침/저녁, 오늘부터 30일간)
        omega3_schedule1 = Schedule(
            user_id=1,
            medicine_id=omega3.id,
            medicine_name="오메가3",
            dose_count=1,
            dose_time=time(8, 30),
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        omega3_schedule2 = Schedule(
            user_id=1,
            medicine_id=omega3.id,
            medicine_name="오메가3",
            dose_count=1,
            dose_time=time(20, 0),
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        db.add(omega3_schedule1)
        db.add(omega3_schedule2)
        
        db.commit()
        
        print("✅ 테스트 데이터 삽입 완료!")
        print(f"- 타이레놀정 500mg (아침 8시, 7일간)")
        print(f"- 지르텍정 10mg (밤 10시, 14일간)")
        print(f"- 오메가3 (아침 8:30, 저녁 8시, 30일간)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 에러 발생: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
