/**
 * Demo scan functionality for barcode scanning.
 * 
 * Handles camera access, barcode scanning, and form submission.
 */

(function() {
    'use strict';
    
    // DOM elements
    const startBtn = document.getElementById('start-scan');
    const stopBtn = document.getElementById('stop-scan');
    const videoElem = document.getElementById('video-preview');
    const statusText = document.getElementById('status-text');
    const barcodeInput = document.getElementById('barcode');
    const scanForm = document.getElementById('scan-form');
    const submitBtn = document.getElementById('submit-btn');
    
    // Global variables
    let codeReader = null;
    let currentDeviceId = null;
    let running = false;
    let mediaStream = null;
    
    /**
     * Set status message with appropriate styling.
     * 
     * @param {string} msg - Status message
     * @param {string} type - Message type (info, success, error)
     */
    function setStatus(msg, type = 'info') {
        console.log('Status:', msg);
        const statusDiv = document.getElementById('scan-status');
        const iconClass = type === 'error' ? 'fa-exclamation-triangle' : 
                         type === 'success' ? 'fa-check-circle' : 'fa-info-circle';
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 'alert-info';
        
        statusDiv.innerHTML = `
            <div class="alert ${alertClass}">
                <i class="fas ${iconClass}"></i> 
                <span id="status-text">${msg}</span>
            </div>
        `;
    }
    
    /**
     * Initialize ZXing library and check availability.
     */
    function initializeZXing() {
        const ZX = window.ZXing || (typeof ZXing !== 'undefined' ? ZXing : null);
        if (!ZX || !ZX.BrowserMultiFormatReader) {
            setStatus('Librairie de scan non chargée. Vérifiez votre connexion Internet.', 'error');
            if (startBtn) startBtn.disabled = true;
            return false;
        }
        
        codeReader = new ZX.BrowserMultiFormatReader();
        return true;
    }
    
    /**
     * List available cameras.
     * 
     * @returns {Promise<Array>} List of camera devices
     */
    async function listCameras() {
        try {
            const devices = await codeReader.listVideoInputDevices();
            console.log('Cameras found:', devices.length);
            return devices;
        } catch (err) {
            console.error('Error listing cameras:', err);
            setStatus('Erreur lors de la détection des caméras: ' + err.message, 'error');
            return [];
        }
    }
    
    /**
     * Configure camera selection.
     * 
     * @param {Array} devices - List of camera devices
     */
    function configureCamera(devices) {
        if (devices.length === 0) {
            setStatus('Aucune caméra détectée.', 'error');
            return;
        }
        
        if (devices.length === 1) {
            currentDeviceId = devices[0].deviceId;
            setStatus(`Caméra détectée: ${devices[0].label || 'Caméra par défaut'}`, 'info');
        } else {
            // Multiple cameras - use the first one for now
            currentDeviceId = devices[0].deviceId;
            setStatus(`${devices.length} caméras détectées. Utilisation de: ${devices[0].label || 'Caméra par défaut'}`, 'info');
        }
    }
    
    /**
     * Start barcode scanning.
     */
    async function startScanning() {
        if (!codeReader || running) return;
        
        try {
            setStatus('Démarrage du scan...', 'info');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            
            running = true;
            
            // Start decoding from video element
            await codeReader.decodeFromVideoDevice(
                currentDeviceId,
                videoElem,
                (result, error) => {
                    if (result) {
                        console.log('Barcode detected:', result.text);
                        handleBarcodeDetected(result.text);
                    }
                    if (error && error.name !== 'NotFoundException') {
                        console.error('Scan error:', error);
                    }
                }
            );
            
            setStatus('Scan en cours... Pointez la caméra vers un code-barres.', 'info');
            
        } catch (err) {
            console.error('Error starting scan:', err);
            setStatus('Erreur lors du démarrage du scan: ' + err.message, 'error');
            stopScanning();
        }
    }
    
    /**
     * Stop barcode scanning.
     */
    function stopScanning() {
        if (!running) return;
        
        try {
            if (codeReader) {
                codeReader.reset();
            }
            
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
                mediaStream = null;
            }
            
            running = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            
            setStatus('Scan arrêté.', 'info');
            
        } catch (err) {
            console.error('Error stopping scan:', err);
        }
    }
    
    /**
     * Handle detected barcode.
     * 
     * @param {string} barcode - Detected barcode value
     */
    function handleBarcodeDetected(barcode) {
        console.log('Barcode detected:', barcode);
        
        // Fill the barcode input
        if (barcodeInput) {
            barcodeInput.value = barcode;
        }
        
        // Stop scanning
        stopScanning();
        
        // Show success message
        setStatus(`Code-barres détecté: ${barcode}`, 'success');
        
        // Auto-submit form after a short delay
        setTimeout(() => {
            if (scanForm) {
                submitScanForm();
            }
        }, 1000);
    }
    
    /**
     * Submit scan form with loading state.
     */
    function submitScanForm() {
        if (!scanForm || !submitBtn) return;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyse en cours...';
        
        // Show progress bar
        showProgressBar();
        
        // Submit form
        scanForm.submit();
    }
    
    /**
     * Show progress bar during analysis.
     */
    function showProgressBar() {
        const progressContainer = document.getElementById('scan-progress');
        const progressBar = document.getElementById('progress-bar');
        const currentStep = document.getElementById('current-step');
        
        if (progressContainer) {
            progressContainer.style.display = 'block';
            
            // Animate progress bar
            let progress = 0;
            const steps = [
                'Recherche du produit...',
                'Analyse des ingrédients...',
                'Calcul du score de sécurité...',
                'Finalisation...'
            ];
            
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 100) progress = 100;
                
                if (progressBar) {
                    progressBar.style.width = progress + '%';
                    progressBar.setAttribute('aria-valuenow', progress);
                }
                
                // Update step text
                const stepIndex = Math.floor((progress / 100) * steps.length);
                if (currentStep && stepIndex < steps.length) {
                    currentStep.textContent = steps[stepIndex];
                }
                
                if (progress >= 100) {
                    clearInterval(interval);
                }
            }, 200);
        }
    }
    
    /**
     * Hide progress bar.
     */
    function hideProgressBar() {
        const progressContainer = document.getElementById('scan-progress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }
    
    /**
     * Initialize the demo scan functionality.
     */
    async function init() {
        // Check browser support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setStatus('Votre navigateur ne supporte pas l\'accès aux périphériques vidéo.', 'error');
            if (startBtn) startBtn.disabled = true;
            return;
        }
        
        // Initialize ZXing
        if (!initializeZXing()) {
            return;
        }
        
        try {
            // Test camera access
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            
            // List and configure cameras
            const devices = await listCameras();
            if (devices.length > 0) {
                configureCamera(devices);
                startBtn.disabled = false;
                setStatus('Scanner prêt. Cliquez sur "Démarrer" pour commencer.', 'info');
            }
        } catch (err) {
            console.error('Initialization error:', err);
            setStatus('Erreur d\'accès au périphérique vidéo: ' + (err.message || err), 'error');
            if (startBtn) startBtn.disabled = true;
        }
    }
    
    /**
     * Show danger details in modal.
     * 
     * @param {string} ingredientName - Name of the ingredient
     * @param {string} categoryName - Name of the category
     * @param {Object} categoryInfo - Category information
     */
    function showDangerDetails(ingredientName, categoryName, categoryInfo) {
        document.getElementById('modalIngredientName').textContent = ingredientName;
        
        const categoryBadge = document.getElementById('modalCategoryName');
        categoryBadge.textContent = categoryName;
        categoryBadge.className = 'badge bg-' +
            (categoryInfo.color === 'red' ? 'danger' :
             categoryInfo.color === 'orange' ? 'warning' : 'success');
        
        const tbody = document.getElementById('modalDangerDetails');
        tbody.innerHTML = '';
        
        if (categoryInfo.details && categoryInfo.details.length > 0) {
            categoryInfo.details.forEach(detail => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${detail.h_code || 'N/A'}</strong></td>
                    <td>${detail.description || 'N/A'}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="2" class="text-muted">Aucun détail disponible</td>';
            tbody.appendChild(row);
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('dangerModal'));
        modal.show();
    }
    
    // Event listeners
    if (startBtn) {
        startBtn.addEventListener('click', startScanning);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopScanning);
    }
    
    if (scanForm) {
        scanForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitScanForm();
        });
    }
    
    // Also handle manual form submission (when user clicks submit button directly)
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            submitScanForm();
        });
    }
    
    // Hide progress bar if results are already shown
    if (document.querySelector('.card-body h3')) {
        hideProgressBar();
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Make functions globally available
    window.showDangerDetails = showDangerDetails;
    
})();