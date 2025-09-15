/**
 * Product analysis functionality for AI routines.
 * 
 * Handles form submission and result display for product analysis.
 */

(function() {
    'use strict';
    
    /**
     * Initialize product analysis functionality.
     */
    function init() {
        const form = document.getElementById('product-analysis-form');
        const submitBtn = document.getElementById('submit-btn');
        const resultContainer = document.getElementById('result-container');
        
        if (!form || !submitBtn || !resultContainer) {
            console.error('Required elements not found');
            return;
        }
        
        // Add form submit handler
        form.addEventListener('submit', handleFormSubmit);
        
        console.log('Product analysis initialized');
    }
    
    /**
     * Handle form submission.
     * 
     * @param {Event} e - Form submit event
     */
    function handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = document.getElementById('submit-btn');
        const resultContainer = document.getElementById('result-container');
        
        // Show loading state
        showLoadingState(submitBtn, resultContainer);
        
        // Prepare form data
        const formData = prepareFormData(form);
        
        // Submit analysis request
        submitAnalysisRequest(formData)
            .then(response => {
                displayAnalysisResult(response, resultContainer);
            })
            .catch(error => {
                displayError(error, resultContainer);
            })
            .finally(() => {
                resetSubmitButton(submitBtn);
            });
    }
    
    /**
     * Show loading state.
     * 
     * @param {HTMLElement} submitBtn - Submit button element
     * @param {HTMLElement} resultContainer - Result container element
     */
    function showLoadingState(submitBtn, resultContainer) {
        // Disable submit button and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyse en cours...';
        
        // Show loading in result container
        resultContainer.innerHTML = `
            <div class="text-center">
                <i class="fas fa-spinner fa-spin fa-2x text-success mb-3"></i>
                <p>Analyse de votre produit en cours...</p>
            </div>
        `;
    }
    
    /**
     * Prepare form data for submission.
     * 
     * @param {HTMLFormElement} form - Form element
     * @returns {FormData} Form data
     */
    function prepareFormData(form) {
        const formData = new FormData(form);
        
        // Add CSRF token if available
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }
        
        return formData;
    }
    
    /**
     * Submit analysis request.
     * 
     * @param {FormData} formData - Form data
     * @returns {Promise} Analysis response
     */
    function submitAnalysisRequest(formData) {
        return fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
    }
    
    /**
     * Display analysis result.
     * 
     * @param {Object} response - Analysis response
     * @param {HTMLElement} resultContainer - Result container element
     */
    function displayAnalysisResult(response, resultContainer) {
        if (response.success) {
            resultContainer.innerHTML = createResultHTML(response.data);
        } else {
            displayError(response.error || 'Erreur lors de l\'analyse', resultContainer);
        }
    }
    
    /**
     * Create result HTML.
     * 
     * @param {Object} data - Analysis data
     * @returns {string} HTML string
     */
    function createResultHTML(data) {
        const analysis = data.analysis || {};
        const recommendations = data.recommendations || [];
        
        return `
            <div class="analysis-result">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-chart-line"></i> Score de Sécurité
                                </h6>
                            </div>
                            <div class="card-body text-center">
                                <div class="score-display">
                                    <span class="score-value ${getScoreClass(analysis.score)}">${analysis.score || 'N/A'}</span>
                                    <div class="score-label">/ 10</div>
                                </div>
                                <div class="risk-level mt-2">
                                    <span class="badge ${getRiskLevelClass(analysis.risk_level)}">
                                        ${getRiskLevelText(analysis.risk_level)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-exclamation-triangle"></i> Ingrédients à Risque
                                </h6>
                            </div>
                            <div class="card-body">
                                ${createRiskIngredientsHTML(analysis.risk_ingredients || [])}
                            </div>
                        </div>
                    </div>
                </div>
                
                ${recommendations.length > 0 ? createRecommendationsHTML(recommendations) : ''}
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-info-circle"></i> Analyse Détaillée
                        </h6>
                    </div>
                    <div class="card-body">
                        <p>${analysis.detailed_analysis || 'Aucune analyse détaillée disponible.'}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create risk ingredients HTML.
     * 
     * @param {Array} riskIngredients - Risk ingredients list
     * @returns {string} HTML string
     */
    function createRiskIngredientsHTML(riskIngredients) {
        if (riskIngredients.length === 0) {
            return '<p class="text-success mb-0"><i class="fas fa-check-circle"></i> Aucun ingrédient à risque détecté</p>';
        }
        
        return `
            <ul class="list-unstyled mb-0">
                ${riskIngredients.map(ingredient => `
                    <li class="mb-1">
                        <span class="badge ${getIngredientRiskClass(ingredient.risk_level)} me-2">
                            ${ingredient.risk_level}
                        </span>
                        ${ingredient.name}
                    </li>
                `).join('')}
            </ul>
        `;
    }
    
    /**
     * Create recommendations HTML.
     * 
     * @param {Array} recommendations - Recommendations list
     * @returns {string} HTML string
     */
    function createRecommendationsHTML(recommendations) {
        return `
            <div class="card mt-3">
                <div class="card-header">
                    <h6 class="mb-0">
                        <i class="fas fa-lightbulb"></i> Recommandations
                    </h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
                        ${recommendations.map(rec => `
                            <li class="mb-2">
                                <i class="fas fa-arrow-right text-primary me-2"></i>
                                ${rec}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    /**
     * Display error message.
     * 
     * @param {string} error - Error message
     * @param {HTMLElement} resultContainer - Result container element
     */
    function displayError(error, resultContainer) {
        resultContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Erreur:</strong> ${error}
            </div>
        `;
    }
    
    /**
     * Reset submit button.
     * 
     * @param {HTMLElement} submitBtn - Submit button element
     */
    function resetSubmitButton(submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-search"></i> Analyser';
    }
    
    /**
     * Get score CSS class.
     * 
     * @param {number} score - Score value
     * @returns {string} CSS class
     */
    function getScoreClass(score) {
        if (score >= 8) return 'text-success';
        if (score >= 6) return 'text-warning';
        return 'text-danger';
    }
    
    /**
     * Get risk level CSS class.
     * 
     * @param {string} riskLevel - Risk level
     * @returns {string} CSS class
     */
    function getRiskLevelClass(riskLevel) {
        const classes = {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger',
            'unknown': 'bg-secondary'
        };
        return classes[riskLevel] || 'bg-secondary';
    }
    
    /**
     * Get risk level text.
     * 
     * @param {string} riskLevel - Risk level
     * @returns {string} Risk level text
     */
    function getRiskLevelText(riskLevel) {
        const texts = {
            'low': 'Faible Risque',
            'medium': 'Risque Moyen',
            'high': 'Risque Élevé',
            'unknown': 'Risque Inconnu'
        };
        return texts[riskLevel] || 'Risque Inconnu';
    }
    
    /**
     * Get ingredient risk CSS class.
     * 
     * @param {string} riskLevel - Risk level
     * @returns {string} CSS class
     */
    function getIngredientRiskClass(riskLevel) {
        const classes = {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger'
        };
        return classes[riskLevel] || 'bg-secondary';
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
