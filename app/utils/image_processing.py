"""
이미지 처리 유틸리티
"""

from PIL import Image
import io
from typing import Tuple, Optional


def resize_image(image: Image.Image, max_size: Tuple[int, int] = (800, 800)) -> Image.Image:
    """이미지 리사이즈"""
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image


def convert_to_jpeg(image: Image.Image, quality: int = 85) -> bytes:
    """이미지를 JPEG로 변환"""
    # RGBA -> RGB 변환 (PNG 등의 투명 이미지 처리)
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    
    # JPEG로 변환
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    return output.read()


def preprocess_ocr_image(image: Image.Image) -> Image.Image:
    """OCR을 위한 이미지 전처리"""
    # 그레이스케일 변환
    image = image.convert('L')
    
    # 대비 향상
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    return image


def get_image_info(image: Image.Image) -> dict:
    """이미지 정보 추출"""
    return {
        'format': image.format,
        'mode': image.mode,
        'size': image.size,
        'width': image.width,
        'height': image.height,
    }
