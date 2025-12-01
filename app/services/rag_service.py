"""
RAG(Retrieval-Augmented Generation) 서비스

DUR 데이터를 ChromaDB에서 검색하여 약물 안전 정보 제공
"""
from pathlib import Path
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ChromaDB 경로
CHROMA_DB_PATH = Path(__file__).parent.parent.parent / "data" / "chroma_db"

# 임베딩 모델 (싱글톤)
_embeddings = None
_vectorstore = None


def get_embeddings():
    """임베딩 모델 가져오기 (싱글톤)"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings


def get_vectorstore():
    """ChromaDB vectorstore 가져오기 (싱글톤)"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=str(CHROMA_DB_PATH),
            embedding_function=get_embeddings(),
            collection_name="dur_safety"
        )
    return _vectorstore


def search_contraindications(drug_names: List[str], k: int = 5) -> List[Dict[str, Any]]:
    """
    병용금기 검색
    
    Args:
        drug_names: 약물 성분명 리스트
        k: 반환할 최대 결과 수
    
    Returns:
        관련 병용금기 정보 리스트
    """
    if not drug_names:
        return []
    
    vectorstore = get_vectorstore()
    
    # 검색 쿼리 생성
    query = f"병용금기 {' '.join(drug_names)}"
    
    # 유사도 검색
    results = vectorstore.similarity_search(
        query,
        k=k,
        filter={"type": "contraindication"}  # 병용금기만 필터링
    )
    
    # 결과 포맷팅
    contraindications = []
    for doc in results:
        contraindications.append({
            "drug_a": doc.metadata.get("drug_a"),
            "drug_b": doc.metadata.get("drug_b"),
            "product_a": doc.metadata.get("product_a"),
            "product_b": doc.metadata.get("product_b"),
            "detail": doc.metadata.get("detail"),
            "date": doc.metadata.get("date"),
            "content": doc.page_content
        })
    
    return contraindications


def search_age_restrictions(drug_names: List[str], k: int = 3) -> List[Dict[str, Any]]:
    """
    연령금기 검색
    
    Args:
        drug_names: 약물 성분명 리스트
        k: 반환할 최대 결과 수
    
    Returns:
        관련 연령금기 정보 리스트
    """
    if not drug_names:
        return []
    
    vectorstore = get_vectorstore()
    query = f"연령금기 {' '.join(drug_names)}"
    
    results = vectorstore.similarity_search(
        query,
        k=k,
        filter={"type": "age_contraindication"}
    )
    
    restrictions = []
    for doc in results:
        restrictions.append({
            "drug": doc.metadata.get("drug"),
            "product": doc.metadata.get("product"),
            "age_restriction": doc.metadata.get("age_restriction"),
            "detail": doc.metadata.get("detail"),
            "content": doc.page_content
        })
    
    return restrictions


def search_pregnancy_restrictions(drug_names: List[str], k: int = 3) -> List[Dict[str, Any]]:
    """
    임부금기 검색
    
    Args:
        drug_names: 약물 성분명 리스트
        k: 반환할 최대 결과 수
    
    Returns:
        관련 임부금기 정보 리스트
    """
    if not drug_names:
        return []
    
    vectorstore = get_vectorstore()
    query = f"임부금기 {' '.join(drug_names)}"
    
    results = vectorstore.similarity_search(
        query,
        k=k,
        filter={"type": "pregnancy_contraindication"}
    )
    
    restrictions = []
    for doc in results:
        restrictions.append({
            "drug": doc.metadata.get("drug"),
            "product": doc.metadata.get("product"),
            "restriction_type": doc.metadata.get("restriction_type"),
            "detail": doc.metadata.get("detail"),
            "content": doc.page_content
        })
    
    return restrictions


def search_elderly_cautions(drug_names: List[str], k: int = 3) -> List[Dict[str, Any]]:
    """
    노인주의 검색
    
    Args:
        drug_names: 약물 성분명 리스트
        k: 반환할 최대 결과 수
    
    Returns:
        관련 노인주의 정보 리스트
    """
    if not drug_names:
        return []
    
    vectorstore = get_vectorstore()
    query = f"노인주의 {' '.join(drug_names)}"
    
    results = vectorstore.similarity_search(
        query,
        k=k,
        filter={"type": "elderly_caution"}
    )
    
    cautions = []
    for doc in results:
        cautions.append({
            "drug": doc.metadata.get("drug"),
            "product": doc.metadata.get("product"),
            "detail": doc.metadata.get("detail"),
            "content": doc.page_content
        })
    
    return cautions


def search_all_safety_info(drug_names: List[str]) -> Dict[str, Any]:
    """
    모든 DUR 안전 정보 통합 검색
    
    Args:
        drug_names: 약물 성분명 리스트
    
    Returns:
        병용금기, 연령금기, 임부금기, 노인주의 정보 통합
    """
    return {
        "contraindications": search_contraindications(drug_names, k=5),
        "age_restrictions": search_age_restrictions(drug_names, k=3),
        "pregnancy_restrictions": search_pregnancy_restrictions(drug_names, k=3),
        "elderly_cautions": search_elderly_cautions(drug_names, k=3)
    }


def search_by_question(question: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    자연어 질문으로 DUR 정보 검색 (챗봇용)
    
    Args:
        question: 사용자 질문
        k: 반환할 최대 결과 수
    
    Returns:
        관련 DUR 안전 정보 리스트
    """
    vectorstore = get_vectorstore()
    
    # 유사도 검색 (타입 필터 없음)
    results = vectorstore.similarity_search(question, k=k)
    
    safety_info = []
    for doc in results:
        safety_info.append({
            "type": doc.metadata.get("type"),
            "metadata": doc.metadata,
            "content": doc.page_content
        })
    
    return safety_info
