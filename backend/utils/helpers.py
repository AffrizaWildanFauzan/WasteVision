import os
from PIL import Image
import io
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def validate_image(image_bytes: bytes) -> bool:
    """Validate if bytes represent a valid image"""
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
        return True
    except Exception:
        return False

def resize_image(
    image_bytes: bytes,
    target_size: Tuple[int, int] = (224, 224),
    maintain_aspect: bool = True
) -> bytes:
    """Resize image to target size"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        if maintain_aspect:
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            # Create new image with padding
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            offset = ((target_size[0] - image.width) // 2,
                     (target_size[1] - image.height) // 2)
            new_img.paste(image, offset)
            image = new_img
        else:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Resize error: {e}")
        return image_bytes

def format_prediction_response(
    result: dict,
    include_all_probabilities: bool = True,
    include_top_k: bool = True
) -> dict:
    """Format prediction response"""
    response = {
        'predicted_class': result.get('predicted_class'),
        'confidence': result.get('confidence'),
        'label': result.get('label'),
        'icon': result.get('icon'),
        'color': result.get('color')
    }
    
    if include_all_probabilities:
        response['probabilities'] = result.get('probabilities', {})
    
    if include_top_k:
        response['top_3'] = result.get('top_3', [])
    
    return response

def get_image_info(image_bytes: bytes) -> dict:
    """Get image metadata"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode,
            'size': len(image_bytes)
        }
    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        return {'error': str(e)}