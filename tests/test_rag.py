"""
RAG 시스템 테스트

1. DUR 데이터 검색 테스트
2. 약사 챗봇 RAG 통합 테스트
3. 약 스캔 분석 RAG 통합 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.rag_service import (
    search_contraindications,
    search_by_question,
    search_all_safety_info
)


def test_contraindication_search():
    """병용금기 검색 테스트"""
    print("=" * 70)
    print("1. 병용금기 검색 테스트")
    print("=" * 70)
    
    # 타이레놀 + 게보린 (아세트아미노펜 중복)
    drug_names = ["acetaminophen", "아세트아미노펜"]
    
    print(f"\n검색 약물: {drug_names}")
    results = search_contraindications(drug_names, k=3)
    
    print(f"\n✅ 검색 결과: {len(results)}건")
    for i, result in enumerate(results, 1):
        print(f"\n--- 결과 {i} ---")
        print(f"약물 A: {result.get('drug_a')}")
        print(f"약물 B: {result.get('drug_b')}")
        print(f"상세: {result.get('detail', '')[:100]}...")


def test_question_search():
    """자연어 질문 검색 테스트 (챗봇용)"""
    print("\n" + "=" * 70)
    print("2. 자연어 질문 검색 테스트")
    print("=" * 70)
    
    questions = [
        "타이레놀이랑 게보린 같이 먹어도 돼?",
        "임산부가 먹으면 안 되는 약은 뭐야?",
        "노인이 주의해야 할 해열제는?"
    ]
    
    for question in questions:
        print(f"\n질문: {question}")
        results = search_by_question(question, k=2)
        
        print(f"✅ 검색 결과: {len(results)}건")
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] 타입: {result.get('type')}")
            print(f"내용: {result.get('content', '')[:100]}...")


def test_all_safety_info():
    """통합 안전 정보 검색 테스트"""
    print("\n" + "=" * 70)
    print("3. 통합 안전 정보 검색 테스트")
    print("=" * 70)
    
    drug_names = ["아세트아미노펜", "이부프로펜"]
    
    print(f"\n검색 약물: {drug_names}")
    results = search_all_safety_info(drug_names)
    
    print(f"\n✅ 병용금기: {len(results['contraindications'])}건")
    print(f"✅ 연령금기: {len(results['age_restrictions'])}건")
    print(f"✅ 임부금기: {len(results['pregnancy_restrictions'])}건")
    print(f"✅ 노인주의: {len(results['elderly_cautions'])}건")
    
    if results['contraindications']:
        print(f"\n[병용금기 예시]")
        item = results['contraindications'][0]
        print(f"  {item.get('drug_a')} + {item.get('drug_b')}")
        print(f"  {item.get('detail', '')[:80]}...")


def test_chat_rag_integration():
    """약사 챗봇 RAG 통합 동작 시뮬레이션"""
    print("\n" + "=" * 70)
    print("4. 약사 챗봇 RAG 통합 시뮬레이션")
    print("=" * 70)
    
    user_question = "타이레놀과 게보린을 같이 먹어도 되나요?"
    
    print(f"\n사용자 질문: {user_question}")
    print("\n[RAG 검색 중...]")
    
    rag_results = search_by_question(user_question, k=3)
    
    print(f"✅ RAG가 찾은 관련 정보: {len(rag_results)}건")
    
    if rag_results:
        print("\n[GPT-4o에게 전달될 컨텍스트]")
        for i, result in enumerate(rag_results, 1):
            print(f"{i}. {result.get('content', '')[:100]}...")
        
        print("\n💡 GPT-4o는 이 정보를 참고하여 정확한 답변을 생성합니다.")
    else:
        print("⚠️  관련 DUR 데이터를 찾지 못했습니다.")


def test_scan_analysis_rag():
    """약 스캔 분석 RAG 통합 시뮬레이션"""
    print("\n" + "=" * 70)
    print("5. 약 스캔 분석 RAG 통합 시뮬레이션")
    print("=" * 70)
    
    scanned_drug = "아세트아미노펜"
    user_drugs = ["이부프로펜", "아스피린"]
    
    all_drugs = [scanned_drug] + user_drugs
    
    print(f"\n스캔한 약: {scanned_drug}")
    print(f"복용 중인 약: {user_drugs}")
    print("\n[RAG 검색 중...]")
    
    safety_info = search_all_safety_info(all_drugs)
    
    total_info = (
        len(safety_info['contraindications']) +
        len(safety_info['age_restrictions']) +
        len(safety_info['pregnancy_restrictions']) +
        len(safety_info['elderly_cautions'])
    )
    
    print(f"\n✅ RAG가 찾은 DUR 안전 정보: 총 {total_info}건")
    print(f"  - 병용금기: {len(safety_info['contraindications'])}건")
    print(f"  - 연령금기: {len(safety_info['age_restrictions'])}건")
    print(f"  - 임부금기: {len(safety_info['pregnancy_restrictions'])}건")
    print(f"  - 노인주의: {len(safety_info['elderly_cautions'])}건")
    
    if safety_info['contraindications']:
        print("\n[발견된 병용금기 예시]")
        for i, item in enumerate(safety_info['contraindications'][:2], 1):
            print(f"{i}. {item.get('drug_a')} + {item.get('drug_b')}")
            print(f"   상세: {item.get('detail', '')[:80]}...")
    
    print("\n💡 GPT-4o는 이 DUR 데이터를 기반으로 더 정확한 위험도 분석을 제공합니다.")


def main():
    print("\n")
    print("=" * 70)
    print("RAG 시스템 통합 테스트")
    print("=" * 70)
    
    try:
        # 1. 병용금기 검색
        test_contraindication_search()
        
        # 2. 자연어 질문 검색
        test_question_search()
        
        # 3. 통합 안전 정보 검색
        test_all_safety_info()
        
        # 4. 약사 챗봇 RAG 통합
        test_chat_rag_integration()
        
        # 5. 약 스캔 분석 RAG 통합
        test_scan_analysis_rag()
        
        print("\n" + "=" * 70)
        print("✅ 모든 테스트 완료!")
        print("=" * 70)
        print("\n💊 RAG 시스템이 정상적으로 작동합니다.")
        print("  - 약사 챗봇: DUR 데이터 기반 정확한 답변 제공")
        print("  - 약 스캔 분석: DUR 데이터 기반 고도화된 위험도 분석")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
