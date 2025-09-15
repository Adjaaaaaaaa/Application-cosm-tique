// =============================================================================
// EXEMPLES D'UTILISATION DU LOADER
// =============================================================================

/**
 * Exemple 1: Utilisation basique avec showLoader/hideLoader
 */
function exampleBasicLoader() {
    showLoader('primary');
    
    // Simuler une tâche longue
    setTimeout(() => {
        hideLoader();
        alert('Tâche terminée !');
    }, 3000);
}

/**
 * Exemple 2: Utilisation avec fetch API classique
 */
async function exampleFetchWithLoader() {
    try {
        showLoader('success');
        
        const response = await fetch('/api/test/');
        const data = await response.json();
        
        console.log('Données reçues:', data);
        alert('Requête réussie !');
        
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la requête');
    } finally {
        hideLoader();
    }
}

/**
 * Exemple 3: Utilisation avec le wrapper fetchWithLoader
 */
async function exampleFetchWithLoaderWrapper() {
    try {
        const data = await fetchJSONWithLoader('/api/test/', {}, 'warning');
        console.log('Données reçues:', data);
        alert('Requête réussie avec wrapper !');
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la requête');
    }
}

/**
 * Exemple 4: Utilisation avec Axios (si disponible)
 */
async function exampleAxiosWithLoader() {
    if (typeof axios !== 'undefined') {
        try {
            showLoader('danger');
            
            const response = await axios.get('/api/test/');
            console.log('Données Axios:', response.data);
            alert('Requête Axios réussie !');
            
        } catch (error) {
            console.error('Erreur Axios:', error);
            alert('Erreur Axios');
        } finally {
            hideLoader();
        }
    } else {
        alert('Axios n\'est pas disponible');
    }
}

/**
 * Exemple 5: Loader avec message personnalisé
 */
function exampleLoaderWithMessage(message = 'Chargement en cours...') {
    // Créer un loader temporaire avec message
    const tempLoader = document.createElement('div');
    tempLoader.className = 'loader-overlay show';
    tempLoader.innerHTML = `
        <div class="text-center">
            <div class="loader-spinner loader-primary mb-3"></div>
            <p class="text-white">${message}</p>
        </div>
    `;
    
    document.body.appendChild(tempLoader);
    
    // Supprimer après 3 secondes
    setTimeout(() => {
        document.body.removeChild(tempLoader);
    }, 3000);
}

/**
 * Exemple 6: Loader pour soumission de formulaire
 */
function exampleFormSubmission() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            showLoader('primary');
            
            // Simuler l'envoi du formulaire
            setTimeout(() => {
                hideLoader();
                alert('Formulaire soumis avec succès !');
            }, 2000);
        });
    }
}

// Ajouter les exemples à la page si on est en mode développement
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.addEventListener('DOMContentLoaded', function() {
        // Créer un panneau de test
        const testPanel = document.createElement('div');
        testPanel.className = 'card mt-3';
        testPanel.innerHTML = `
            <div class="card-header">
                <h6 class="mb-0"><i class="fas fa-flask me-2"></i>Tests du Loader</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <button class="btn btn-primary btn-sm me-2 mb-2" onclick="exampleBasicLoader()">
                            Test Basique
                        </button>
                        <button class="btn btn-success btn-sm me-2 mb-2" onclick="exampleFetchWithLoader()">
                            Test Fetch
                        </button>
                        <button class="btn btn-warning btn-sm me-2 mb-2" onclick="exampleFetchWithLoaderWrapper()">
                            Test Wrapper
                        </button>
                    </div>
                    <div class="col-md-6">
                        <button class="btn btn-danger btn-sm me-2 mb-2" onclick="exampleAxiosWithLoader()">
                            Test Axios
                        </button>
                        <button class="btn btn-info btn-sm me-2 mb-2" onclick="exampleLoaderWithMessage('Traitement spécial...')">
                            Test Message
                        </button>
                        <button class="btn btn-secondary btn-sm me-2 mb-2" onclick="exampleFormSubmission()">
                            Test Formulaire
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Ajouter après le formulaire de scan
        const scanForm = document.querySelector('.card');
        if (scanForm) {
            scanForm.parentNode.insertBefore(testPanel, scanForm.nextSibling);
        }
    });
}
