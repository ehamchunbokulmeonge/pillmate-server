"""
MVP용 초기 데이터 생성 스크립트
사용자 ID 1로 테스트 데이터를 생성합니다.
"""

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.medicine import Medicine
from app.models.schedule import Schedule, TimeOfDay, FrequencyType

# 테이블 생성
Base.metadata.create_all(bind=engine)

def create_initial_data():
    db = SessionLocal()
    
    try:
        # MVP 사용자 생성 (ID = 1)
        existing_user = db.query(User).filter(User.id == 1).first()
        if not existing_user:
            mvp_user = User(
                id=1,
                email="mvp@pillmate.com",
                username="mvp_user",
                hashed_password="not_used_in_mvp",
                full_name="MVP 테스트 사용자",
                is_active=True
            )
            db.add(mvp_user)
            db.commit()
            print("✅ MVP 사용자 생성 완료")
        else:
            print("ℹ️  MVP 사용자가 이미 존재합니다")
        
        # 샘플 약 데이터 생성
        existing_medicines = db.query(Medicine).filter(Medicine.user_id == 1).count()
        if existing_medicines == 0:
            sample_medicines = [
                Medicine(
                    user_id=1,
                    name="타이레놀",
                    company="한국얀센",
                    description="해열·진통제",
                    efficacy="두통, 치통, 발열 등의 일시적 완화",
                    dosage="1회 1~2정, 1일 3~4회",
                    ingredients='["아세트아미노펜"]',
                    dosage_per_time=1,
                    dosage_unit="정"
                ),
                Medicine(
                    user_id=1,
                    name="게보린",
                    company="삼진제약",
                    description="복합 진통제",
                    efficacy="두통, 치통, 근육통 등의 통증 완화",
                    dosage="1회 1정, 1일 3회",
                    ingredients='["아세트아미노펜", "이소프로필안티피린", "무수카페인"]',
                    dosage_per_time=1,
                    dosage_unit="정"
                ),
                Medicine(
                    user_id=1,
                    name="비타민C",
                    company="종근당",
                    description="비타민 보충제",
                    efficacy="비타민C 보충",
                    dosage="1일 1회 1정",
                    ingredients='["아스코르브산"]',
                    dosage_per_time=1,
                    dosage_unit="정"
                )
            ]
            
            for med in sample_medicines:
                db.add(med)
            
            db.commit()
            print(f"✅ {len(sample_medicines)}개 샘플 약 데이터 생성 완료")
            
            # 샘플 스케줄 생성
            medicine_ids = [m.id for m in db.query(Medicine).filter(Medicine.user_id == 1).all()]
            
            if medicine_ids:
                sample_schedules = [
                    Schedule(
                        user_id=1,
                        medicine_id=medicine_ids[0],
                        time_of_day=TimeOfDay.MORNING,
                        frequency_type=FrequencyType.DAILY,
                        frequency_value=1,
                        start_date=datetime.now(),
                        end_date=datetime.now() + timedelta(days=30),
                        notification_enabled=True
                    ),
                    Schedule(
                        user_id=1,
                        medicine_id=medicine_ids[2],
                        time_of_day=TimeOfDay.AFTER_MEAL,
                        frequency_type=FrequencyType.DAILY,
                        frequency_value=3,
                        start_date=datetime.now(),
                        notification_enabled=True
                    )
                ]
                
                for schedule in sample_schedules:
                    db.add(schedule)
                
                db.commit()
                print(f"✅ {len(sample_schedules)}개 샘플 스케줄 생성 완료")
        else:
            print(f"ℹ️  이미 {existing_medicines}개의 약 데이터가 존재합니다")
        
        print("\n🎉 초기 데이터 생성 완료!")
        print("📌 MVP 모드로 실행됩니다 - 모든 데이터는 사용자 ID 1에 저장됩니다")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_data()
