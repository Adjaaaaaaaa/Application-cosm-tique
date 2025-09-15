/* =============================================================================
   BEAUTYSCAN - JAVASCRIPT DE BASE
   ============================================================================= */

// Objet principal de l'application
const BeautyScan = {
    
    // Initialisation de l'application
    init: function() {
        this.setupAlerts();
        this.setupTooltips();
        this.setupAnimations();
        console.log('BeautyScan initialisé avec succès');
    },
    
    // Configuration des alertes
    setupAlerts: function() {
        // Auto-dismiss des alertes après 5 secondes
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert && alert.parentNode) {
                    alert.style.opacity = '0';
                    setTimeout(() => {
                        if (alert && alert.parentNode) {
                            alert.remove();
                        }
                    }, 300);
                }
            }, 5000);
        });
    },
    
    // Configuration des tooltips Bootstrap
    setupTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Configuration des animations
    setupAnimations: function() {
        // Animation des éléments au scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, observerOptions);
        
        // Observer les éléments avec la classe .animate-on-scroll
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    },
    
    // Afficher une alerte
    showAlert: function(message, type = 'info', duration = 5000) {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-dismiss
        setTimeout(() => {
            const alert = alertContainer.lastElementChild;
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, duration);
    },
    
    // Méthodes d'alerte spécifiques
    showSuccess: function(message) {
        this.showAlert(message, 'success');
    },
    
    showError: function(message) {
        this.showAlert(message, 'danger');
    },
    
    showWarning: function(message) {
        this.showAlert(message, 'warning');
    },
    
    showInfo: function(message) {
        this.showAlert(message, 'info');
    },
    
    // Créer un conteneur d'alertes s'il n'existe pas
    createAlertContainer: function() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    },
    
    // Validation de formulaire
    validateForm: function(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },
    
    // Formatage des nombres
    formatNumber: function(number, decimals = 2) {
        return new Intl.NumberFormat('fr-FR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    },
    
    // Formatage des dates
    formatDate: function(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    },
    
    // Requêtes AJAX
    ajax: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('Erreur AJAX:', error);
                this.handleNetworkError(error);
                throw error;
            });
    },
    
    // Obtenir le token CSRF
    getCSRFToken: function() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    },
    
    // Gestion des erreurs réseau
    handleNetworkError: function(error) {
        this.showError('Erreur de connexion. Veuillez réessayer.');
    },
    
    // Gestion des erreurs serveur
    handleServerError: function(error) {
        this.showError('Erreur serveur. Veuillez contacter l\'administrateur.');
    },
    
    // Chargement d'image avec fallback
    loadImage: function(imgElement, src, fallbackSrc) {
        imgElement.onerror = function() {
            this.src = fallbackSrc;
            this.onerror = null;
        };
        imgElement.src = src;
    },
    
    // Debounce pour les fonctions
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle pour les fonctions
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    BeautyScan.init();
});

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BeautyScan;
}
