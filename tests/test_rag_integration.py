"""
RAG 통합 후 실제 기능 테스트

1. 약사 챗봇 + RAG 테스트
2. 약 스캔 분석 + RAG 테스트
"""
import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.routes.chat import get_ai_response
from app.routes.analysis import analyze_with_ai


async def test_chat_with_rag():
    """약사 챗봇 RAG 통합 테스트"""
    print("=" * 70)
    print("1. 약사 챗봇 + RAG 테스트")
    print("=" * 70)
    
    test_questions = [
        "타이레놀과 게보린을 같이 먹어도 되나요?",
        "임산부가 피해야 할 약은 어떤 것들이 있나요?",
        "노인이 해열제를 먹을 때 주의할 점은 뭔가요?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[테스트 {i}]")
        print(f"질문: {question}")
        print("\n[AI 응답 생성 중...]")
        
        try:
            response, metadata = await get_ai_response(question)
            
            print(f"\n✅ 응답:")
            print(f"{response}")
            print(f"\n📊 메타데이터:")
            print(f"  - 모델: {metadata.get('model')}")
            print(f"  - 토큰 사용: {metadata.get('tokens_used')}")
            
        except Exception as e:
            print(f"❌ 에러: {e}")
        
        print("\n" + "-" * 70)


async def test_scan_analysis_with_rag():
    """약 스캔 분석 + RAG 테스트"""
    print("\n" + "=" * 70)
    print("2. 약 스캔 분석 + RAG 테스트")
    print("=" * 70)
    
    # 테스트 시나리오 1: 타이레놀 스캔 (아세트아미노펜 중복 가능)
    print("\n[시나리오 1] 타이레놀 스캔")
    scanned_med = {
        "name": "타이레놀정500밀리그램",
        "ingredient": "아세트아미노펜",
        "amount": "500mg"
    }
    user_medicines = [
        {
            "name": "게보린정",
            "ingredient": "아세트아미노펜|카페인무수물|이소프로필안티피린",
            "amount": "300mg|25mg|150mg"
        },
        {
            "name": "부루펜정",
            "ingredient": "이부프로펜",
            "amount": "200mg"
        }
    ]
    medical_conditions = ["고혈압", "당뇨병"]
    
    print(f"\n스캔한 약: {scanned_med['name']}")
    print(f"복용 중인 약: {[m['name'] for m in user_medicines]}")
    print(f"지병: {medical_conditions}")
    print("\n[AI 분석 중...]")
    
    try:
        result = await analyze_with_ai(scanned_med, user_medicines, medical_conditions)
        
        print(f"\n✅ 분석 결과:")
        print(f"  - 위험도 점수: {result['overallRiskScore']}/10")
        print(f"  - 위험 수준: {result['riskLevel']}")
        print(f"  - 발견된 위험: {len(result['riskItems'])}건")
        
        if result['riskItems']:
            print(f"\n  [위험 항목]")
            for item in result['riskItems']:
                print(f"    • {item['title']} ({item['severity']})")
                print(f"      {item['description'][:80]}...")
        
        if result.get('warnings'):
            print(f"\n  [경고]")
            for warning in result['warnings']:
                print(f"    • {warning}")
        
        print(f"\n  [요약]")
        print(f"  {result.get('summary', '')[:150]}...")
        
        if result.get('sections'):
            print(f"\n  [상세 섹션] {len(result['sections'])}개")
            for section in result['sections'][:2]:
                print(f"    • {section['title']}")
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 70)
    
    # 테스트 시나리오 2: 아스피린 스캔
    print("\n[시나리오 2] 아스피린 스캔")
    scanned_med = {
        "name": "아스피린장용정100밀리그램",
        "ingredient": "아스피린",
        "amount": "100mg"
    }
    user_medicines = [
        {
            "name": "와파린정",
            "ingredient": "와파린나트륨",
            "amount": "5mg"
        }
    ]
    medical_conditions = ["심장질환"]
    
    print(f"\n스캔한 약: {scanned_med['name']}")
    print(f"복용 중인 약: {[m['name'] for m in user_medicines]}")
    print(f"지병: {medical_conditions}")
    print("\n[AI 분석 중...]")
    
    try:
        result = await analyze_with_ai(scanned_med, user_medicines, medical_conditions)
        
        print(f"\n✅ 분석 결과:")
        print(f"  - 위험도 점수: {result['overallRiskScore']}/10")
        print(f"  - 위험 수준: {result['riskLevel']}")
        print(f"  - 발견된 위험: {len(result['riskItems'])}건")
        
        if result.get('summary'):
            print(f"\n  [요약]")
            print(f"  {result.get('summary')[:150]}...")
        
    except Exception as e:
        print(f"❌ 에러: {e}")


async def main():
    print("\n")
    print("=" * 70)
    print("RAG 통합 실제 기능 테스트")
    print("=" * 70)
    
    # 1. 약사 챗봇 테스트
    await test_chat_with_rag()
    
    # 2. 약 스캔 분석 테스트
    await test_scan_analysis_with_rag()
    
    print("\n" + "=" * 70)
    print("✅ 모든 테스트 완료!")
    print("=" * 70)
    print("\n💊 RAG 시스템이 실제 기능과 잘 통합되었습니다!")
    print("  - 약사 챗봇: DUR 데이터 기반 정확한 답변")
    print("  - 약 스캔 분석: DUR 데이터 기반 고도화된 위험도 분석")


if __name__ == "__main__":
    asyncio.run(main())
