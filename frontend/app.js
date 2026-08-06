/**
 * Alternative app.js with different styling approach
 * Can be used alongside or instead of script.js
 */

class WasteClassifier {
    constructor() {
        this.API_URL = window.location.origin + '/api';
        this.currentFile = null;
        this.currentResult = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkHealth();
    }
    
    setupEventListeners() {
        // Upload
        document.getElementById('uploadBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            if (e.target.files[0]) {
                this.handleFile(e.target.files[0]);
            }
        });
        
        // Drag and drop
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files[0]) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });
        
        // Reset
        document.getElementById('newImageBtn').addEventListener('click', () => {
            this.resetToUpload();
        });
    }
    
    async handleFile(file) {
        // Validate
        if (!this.validateFile(file)) return;
        
        this.currentFile = file;
        this.showPreview(file);
        await this.predict(file);
    }
    
    validateFile(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            alert('Format file tidak didukung. Gunakan JPG, PNG, atau WebP.');
            return false;
        }
        
        if (file.size > 16 * 1024 * 1024) {
            alert('Ukuran file terlalu besar. Maksimal 16MB.');
            return false;
        }
        
        return true;
    }
    
    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('previewImage').src = e.target.result;
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('previewSection').style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    
    async predict(file) {
        this.showLoading(true);
        this.updateStatus('loading', '⏳ Menganalisis...');
        
        try {
            const formData = new FormData();
            formData.append('image', file);
            
            const response = await fetch(`${this.API_URL}/predict`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentResult = data.result;
                this.displayResult(data.result);
                this.updateStatus('ready', '✅ Selesai');
            } else {
                throw new Error(data.error || 'Prediksi gagal');
            }
        } catch (error) {
            console.error('Prediction error:', error);
            this.updateStatus('error', '❌ Error');
            alert('Terjadi kesalahan: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    displayResult(result) {
        const { label, icon, color, confidence, probabilities } = result;
        
        // Main result
        document.getElementById('resultIcon').textContent = icon;
        document.getElementById('resultLabel').textContent = label;
        document.getElementById('resultLabel').style.color = color;
        document.getElementById('resultConfidence').textContent = `${(confidence * 100).toFixed(1)}%`;
        document.getElementById('resultConfidence').style.color = color;
        
        // Overlay
        document.getElementById('overlayIcon').textContent = icon;
        document.getElementById('overlayLabel').textContent = label;
        document.getElementById('overlayConfidence').textContent = `${(confidence * 100).toFixed(1)}%`;
        
        // Probabilities
        this.updateProbability('Recyclable', probabilities['Recyclable'] || 0);
        this.updateProbability('Electronic', probabilities['Electronic'] || 0);
        this.updateProbability('Organic', probabilities['Organic'] || 0);
    }
    
    updateProbability(className, value) {
        const id = `prob${className}`;
        const valId = `prob${className}Val`;
        const element = document.getElementById(id);
        const valueElement = document.getElementById(valId);
        
        if (element) {
            element.style.width = '0%';
            setTimeout(() => {
                element.style.width = (value * 100) + '%';
            }, 100);
        }
        
        if (valueElement) {
            valueElement.textContent = `${(value * 100).toFixed(1)}%`;
        }
    }
    
    updateStatus(type, text) {
        const badge = document.getElementById('statusBadge');
        badge.textContent = text;
        badge.className = 'status-badge ' + type;
    }
    
    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }
    
    resetToUpload() {
        document.getElementById('previewSection').style.display = 'none';
        document.getElementById('uploadSection').style.display = 'block';
        this.currentFile = null;
        this.currentResult = null;
        document.getElementById('fileInput').value = '';
    }
    
    async checkHealth() {
        try {
            const response = await fetch(`${this.API_URL}/health`);
            const data = await response.json();
            console.log('✅ API Health:', data);
            return data;
        } catch (error) {
            console.error('❌ API not available:', error);
            return null;
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.classifier = new WasteClassifier();
});