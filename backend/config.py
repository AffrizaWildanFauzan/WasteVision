import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent
    MODEL_DIR = BASE_DIR / 'model'
    UPLOAD_DIR = BASE_DIR / 'uploads'
    
    # Create directories if not exist
    UPLOAD_DIR.mkdir(exist_ok=True)
    (UPLOAD_DIR / 'images').mkdir(exist_ok=True)
    (UPLOAD_DIR / 'results').mkdir(exist_ok=True)
    
    # Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', str(MODEL_DIR / 'best_model.pth'))
    IMG_SIZE = int(os.getenv('IMG_SIZE', 224))
    NUM_CLASSES = int(os.getenv('NUM_CLASSES', 3))
    
    # Normalization (ImageNet default)
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    UPLOAD_URL = '/uploads/'
    
    # Class mapping
    CLASS_NAMES = ['Recyclable', 'Electronic', 'Organic']
    CLASS_LABELS = {
        'Recyclable': '♻️ Daur Ulang',
        'Electronic': '🔌 Elektronik',
        'Organic': '🌿 Organik'
    }
    CLASS_COLORS = {
        'Recyclable': '#2ecc71',
        'Electronic': '#3498db',
        'Organic': '#e74c3c'
    }
    CLASS_ICONS = {
        'Recyclable': '♻️',
        'Electronic': '💻',
        'Organic': '🍂'
    }
    CLASS_DESCRIPTIONS = {
        'Recyclable': 'Bahan yang dapat didaur ulang seperti kertas, plastik, kaca, dan logam',
        'Electronic': 'Perangkat elektronik dan komponennya seperti ponsel, laptop, dan baterai',
        'Organic': 'Bahan organik seperti sisa makanan, daun, dan limbah dapur'
    }
    
    @classmethod
    def get_class_info(cls, class_name):
        return {
            'name': class_name,
            'label': cls.CLASS_LABELS.get(class_name, class_name),
            'color': cls.CLASS_COLORS.get(class_name, '#000000'),
            'icon': cls.CLASS_ICONS.get(class_name, '📦'),
            'description': cls.CLASS_DESCRIPTIONS.get(class_name, '')
        }
    
    @classmethod
    def validate_model_path(cls):
        return Path(cls.MODEL_PATH).exists()