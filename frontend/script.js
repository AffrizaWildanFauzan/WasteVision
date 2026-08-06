// ============================================
// WASTEVISION - Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // ============================================
    // NAVIGATION
    // ============================================
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    // Navigasi antar halaman
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.dataset.page;

            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show selected page
            pages.forEach(p => p.classList.remove('active'));
            document.getElementById(`page-${pageId}`).classList.add('active');

            // Close mobile menu
            navMenu.classList.remove('open');
        });
    });

    // Mobile nav toggle
    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('open');
    });

    // ============================================
    // DARK MODE TOGGLE
    // ============================================
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = themeToggle.querySelector('i');

    // Check saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
    }

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            themeIcon.className = 'fas fa-moon';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeIcon.className = 'fas fa-sun';
        }
    });

    // ============================================
    // UPLOAD & PREDICTION
    // ============================================
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const API_URL = window.location.origin + '/api';

    // Upload button
    uploadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    // Drop zone click
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    });

    // Drag and drop
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
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Handle file upload
    async function handleFile(file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            alert('❌ Format file tidak didukung. Gunakan JPG, PNG, atau WebP.');
            return;
        }

        // Validate file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            alert('❌ Ukuran file terlalu besar. Maksimal 16MB.');
            return;
        }

        // Show loading
        loadingOverlay.style.display = 'flex';

        try {
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                displayResult(data.result);
                // Switch to home page if not already
                document.querySelector('.nav-link[data-page="home"]').click();
            } else {
                throw new Error(data.error || 'Prediksi gagal');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Terjadi kesalahan: ' + error.message);
        } finally {
            loadingOverlay.style.display = 'none';
            fileInput.value = '';
        }
    }

    // Display prediction result
    function displayResult(result) {
        const { predicted_class, confidence, probabilities, label, icon, color } = result;

        // Create result card
        const resultHTML = `
            <div class="result-container" style="margin-top: 24px;">
                <div class="result-card" style="background: var(--bg-card); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); border-left: 6px solid ${color};">
                    <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                        <div style="font-size: 4rem;">${icon}</div>
                        <div style="flex: 1;">
                            <h3 style="font-size: 1.5rem; font-weight: 800; color: ${color};">${label}</h3>
                            <p style="color: var(--text-light);">Confidence: <strong style="color: ${color};">${(confidence * 100).toFixed(1)}%</strong></p>
                        </div>
                    </div>
                    <div style="margin-top: 16px;">
                        ${Object.entries(probabilities).map(([cls, prob]) => `
                            <div style="display: grid; grid-template-columns: 120px 1fr 60px; gap: 12px; align-items: center; margin-bottom: 8px;">
                                <span style="font-weight: 500;">${cls}</span>
                                <div style="height: 10px; background: var(--border); border-radius: 10px; overflow: hidden;">
                                    <div style="height: 100%; width: ${prob * 100}%; background: var(--gradient); border-radius: 10px; transition: width 0.8s ease;"></div>
                                </div>
                                <span style="font-weight: 600; text-align: right;">${(prob * 100).toFixed(1)}%</span>
                            </div>
                        `).join('')}
                    </div>
                    <div style="margin-top: 16px; display: flex; gap: 12px; flex-wrap: wrap;">
                        <button onclick="location.reload()" class="btn-primary" style="padding: 10px 24px;">
                            <i class="fas fa-upload"></i> Gambar Baru
                        </button>
                        <button onclick="downloadResult()" class="btn-primary" style="background: var(--gradient); padding: 10px 24px;">
                            <i class="fas fa-download"></i> Download Hasil
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Insert result after upload section
        const uploadSection = document.getElementById('uploadSection');
        const existingResult = document.querySelector('.result-container');
        if (existingResult) {
            existingResult.remove();
        }
        uploadSection.insertAdjacentHTML('afterend', resultHTML);

        // Scroll to result
        document.querySelector('.result-container').scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Download result function (global)
    window.downloadResult = function() {
        const resultCard = document.querySelector('.result-card');
        if (!resultCard) {
            alert('Tidak ada hasil untuk di-download');
            return;
        }

        // Extract data from result card
        const label = resultCard.querySelector('h3')?.textContent || 'Unknown';
        const confidence = resultCard.querySelector('strong')?.textContent || '0%';
        
        // Get probabilities
        const probItems = resultCard.querySelectorAll('div[style*="grid-template-columns: 120px 1fr 60px"]');
        const probabilities = {};
        probItems.forEach(item => {
            const spans = item.querySelectorAll('span');
            if (spans.length >= 3) {
                const className = spans[0].textContent.trim();
                const probValue = spans[2].textContent.trim();
                probabilities[className] = probValue;
            }
        });

        const data = {
            timestamp: new Date().toISOString(),
            result: {
                label: label,
                confidence: confidence,
                probabilities: probabilities
            },
            model: 'ConvNeXt-Large',
            developer: 'Affriza Wildan Fauzan'
        };

        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `wastevision_result_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    // ============================================
    // HEALTH CHECK
    // ============================================
    async function checkHealth() {
        try {
            const response = await fetch(`${API_URL}/health`);
            const data = await response.json();
            console.log('✅ API Status:', data);
            if (!data.model_loaded) {
                console.warn('⚠️ Model tidak loaded!');
            }
        } catch (error) {
            console.error('❌ API tidak tersedia:', error);
        }
    }

    checkHealth();
});