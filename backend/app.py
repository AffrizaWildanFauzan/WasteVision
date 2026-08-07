import os
import sys
import logging
import gdown  # Library untuk download dari Google Drive
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
from PIL import Image
from torchvision import transforms
import io
import base64

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from config import Config
from utils.model_utils import ModelService
from utils.file_utils import get_file_storage

# DOWNLOAD MODEL DARI GOOGLE DRIVE

# Path yang benar (sama dengan config.py)
MODEL_PATH = Path("backend/model/best_model.pth")
MODEL_URL = "https://drive.google.com/uc?id=1uZbI8Qe060lJtI_t0NyrShi5MQgsK26z"

def download_model():
    """Download model dari Google Drive jika tidak ditemukan"""
    if not MODEL_PATH.exists():
        print(f"📥 Model tidak ditemukan di {MODEL_PATH}")
        print(f"📥 Mengunduh dari Google Drive...")
        
        # Buat folder model jika belum ada
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            gdown.download(MODEL_URL, str(MODEL_PATH), quiet=False)
            print(f"✅ Model berhasil diunduh ke {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Gagal mengunduh model: {e}")
            raise
    else:
        print(f"✅ Model sudah ada di {MODEL_PATH}")
        print(f"   Ukuran: {MODEL_PATH.stat().st_size / (1024*1024):.2f} MB")

# SETUP LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# INIT FLASK APP
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.secret_key = Config.SECRET_KEY

# CORS
CORS(app, origins=Config.CORS_ORIGINS)

# INIT SERVICES
model_service = None
file_storage = None

def init_services():
    """Initialize all services"""
    global model_service, file_storage
    
    # DOWNLOAD MODEL DULU!
    try:
        download_model()
    except Exception as e:
        logger.error(f"❌ Gagal download model: {e}")
    
    # Load model
    try:
        if Config.validate_model_path():
            model_service = ModelService(
                model_path=Config.MODEL_PATH,
                num_classes=Config.NUM_CLASSES,
                img_size=Config.IMG_SIZE,
                mean=Config.MEAN,
                std=Config.STD,
                class_names=Config.CLASS_NAMES,
                class_labels=Config.CLASS_LABELS,
                class_colors=Config.CLASS_COLORS,
                class_icons=Config.CLASS_ICONS
            )
            logger.info(f"✅ Model loaded successfully: {Config.MODEL_PATH}")
        else:
            logger.error(f"❌ Model not found: {Config.MODEL_PATH}")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
    
    # Initialize file storage
    try:
        file_storage = get_file_storage()
        logger.info(f"✅ File storage initialized: {Config.UPLOAD_FOLDER}")
    except Exception as e:
        logger.error(f"❌ Error initializing file storage: {e}")

# ROUTES

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@app.route('/')
def serve_frontend():
    """Serve main frontend page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../frontend', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ready' if model_service else 'error',
        'model_loaded': model_service is not None,
        'device': str(model_service.device) if model_service else 'None',
        'classes': Config.CLASS_NAMES,
        'storage_available': file_storage is not None,
        'version': '1.0.0'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict image from file upload"""
    if not model_service:
        return jsonify({'error': 'Model not loaded'}), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({
            'error': f'File type not allowed. Allowed: {", ".join(Config.ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        image_bytes = file.read()
        result, error = model_service.predict(image_bytes)
        
        if error:
            logger.error(f"Prediction error: {error}")
            return jsonify({'error': error}), 500
        
        if file_storage:
            image_info = file_storage.save_image(
                image_bytes, 
                original_filename=file.filename,
                folder='images'
            )
            if image_info:
                result['image_url'] = image_info['url']
                result['image_path'] = image_info['path']
                file_storage.save_prediction_result(result, image_info)
        
        return jsonify({
            'success': True,
            'result': result,
            'image_info': image_info
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict_base64', methods=['POST'])
def predict_base64():
    """Predict image from base64 string"""
    if not model_service:
        return jsonify({'error': 'Model not loaded'}), 503
    
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        image_data = base64.b64decode(data['image'])
        result, error = model_service.predict(image_data)
        
        if error:
            return jsonify({'error': error}), 500
        
        if file_storage:
            image_info = file_storage.save_image(
                image_data,
                original_filename='base64_image.jpg',
                folder='images'
            )
            if image_info:
                result['image_url'] = image_info['url']
                result['image_path'] = image_info['path']
                file_storage.save_prediction_result(result, image_info)
        
        return jsonify({
            'success': True,
            'result': result,
            'image_info': image_info
        })
        
    except Exception as e:
        logger.error(f"Error processing base64: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get class information"""
    class_info = []
    for class_name in Config.CLASS_NAMES:
        class_info.append(Config.get_class_info(class_name))
    
    return jsonify({
        'classes': class_info
    })

@app.route('/api/files', methods=['GET'])
def list_files():
    """List uploaded files"""
    if not file_storage:
        return jsonify({'error': 'File storage not available'}), 503
    
    limit = request.args.get('limit', 50, type=int)
    files = file_storage.list_files('images', limit=limit)
    
    return jsonify({
        'files': files,
        'count': len(files)
    })

# ERROR HANDLERS

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({
        'error': f'File too large. Maximum size: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB'
    }), 413

# MAIN

if __name__ == '__main__':
    # Initialize services
    init_services()
    
    logger.info(f"🚀 Starting Waste Classification API on {Config.API_HOST}:{Config.API_PORT}")
    logger.info(f"📊 Model loaded: {Config.validate_model_path()}")
    logger.info(f"📁 Upload folder: {Config.UPLOAD_FOLDER}")
    logger.info(f"🔧 Debug mode: {Config.API_DEBUG}")
    
    # TARUH KODE PRINT DI SINI (SEBELUM app.run)
    print("🚀 Flask is starting...")
    print(f"📡 Listening on port {Config.API_PORT}")
    
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.API_DEBUG
    )
