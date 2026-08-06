import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from app import app, init_services
from config import Config

if __name__ == '__main__':
    # Initialize services
    init_services()
    
    # Run app
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=False,  # Always False for production
        threaded=True
    )