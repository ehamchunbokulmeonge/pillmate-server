"""
유틸리티 함수들
"""

import os
from datetime import datetime
from typing import Optional


def ensure_dir(directory: str) -> None:
    """디렉토리가 없으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_file_extension(filename: str) -> str:
    """파일 확장자 추출"""
    return os.path.splitext(filename)[1].lower()


def is_valid_image(filename: str) -> bool:
    """이미지 파일 유효성 검사"""
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    return get_file_extension(filename) in valid_extensions


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """datetime을 문자열로 포맷팅"""
    if dt is None:
        return ""
    return dt.strftime(format_str)


def parse_time_range(time_of_day: str) -> tuple:
    """
    time_of_day를 시간 범위로 변환
    예: 'morning' -> (6, 11)
    """
    time_ranges = {
        'morning': (6, 11),
        'afternoon': (12, 17),
        'evening': (18, 21),
        'night': (22, 5),
    }
    return time_ranges.get(time_of_day, (0, 23))
