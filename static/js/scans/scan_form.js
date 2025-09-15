/**
 * Script pour le formulaire de scan de produits
 * Gère le scanner de codes-barres avec la bibliothèque ZXing
 * Inclut une barre de progression pour indiquer l'avancement
 */

(function() {
    const startBtn = document.getElementById('start-scan');
    const stopBtn = document.getElementById('stop-scan');
    const videoElem = document.getElementById('video-preview');
    const statusText = document.getElementById('status-text');
    const barcodeInput = document.getElementById('id_barcode');
    
    // Éléments de la barre de progression
    const progressContainer = document.getElementById('scan-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressSteps = document.querySelector('.progress-steps');
    
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
    
    // Fonctions pour gérer la barre de progression
    function showProgress() {
        if (progressContainer) {
            progressContainer.style.display = 'block';
            updateProgress(0, 'Initialisation du scan...');
        }
    }
    
    function hideProgress() {
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }
    
    function updateProgress(percentage, message) {
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            
            // Forcer la couleur bleue
            progressBar.style.background = 'linear-gradient(90deg, #007bff 0%, #0056b3 100%)';
            progressBar.style.backgroundColor = '#007bff';
            progressBar.classList.add('bg-primary');
        }
        
        if (progressSteps) {
            progressSteps.innerHTML = `<small class="text-muted">${message}</small>`;
        }
    }
    
    function simulateProgress() {
        const steps = [
            { progress: 10, message: 'Initialisation de la caméra...' },
            { progress: 25, message: 'Recherche du code-barres...' },
            { progress: 50, message: 'Analyse en cours...' },
            { progress: 75, message: 'Traitement des données...' },
            { progress: 90, message: 'Finalisation...' },
            { progress: 100, message: 'Scan terminé !' }
        ];
        
        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                updateProgress(step.progress, step.message);
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 800); // Chaque étape dure 800ms
        
        return interval;
    }

    // Vérifier si la bibliothèque ZXing est chargée
    const ZX = window.ZXing || (typeof ZXing !== 'undefined' ? ZXing : null);
    if (!ZX || !ZX.BrowserMultiFormatReader) {
        setStatus('Librairie de scan non chargée. Vérifiez votre connexion Internet.', 'error');
        if (startBtn) startBtn.disabled = true;
        return;
    }

    const codeReader = new ZX.BrowserMultiFormatReader();
    let currentDeviceId = null;
    let running = false;

    // Fonction pour lister les périphériques vidéo disponibles
    async function listCameras() {
        try {
            const devices = await codeReader.listVideoInputDevices();
            if (!devices || devices.length === 0) {
                setStatus('Aucun périphérique vidéo détecté.', 'error');
                startBtn.disabled = true;
                return [];
            }
            return devices;
        } catch (err) {
            console.error('Erreur liste périphériques:', err);
            setStatus('Erreur d\'accès aux périphériques: ' + (err.message || err), 'error');
            return [];
        }
    }

    // Configuration automatique du périphérique vidéo
    function configureCamera(devices) {
        if (devices && devices.length > 0) {
            // Essayer de sélectionner le périphérique arrière par défaut
            const backCamera = devices.find(device => 
                /back|rear|arrière|environment/gi.test(device.label || '')
            );
            
            currentDeviceId = backCamera ? backCamera.deviceId : devices[0].deviceId;
        }
    }

    // Démarrer le scan
    async function startScan() {
        if (running) return;
        
        setStatus('Initialisation du scanner...', 'info');
        showProgress();
        startBtn.disabled = true;
        stopBtn.disabled = false;
        running = true;
        
        // Démarrer la simulation de progression
        const progressInterval = simulateProgress();
        
        try {
            // Si pas de deviceId spécifique, essayer de détecter automatiquement
            const constraints = currentDeviceId 
                ? { deviceId: { exact: currentDeviceId } }
                : { facingMode: 'environment' };
            
            // Démarrer le périphérique vidéo
            const stream = await navigator.mediaDevices.getUserMedia({
                video: constraints,
                audio: false
            });
            
            videoElem.srcObject = stream;
            await videoElem.play();
            
            // Démarrer la détection de codes-barres
            codeReader.decodeFromVideoDevice(currentDeviceId, videoElem, (result, err) => {
                if (result) {
                    clearInterval(progressInterval);
                    handleResult(result);
                }
                if (err && !(err instanceof ZX.NotFoundException)) {
                    console.error('Erreur scan:', err);
                    clearInterval(progressInterval);
                    setStatus('Erreur: ' + (err.message || err), 'error');
                    hideProgress();
                }
            });
            
            setStatus('Recherche de code-barres...', 'info');
            
        } catch (err) {
            console.error('Erreur démarrage scan:', err);
            setStatus('Erreur: ' + (err.message || err), 'error');
            stopScan();
        }
    }

    // Arrêter le scan
    function stopScan() {
        if (!running) return;
        
        try {
            codeReader.reset();
            if (videoElem.srcObject) {
                const tracks = videoElem.srcObject.getTracks();
                tracks.forEach(track => track.stop());
                videoElem.srcObject = null;
            }
        } catch (err) {
            console.error('Erreur arrêt scan:', err);
        } finally {
            running = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            hideProgress();
            setStatus('Scanner arrêté. Cliquez sur "Démarrer" pour recommencer.', 'info');
        }
    }

    // Gérer le résultat du scan
    function handleResult(result) {
        if (!result || !result.text) return;
        
        console.log('Code-barres détecté:', result.text);
        updateProgress(100, 'Code-barres détecté ! Redirection...');
        setStatus('Code détecté: ' + result.text, 'success');
        
        if (barcodeInput && barcodeInput.form) {
            barcodeInput.value = result.text;
            // Petit délai avant la soumission pour laisser le temps de voir le résultat
            setTimeout(() => {
                stopScan();
                barcodeInput.form.submit();
            }, 1500);
        }
    }

    // Gérer la soumission du formulaire manuel
    function handleFormSubmit() {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                const barcodeInput = document.getElementById('id_barcode');
                if (barcodeInput && barcodeInput.value.trim()) {
                    showProgress();
                    updateProgress(20, 'Envoi de la requête...');
                    
                    // Simuler la progression pendant l'envoi
                    const progressSteps = [
                        { progress: 40, message: 'Recherche du produit...' },
                        { progress: 60, message: 'Analyse des ingrédients...' },
                        { progress: 80, message: 'Calcul du score...' },
                        { progress: 100, message: 'Redirection vers les résultats...' }
                    ];
                    
                    let currentStep = 0;
                    const interval = setInterval(() => {
                        if (currentStep < progressSteps.length) {
                            const step = progressSteps[currentStep];
                            updateProgress(step.progress, step.message);
                            currentStep++;
                        } else {
                            clearInterval(interval);
                        }
                    }, 600);
                }
            });
        }
    }
    
    // Événements
    startBtn.addEventListener('click', (e) => {
        e.preventDefault();
        startScan();
    });
    
    stopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        stopScan();
    });
    
    // Initialisation
    async function init() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setStatus('Votre navigateur ne supporte pas l\'accès aux périphériques vidéo.', 'error');
            startBtn.disabled = true;
            return;
        }
        
        try {
            // D'abord, demander la permission d'accéder au périphérique vidéo
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            // Libérer immédiatement le flux
            stream.getTracks().forEach(track => track.stop());
            
            // Ensuite, configurer le périphérique vidéo automatiquement
            const devices = await listCameras();
            if (devices.length > 0) {
                configureCamera(devices);
                startBtn.disabled = false;
                setStatus('Scanner prêt. Cliquez sur "Démarrer" pour commencer.', 'info');
            }
        } catch (err) {
            console.error('Erreur initialisation:', err);
            setStatus('Erreur d\'accès au périphérique vidéo: ' + (err.message || err), 'error');
            startBtn.disabled = true;
        }
    }
    
    // Fonction de test pour vérifier la couleur bleue
    function testProgressBar() {
        if (progressBar) {
            console.log('Test de la barre de progression...');
            showProgress();
            updateProgress(50, 'Test de la couleur bleue...');
            
            setTimeout(() => {
                updateProgress(100, 'Test terminé !');
                setTimeout(() => {
                    hideProgress();
                }, 1000);
            }, 2000);
        }
    }
    
    // Exposer la fonction de test globalement pour debug
    window.testProgressBar = testProgressBar;
    
    // Démarrer l'initialisation
    init();
    handleFormSubmit();
})();