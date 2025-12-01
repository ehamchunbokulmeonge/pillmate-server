"""
AI Hub 의약품 이미지 데이터셋 로더

사용법:
1. AI Hub에서 데이터 다운로드: https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=576
2. JSON 파일을 data/aihub/ 폴더에 저장
3. load_aihub_data() 함수로 데이터 로드
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class AIHubDataLoader:
    def __init__(self, data_path: str = "data/aihub"):
        self.data_path = Path(data_path)
        self.medicine_data: List[Dict] = []
        self.loaded = False
    
    def load_data(self) -> bool:
        """AI Hub JSON 파일들을 로드"""
        try:
            if not self.data_path.exists():
                print(f"⚠️  AI Hub 데이터 경로가 없습니다: {self.data_path}")
                print(f"   {self.data_path.absolute()} 폴더를 생성하고 JSON 파일을 넣어주세요.")
                return False
            
            json_files = list(self.data_path.glob("*.json"))
            
            if not json_files:
                print(f"⚠️  {self.data_path}에 JSON 파일이 없습니다.")
                return False
            
            print(f"📂 {len(json_files)}개의 JSON 파일을 찾았습니다.")
            
            for json_file in json_files:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # AI Hub 데이터 구조: {"images": [...], "annotations": [...]}
                    if "images" in data:
                        self.medicine_data.extend(data["images"])
            
            self.loaded = True
            print(f"✅ 총 {len(self.medicine_data)}개의 약 데이터 로드 완료")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def search_by_name(self, query: str, limit: int = 10) -> List[Dict]:
        """약 이름으로 검색"""
        if not self.loaded:
            return []
        
        query_lower = query.lower()
        results = []
        
        for med in self.medicine_data:
            # 한글 이름 검색
            if "dl_name" in med and query_lower in med["dl_name"].lower():
                results.append(med)
            # 영문 이름 검색
            elif "dl_name_en" in med and query_lower in med.get("dl_name_en", "").lower():
                results.append(med)
            # 제조사 검색
            elif "dl_company" in med and query_lower in med.get("dl_company", "").lower():
                results.append(med)
            
            if len(results) >= limit:
                break
        
        return results
    
    def search_by_print(self, front: str = "", back: str = "") -> List[Dict]:
        """각인으로 검색"""
        if not self.loaded:
            return []
        
        results = []
        
        for med in self.medicine_data:
            match = True
            
            if front and med.get("print_front", "").upper() != front.upper():
                match = False
            
            if back and med.get("print_back", "").upper() != back.upper():
                match = False
            
            if match and (front or back):
                results.append(med)
        
        return results
    
    def get_medicine_by_item_seq(self, item_seq: str) -> Optional[Dict]:
        """품목기준코드로 검색"""
        if not self.loaded:
            return None
        
        for med in self.medicine_data:
            if str(med.get("item_seq")) == str(item_seq):
                return med
        
        return None


# 싱글톤 인스턴스
_loader = None

def get_aihub_loader() -> AIHubDataLoader:
    """AI Hub 데이터 로더 싱글톤"""
    global _loader
    if _loader is None:
        _loader = AIHubDataLoader()
        _loader.load_data()
    return _loader
