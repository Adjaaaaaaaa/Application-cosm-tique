/**
 * Beauty Assistant JavaScript functionality
 * 
 * This module handles all client-side interactions for the beauty assistant,
 * including form submission, API calls, and dynamic content rendering.
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Mise à jour de l'affichage du budget
    const budgetSlider = document.getElementById('budget');
    const budgetValue = document.getElementById('budget-value');
    
    if (budgetSlider && budgetValue) {
        budgetSlider.addEventListener('input', function() {
            budgetValue.textContent = this.value + '€';
        });
    }

    // Gestion du formulaire
    const form = document.getElementById('beauty-assistant-form');
    const submitBtn = document.getElementById('submit-btn');
    const resultContainer = document.getElementById('result-container');
    const routineTypeSelect = document.getElementById('routine_type');
    const questionTextarea = document.getElementById('question');

    if (!form || !submitBtn || !resultContainer) {
        console.error('Required form elements not found');
        return;
    }

    // Adapter le placeholder et la validation selon le type
    if (routineTypeSelect && questionTextarea) {
        routineTypeSelect.addEventListener('change', function() {
            const value = routineTypeSelect.value;
            if (value === 'ingredients') {
                questionTextarea.placeholder = "Entrez le nom de l'ingrédient (ex: zinc, niacinamide, rétinol)";
            } else {
                questionTextarea.placeholder = "Ex: J'ai la peau sensible, que me recommandez-vous ?";
            }
        });
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Afficher le loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Envoi en cours...';
        
        resultContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border mb-3" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <p class="lead text-brown-medium">Génération de votre réponse personnalisée...</p>
            </div>
        `;

        // Préparer les données
        const formData = new FormData(form);
        const routineType = formData.get('routine_type');
        const userQuestion = formData.get('question');
        
        // Validation : au moins une question ou un type de routine
        if (!routineType && !userQuestion) {
            displayError('Veuillez poser une question ou sélectionner un type de routine');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Envoyer';
            return;
        }

        // Si l'utilisateur a choisi Analyse d'ingrédient, la question (nom de l'ingrédient) est obligatoire
        if (routineType === 'ingredients' && (!userQuestion || userQuestion.trim().length === 0)) {
            displayError("Veuillez saisir le nom de l'ingrédient dans 'Votre question'");
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Envoyer';
            return;
        }
        
        const data = {
            user_id: window.userId || null,
            routine_type: routineType || 'general',
            user_question: userQuestion || "Je veux des conseils beauté personnalisés",
            budget: parseInt(formData.get('budget')),
            product_ingredients: null
        };

        // Appeler l'API
        fetch('/api/v1/enhanced-ai/comprehensive-routine/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayRoutine(data.data);
            } else {
                displayError(data.message || 'Erreur lors de la génération');
            }
        })
        .catch(error => {
            console.error('API Error:', error);
            displayError('Erreur de connexion au serveur');
        })
        .finally(() => {
            // Réactiver le bouton
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Envoyer';
        });
    });
});

/**
 * Display routine results in the result container
 * @param {Object} routine - The routine data from the API
 */
function displayRoutine(routine) {
    const resultContainer = document.getElementById('result-container');
    
    // Extraire les données de la routine depuis la structure de réponse
    const aiRoutine = routine.ai_routine || routine;
    const steps = aiRoutine.steps || [];
    const tips = aiRoutine.tips || [];
    const faq = aiRoutine.faq || [];
    const ingredientInfo = aiRoutine.ingredient_info || null;
    const personalizedAdvice = aiRoutine.personalized_advice || null;
    
    // Pour les questions générales
    const answer = aiRoutine.answer || aiRoutine["réponse"] || aiRoutine["reponse"] || routine.answer || routine["réponse"] || routine["reponse"] || null;
    const personalizedAdviceGeneral = aiRoutine.personalized_advice || null;
    const recommendations = aiRoutine.recommendations || [];
    const warnings = aiRoutine.warnings || [];
    const nextSteps = aiRoutine.next_steps || [];
    const routineSuggestions = aiRoutine.routine_suggestions || null;
    
    // Traduction FR pour certaines valeurs de profil
    const translateValueFr = (val) => {
        if (!val) return val;
        const v = String(val).toLowerCase();
        const map = {
            // Types de peau
            'normal': 'normale',
            'dry': 'sèche',
            'oily': 'grasse',
            'combination': 'mixte',
            'sensitive': 'sensible',
            // Préoccupations
            'aging': 'vieillissement',
            'acne': 'acné',
            'dryness': 'sécheresse',
            'oiliness': 'excès de sébum',
            'sensitivity': 'sensibilité',
            'hyperpigmentation': 'taches pigmentaires',
            'dark spots': 'taches pigmentaires',
            'texture': 'texture irrégulière',
            'pores': 'pores dilatés',
            'redness': 'rougeurs',
            'scars': 'cicatrices',
            // Allergies courantes
            'fragrance': 'parfum',
            // Pathologies
            'eczema': 'eczéma',
            'psoriasis': 'psoriasis',
            'rosacea': 'rosacée'
        };
        return map[v] || val;
    };
    const translateListFr = (arr) => (arr || []).map(translateValueFr);
    
    let stepsHtml = '';
    if (steps && steps.length > 0) {
        stepsHtml = `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-list-ol me-2 text-sand-dark"></i>Étapes de votre routine
                </h5>
                ${steps.map((step, index) => `
                    <div class="card mb-3 border-0 shadow-sm">
                        <div class="card-body">
                            <h6 class="card-title text-sand-dark fw-semibold">
                                Étape ${index + 1}: ${step.step || step.name || 'Étape'}
                            </h6>
                            ${step.produit || step.product_type || step.product ? `
                                <p class="card-text fw-semibold text-brown-dark mb-2">
                                    ${step.produit || step.product_type || step.product}
                                    ${step.marque ? ` - ${step.marque}` : ''}
                                </p>
                            ` : ''}
                            <p class="card-text text-brown-medium mb-2">
                                ${step.explication || step.details || step.description || ''}
                            </p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="text-brown-medium">
                                    <i class="fas fa-clock me-1"></i>${step.duration || step.fréquence || 'N/A'}
                                </span>
                                <span class="badge bg-primary fs-6">${step.budget || step.prix || 'N/A'}${step.budget || step.prix ? '€' : ''}</span>
                            </div>
                            ${step.recommended_products && step.recommended_products.length > 0 ? `
                                <div class="mt-2">
                                    <small class="text-brown-medium">
                                        <i class="fas fa-star me-1 text-sand-dark"></i>
                                        <strong>Produits recommandés :</strong> ${step.recommended_products.join(', ')}
                                    </small>
                                </div>
                            ` : ''}
                            ${step.tips ? `
                                <div class="mt-3 p-3 bg-beige-medium rounded">
                                    <small class="text-brown-medium">
                                        <i class="fas fa-lightbulb me-1 text-sand-dark"></i>
                                        <strong>Conseils :</strong> ${step.tips}
                                    </small>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    let tipsHtml = '';
    if (tips && tips.length > 0) {
        tipsHtml = `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-lightbulb me-2 text-sand-dark"></i>Conseils généraux
                </h5>
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            ${tips.map(tip => `
                                <li class="mb-2">
                                    <i class="fas fa-check-circle text-brown-light me-2"></i>${tip}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    let faqHtml = '';
    if (faq && faq.length > 0) {
        faqHtml = `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-question-circle me-2 text-brown-medium"></i>Questions fréquentes
                </h5>
                <div class="accordion" id="faqAccordion">
                    ${faq.map((item, index) => `
                        <div class="accordion-item border-0 shadow-sm mb-2">
                            <h2 class="accordion-header" id="faq${index}">
                                <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#faqCollapse${index}">
                                    ${item.question}
                                </button>
                            </h2>
                            <div id="faqCollapse${index}" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                <div class="accordion-body text-brown-medium">
                                    ${item.answer}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Afficher un résumé du profil utilisateur dans la réponse (uniquement pour routines)
    let profileSummaryHtml = '';
    if (routine.user_profile && !( (routine.type === 'general_response') || ((!steps || steps.length === 0) && !!answer && !ingredientInfo) ) ) {
        const profile = routine.user_profile;
        const skinTypeFr = translateValueFr(profile.skin_type || '');
        const concernsFr = translateListFr(profile.skin_concerns || []);
        const allergiesFr = translateListFr(profile.allergies || []);
        const conditionsFr = translateListFr(profile.dermatological_conditions || []);
        profileSummaryHtml = `
            <div class="alert alert-info border-0 shadow-sm mb-4">
                <h6 class="fw-semibold mb-3 text-brown-dark">
                    <i class="fas fa-user-check me-2"></i>Réponse adaptée à votre profil
                </h6>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-birthday-cake text-sand-dark me-2"></i>
                            <small class="fw-semibold text-brown-dark">Âge: ${profile.age_range || 'Non spécifié'} | Type de peau: ${skinTypeFr || 'Non spécifié'}</small>
                        </div>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-exclamation-triangle text-sand-dark me-2"></i>
                            <small class="fw-semibold text-brown-dark">Problèmes: ${concernsFr && concernsFr.length > 0 ? concernsFr.join(', ') : 'Aucun'}</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-allergies text-brown-medium me-2"></i>
                            <small class="fw-semibold text-brown-dark">Allergies: ${allergiesFr && allergiesFr.length > 0 ? allergiesFr.join(', ') : 'Aucune'}</small>
                        </div>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-heartbeat text-brown-medium me-2"></i>
                            <small class="fw-semibold text-brown-dark">Pathologies: ${conditionsFr && conditionsFr.length > 0 ? conditionsFr.join(', ') : 'Aucune'}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Détection d'une réponse générale
    const isGeneralQuestion = (routine.type === 'general_response') || ((!steps || steps.length === 0) && !!answer && !ingredientInfo);

    // Calcul des métriques disponibles
    const computedStepsBudget = (steps && steps.length > 0) ? steps.reduce((sum, step) => sum + (step.budget || step.prix || 0), 0) : 0;
    const hasBudget = Boolean(aiRoutine.total_budget) || computedStepsBudget > 0;
    const hasDuration = Boolean(aiRoutine.total_duration);
    const hasTolerance = Boolean(aiRoutine.average_tolerance_score);
    const hasTypeMetric = Boolean(aiRoutine.routine_type) && !isGeneralQuestion;
    const hasAnyMetric = hasBudget || hasDuration || hasTolerance || hasTypeMetric;

    // Bloc métriques conditionnel (on n'affiche rien si aucune donnée)
    const metricsHtml = hasAnyMetric ? `
        <div class="row g-3 mb-4">
            ${hasBudget ? `
            <div class="col-md-3 col-6">
                <div class="card border-0 shadow-sm text-center">
                    <div class="card-body py-3">
                        <div class="text-sand-dark fw-bold fs-5">${aiRoutine.total_budget || computedStepsBudget}€</div>
                        <small class="text-brown-medium">Budget total</small>
                    </div>
                </div>
            </div>` : ''}

            ${hasTypeMetric ? `
            <div class="col-md-3 col-6">
                <div class="card border-0 shadow-sm text-center">
                    <div class="card-body py-3">
                        <div class="text-brown-light fw-bold fs-5">${aiRoutine.routine_type}</div>
                        <small class="text-brown-medium">Type</small>
                    </div>
                </div>
            </div>` : ''}

            ${hasDuration ? `
            <div class="col-md-3 col-6">
                <div class="card border-0 shadow-sm text-center">
                    <div class="card-body py-3">
                        <div class="text-brown-medium fw-bold fs-5">${aiRoutine.total_duration}</div>
                        <small class="text-brown-medium">Durée totale</small>
                    </div>
                </div>
            </div>` : ''}

            ${hasTolerance ? `
            <div class="col-md-3 col-6">
                <div class="card border-0 shadow-sm text-center">
                    <div class="card-body py-3">
                        <div class="text-sand-dark fw-bold fs-5">${aiRoutine.average_tolerance_score}</div>
                        <small class="text-brown-medium">Score tolérance</small>
                    </div>
                </div>
            </div>` : ''}
        </div>
    ` : '';

    // Bloc de réponse directe pour questions générales
    const generalAnswerHtml = (isGeneralQuestion && answer) ? `
        <div class="mt-2">
            <div class="card border-0 shadow-sm mb-3">
                <div class="card-body">
                    <p class="card-text text-brown-medium">${answer}</p>
                </div>
            </div>
        </div>
    ` : '';

    resultContainer.innerHTML = `
        ${profileSummaryHtml}
        <div class="mb-4">
            <h4 class="fw-bold text-brown-dark mb-3">${isGeneralQuestion ? 'Réponse adaptée à votre profil' : (aiRoutine.routine_name || aiRoutine.title || 'Routine Personnalisée')}</h4>
            ${isGeneralQuestion ? '' : `<p class="text-brown-medium lead">${aiRoutine.description || ''}</p>`}
        </div>
        ${generalAnswerHtml}
        ${metricsHtml}
        ${ingredientInfo ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-info-circle me-2 text-sand-dark"></i>Informations sur l'ingrédient
                </h5>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Qu'est-ce que c'est ?</h6>
                        <p class="card-text text-brown-medium">${ingredientInfo.what_is_it || 'Information non disponible'}</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Comment ça fonctionne ?</h6>
                        <p class="card-text text-brown-medium">${ingredientInfo.how_it_works || 'Information non disponible'}</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Utilisations courantes</h6>
                        <p class="card-text text-brown-medium">${ingredientInfo.common_uses || 'Information non disponible'}</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Concentrations recommandées</h6>
                        <p class="card-text text-brown-medium">${ingredientInfo.concentrations || 'Information non disponible'}</p>
                    </div>
                </div>
            </div>
        ` : ''}
        ${personalizedAdvice ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-user-md me-2 text-sand-dark"></i>Conseils personnalisés pour vous
                </h5>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Sécurité pour votre profil</h6>
                        <p class="card-text text-brown-medium">${personalizedAdvice.safety_for_you || 'Analyse non disponible'}</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Bénéfices pour vous</h6>
                        <p class="card-text text-brown-medium">${personalizedAdvice.benefits_for_you || 'Information non disponible'}</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Comment l'utiliser</h6>
                        <p class="card-text text-brown-medium">${personalizedAdvice.how_to_use || 'Conseils non disponibles'}</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-sand-dark fw-semibold">Fréquence recommandée</h6>
                        <p class="card-text text-brown-medium">${personalizedAdvice.frequency || 'Information non disponible'}</p>
                    </div>
                </div>
            </div>
        ` : ''}
        ${warnings && warnings.length > 0 ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-exclamation-triangle me-2 text-sand-dark"></i>Avertissements importants
                </h5>
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            ${warnings.map(warning => `
                                <li class="mb-2 text-brown-medium">${warning}</li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        ` : ''}
        ${(!isGeneralQuestion && answer) ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-comment-dots me-2 text-sand-dark"></i>Réponse personnalisée
                </h5>
                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <p class="card-text text-brown-medium">${answer}</p>
                    </div>
                </div>
            </div>
        ` : ''}
        ${personalizedAdviceGeneral ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-user-md me-2 text-sand-dark"></i>Conseils pratiques
                </h5>
                <div class="row">
                    ${personalizedAdviceGeneral.skin_type_advice ? `
                        <div class="col-md-6 mb-3">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h6 class="card-title text-sand-dark fw-semibold">Conseils pour votre type de peau</h6>
                                    <p class="card-text text-brown-medium">${personalizedAdviceGeneral.skin_type_advice}</p>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    ${personalizedAdviceGeneral.age_advice ? `
                        <div class="col-md-6 mb-3">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h6 class="card-title text-sand-dark fw-semibold">Conseils adaptés à votre âge</h6>
                                    <p class="card-text text-brown-medium">${personalizedAdviceGeneral.age_advice}</p>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    ${personalizedAdviceGeneral.condition_advice ? `
                        <div class="col-12 mb-3">
                            <div class="card border-0 shadow-sm">
                                <div class="card-body">
                                    <h6 class="card-title text-sand-dark fw-semibold">Conseils pour vos conditions</h6>
                                    <p class="card-text text-brown-medium">${personalizedAdviceGeneral.condition_advice}</p>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
                ${personalizedAdviceGeneral.allergy_warnings && personalizedAdviceGeneral.allergy_warnings.length > 0 ? `
                    <div class="card border-0 shadow-sm mb-3">
                        <div class="card-body">
                            <h6 class="card-title text-sand-dark fw-semibold">⚠️ Avertissements allergies</h6>
                            <ul class="list-unstyled mb-0">
                                ${personalizedAdviceGeneral.allergy_warnings.map(warning => `
                                    <li class="mb-2 text-brown-medium">${warning}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                ` : ''}
                ${personalizedAdviceGeneral.practical_tips && personalizedAdviceGeneral.practical_tips.length > 0 ? `
                    <div class="card border-0 shadow-sm mb-3">
                        <div class="card-body">
                            <h6 class="card-title text-sand-dark fw-semibold">💡 Conseils pratiques</h6>
                            <ul class="list-unstyled mb-0">
                                ${personalizedAdviceGeneral.practical_tips.map(tip => `
                                    <li class="mb-2 text-brown-medium">${tip}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                ` : ''}
            </div>
        ` : ''}
        ${recommendations && recommendations.length > 0 ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-star me-2 text-sand-dark"></i>Recommandations personnalisées
                </h5>
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            ${recommendations.map((rec, index) => `
                                <li class="mb-3">
                                    <div class="d-flex align-items-start">
                                        <span class="badge bg-primary me-3 mt-1">${index + 1}</span>
                                        <div class="flex-grow-1">
                                            <p class="card-text text-brown-medium mb-2">${typeof rec === 'string' ? rec : (rec.suggestion || rec.category || rec)}</p>
                                            ${rec.reason ? `<p class="card-text text-brown-medium mb-2"><strong>Pourquoi :</strong> ${rec.reason}</p>` : ''}
                                            ${rec.brand_examples && rec.brand_examples.length > 0 ? `
                                                <p class="card-text text-brown-medium mb-2">
                                                    <strong>Marques recommandées :</strong> ${rec.brand_examples.join(', ')}
                                                </p>
                                            ` : ''}
                                            ${rec.ingredients_to_look_for && rec.ingredients_to_look_for.length > 0 ? `
                                                <p class="card-text text-brown-medium mb-2">
                                                    <strong>Ingrédients à privilégier :</strong> ${rec.ingredients_to_look_for.join(', ')}
                                                </p>
                                            ` : ''}
                                            ${rec.ingredients_to_avoid && rec.ingredients_to_avoid.length > 0 ? `
                                                <p class="card-text text-brown-medium mb-2">
                                                    <strong>Ingrédients à éviter :</strong> ${rec.ingredients_to_avoid.join(', ')}
                                                </p>
                                            ` : ''}
                                        </div>
                                    </div>
                                    ${index < recommendations.length - 1 ? '<hr class="my-3">' : ''}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        ` : ''}
        ${nextSteps && nextSteps.length > 0 ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-arrow-right me-2 text-sand-dark"></i>Prochaines étapes
                </h5>
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            ${nextSteps.map(step => `
                                <li class="mb-2 text-brown-medium">${step}</li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        ` : ''}
        ${routineSuggestions ? `
            <div class="mt-4">
                <h5 class="fw-semibold text-brown-dark mb-3">
                    <i class="fas fa-clock me-2 text-sand-dark"></i>Suggestions de routine
                </h5>
                <div class="row">
                    ${routineSuggestions.morning && routineSuggestions.morning.length > 0 ? `
                        <div class="col-md-4 mb-3">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h6 class="card-title text-sand-dark fw-semibold">🌅 Matin</h6>
                                    <ul class="list-unstyled mb-0">
                                        ${routineSuggestions.morning.map(step => `
                                            <li class="mb-1 text-brown-medium">${step}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    ${routineSuggestions.evening && routineSuggestions.evening.length > 0 ? `
                        <div class="col-md-4 mb-3">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h6 class="card-title text-sand-dark fw-semibold">🌙 Soir</h6>
                                    <ul class="list-unstyled mb-0">
                                        ${routineSuggestions.evening.map(step => `
                                            <li class="mb-1 text-brown-medium">${step}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    ${routineSuggestions.weekly && routineSuggestions.weekly.length > 0 ? `
                        <div class="col-md-4 mb-3">
                            <div class="card border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h6 class="card-title text-sand-dark fw-semibold">📅 Hebdomadaire</h6>
                                    <ul class="list-unstyled mb-0">
                                        ${routineSuggestions.weekly.map(step => `
                                            <li class="mb-1 text-brown-medium">${step}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        ` : ''}
        ${stepsHtml}
        ${tipsHtml}
        ${faqHtml}
    `;

    // Mettre en évidence l'effet correspondant au type de peau de l'utilisateur
    try {
        const skinType = (routine.user_profile && routine.user_profile.skin_type) || (aiRoutine.user_profile && aiRoutine.user_profile.skin_type);
        if (skinType) {
            const item = resultContainer.querySelector(`li[data-skin-type="${String(skinType).toLowerCase()}"]`);
            if (item) {
                item.style.fontWeight = '600';
                item.style.background = '#f4f1e8';
                item.style.borderRadius = '6px';
                item.style.padding = '2px 6px';
            }
        }
    } catch (e) {
        // ignore highlighting errors
    }
}

/**
 * Display error message in the result container
 * @param {string} message - The error message to display
 */
function displayError(message) {
    const resultContainer = document.getElementById('result-container');
    resultContainer.innerHTML = `
        <div class="alert alert-danger border-0 shadow-sm">
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-triangle text-brown-medium me-3 fs-4"></i>
                <div>
                    <h6 class="fw-semibold mb-1 text-brown-dark">Erreur</h6>
                    <p class="mb-0 text-brown-dark">${message}</p>
                </div>
            </div>
        </div>
    `;
}