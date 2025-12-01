"""
DUR(의약품안전사용서비스) CSV 데이터를 ChromaDB에 로드하는 스크립트

UC-KR 인코딩 CSV → UTF-8 읽기 → 임베딩 생성 → ChromaDB 저장
"""
import csv
import sys
import os
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from tqdm import tqdm

# ChromaDB 저장 경로
CHROMA_DB_PATH = project_root / "data" / "chroma_db"

# CSV 파일 경로
CSV_DIR = project_root / "data" / "rag" / "raw"

# 무료 임베딩 모델 (HuggingFace)
# paraphrase-multilingual-MiniLM-L12-v2: 한국어 지원, 빠름, 무료
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)


def load_contraindication_csv(file_path: Path) -> list[Document]:
    """병용금기 CSV 로드"""
    documents = []
    
    print(f"📄 {file_path.name} 로드 중...")
    
    with open(file_path, 'r', encoding='cp949') as f:
        reader = csv.DictReader(f)
        
        for row in tqdm(reader, desc="병용금기 데이터 처리"):
            # 임베딩용 텍스트 생성
            content = f"""
[병용금기]
약물 A: {row['성분명A']} ({row['제품명A']})
약물 B: {row['성분명B']} ({row['제품명B']})
상세정보: {row['상세정보']}
고시일자: {row['고시일자']}
"""
            
            metadata = {
                "type": "contraindication",  # 병용금기
                "drug_a": row['성분명A'],
                "drug_b": row['성분명B'],
                "product_a": row['제품명A'],
                "product_b": row['제품명B'],
                "detail": row['상세정보'],
                "date": row['고시일자']
            }
            
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
    
    return documents


def load_age_contraindication_csv(file_path: Path) -> list[Document]:
    """연령금기 CSV 로드"""
    documents = []
    
    print(f"📄 {file_path.name} 로드 중...")
    
    with open(file_path, 'r', encoding='cp949') as f:
        reader = csv.DictReader(f)
        
        for row in tqdm(reader, desc="연령금기 데이터 처리"):
            content = f"""
[연령금기]
성분명: {row['성분명']}
제품명: {row['제품명']}
금기연령: {row.get('금기연령', row.get('제한연령', 'N/A'))}
상세정보: {row.get('상세정보', row.get('주의내용', ''))}
"""
            
            metadata = {
                "type": "age_contraindication",  # 연령금기
                "drug": row['성분명'],
                "product": row['제품명'],
                "age_restriction": row.get('금기연령', row.get('제한연령', '')),
                "detail": row.get('상세정보', row.get('주의내용', ''))
            }
            
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
    
    return documents


def load_pregnancy_contraindication_csv(file_path: Path) -> list[Document]:
    """임부금기 CSV 로드"""
    documents = []
    
    print(f"📄 {file_path.name} 로드 중...")
    
    with open(file_path, 'r', encoding='cp949') as f:
        reader = csv.DictReader(f)
        
        for row in tqdm(reader, desc="임부금기 데이터 처리"):
            content = f"""
[임부금기]
성분명: {row['성분명']}
제품명: {row['제품명']}
금기구분: {row.get('금기구분', '임부금기')}
상세정보: {row.get('상세정보', row.get('주의내용', ''))}
"""
            
            metadata = {
                "type": "pregnancy_contraindication",  # 임부금기
                "drug": row['성분명'],
                "product": row['제품명'],
                "restriction_type": row.get('금기구분', '임부금기'),
                "detail": row.get('상세정보', row.get('주의내용', ''))
            }
            
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
    
    return documents


def load_elderly_caution_csv(file_path: Path) -> list[Document]:
    """노인주의 CSV 로드"""
    documents = []
    
    print(f"📄 {file_path.name} 로드 중...")
    
    with open(file_path, 'r', encoding='cp949') as f:
        reader = csv.DictReader(f)
        
        for row in tqdm(reader, desc="노인주의 데이터 처리"):
            content = f"""
[노인주의]
성분명: {row['성분명']}
제품명: {row['제품명']}
상세정보: {row.get('상세정보', row.get('주의내용', ''))}
"""
            
            metadata = {
                "type": "elderly_caution",  # 노인주의
                "drug": row['성분명'],
                "product": row['제품명'],
                "detail": row.get('상세정보', row.get('주의내용', ''))
            }
            
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
    
    return documents


def main():
    print("=" * 70)
    print("DUR 데이터 ChromaDB 로드 시작")
    print("=" * 70)
    
    all_documents = []
    
    # 1. 병용금기 (가장 중요)
    contraindication_file = CSV_DIR / "의약품안전사용서비스(DUR)_병용금기 품목리스트 2025.6.csv"
    if contraindication_file.exists():
        docs = load_contraindication_csv(contraindication_file)
        print(f"✅ 병용금기: {len(docs)}건 로드")
        all_documents.extend(docs[:5000])  # 처음 5,000건만 (무료 모델, 빠른 처리)
    
    # 2. 임부금기
    pregnancy_file = CSV_DIR / "의약품안전사용서비스(DUR)_임부금기 품목리스트 2025.6.csv"
    if pregnancy_file.exists():
        docs = load_pregnancy_contraindication_csv(pregnancy_file)
        print(f"✅ 임부금기: {len(docs)}건 로드")
        all_documents.extend(docs)
    
    # 3. 연령금기
    age_file = CSV_DIR / "의약품안전사용서비스(DUR)_연령금기 품목리스트 2025.6.csv"
    if age_file.exists():
        docs = load_age_contraindication_csv(age_file)
        print(f"✅ 연령금기: {len(docs)}건 로드")
        all_documents.extend(docs)
    
    # 4. 노인주의
    elderly_file = CSV_DIR / "의약품안전사용서비스(DUR)_노인주의 품목리스트 2025.6.csv"
    if elderly_file.exists():
        docs = load_elderly_caution_csv(elderly_file)
        print(f"✅ 노인주의: {len(docs)}건 로드")
        all_documents.extend(docs)
    
    # 5. 노인주의(해열진통소염제)
    elderly_nsaid_file = CSV_DIR / "의약품안전사용서비스(DUR)_노인주의(해열진통소염제) 품목리스트 2025.6.csv"
    if elderly_nsaid_file.exists():
        docs = load_elderly_caution_csv(elderly_nsaid_file)
        print(f"✅ 노인주의(해열진통소염제): {len(docs)}건 로드")
        all_documents.extend(docs)
    
    print(f"\n📊 총 {len(all_documents)}건의 문서를 ChromaDB에 저장합니다...")
    print("⚠️  무료 HuggingFace 모델로 임베딩을 생성합니다. 시간이 걸릴 수 있습니다.")
    
    # ChromaDB에 저장
    try:
        vectorstore = Chroma.from_documents(
            documents=all_documents,
            embedding=embeddings,
            persist_directory=str(CHROMA_DB_PATH),
            collection_name="dur_safety"
        )
        
        print(f"\n✅ ChromaDB 저장 완료!")
        print(f"   저장 경로: {CHROMA_DB_PATH}")
        print(f"   총 문서 수: {vectorstore._collection.count()}")
        
    except Exception as e:
        print(f"\n❌ ChromaDB 저장 실패: {e}")
        raise


if __name__ == "__main__":
    main()
