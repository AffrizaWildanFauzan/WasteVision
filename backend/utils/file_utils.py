import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import shutil
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class FileStorage:
    """Service untuk menyimpan file secara lokal"""
    
    def __init__(self, upload_folder: str, upload_url: str = '/uploads/'):
        self.upload_folder = Path(upload_folder)
        self.upload_url = upload_url
        
        # Buat folder jika belum ada
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        
        # Buat subfolder
        self.images_folder = self.upload_folder / 'images'
        self.results_folder = self.upload_folder / 'results'
        self.images_folder.mkdir(exist_ok=True)
        self.results_folder.mkdir(exist_ok=True)
        
        logger.info(f"FileStorage initialized: {self.upload_folder}")
    
    def save_image(
        self, 
        file_bytes: bytes, 
        original_filename: str = None,
        folder: str = 'images'
    ) -> Optional[Dict[str, Any]]:
        """Simpan gambar ke lokal"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            
            if original_filename:
                ext = original_filename.rsplit('.', 1)[-1].lower()
            else:
                ext = 'jpg'
            
            filename = f"{timestamp}_{unique_id}.{ext}"
            
            # Tentukan path
            if folder == 'images':
                save_path = self.images_folder / filename
                url_path = f"{self.upload_url}images/{filename}"
            else:
                save_path = self.results_folder / filename
                url_path = f"{self.upload_url}results/{filename}"
            
            # Simpan file
            with open(save_path, 'wb') as f:
                f.write(file_bytes)
            
            file_size = len(file_bytes)
            logger.info(f"Image saved: {save_path} ({file_size} bytes)")
            
            return {
                'filename': filename,
                'path': str(save_path),
                'url': url_path,
                'size': file_size,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return None
    
    def save_prediction_result(
        self, 
        result: Dict[str, Any],
        image_info: Dict[str, Any]
    ) -> Optional[str]:
        """Simpan hasil prediksi sebagai JSON"""
        try:
            import json
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"result_{timestamp}.json"
            save_path = self.results_folder / filename
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'result': result,
                'image': image_info
            }
            
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Result saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            return None
    
    def get_file_url(self, filename: str, folder: str = 'images') -> str:
        """Mendapatkan URL untuk file yang disimpan"""
        return f"{self.upload_url}{folder}/{filename}"
    
    def delete_file(self, filename: str, folder: str = 'images') -> bool:
        """Hapus file"""
        try:
            if folder == 'images':
                file_path = self.images_folder / filename
            else:
                file_path = self.results_folder / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def list_files(self, folder: str = 'images', limit: int = 100) -> list:
        """List file dalam folder"""
        try:
            if folder == 'images':
                folder_path = self.images_folder
            else:
                folder_path = self.results_folder
            
            files = []
            for file_path in sorted(folder_path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
                if file_path.is_file():
                    files.append({
                        'filename': file_path.name,
                        'url': self.get_file_url(file_path.name, folder),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def get_file_size(self, filename: str, folder: str = 'images') -> int:
        """Mendapatkan ukuran file"""
        try:
            if folder == 'images':
                file_path = self.images_folder / filename
            else:
                file_path = self.results_folder / filename
            
            if file_path.exists():
                return file_path.stat().st_size
            return 0
            
        except Exception:
            return 0

# Singleton instance
_file_storage = None

def get_file_storage():
    """Get singleton file storage instance"""
    global _file_storage
    if _file_storage is None:
        from config import Config
        _file_storage = FileStorage(Config.UPLOAD_FOLDER, Config.UPLOAD_URL)
    return _file_storage