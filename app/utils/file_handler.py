"""
파일 처리 관련 유틸리티
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from app.config import get_settings

settings = get_settings()


def generate_filename(original_filename: str, prefix: str = "") -> str:
    """고유한 파일명 생성"""
    ext = os.path.splitext(original_filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}{ext}"
    return f"{timestamp}_{unique_id}{ext}"


def save_upload_file(file_data: bytes, filename: str, subdirectory: str = "") -> str:
    """
    업로드된 파일 저장
    
    Args:
        file_data: 파일 바이너리 데이터
        filename: 파일명
        subdirectory: 서브 디렉토리 (예: 'medicines', 'profiles')
    
    Returns:
        저장된 파일 경로
    """
    # 저장 디렉토리 생성
    base_dir = settings.upload_dir
    if subdirectory:
        save_dir = os.path.join(base_dir, subdirectory)
    else:
        save_dir = base_dir
    
    os.makedirs(save_dir, exist_ok=True)
    
    # 고유 파일명 생성
    unique_filename = generate_filename(filename)
    file_path = os.path.join(save_dir, unique_filename)
    
    # 파일 저장
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    return file_path


def delete_file(file_path: str) -> bool:
    """파일 삭제"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """파일 크기 반환 (bytes)"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0
