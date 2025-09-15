/**
 * Scan analysis functionality.
 * 
 * Handles chart rendering and modal interactions for scan analysis.
 */

(function() {
    'use strict';
    
    let riskChart = null;
    
    /**
     * Initialize risk distribution chart.
     */
    function initializeRiskChart() {
        const ctx = document.getElementById('riskChart');
        if (!ctx) return;
        
        // Get data from the page
        const analysisData = window.analysisData || {};
        const riskDistribution = analysisData.risk_distribution || { low: 0, medium: 0, high: 0 };
        
        riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Faible Risque', 'Risque Moyen', 'Risque Élevé'],
                datasets: [{
                    data: [riskDistribution.low, riskDistribution.medium, riskDistribution.high],
                    backgroundColor: [
                        '#28a745', // Green for low risk
                        '#ffc107', // Yellow for medium risk
                        '#dc3545'  // Red for high risk
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                return `${label}: ${value} ingrédient${value > 1 ? 's' : ''} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Show H-code details in modal.
     * 
     * @param {string} ingredientName - Name of the ingredient
     * @param {string} categoryName - Name of the category
     * @param {Object} categoryInfo - Category information
     */
    function showHCodeDetails(ingredientName, categoryName, categoryInfo) {
        // Update modal title
        document.getElementById('ingredientName').textContent = ingredientName;
        
        // Update category badge
        const categoryBadge = document.getElementById('categoryName');
        categoryBadge.textContent = categoryName;
        categoryBadge.className = 'badge bg-' + getCategoryColor(categoryInfo.color);
        
        // Update H-code details
        const detailsContainer = document.getElementById('hCodeDetails');
        detailsContainer.innerHTML = '';
        
        if (categoryInfo.details && categoryInfo.details.length > 0) {
            categoryInfo.details.forEach(detail => {
                const detailCard = createDetailCard(detail);
                detailsContainer.appendChild(detailCard);
            });
        } else {
            const noDetailsCard = createNoDetailsCard();
            detailsContainer.appendChild(noDetailsCard);
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('hCodeModal'));
        modal.show();
    }
    
    /**
     * Get Bootstrap color class for category.
     * 
     * @param {string} color - Color name
     * @returns {string} Bootstrap color class
     */
    function getCategoryColor(color) {
        switch (color) {
            case 'red': return 'danger';
            case 'orange': return 'warning';
            case 'green': return 'success';
            default: return 'secondary';
        }
    }
    
    /**
     * Create detail card for H-code information.
     * 
     * @param {Object} detail - Detail information
     * @returns {HTMLElement} Detail card element
     */
    function createDetailCard(detail) {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        
        card.innerHTML = `
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <h6 class="text-muted">Code H</h6>
                        <span class="badge bg-primary">${detail.h_code || 'N/A'}</span>
                    </div>
                    <div class="col-md-9">
                        <h6 class="text-muted">Description</h6>
                        <p class="mb-0">${detail.description || 'Aucune description disponible'}</p>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    /**
     * Create no details card.
     * 
     * @returns {HTMLElement} No details card element
     */
    function createNoDetailsCard() {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        
        card.innerHTML = `
            <div class="card-body text-center text-muted">
                <i class="fas fa-info-circle fa-2x mb-2"></i>
                <p class="mb-0">Aucun détail disponible pour cette catégorie</p>
            </div>
        `;
        
        return card;
    }
    
    /**
     * Initialize ingredient analysis interactions.
     */
    function initializeIngredientAnalysis() {
        // Add click handlers to ingredient cards
        const ingredientCards = document.querySelectorAll('.ingredient-card');
        ingredientCards.forEach(card => {
            card.addEventListener('click', function() {
                const ingredientName = this.dataset.ingredient;
                const categoryName = this.dataset.category;
                const categoryInfo = JSON.parse(this.dataset.categoryInfo || '{}');
                
                showHCodeDetails(ingredientName, categoryName, categoryInfo);
            });
        });
        
        // Add hover effects
        ingredientCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.cursor = 'pointer';
                this.style.transform = 'translateY(-2px)';
                this.style.transition = 'transform 0.2s ease';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }
    
    /**
     * Initialize analysis summary.
     */
    function initializeAnalysisSummary() {
        const analysisData = window.analysisData || {};
        const enhancedAnalysis = analysisData.enhanced_analysis || {};
        
        // Update summary statistics
        updateSummaryStatistics(analysisData);
        
        // Update risk indicators
        updateRiskIndicators(enhancedAnalysis);
    }
    
    /**
     * Update summary statistics.
     * 
     * @param {Object} analysisData - Analysis data
     */
    function updateSummaryStatistics(analysisData) {
        const totalIngredients = analysisData.total_ingredients || 0;
        const riskDistribution = analysisData.risk_distribution || { low: 0, medium: 0, high: 0 };
        
        // Update total ingredients
        const totalElement = document.getElementById('total-ingredients');
        if (totalElement) {
            totalElement.textContent = totalIngredients;
        }
        
        // Update risk counts
        const lowRiskElement = document.getElementById('low-risk-count');
        if (lowRiskElement) {
            lowRiskElement.textContent = riskDistribution.low;
        }
        
        const mediumRiskElement = document.getElementById('medium-risk-count');
        if (mediumRiskElement) {
            mediumRiskElement.textContent = riskDistribution.medium;
        }
        
        const highRiskElement = document.getElementById('high-risk-count');
        if (highRiskElement) {
            highRiskElement.textContent = riskDistribution.high;
        }
    }
    
    /**
     * Update risk indicators.
     * 
     * @param {Object} enhancedAnalysis - Enhanced analysis data
     */
    function updateRiskIndicators(enhancedAnalysis) {
        const overallScore = enhancedAnalysis.overall_score || 0;
        const riskLevel = enhancedAnalysis.overall_risk_level || 'unknown';
        
        // Update overall score
        const scoreElement = document.getElementById('overall-score');
        if (scoreElement) {
            scoreElement.textContent = overallScore.toFixed(1);
            scoreElement.className = 'badge ' + getScoreBadgeClass(overallScore);
        }
        
        // Update risk level
        const riskElement = document.getElementById('risk-level');
        if (riskElement) {
            riskElement.textContent = getRiskLevelText(riskLevel);
            riskElement.className = 'badge ' + getRiskLevelBadgeClass(riskLevel);
        }
    }
    
    /**
     * Get score badge class.
     * 
     * @param {number} score - Score value
     * @returns {string} Badge class
     */
    function getScoreBadgeClass(score) {
        if (score >= 8) return 'bg-success';
        if (score >= 6) return 'bg-warning';
        return 'bg-danger';
    }
    
    /**
     * Get risk level text.
     * 
     * @param {string} riskLevel - Risk level
     * @returns {string} Risk level text
     */
    function getRiskLevelText(riskLevel) {
        const riskTexts = {
            'low': 'Faible',
            'medium': 'Moyen',
            'high': 'Élevé',
            'unknown': 'Inconnu'
        };
        return riskTexts[riskLevel] || 'Inconnu';
    }
    
    /**
     * Get risk level badge class.
     * 
     * @param {string} riskLevel - Risk level
     * @returns {string} Badge class
     */
    function getRiskLevelBadgeClass(riskLevel) {
        const riskClasses = {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger',
            'unknown': 'bg-secondary'
        };
        return riskClasses[riskLevel] || 'bg-secondary';
    }
    
    /**
     * Initialize all functionality.
     */
    function init() {
        // Wait for Chart.js to be available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return;
        }
        
        // Initialize components
        initializeRiskChart();
        initializeIngredientAnalysis();
        initializeAnalysisSummary();
        
        console.log('Scan analysis initialized');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Make functions globally available
    window.showHCodeDetails = showHCodeDetails;
    
})();
