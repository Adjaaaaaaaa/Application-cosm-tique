"""
Premium Service for BeautyScan - Enhanced skincare recommendations with personalized routines.

This module implements the complete Premium AI service following the specified architecture:
[Utilisateur Premium] → [Interface IA Beauté] → [Frontend → Backend Django] → [Backend IA Service]
→ [Construction Contexte IA] → [LLM Beauté Personnalisé] → [Sortie JSON formatée] → [Frontend IA UX]
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, Allergy
from apps.scans.models import Scan


logger = logging.getLogger(__name__)


class PremiumAIService:
    """
    Enhanced AI service for Premium users providing personalized skincare assistance.
    
    This service implements the complete Premium workflow:
    - Questions suggérées (boutons) et champ question libre
    - Récupération du profil utilisateur complet
    - Construction du contexte IA avec données dermatologiques
    - Génération de routines personnalisées matin/soir
    - Analyse d'ingrédients avec RAG
    - Filtrage par budget en temps réel
    - Alertes de sécurité et allergies
    """
    
    def __init__(self):
        """Initialize the Premium AI service with required components."""

        # Questions suggérées selon le schéma
        self.suggested_questions = [
            "Routine visage matin",
            "Routine visage soir", 
            "Routine cheveux",
            "Routine corps",
            "Explication ingrédients",
            "Alternatives budget friendly"
        ]
        
        # Base de connaissances dermatologiques
        self.dermatological_knowledge = self._initialize_dermatological_knowledge()
        
        # Base de produits internes avec scores
        self.internal_product_database = self._initialize_product_database()
    
    def _initialize_dermatological_knowledge(self) -> Dict[str, Any]:
        """
        Initialize comprehensive dermatological knowledge base for RAG integration.
        
        Returns:
            Dict containing structured dermatological knowledge
        """
        return {
            'skin_types': {
                'dry': {
                    'characteristics': 'Manque d\'hydratation, tiraillements, desquamation',
                    'needs': ['Hydratation intense', 'Barrière lipidique', 'Ingrédients nourrissants', 'Céramides'],
                    'avoid': ['Alcools dénaturés', 'Ingrédients astringents', 'Nettoyants moussants', 'Exfoliants agressifs'],
                    'recommended_ingredients': ['Acide hyaluronique', 'Glycérine', 'Céramides', 'Huiles végétales', 'Beurre de karité'],
                    'routine_focus': 'Hydratation et réparation de la barrière cutanée'
                },
                'oily': {
                    'characteristics': 'Production excessive de sébum, brillance, pores dilatés',
                    'needs': ['Régulation du sébum', 'Nettoyage doux', 'Hydratation légère', 'Exfoliation chimique'],
                    'avoid': ['Huiles comédogènes', 'Ingrédients occlusifs', 'Nettoyants agressifs', 'Produits trop riches'],
                    'recommended_ingredients': ['Niacinamide', 'Acide salicylique', 'Zinc', 'Argile', 'Acide glycolique'],
                    'routine_focus': 'Contrôle du sébum et prévention des imperfections'
                },
                'sensitive': {
                    'characteristics': 'Réactivité, rougeurs, irritations, picotements',
                    'needs': ['Ingrédients apaisants', 'Formules minimalistes', 'Test patch obligatoire', 'Protection renforcée'],
                    'avoid': ['Parfums', 'Alcools', 'Actifs forts', 'Exfoliants mécaniques', 'Ingrédients irritants'],
                    'recommended_ingredients': ['Centella asiatica', 'Aloe vera', 'Panthenol', 'Acide hyaluronique', 'Thermal water'],
                    'routine_focus': 'Apaisement et renforcement de la barrière cutanée'
                },
                'combination': {
                    'characteristics': 'Zones sèches et grasses, T-zone brillante',
                    'needs': ['Équilibre hydratation', 'Produits adaptables', 'Zonage possible', 'Nettoyage équilibré'],
                    'avoid': ['Produits trop riches', 'Produits trop astringents', 'Formules uniformes'],
                    'recommended_ingredients': ['Niacinamide', 'Acide hyaluronique', 'Glycérine', 'Acide lactique'],
                    'routine_focus': 'Équilibre et harmonisation des différentes zones'
                },
                'normal': {
                    'characteristics': 'Équilibre naturel, peu de problèmes',
                    'needs': ['Maintien de l\'équilibre', 'Protection préventive', 'Hydratation modérée'],
                    'avoid': ['Produits trop agressifs', 'Surcharge de produits'],
                    'recommended_ingredients': ['Vitamine C', 'Antioxydants', 'Acide hyaluronique', 'Peptides'],
                    'routine_focus': 'Maintien et prévention'
                }
            },
            'age_concerns': {
                '20s': {
                    'focus': ['Protection solaire', 'Hydratation de base', 'Prévention', 'Antioxydants'],
                    'recommended_actives': ['Vitamine C', 'Niacinamide', 'Acide hyaluronique'],
                    'routine_structure': 'Nettoyant → Sérum → Hydratant → SPF'
                },
                '30s': {
                    'focus': ['Antioxydants', 'Rétinol débutant', 'Protection renforcée', 'Prévention rides'],
                    'recommended_actives': ['Rétinol', 'Vitamine C', 'Peptides', 'Acide hyaluronique'],
                    'routine_structure': 'Nettoyant → Sérum → Rétinol → Hydratant → SPF'
                },
                '40s': {
                    'focus': ['Peptides', 'Rétinol', 'Hydratation intense', 'Réparation'],
                    'recommended_actives': ['Rétinol', 'Peptides', 'Acide hyaluronique', 'Antioxydants'],
                    'routine_structure': 'Nettoyant → Sérum → Rétinol → Hydratant riche → SPF'
                },
                '50s+': {
                    'focus': ['Hydratation maximale', 'Actifs anti-âge', 'Soins réparateurs', 'Protection renforcée'],
                    'recommended_actives': ['Rétinol', 'Peptides', 'Acide hyaluronique', 'Antioxydants', 'Lipides'],
                    'routine_structure': 'Nettoyant doux → Sérum → Rétinol → Crème riche → SPF'
                }
            },
            'ingredient_safety': {
                'high_risk': ['Parabènes', 'Sulfates', 'Alcools dénaturés', 'Parfums synthétiques'],
                'moderate_risk': ['Rétinol', 'Acides de fruits', 'Vitamine C instable'],
                'safe': ['Acide hyaluronique', 'Glycérine', 'Niacinamide', 'Céramides', 'Panthenol'],
                'allergenic': ['Lanoline', 'Parfums', 'Conservateurs', 'Colorants']
            },
            'common_ingredients_info': {
                'acide hyaluronique': {
                    'description': 'Hydratant puissant qui retient l\'eau dans la peau',
                    'benefits': ['Hydratation intense', 'Anti-rides', 'Plénitude'],
                    'risks': ['Peut causer des irritations chez les peaux très sensibles'],
                    'best_for': ['Tous types de peau', 'Peau sèche', 'Anti-âge'],
                    'avoid_if': ['Allergie connue à l\'acide hyaluronique']
                },
                'rétinol': {
                    'description': 'Vitamine A dérivée, actif anti-âge puissant',
                    'benefits': ['Anti-rides', 'Régénération cellulaire', 'Uniformisation du teint'],
                    'risks': ['Irritation', 'Sensibilité au soleil', 'Desquamation'],
                    'best_for': ['Peau mature', 'Acné', 'Taches pigmentaires'],
                    'avoid_if': ['Peau très sensible', 'Grossesse', 'Allaitement']
                },
                'vitamine c': {
                    'description': 'Antioxydant puissant qui protège et éclaircit la peau',
                    'benefits': ['Protection antioxydante', 'Éclaircissement', 'Stimulation du collagène'],
                    'risks': ['Instabilité à la lumière', 'Peut irriter les peaux sensibles'],
                    'best_for': ['Tous types de peau', 'Anti-âge', 'Taches pigmentaires'],
                    'avoid_if': ['Peau très sensible', 'Allergie à la vitamine C']
                },
                'niacinamide': {
                    'description': 'Vitamine B3 qui régule le sébum et améliore la texture',
                    'benefits': ['Régulation du sébum', 'Réduction des pores', 'Anti-inflammatoire'],
                    'risks': ['Rarement, légère irritation'],
                    'best_for': ['Peau grasse', 'Peau mixte', 'Acné'],
                    'avoid_if': ['Allergie à la niacinamide']
                }
            },
            'recommended_ingredients_list': [
                'Acide hyaluronique', 'Glycérine', 'Niacinamide', 'Céramides', 'Panthenol',
                'Vitamine C', 'Rétinol', 'Peptides', 'Acide salicylique', 'Acide glycolique',
                'Centella asiatica', 'Aloe vera', 'Thermal water', 'Huiles végétales'
            ]
        }
    
    def _initialize_product_database(self) -> List[Dict[str, Any]]:
        """
        Initialize internal product database with scores and prices.
        
        Returns:
            List of product dictionaries with comprehensive information
        """
        return [
            # Nettoyants
            {
                'name': 'Gel nettoyant doux',
                'brand': 'CeraVe',
                'type': 'nettoyant',
                'price': 12.99,
                'score': 85,
                'ingredients': ['Céramides', 'Acide hyaluronique', 'Niacinamide'],
                'skin_types': ['dry', 'sensitive', 'normal'],
                'size': '236ml',
                'description': 'Nettoyant doux sans savon, adapté à tous types de peau'
            },
            {
                'name': 'Gel nettoyant moussant',
                'brand': 'La Roche-Posay',
                'type': 'nettoyant',
                'price': 15.99,
                'score': 88,
                'ingredients': ['Thermal water', 'Niacinamide', 'Zinc'],
                'skin_types': ['oily', 'combination', 'normal'],
                'size': '200ml',
                'description': 'Nettoyant moussant pour peau mixte à grasse'
            },
            # Sérums
            {
                'name': 'Sérum Niacinamide 10%',
                'brand': 'The Ordinary',
                'type': 'sérum',
                'price': 8.99,
                'score': 90,
                'ingredients': ['Niacinamide', 'Zinc'],
                'skin_types': ['oily', 'combination', 'normal'],
                'size': '30ml',
                'description': 'Sérum régulateur de sébum et anti-imperfections'
            },
            {
                'name': 'Sérum Acide Hyaluronique',
                'brand': 'The Ordinary',
                'type': 'sérum',
                'price': 7.99,
                'score': 92,
                'ingredients': ['Acide hyaluronique', 'Vitamine B5'],
                'skin_types': ['all'],
                'size': '30ml',
                'description': 'Hydratation intense et réparatrice'
            },
            # Hydratants
            {
                'name': 'Crème hydratante',
                'brand': 'La Roche-Posay',
                'type': 'hydratant',
                'price': 18.99,
                'score': 90,
                'ingredients': ['Acide hyaluronique', 'Glycérine', 'Thermal water'],
                'skin_types': ['dry', 'sensitive', 'normal'],
                'size': '50ml',
                'description': 'Hydratation intense et apaisante'
            },
            {
                'name': 'Gel hydratant',
                'brand': 'Neutrogena',
                'type': 'hydratant',
                'price': 14.99,
                'score': 85,
                'ingredients': ['Acide hyaluronique', 'Glycérine'],
                'skin_types': ['oily', 'combination', 'normal'],
                'size': '50ml',
                'description': 'Hydratation légère sans effet gras'
            },
            # SPF
            {
                'name': 'Anthelios UVMune 400',
                'brand': 'La Roche-Posay',
                'type': 'SPF',
                'price': 22.99,
                'score': 92,
                'ingredients': ['Mexoryl 400', 'Mexoryl SX', 'Mexoryl XL'],
                'skin_types': ['all'],
                'size': '50ml',
                'description': 'Protection solaire large spectre invisible'
            },
            {
                'name': 'SPF 50+ Invisible',
                'brand': 'CeraVe',
                'type': 'SPF',
                'price': 19.99,
                'score': 88,
                'ingredients': ['Zinc oxide', 'Titanium dioxide', 'Céramides'],
                'skin_types': ['all'],
                'size': '50ml',
                'description': 'Protection minérale adaptée aux peaux sensibles'
            },
            # Actifs
            {
                'name': 'Rétinol 0.5%',
                'brand': 'The Ordinary',
                'type': 'actif',
                'price': 9.99,
                'score': 85,
                'ingredients': ['Rétinol', 'Squalane'],
                'skin_types': ['normal', 'combination', 'dry'],
                'size': '30ml',
                'description': 'Actif anti-âge pour débutants'
            },
            {
                'name': 'Vitamine C 23%',
                'brand': 'The Ordinary',
                'type': 'actif',
                'price': 11.99,
                'score': 87,
                'ingredients': ['Vitamine C', 'Acide hyaluronique'],
                'skin_types': ['all'],
                'size': '30ml',
                'description': 'Antioxydant et éclaircissant'
            }
        ]
        
    def process_premium_request(
        self, 
        user: User, 
        question: str, 
        context_product_id: Optional[int] = None,
        budget_filter: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a Premium user request and return comprehensive response.
        
        Args:
            user: The authenticated user
            question: User's question or request
            context_product_id: Optional product ID for context-aware responses
            budget_filter: Optional budget limit in euros
            
        Returns:
            Dictionary containing structured response with routine, explanations, and recommendations
        """
        try:
            # Get user profile and context
            user_profile = self._get_user_profile(user)
            context_data = self._build_context(user, user_profile, context_product_id)
            
            # Generate AI response based on question type
            if self._is_routine_request(question):
                try:
                    response = self._generate_routine_response(user_profile, question, budget_filter, context_data)
                except Exception as routine_error:
                    logger.error(f"Error in routine generation: {str(routine_error)}")
                    response = self._generate_error_response(f"Erreur routine: {str(routine_error)}")
            elif self._is_ingredient_question(question):
                try:
                    response = self._generate_ingredient_response(question, context_data)
                except Exception as ingredient_error:
                    logger.error(f"Error in ingredient analysis: {str(ingredient_error)}")
                    response = self._generate_error_response(f"Erreur ingrédient: {str(ingredient_error)}")
            else:
                try:
                    response = self._generate_general_response(question, context_data)
                except Exception as general_error:
                    logger.error(f"Error in general response: {str(general_error)}")
                    response = self._generate_error_response(f"Erreur générale: {str(general_error)}")
            
            # Add common elements
            response.update({
                'suggested_questions': self.suggested_questions,
                'user_context': self._get_user_context_summary(user_profile),
                'alerts': self._generate_alerts(user_profile, context_data)
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing Premium request: {str(e)}")
            return self._generate_error_response(str(e))
    
    def _get_user_profile(self, user: User) -> UserProfile:
        """Get or create user profile with all skincare preferences."""
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    def _build_context(
        self, 
        user: User, 
        profile: UserProfile, 
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build comprehensive context for AI responses following the specified architecture.
        
        Constructs the complete context including:
        - User profile data (skin type, age, budget, concerns)
        - Allergies and sensitivities
        - Scan history for product context
        - Dermatological knowledge base (RAG)
        - Internal product database with scores
        - Product-specific context if available
        
        Args:
            user: The authenticated user
            profile: User profile containing skin information
            product_id: Optional product ID for context-aware responses
            
        Returns:
            Dict containing comprehensive context for AI processing
        """
        # Get user profile data
        user_profile_data = {
                'skin_type': profile.skin_type,
                'skin_concerns': profile.skin_concerns,
                'age_range': profile.age_range,
                'budget': profile.budget,
                'pathologies': profile.pathologies
        }
        
        # Get user allergies
        allergies = self._get_user_allergies(user)
        
        # Get recent scan history
        scan_history = self._get_recent_scans(user)
        
        # Get product context if available
        product_context = None
        if product_id:
            product_context = self._get_product_context(product_id)
        
        # Build comprehensive context
        context = {
            'user_profile': user_profile_data,
            'allergies': allergies,
            'scan_history': scan_history,
            'product_context': product_context,
            'dermatological_knowledge': self.dermatological_knowledge,
            'internal_product_database': self.internal_product_database,
            'user_preferences': self._get_user_preferences(user),
            'seasonal_factors': self._get_seasonal_factors(),
            'skin_analysis': self._analyze_skin_needs(user_profile_data, allergies, scan_history)
        }
            
        return context
    
    def _get_user_preferences(self, user: User) -> Dict[str, Any]:
        """
        Get user preferences for product recommendations.
        
        Args:
            user: The authenticated user
            
        Returns:
            Dict containing user preferences
        """
        # This would typically come from user settings
        # For now, returning default preferences
        return {
            'preferred_brands': [],
            'avoided_ingredients': [],
            'preferred_textures': ['légère', 'non-grasse'],
            'sensitivity_level': 'moderate',
            'application_preferences': ['matin', 'soir']
        }
    
    def _get_seasonal_factors(self) -> Dict[str, Any]:
        """
        Get seasonal factors that affect skincare recommendations.
        
        Returns:
            Dict containing seasonal information
        """
        # This would typically use current date and location
        # For now, returning general seasonal factors
        return {
            'season': 'été',  # Would be calculated based on date
            'humidity': 'modérée',
            'temperature': 'chaude',
            'uv_index': 'élevé',
            'recommendations': {
                'summer': ['SPF renforcé', 'Hydratation légère', 'Protection contre la chaleur'],
                'winter': ['Hydratation intense', 'Barrière lipidique', 'Protection contre le froid'],
                'spring': ['Exfoliation douce', 'Antioxydants', 'Préparation pour l\'été'],
                'autumn': ['Réparation', 'Hydratation modérée', 'Préparation pour l\'hiver']
            }
        }
    
    def _analyze_skin_needs(
        self, 
        user_profile: Dict[str, Any], 
        allergies: List[Dict[str, str]], 
        scan_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze skin needs based on profile, allergies, and scan history.
        
        Args:
            user_profile: User profile data
            allergies: User allergies
            scan_history: Recent scan history
            
        Returns:
            Dict containing analyzed skin needs
        """
        skin_type = user_profile.get('skin_type', 'normal')
        concerns = user_profile.get('skin_concerns', [])
        age_range = user_profile.get('age_range', '20s')
        
        # Get dermatological knowledge for skin type
        skin_knowledge = self.dermatological_knowledge['skin_types'].get(skin_type, {})
        age_knowledge = self.dermatological_knowledge['age_concerns'].get(age_range, {})
        
        # Analyze scan history for patterns
        scan_analysis = self._analyze_scan_history(scan_history)
        
        # Determine priority needs
        priority_needs = []
        if skin_knowledge:
            priority_needs.extend(skin_knowledge.get('needs', []))
        if age_knowledge:
            priority_needs.extend(age_knowledge.get('focus', []))
        
        # Add concerns-specific needs
        if concerns:
            priority_needs.extend(concerns)
        
        return {
            'primary_needs': priority_needs[:3],  # Top 3 needs
            'skin_characteristics': skin_knowledge.get('characteristics', ''),
            'recommended_ingredients': skin_knowledge.get('recommended_ingredients', []),
            'avoided_ingredients': skin_knowledge.get('avoid', []),
            'routine_focus': skin_knowledge.get('routine_focus', ''),
            'age_focus': age_knowledge.get('focus', []),
            'scan_analysis': scan_analysis,
            'allergy_risks': [allergy['ingredient'] for allergy in allergies]
        }
    
    def _analyze_scan_history(self, scan_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze scan history for patterns and insights.
        
        Args:
            scan_history: List of recent scans
            
        Returns:
            Dict containing scan analysis
        """
        if not scan_history:
            return {
                'total_scans': 0,
                'average_score': 0,
                'common_ingredients': [],
                'risk_patterns': [],
                'recommendations': []
            }
        
        total_scans = len(scan_history)
        scores = [scan.get('score', 0) for scan in scan_history if scan.get('score') is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Extract common ingredients
        all_ingredients = []
        for scan in scan_history:
            ingredients = scan.get('ingredients', [])
            all_ingredients.extend(ingredients)
        
        # Count ingredient frequency
        ingredient_counts = {}
        for ingredient in all_ingredients:
            ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
        
        common_ingredients = sorted(ingredient_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Identify risk patterns
        low_score_products = [scan for scan in scan_history if scan.get('score') is not None and scan.get('score', 100) < 50]
        risk_patterns = []
        if low_score_products:
            risk_patterns.append(f"{len(low_score_products)} produits avec score faible détectés")
        
        return {
            'total_scans': total_scans,
            'average_score': round(average_score, 1),
            'common_ingredients': [ingredient for ingredient, count in common_ingredients],
            'risk_patterns': risk_patterns,
            'recommendations': self._generate_scan_recommendations(average_score, common_ingredients, risk_patterns)
        }
    
    def _generate_scan_recommendations(
        self, 
        average_score: float, 
        common_ingredients: List[Tuple[str, int]], 
        risk_patterns: List[str]
    ) -> List[str]:
        """
        Generate recommendations based on scan analysis.
        
        Args:
            average_score: Average safety score
            common_ingredients: Most common ingredients
            risk_patterns: Identified risk patterns
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if average_score < 60:
            recommendations.append("Considérez des alternatives plus sûres pour vos produits")
        
        if risk_patterns:
            recommendations.append("Évitez les produits avec des scores de sécurité faibles")
        
        if common_ingredients:
            ingredient_names = [ingredient[0] for ingredient in common_ingredients[:3]]
            recommendations.append(f"Vous utilisez souvent: {', '.join(ingredient_names)}")
        
        return recommendations
    
    def _get_user_allergies(self, user: User) -> List[Dict[str, str]]:
        """Get user's allergies and sensitivities."""
        allergies = Allergy.objects.filter(user=user)
        return [
            {
                'ingredient': allergy.ingredient_name,
                'severity': allergy.severity,
                'notes': allergy.notes
            }
            for allergy in allergies
        ]
    
    def _get_recent_scans(self, user: User, limit: int = 5) -> List[Dict[str, Any]]:
        """Get user's recent scan history for context."""
        try:
            scans = Scan.objects.filter(user=user).order_by('-scanned_at')[:limit]
            return [
                {
                    'product_name': getattr(scan, 'product_name', None) or 'Produit inconnu',
                    'score': getattr(scan, 'product_score', None),
                    'ingredients': getattr(scan, 'product_ingredients_text', '').split(', ') if getattr(scan, 'product_ingredients_text', None) else [],
                    'created_at': scan.scanned_at.isoformat()
                }
                for scan in scans
            ]
        except Exception as e:
            logger.warning(f"Error getting recent scans for user {user.username}: {e}")
            # Fallback if database fields don't exist yet
            return []
    
    def _get_product_context(self, scan_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed product information for context-aware responses."""
        try:
            # Note: Product model has been removed, so we'll use scan data
            scan = Scan.objects.filter(id=scan_id).first()
            if scan and scan.product_name:
                return {
                    'name': scan.product_name,
                    'brand': scan.product_brand or 'Marque inconnue',
                    'ingredients': scan.product_ingredients_text.split(', ') if scan.product_ingredients_text else [],
                    'safety_score': scan.product_score,
                    'risk_level': scan.product_risk_level
                }
            return None
        except Exception as e:
            logger.warning(f"Error getting product context: {e}")
            return None
    

    
    def _is_routine_request(self, question: str) -> bool:
        """
        Check if the question is requesting a routine.
        Amélioré pour distinguer clairement les demandes de routine des questions générales.
        """
        question_lower = question.lower()
        
        # Mots-clés indiquant une demande de routine
        routine_keywords = [
            "routine", "routines", "fais-moi", "crée", "génère", "établis",
            "matin", "soir", "quotidienne", "hebdomadaire", "étapes",
            "programme", "plan", "ordonnance", "prescription"
        ]
        
        # Phrases typiques de demande de routine
        routine_phrases = [
            "fais-moi une routine",
            "crée une routine",
            "génère une routine",
            "établis une routine",
            "routine du matin",
            "routine du soir",
            "routine quotidienne",
            "routine hebdomadaire",
            "programme de soins",
            "plan de soins",
            "étapes de soins"
        ]
        
        # Vérifier les phrases complètes
        for phrase in routine_phrases:
            if phrase in question_lower:
                return True
        
        # Vérifier les mots-clés avec contexte
        for keyword in routine_keywords:
            if keyword in question_lower:
                # Vérifier le contexte pour éviter les faux positifs
                if any(context in question_lower for context in ["routine", "soins", "matin", "soir", "quotidien"]):
                    return True
        
        return False
    
    def _is_ingredient_question(self, question: str) -> bool:
        """Check if the question is about ingredients."""
        ingredient_keywords = ['ingrédient', 'composant', 'substance', 'formule', 'acide', 'vitamine']
        return any(keyword in question.lower() for keyword in ingredient_keywords)
    
    def _generate_routine_response(
        self, 
        profile: UserProfile, 
        question: str, 
        budget_filter: Optional[float] = None,
        context_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized routine response following the specified architecture.
        
        Implements the complete routine generation workflow:
        - Analyze user profile and skin needs
        - Select appropriate products from internal database
        - Generate morning/evening sequencing
        - Apply budget filtering
        - Provide explanations and alternatives
        
        Args:
            profile: User profile containing skin information
            question: User's routine request
            budget_filter: Optional budget limit in euros
            context_data: Comprehensive context data
            
        Returns:
            Dict containing structured routine response with JSON format
        """
        try:
            # Determine routine type from question
            routine_type = self._extract_routine_type(question)
            
            # Get skin analysis from context
            skin_analysis = context_data.get('skin_analysis', {}) if context_data else {}
            
            # Generate AI response using the AI service
            ai_response = self._call_ai_service(self._build_routine_prompt(profile, routine_type, budget_filter, context_data))
            
            # Parse the AI response and create structured routine data
            routine_data = self._parse_ai_routine_response(ai_response, routine_type)
            
            # Apply budget filtering
            if budget_filter:
                routine_data = self._apply_budget_filter(routine_data, budget_filter)
            
            # Generate comprehensive response
            response = {
                'type': 'routine',
                'explanation': self._extract_explanation_from_ai_response(ai_response),
                'routine': routine_data,
                'alternatives': self._generate_budget_alternatives(profile, budget_filter, context_data),
                'faq': self._generate_routine_faq(routine_type),
                'skin_analysis': skin_analysis,
                'budget_applied': budget_filter
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating routine response: {str(e)}")
            # Return a fallback response
            return {
                'type': 'routine',
                'explanation': f"Voici une routine {routine_type} adaptée à votre type de peau.",
                'routine': self._create_fallback_routine(routine_type),
                'alternatives': [],
                'faq': [],
                'error': str(e)
            }
    
    def _generate_personalized_routine(
        self,
        profile: UserProfile,
        routine_type: str,
        budget_filter: Optional[float],
        skin_analysis: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized routine using internal product database.
        
        Args:
            profile: User profile
            routine_type: Type of routine (morning, evening, etc.)
            budget_filter: Budget limit
            skin_analysis: Analyzed skin needs
            context_data: Complete context data
            
        Returns:
            Dict containing structured routine data
        """
        # Get user skin type and preferences
        skin_type = profile.skin_type
        if isinstance(skin_type, list):
            skin_type = skin_type[0] if skin_type else 'normal'
        elif not skin_type:
            skin_type = 'normal'
        
        # Get recommended ingredients and avoided ingredients
        recommended_ingredients = skin_analysis.get('recommended_ingredients', [])
        avoided_ingredients = skin_analysis.get('avoided_ingredients', [])
        
        # Filter products based on skin type and budget
        available_products = self._filter_products_for_user(
            skin_type, budget_filter, recommended_ingredients, avoided_ingredients
        )
        
        # Generate routine structure based on type
        if routine_type == 'morning':
            routine_structure = self._generate_morning_routine(available_products, skin_analysis)
        elif routine_type == 'evening':
            routine_structure = self._generate_evening_routine(available_products, skin_analysis)
        else:
            routine_structure = self._generate_general_routine(available_products, routine_type, skin_analysis)
        
        return {
            "routine": routine_structure,
            "explication_globale": self._generate_routine_explanation(profile, routine_type, context_data),
            "conseils": self._generate_routine_tips(routine_type, skin_analysis),
            "total_prix": self._calculate_total_price(routine_structure),
            "score_moyen": self._calculate_average_score(routine_structure)
        }
    
    def _filter_products_for_user(
        self,
        skin_type: str,
        budget_filter: Optional[float],
        recommended_ingredients: List[str],
        avoided_ingredients: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter products from internal database based on user criteria.
        
        Args:
            skin_type: User's skin type
            budget_filter: Budget limit
            recommended_ingredients: Recommended ingredients for skin type
            avoided_ingredients: Ingredients to avoid
            
        Returns:
            List of filtered products
        """
        filtered_products = []
        
        for product in self.internal_product_database:
            # Check skin type compatibility
            if skin_type not in product.get('skin_types', []) and 'all' not in product.get('skin_types', []):
                continue
            
            # Check budget
            if budget_filter is not None:
                product_price = product.get('price', 0)
                if not isinstance(product_price, (int, float)) or product_price > budget_filter:
                    continue
            
            # Check for avoided ingredients
            product_ingredients = product.get('ingredients', [])
            has_avoided_ingredient = any(
                avoided.lower() in ingredient.lower() 
                for ingredient in product_ingredients 
                for avoided in avoided_ingredients
            )
            if has_avoided_ingredient:
                continue
            
            # Add product with priority score
            priority_score = self._calculate_product_priority(product, recommended_ingredients)
            product_with_priority = product.copy()
            product_with_priority['priority_score'] = priority_score
            filtered_products.append(product_with_priority)
        
        # Sort by priority score and then by price
        filtered_products.sort(key=lambda x: (-x['priority_score'], x.get('price', 0) if x.get('price') is not None else 0))
        
        return filtered_products
    
    def _calculate_product_priority(
        self, 
        product: Dict[str, Any], 
        recommended_ingredients: List[str]
    ) -> float:
        """
        Calculate priority score for a product based on recommended ingredients.
        
        Args:
            product: Product information
            recommended_ingredients: Recommended ingredients for user's skin type
            
        Returns:
            Priority score (higher is better)
        """
        score = 0.0
        
        # Base score from product safety score
        score += product.get('score', 0) * 0.5
        
        # Bonus for recommended ingredients
        product_ingredients = product.get('ingredients', [])
        for ingredient in product_ingredients:
            if any(rec.lower() in ingredient.lower() for rec in recommended_ingredients):
                score += 10
        
        # Bonus for high-quality brands
        brand = product.get('brand', '').lower()
        premium_brands = ['la roche-posay', 'cerave', 'the ordinary', 'neutrogena']
        if brand in premium_brands:
            score += 5
        
        return score
    
    def _generate_morning_routine(
        self, 
        available_products: List[Dict[str, Any]], 
        skin_analysis: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate morning routine structure.
        
        Args:
            available_products: Filtered products for user
            skin_analysis: Analyzed skin needs
            
        Returns:
            Dict with morning routine structure
        """
        morning_products = []
        
        # Select products by type in order
        product_types = ['nettoyant', 'sérum', 'hydratant', 'SPF']
        
        for product_type in product_types:
            type_products = [p for p in available_products if p['type'] == product_type]
            if type_products:
                selected_product = type_products[0]  # Take the highest priority
                morning_products.append({
                    "type": product_type,
                    "produit": selected_product['name'],
                    "marque": selected_product['brand'],
                    "prix": selected_product['price'],
                    "score": selected_product['score'],
                    "explication": self._generate_product_explanation(selected_product, product_type, 'matin')
                })
        
        return {"matin": morning_products, "soir": []}
    
    def _generate_evening_routine(
        self, 
        available_products: List[Dict[str, Any]], 
        skin_analysis: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate evening routine structure.
        
        Args:
            available_products: Filtered products for user
            skin_analysis: Analyzed skin needs
            
        Returns:
            Dict with evening routine structure
        """
        evening_products = []
        
        # Select products by type in order
        product_types = ['nettoyant', 'actif', 'hydratant']
        
        for product_type in product_types:
            type_products = [p for p in available_products if p['type'] == product_type]
            if type_products:
                selected_product = type_products[0]  # Take the highest priority
                evening_products.append({
                    "type": product_type,
                    "produit": selected_product['name'],
                    "marque": selected_product['brand'],
                    "prix": selected_product['price'],
                    "score": selected_product['score'],
                    "explication": self._generate_product_explanation(selected_product, product_type, 'soir')
                })
        
        return {"matin": [], "soir": evening_products}
    
    def _generate_general_routine(
        self, 
        available_products: List[Dict[str, Any]], 
        routine_type: str, 
        skin_analysis: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate general routine structure for other types.
        
        Args:
            available_products: Filtered products for user
            routine_type: Type of routine
            skin_analysis: Analyzed skin needs
            
        Returns:
            Dict with routine structure
        """
        # For hair and body routines, we'll use a simplified structure
        selected_products = available_products[:3]  # Take top 3 products
        
        products_list = []
        for product in selected_products:
            products_list.append({
                "type": product['type'],
                "produit": product['name'],
                "marque": product['brand'],
                "prix": product['price'],
                "score": product['score'],
                "explication": f"Produit adapté pour routine {routine_type}"
            })
        
        return {"matin": products_list, "soir": []}
    
    def _generate_product_explanation(
        self, 
        product: Dict[str, Any], 
        product_type: str, 
        time_of_day: str
    ) -> str:
        """
        Generate explanation for why a product is recommended.
        
        Args:
            product: Product information
            product_type: Type of product
            time_of_day: Time of day (matin/soir)
            
        Returns:
            Explanation string
        """
        explanations = {
            'nettoyant': {
                'matin': 'Nettoyage doux pour éliminer les impuretés de la nuit',
                'soir': 'Double nettoyage pour éliminer maquillage et impuretés'
            },
            'sérum': {
                'matin': 'Actif ciblé pour traiter les préoccupations spécifiques',
                'soir': 'Actif réparateur pour la régénération nocturne'
            },
            'hydratant': {
                'matin': 'Hydratation pour préparer la peau à la journée',
                'soir': 'Hydratation réparatrice pour la nuit'
            },
            'SPF': {
                'matin': 'Protection solaire essentielle pour la journée',
                'soir': 'Non recommandé le soir'
            },
            'actif': {
                'matin': 'Actif préventif pour la journée',
                'soir': 'Actif réparateur pour la régénération'
            }
        }
        
        base_explanation = explanations.get(product_type, {}).get(time_of_day, 'Produit adapté à vos besoins')
        
        # Add product-specific information
        if product.get('description'):
            base_explanation += f" - {product['description']}"
        
        return base_explanation
    
    def _calculate_total_price(self, routine_structure: Dict[str, List[Dict[str, Any]]]) -> float:
        """Calculate total price of routine."""
        total = 0.0
        for time_products in routine_structure.values():
            for product in time_products:
                price = product.get('prix', 0)
                if isinstance(price, (int, float)):
                    total += price
        return round(total, 2)
    
    def _calculate_average_score(self, routine_structure: Dict[str, List[Dict[str, Any]]]) -> float:
        """Calculate average safety score of routine."""
        scores = []
        for time_products in routine_structure.values():
            for product in time_products:
                scores.append(product.get('score', 0))
        
        if scores:
            return round(sum(scores) / len(scores), 1)
        return 0.0
    
    def _generate_routine_tips(self, routine_type: str, skin_analysis: Dict[str, Any]) -> List[str]:
        """Generate tips for the routine."""
        tips = []
        
        if routine_type == 'morning':
            tips.extend([
                "Appliquez les produits du plus léger au plus épais",
                "Attendez 2-3 minutes entre chaque étape",
                "Protégez toujours votre peau du soleil",
                "Adaptez les produits selon votre type de peau"
            ])
        elif routine_type == 'evening':
            tips.extend([
                "Double nettoyage obligatoire pour éliminer toutes les impuretés",
                "Le soir est idéal pour les actifs forts comme le rétinol",
                "Utilisez une crème plus riche pour la nuit",
                "Évitez les actifs photosensibilisants le matin"
            ])
        
        # Add skin-specific tips
        if skin_analysis.get('routine_focus'):
            tips.append(f"Focus: {skin_analysis['routine_focus']}")
        
        return tips
    
    def _extract_routine_type(self, question: str) -> str:
        """Extract routine type from user question."""
        question_lower = question.lower()
        if 'matin' in question_lower:
            return 'morning'
        elif 'soir' in question_lower:
            return 'evening'
        elif 'cheveux' in question_lower:
            return 'hair'
        elif 'corps' in question_lower:
            return 'body'
        else:
            return 'morning'  # Default
    
    def _build_routine_prompt(
        self, 
        profile: UserProfile, 
        routine_type: str, 
        budget_filter: Optional[float] = None,
        context_data: Dict[str, Any] = None
    ) -> str:
        """
        Build comprehensive prompt for routine generation.
        
        Args:
            profile: User profile containing skin information
            routine_type: Type of routine to generate
            budget_filter: Optional budget limit
            context_data: Additional context data
            
        Returns:
            str: Formatted prompt for AI routine generation
        """
        budget_text = f"Budget maximum: {budget_filter}€" if budget_filter else "Budget flexible"
        
        # Handle skin_type - convert list to string if necessary
        skin_type = profile.skin_type
        if isinstance(skin_type, list):
            skin_type = ", ".join(skin_type) if skin_type else "Non spécifié"
        elif not skin_type:
            skin_type = "Non spécifié"
        
        # Handle skin_concerns - convert list to string if necessary
        skin_concerns = profile.skin_concerns
        if isinstance(skin_concerns, list):
            skin_concerns = ", ".join(skin_concerns) if skin_concerns else "Aucune"
        elif not skin_concerns:
            skin_concerns = "Aucune"
        
        # Handle pathologies - convert list to string if necessary
        pathologies = profile.pathologies
        if isinstance(pathologies, list):
            pathologies = ", ".join(pathologies) if pathologies else "Aucune"
        elif not pathologies:
            pathologies = "Aucune"
        
        # Build context information
        context_info = ""
        if context_data:
            if context_data.get('allergies'):
                allergies_text = ", ".join([a['ingredient'] for a in context_data['allergies']])
                context_info += f"\nAllergies: {allergies_text}"
            
            if context_data.get('scan_history'):
                context_info += f"\nHistorique scans: {len(context_data['scan_history'])} produits récents"
        
        prompt = f"""
        Créez une routine de soins {routine_type} personnalisée en français avec les spécifications suivantes:
        
        Profil utilisateur:
        - Type de peau: {skin_type}
        - Préoccupations: {skin_concerns}
        - Âge: {profile.age_range or 'Non spécifié'}
        - Budget: {budget_text}
        - Pathologies: {pathologies}{context_info}
        
        Format de réponse JSON requis:
        {{
            "routine": {{
                "matin": [
                    {{
                        "type": "nettoyant",
                        "produit": "Nom du produit",
                        "marque": "Marque",
                        "prix": 15.99,
                        "score": 85,
                        "explication": "Pourquoi ce produit est recommandé"
                    }}
                ],
                "soir": [
                    {{
                        "type": "démaquillant",
                        "produit": "Nom du produit",
                        "marque": "Marque",
                        "prix": 12.99,
                        "score": 88,
                        "explication": "Pourquoi ce produit est recommandé"
                    }}
                ]
            }},
            "explication_globale": "Explication des besoins de la peau",
            "conseils": ["Conseil 1", "Conseil 2"]
        }}
        
        Assurez-vous que tous les produits sont adaptés au type de peau et au budget.
        Incluez des explications sur les besoins spécifiques de la peau.
        """
        
        return prompt
    
    def _parse_routine_response(self, ai_response: str, routine_type: str) -> Dict[str, Any]:
        """
        Parse AI response and extract structured routine data.
        
        Args:
            ai_response: Raw response from the AI service
            routine_type: Type of routine being generated
            
        Returns:
            Dict containing structured routine data
        """
        try:
            # Try to extract JSON from response
            if '{' in ai_response and '}' in ai_response:
                start = ai_response.find('{')
                end = ai_response.rfind('}') + 1
                json_str = ai_response[start:end]
                parsed_response = json.loads(json_str)
                
                # Validate the structure
                if 'routine' in parsed_response:
                    return parsed_response
                else:
                    logger.warning("AI response missing 'routine' key, using fallback")
                    return self._create_fallback_routine(routine_type)
            else:
                # If no JSON found, create a fallback routine
                logger.info("No JSON found in AI response, using fallback")
                return self._create_fallback_routine(routine_type)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}, using fallback")
            return self._create_fallback_routine(routine_type)
        except Exception as e:
            logger.error(f"Unexpected error parsing AI response: {e}, using fallback")
            return self._create_fallback_routine(routine_type)
    
    def _create_fallback_routine(self, routine_type: str) -> Dict[str, Any]:
        """
        Create a comprehensive fallback routine structure when AI parsing fails.
        
        Args:
            routine_type: Type of routine to generate (morning, evening, hair, body)
            
        Returns:
            Dict containing structured routine data with realistic products
        """
        if routine_type == 'morning':
            return {
                "routine": {
                    "matin": [
                        {
                            "type": "nettoyant",
                            "produit": "Gel nettoyant doux",
                            "marque": "CeraVe",
                            "prix": 12.99,
                            "score": 85,
                            "explication": "Nettoyage doux sans irritation, adapté à tous types de peau"
                        },
                        {
                            "type": "sérum",
                            "produit": "Sérum hydratant",
                            "marque": "The Ordinary",
                            "prix": 8.99,
                            "score": 88,
                            "explication": "Hydratation intense avec acide hyaluronique"
                        },
                        {
                            "type": "hydratant",
                            "produit": "Crème hydratante",
                            "marque": "La Roche-Posay",
                            "prix": 18.99,
                            "score": 90,
                            "explication": "Hydratation intense et réparatrice"
                        },
                        {
                            "type": "SPF",
                            "produit": "Anthelios UVMune 400",
                            "marque": "La Roche-Posay",
                            "prix": 22.99,
                            "score": 92,
                            "explication": "Protection solaire large spectre"
                        }
                    ],
                    "soir": []
                },
                "explication_globale": "Routine matinale complète pour protéger et préparer votre peau pour la journée",
                "conseils": [
                    "Appliquez les produits du plus léger au plus épais",
                    "Attendez 2-3 minutes entre chaque étape",
                    "Protégez toujours votre peau du soleil",
                    "Adaptez les produits selon votre type de peau"
                ]
            }
        elif routine_type == 'evening':
            return {
                "routine": {
                    "matin": [],
                    "soir": [
                        {
                            "type": "démaquillant",
                            "produit": "Eau micellaire",
                            "marque": "Bioderma",
                            "prix": 14.99,
                            "score": 87,
                            "explication": "Démaquillage doux et efficace"
                        },
                        {
                            "type": "nettoyant",
                            "produit": "Gel nettoyant",
                            "marque": "CeraVe",
                            "prix": 12.99,
                            "score": 85,
                            "explication": "Double nettoyage pour une peau parfaitement propre"
                        },
                        {
                            "type": "sérum",
                            "produit": "Sérum rétinol",
                            "marque": "The Ordinary",
                            "prix": 9.99,
                            "score": 86,
                            "explication": "Actif anti-âge pour la régénération nocturne"
                        },
                        {
                            "type": "hydratant",
                            "produit": "Crème de nuit",
                            "marque": "Neutrogena",
                            "prix": 16.99,
                            "score": 89,
                            "explication": "Hydratation réparatrice pour la nuit"
                        }
                    ]
                },
                "explication_globale": "Routine du soir pour réparer et régénérer votre peau pendant le sommeil",
                "conseils": [
                    "Double nettoyage obligatoire pour éliminer toutes les impuretés",
                    "Le soir est idéal pour les actifs forts comme le rétinol",
                    "Utilisez une crème plus riche pour la nuit",
                    "Évitez les actifs photosensibilisants le matin"
                ]
            }
        else:
            return {
                "routine": {
                    "matin": [],
                    "soir": []
                },
                "explication_globale": f"Routine {routine_type} personnalisée en cours de génération",
                "conseils": [
                    "Consultez un dermatologue pour des conseils personnalisés",
                    "Adaptez toujours les produits à votre type de peau",
                    "Testez les nouveaux produits sur une petite zone"
                ]
            }
    
    def _apply_budget_filter(self, routine_data: Dict[str, Any], budget_filter: float) -> Dict[str, Any]:
        """
        Apply budget filtering to routine products.
        
        Args:
            routine_data: Routine data containing products
            budget_filter: Budget limit (can be None for no limit)
            
        Returns:
            Filtered routine data
        """
        if not routine_data.get('routine'):
            return routine_data
        
        # If no budget filter, return original data
        if budget_filter is None:
            return routine_data
        
        filtered_routine = {'matin': [], 'soir': []}
        
        for time_of_day in ['matin', 'soir']:
            if routine_data['routine'].get(time_of_day):
                for product in routine_data['routine'][time_of_day]:
                    product_price = product.get('prix', 0)
                    # Ensure product_price is a number and budget_filter is valid
                    if isinstance(product_price, (int, float)) and product_price <= budget_filter:
                        filtered_routine[time_of_day].append(product)
        
        routine_data['routine'] = filtered_routine
        return routine_data
    
    def _generate_routine_explanation(self, profile: UserProfile, routine_type: str, context_data: Dict[str, Any] = None) -> str:
        """
        Generate explanation of skin needs based on profile.
        
        Args:
            profile: User profile containing skin information
            routine_type: Type of routine being generated
            context_data: Additional context data
            
        Returns:
            str: Personalized explanation for the routine
        """
        # Handle skin_type - convert list to string if necessary
        skin_type = profile.skin_type
        if isinstance(skin_type, list):
            skin_type = ", ".join(skin_type) if skin_type else "votre type de peau"
        elif not skin_type:
            skin_type = "votre type de peau"
        
        # Handle skin_concerns - convert list to string if necessary
        concerns = profile.skin_concerns
        if isinstance(concerns, list):
            concerns = ", ".join(concerns) if concerns else "la santé générale de votre peau"
        elif not concerns:
            concerns = "la santé générale de votre peau"
        
        # Add context-specific information
        context_info = ""
        if context_data and context_data.get('dermatological_knowledge'):
            knowledge = context_data['dermatological_knowledge']
            if isinstance(skin_type, str) and skin_type in knowledge.get('skin_types', {}):
                skin_info = knowledge['skin_types'][skin_type]
                context_info = f" Votre peau {skin_type} a besoin de: {', '.join(skin_info.get('needs', []))}."
        
        explanations = {
            'morning': f"Votre peau {skin_type} nécessite une routine matinale qui protège et prépare votre peau pour la journée. Nous nous concentrons sur {concerns}.{context_info}",
            'evening': f"Le soir, votre peau {skin_type} a besoin de récupération et de réparation. Cette routine cible {concerns} pour optimiser la régénération nocturne.{context_info}",
            'hair': "Vos cheveux méritent autant d'attention que votre peau. Cette routine capillaire est adaptée à vos besoins spécifiques.",
            'body': "Votre corps a des besoins différents de votre visage. Cette routine corporelle cible vos zones de préoccupation."
        }
        
        return explanations.get(routine_type, "Routine personnalisée adaptée à vos besoins.")
    
    def _generate_budget_alternatives(self, profile: UserProfile, budget_filter: Optional[float], context_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate budget-friendly alternatives for recommended products."""
        if budget_filter is None or budget_filter > 50:
            return []
        
        # Generate alternatives for budget-conscious users
        alternatives = [
            {
                "type": "nettoyant",
                "produit": "Gel nettoyant doux",
                "marque": "Garnier",
                "prix": 6.99,
                "score": 75,
                "explication": "Alternative économique efficace"
            },
            {
                "type": "hydratant", 
                "produit": "Crème hydratante",
                "marque": "Nivea",
                "prix": 8.99,
                "score": 80,
                "explication": "Hydratation de qualité à prix abordable"
            }
        ]
        
        return alternatives
    
    def _generate_routine_faq(self, routine_type: str) -> List[Dict[str, str]]:
        """Generate FAQ for the specific routine type."""
        faqs = {
            'morning': [
                {
                    "question": "Dans quel ordre appliquer les produits ?",
                    "reponse": "Nettoyant → Sérum → Hydratant → SPF"
                },
                {
                    "question": "Faut-il utiliser un SPF même en hiver ?",
                    "reponse": "Oui, les UV traversent les nuages et la neige réfléchit les rayons."
                }
            ],
            'evening': [
                {
                    "question": "Peut-on utiliser des actifs forts le soir ?",
                    "reponse": "Oui, le soir est idéal pour les rétinoïdes et acides de fruits."
                },
                {
                    "question": "Faut-il se démaquiller avant la routine ?",
                    "reponse": "Absolument, un double nettoyage est recommandé."
                }
            ]
        }
        
        return faqs.get(routine_type, [])
    
    def _generate_ingredient_response(self, question: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ingredient analysis response using enhanced assistant.
        
        Args:
            question: User's question about ingredients
            context_data: User context and profile information
            
        Returns:
            Dict containing ingredient analysis and recommendations
        """
        try:
            # Extract ingredient name from question
            ingredient_name = self._extract_ingredient_from_question(question)
            
            if not ingredient_name:
                return {
                    'type': 'ingredient_analysis',
                    'explanation': 'Pouvez-vous préciser le nom de l\'ingrédient que vous souhaitez analyser ?',
                    'ingredients_analyzed': [],
                    'alerts': ['Nom d\'ingrédient non spécifié']
                }
            
            # Build prompt for ingredient analysis
            prompt = self._build_ingredient_prompt(ingredient_name, context_data)
            
            # Get AI response using real AI service
            analysis = self._call_ai_service(prompt)
            
            # Generate personalized explanation
            explanation = self._generate_ingredient_explanation(ingredient_name, analysis, context_data)
            
            return {
                'type': 'ingredient_analysis',
                'explanation': explanation,
                'ingredients_analyzed': [ingredient_name],
                'analysis_details': analysis,
                'alerts': self._generate_ingredient_alerts(ingredient_name, analysis, context_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating ingredient response: {str(e)}")
            return {
                'type': 'ingredient_analysis',
                'explanation': 'Je ne peux pas analyser cet ingrédient pour le moment. Veuillez réessayer plus tard.',
                'ingredients_analyzed': [],
                'alerts': ['Erreur lors de l\'analyse de l\'ingrédient']
            }
    
    def _extract_ingredient_from_question(self, question: str) -> Optional[str]:
        """Extract ingredient name from user question."""
        question_lower = question.lower()
        
        # Common ingredient keywords
        ingredient_keywords = [
            'acide hyaluronique', 'rétinol', 'vitamine c', 'niacinamide', 'peptides',
            'acide salicylique', 'acide glycolique', 'acide lactique', 'collagène',
            'élastine', 'céramides', 'acides gras', 'antioxydants', 'spf'
        ]
        
        for keyword in ingredient_keywords:
            if keyword in question_lower:
                return keyword
        
        # Try to extract from question structure
        if 'qu\'est-ce que' in question_lower or 'c\'est quoi' in question_lower:
            # Extract text after these phrases
            for phrase in ['qu\'est-ce que', 'c\'est quoi']:
                if phrase in question_lower:
                    start = question_lower.find(phrase) + len(phrase)
                    ingredient = question_lower[start:].strip().rstrip('?').strip()
                    if ingredient and len(ingredient) > 2:
                        return ingredient
        
        return None
    
    def _generate_ingredient_explanation(self, ingredient_name: str, analysis: str, context_data: Dict[str, Any]) -> str:
        """
        Generate personalized ingredient explanation.
        
        Args:
            ingredient_name: Name of the ingredient
            analysis: Raw analysis from enhanced assistant
            context_data: User context information
            
        Returns:
            str: Personalized explanation
        """
        try:
            # Get user skin type for personalization
            skin_type = context_data.get('user_profile', {}).get('skin_type', 'Non spécifié')
            
            # Create personalized explanation
            explanation = f"Analyse de l'ingrédient '{ingredient_name}':\n\n"
            explanation += analysis
            
            # Add skin type specific advice
            if skin_type and skin_type != 'Non spécifié':
                explanation += f"\n\n💡 Conseil pour votre type de peau ({skin_type}): "
                if 'sensible' in skin_type.lower():
                    explanation += "Testez toujours cet ingrédient sur une petite zone avant utilisation complète."
                elif 'sèche' in skin_type.lower():
                    explanation += "Cet ingrédient peut être bénéfique pour votre peau sèche."
                elif 'grasse' in skin_type.lower():
                    explanation += "Cet ingrédient peut aider à réguler la production de sébum."
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating ingredient explanation: {str(e)}")
            return f"Analyse de l'ingrédient '{ingredient_name}':\n\n{analysis}"
    
    def _generate_ingredient_alerts(self, ingredient_name: str, analysis: str, context_data: Dict[str, Any]) -> List[str]:
        """
        Generate alerts for ingredient based on user context.
        
        Args:
            ingredient_name: Name of the ingredient
            analysis: Analysis result
            context_data: User context including allergies
            
        Returns:
            List[str]: List of alerts
        """
        alerts = []
        
        try:
            # Check for allergies
            user_allergies = context_data.get('allergies', [])
            for allergy in user_allergies:
                if allergy['ingredient'].lower() in ingredient_name.lower():
                    alerts.append(f"⚠️ Attention : Vous êtes allergique à {allergy['ingredient']}")
            
            # Check for sensitive skin
            skin_type = context_data.get('user_profile', {}).get('skin_type', '')
            if 'sensible' in skin_type.lower():
                alerts.append("⚠️ Testez cet ingrédient sur une petite zone avant utilisation complète")
            
            # Add general safety reminder
            alerts.append("💡 Consultez toujours la liste INCI et faites un test patch")
            
        except Exception as e:
            logger.error(f"Error generating ingredient alerts: {str(e)}")
            alerts.append("⚠️ Erreur lors de la génération des alertes")
        
        return alerts
    
    def _suggest_ingredient_alternatives(self, question: str, context_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Suggest alternative ingredients based on user profile.
        
        Args:
            question: User's question about ingredients
            context_data: User context including profile
            
        Returns:
            List of alternative ingredient suggestions
        """
        alternatives = []
        skin_type = context_data['user_profile']['skin_type']
        
        # Handle skin_type - convert list to string if necessary
        if isinstance(skin_type, list):
            skin_type = skin_type[0] if skin_type else None
        elif not skin_type:
            skin_type = None
        
        # Suggest alternatives based on skin type
        if skin_type == 'sensitive':
            alternatives.append({
                "ingredient": "acide hyaluronique",
                "alternative": "glycérine",
                "raison": "Plus doux pour les peaux sensibles"
            })
        
        return alternatives
    
    def _generate_general_response(self, question: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate general skincare advice response with natural, conversational tone.
        
        Args:
            question: User's general question
            context_data: User context and profile information
            
        Returns:
            Dict containing natural advice and recommendations
        """
        try:
            # Build personalized prompt for natural response
            prompt = self._build_natural_general_prompt(question, context_data)
            
            # Get AI response using real AI service
            ai_response = self._call_ai_service(prompt)
            
            # Log the response for debugging
            logger.info(f"AI Response for general question: {ai_response[:200]}...")
            
            return {
                'type': 'natural_response',
                'answer': ai_response,
                'user_profile_used': {
                    'skin_type': context_data.get('user_profile', {}).get('skin_type', 'N/A'),
                    'age_range': context_data.get('user_profile', {}).get('age_range', 'N/A'),
                    'allergies': context_data.get('user_profile', {}).get('allergies', []),
                    'conditions': context_data.get('user_profile', {}).get('dermatological_conditions', [])
                },
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error generating general response: {str(e)}")
            return {
                'type': 'natural_response',
                'answer': 'Je suis désolé, je ne peux pas répondre à votre question pour le moment. Veuillez réessayer plus tard.',
                'user_profile_used': {},
                'timestamp': self._get_current_timestamp()
            }
    
    def _build_natural_general_prompt(self, question: str, context_data: Dict[str, Any]) -> str:
        """
        Build natural, conversational prompt for general questions.
        
        Args:
            question: User's general question
            context_data: User context information
            
        Returns:
            str: Natural prompt for AI
        """
        user_profile = context_data.get('user_profile', {})
        skin_type = user_profile.get('skin_type', 'Non spécifié')
        age_range = user_profile.get('age_range', 'Non spécifié')
        allergies = user_profile.get('allergies', [])
        conditions = user_profile.get('dermatological_conditions', [])
        
        allergies_text = ", ".join(allergies) if allergies else "aucune"
        conditions_text = ", ".join(conditions) if conditions else "aucune"
        
        prompt = f"""
Tu es un expert en cosmétiques et soins de la peau. Réponds directement et de façon concise à la question de l'utilisateur.

## Profil Utilisateur
Type de peau: {skin_type} | Âge: {age_range} | Allergies: {allergies_text} | Conditions: {conditions_text}

## Question
{question}

## Instructions
- Réponds DIRECTEMENT à la question posée, sans ajouter d'informations non demandées
- Adapte ta réponse au profil utilisateur (allergies, type de peau, âge)
- Sois concis et précis
- Mentionne uniquement les précautions liées au profil si pertinentes
- Utilise un ton professionnel mais accessible
- Ne génère PAS de routine ou de conseils généraux sauf si explicitement demandé

Réponds comme si tu répondais à une question ponctuelle, de façon naturelle et directe.
        """
        
        return prompt.strip()
    
    def _get_current_timestamp(self) -> str:
        """Retourne le timestamp actuel."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _build_ingredient_prompt(self, ingredient_name: str, context_data: Dict[str, Any]) -> str:
        """
        Build personalized prompt for ingredient analysis.
        
        Args:
            ingredient_name: Name of the ingredient to analyze
            context_data: User context information
            
        Returns:
            str: Personalized prompt for AI
        """
        # Get user skin type for personalization
        skin_type = context_data.get('user_profile', {}).get('skin_type', 'Non spécifié')
        if isinstance(skin_type, list):
            skin_type = ", ".join(skin_type) if skin_type else "Non spécifié"
        
        # Get user allergies
        allergies = context_data.get('allergies', [])
        allergy_text = ""
        if allergies:
            allergy_list = [a['ingredient'] for a in allergies]
            allergy_text = f"\nAllergies de l'utilisateur: {', '.join(allergy_list)}"
        
        prompt = f"""
        Analysez l'ingrédient cosmétique "{ingredient_name}" en français.
        
        Contexte utilisateur:
        - Type de peau: {skin_type}{allergy_text}
        
        Fournissez une analyse détaillée incluant:
        1. Description et fonction de l'ingrédient
        2. Avantages pour la peau
        3. Risques potentiels et précautions
        4. Compatibilité avec le type de peau de l'utilisateur
        5. Conseils d'utilisation
        6. Alternatives si nécessaire
        
        Répondez de manière claire et accessible en français.
        """
        
        return prompt
    
    def _build_general_prompt(self, question: str, context_data: Dict[str, Any]) -> str:
        """
        Build personalized prompt for general skincare questions.
        
        Args:
            question: User's question
            context_data: User context information
            
        Returns:
            str: Personalized prompt for AI
        """
        # Get user profile information
        user_profile = context_data.get('user_profile', {})
        skin_type = user_profile.get('skin_type', 'Non spécifié')
        age_range = user_profile.get('age_range', 'Non spécifié')
        concerns = user_profile.get('skin_concerns', 'Aucune')
        
        # Handle list types
        if isinstance(skin_type, list):
            skin_type = ", ".join(skin_type) if skin_type else "Non spécifié"
        if isinstance(concerns, list):
            concerns = ", ".join(concerns) if concerns else "Aucune"
        
        prompt = f"""
        Répondez à cette question sur les soins de la peau en français :
        
        Question : {question}
        
        Contexte utilisateur :
        - Type de peau : {skin_type}
        - Tranche d'âge : {age_range}
        - Préoccupations : {concerns}
        
        Fournissez une réponse personnalisée et utile en tenant compte du profil utilisateur.
        Incluez des conseils pratiques et des recommandations adaptées.
        """
        
        return prompt
    
    def _extract_recommendations_from_response(self, response: str) -> List[str]:
        """
        Extract recommendations from AI response.
        
        Args:
            response: AI response text
            
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        # Simple extraction based on common patterns
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                recommendations.append(line.lstrip('•-*123456789. '))
            elif 'conseil' in line.lower() or 'recommandation' in line.lower():
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _generate_related_questions(self, original_question: str) -> List[str]:
        """
        Generate related questions based on the original question.
        
        Args:
            original_question: User's original question
            
        Returns:
            List[str]: List of related questions
        """
        question_lower = original_question.lower()
        
        related_questions = []
        
        if 'routine' in question_lower:
            related_questions.extend([
                "Quels produits sont essentiels pour ma routine ?",
                "Dans quel ordre appliquer mes produits ?",
                "Combien de fois par jour dois-je faire ma routine ?"
            ])
        elif 'ingrédient' in question_lower or 'composant' in question_lower:
            related_questions.extend([
                "Quels ingrédients éviter pour ma peau ?",
                "Quels sont les ingrédients les plus sûrs ?",
                "Comment lire une liste INCI ?"
            ])
        elif 'allergie' in question_lower or 'irritation' in question_lower:
            related_questions.extend([
                "Comment tester un nouveau produit ?",
                "Que faire en cas de réaction allergique ?",
                "Quels produits pour peau sensible ?"
            ])
        else:
            related_questions.extend([
                "Comment choisir mes produits de soin ?",
                "Quelle routine pour mon type de peau ?",
                "Comment prendre soin de ma peau au quotidien ?"
            ])
        
        return related_questions[:3]  # Limit to 3 related questions
    
    def _extract_personalized_tips(self, ai_response: str) -> List[str]:
        """Extract personalized tips from AI response."""
        # Simple extraction - in a real implementation, this would use NLP
        tips = []
        lines = ai_response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['conseil', 'astuce', 'tip', 'recommandation']):
                tips.append(line.strip())
        return tips[:3]  # Limit to 3 tips
    
    def _suggest_related_questions(self, original_question: str) -> List[str]:
        """Suggest related questions based on the original question."""
        related_questions = [
            "Comment adapter ma routine selon la saison ?",
            "Quels ingrédients éviter avec mon type de peau ?",
            "Comment optimiser l'efficacité de mes produits ?"
        ]
        return related_questions
    
    def _get_user_context_summary(self, profile: UserProfile) -> Dict[str, str]:
        """
        Get summary of user context for display.
        
        Args:
            profile: User profile containing skin information
            
        Returns:
            Dict containing user context summary for display
        """
        # Handle skin_type - convert list to string if necessary
        skin_type = profile.skin_type
        if isinstance(skin_type, list):
            skin_type = ", ".join(skin_type) if skin_type else "Non spécifié"
        elif not skin_type:
            skin_type = "Non spécifié"
        
        # Handle skin_concerns - convert list to string if necessary
        concerns = profile.skin_concerns
        if isinstance(concerns, list):
            concerns = ", ".join(concerns) if concerns else "Aucune préoccupation spécifique"
        elif not concerns:
            concerns = "Aucune préoccupation spécifique"
        
        return {
            'skin_type': skin_type,
            'age_range': profile.age_range or 'Non spécifié',
            'budget': profile.budget or 'Non spécifié',
            'concerns': concerns
        }
    
    def _generate_alerts(self, profile: UserProfile, context_data: Dict[str, Any]) -> List[str]:
        """Generate alerts based on user profile and context."""
        alerts = []
        
        # Check for missing profile information
        if not profile.skin_type:
            alerts.append("ℹ️ Complétez votre profil pour des recommandations plus précises")
        
        # Check for allergies
        if context_data['allergies']:
            alerts.append("⚠️ Vos allergies ont été prises en compte dans les recommandations")
        
        # Check for recent scans with low scores
        recent_scans = context_data['scan_history']
        low_score_products = [scan for scan in recent_scans if scan.get('score', 100) is not None and scan.get('score', 100) < 50]
        if low_score_products:
            alerts.append("⚠️ Certains produits récemment scannés ont un score de sécurité faible")
        
        return alerts
    
    def _call_ai_service(self, prompt: str) -> str:
        """
        Call AI service (Ollama or external API) to get response.
        
        Args:
            prompt: The prompt to send to the AI service
            
        Returns:
            str: AI response
        """
        try:
            # Check if fallback mode is enabled for development
            if getattr(settings, 'ENABLE_AI_FALLBACK_MODE', False):
                logger.info("Using development fallback mode for AI responses")
                return self._generate_fallback_response(prompt)
            
            # Try Ollama first (local AI)
            if hasattr(settings, 'OLLAMA_URL') and settings.OLLAMA_URL:
                return self._call_ollama(prompt)
            
            # Fallback to external API if configured
            elif hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                return self._call_openai(prompt)
            
            # If no AI service configured, return fallback response
            else:
                logger.warning("No AI service configured, using fallback response")
                return self._generate_fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Error calling AI service: {str(e)}")
            return self._generate_fallback_response(prompt)
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama local AI service."""
        try:
            import requests
            
            ollama_url = getattr(settings, 'OLLAMA_URL', 'http://localhost:11434')
            model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2')
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            raise
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API service."""
        try:
            import openai
            
            openai.api_key = settings.OPENAI_API_KEY
            model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en dermatologie et soins de la peau. Répondez en français."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            raise
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """
        Generate comprehensive fallback response when AI services are unavailable.
        
        This method provides realistic responses for development and testing purposes.
        """
        prompt_lower = prompt.lower()
        
        # Routine requests
        if 'routine' in prompt_lower:
            if 'matin' in prompt_lower:
                return self._generate_fallback_morning_routine()
            elif 'soir' in prompt_lower:
                return self._generate_fallback_evening_routine()
            elif 'cheveux' in prompt_lower:
                return self._generate_fallback_hair_routine()
            elif 'corps' in prompt_lower:
                return self._generate_fallback_body_routine()
            else:
                return self._generate_fallback_morning_routine()
        
        # Ingredient questions
        elif any(keyword in prompt_lower for keyword in ['ingrédient', 'composant', 'acide', 'vitamine']):
            return self._generate_fallback_ingredient_response(prompt)
        
        # General skincare questions
        else:
            return self._generate_fallback_general_response(prompt)
    
    def _generate_fallback_morning_routine(self) -> str:
        """Generate fallback morning routine response."""
        return """
        Voici votre routine matin personnalisée :

        🌅 **Routine Matin**

        1. **Nettoyant doux** - La Roche-Posay Toleriane Caring Wash (15€)
           Score: 92/100 - Nettoyage respectueux de la barrière cutanée

        2. **Sérum hydratant** - The Ordinary Acide Hyaluronique 2% + B5 (7€)
           Score: 88/100 - Hydratation intense et réparation

        3. **Crème hydratante** - CeraVe Moisturizing Cream (12€)
           Score: 90/100 - Hydratation 24h avec céramides

        4. **Protection solaire** - Bioderma Photoderm MAX Aquafluide (18€)
           Score: 94/100 - Protection SPF50+ invisible

        💡 **Conseils d'application** : Appliquez les produits du plus léger au plus épais. Attendez 2-3 minutes entre chaque étape pour une meilleure pénétration.

        ⚠️ **Rappel** : N'oubliez pas votre protection solaire même en hiver !
        """
    
    def _generate_fallback_evening_routine(self) -> str:
        """Generate fallback evening routine response."""
        return """
        Voici votre routine soir personnalisée :

        🌙 **Routine Soir**

        1. **Démaquillant** - Bioderma Sensibio H2O (12€)
           Score: 91/100 - Démaquillage doux et efficace

        2. **Nettoyant** - Avène Cleanance Cleansing Gel (10€)
           Score: 87/100 - Nettoyage en profondeur

        3. **Sérum actif** - The Ordinary Niacinamide 10% + Zinc 1% (6€)
           Score: 89/100 - Régulation du sébum et anti-imperfections

        4. **Crème de nuit** - La Roche-Posay Cicaplast Baume B5 (8€)
           Score: 93/100 - Réparation et apaisement nocturne

        💡 **Conseils d'application** : Le soir, privilégiez les actifs réparateurs. Évitez les exfoliants si votre peau est sensible.

        ⚠️ **Rappel** : Laissez votre peau respirer la nuit, évitez les formules trop occlusives.
        """
    
    def _generate_fallback_hair_routine(self) -> str:
        """Generate fallback hair routine response."""
        return """
        Voici votre routine cheveux personnalisée :

        💇‍♀️ **Routine Cheveux**

        1. **Shampoing** - Klorane Shampooing à la Camomille (14€)
           Score: 88/100 - Douceur et brillance naturelle

        2. **Après-shampoing** - Garnier Fructis Aloe Vera (4€)
           Score: 85/100 - Hydratation et démêlage

        3. **Masque hebdomadaire** - L'Oréal Elvive Extraordinary Oil (8€)
           Score: 87/100 - Nutrition et réparation

        4. **Sérum protecteur** - The Ordinary Multi-Peptide Serum (15€)
           Score: 90/100 - Protection et fortification

        💡 **Conseils d'application** : Massez doucement le cuir chevelu, rincez à l'eau tiède. Utilisez le masque 1-2 fois par semaine.

        ⚠️ **Rappel** : Évitez l'eau trop chaude qui agresse les cheveux.
        """
    
    def _generate_fallback_body_routine(self) -> str:
        """Generate fallback body routine response."""
        return """
        Voici votre routine corps personnalisée :

        🧴 **Routine Corps**

        1. **Gel douche** - Dove Nourishing Secrets (6€)
           Score: 86/100 - Nettoyage doux et hydratant

        2. **Gommage hebdomadaire** - The Body Shop Shea Body Scrub (18€)
           Score: 88/100 - Exfoliation douce et nourrissante

        3. **Lait hydratant** - Nivea Q10 Plus (8€)
           Score: 89/100 - Hydratation et fermeté

        4. **Huile sèche** - Nuxe Huile Prodigieuse (25€)
           Score: 92/100 - Nutrition et éclat

        💡 **Conseils d'application** : Appliquez le lait sur peau humide pour une meilleure pénétration. Le gommage 1-2 fois par semaine maximum.

        ⚠️ **Rappel** : N'oubliez pas les zones sensibles comme les coudes et les genoux.
        """
    
    def _generate_fallback_ingredient_response(self, prompt: str) -> str:
        """Generate fallback ingredient analysis response."""
        return """
        **Analyse d'Ingrédient Cosmétique**

        Voici une analyse détaillée de l'ingrédient demandé :

        🔬 **Description** : Cet ingrédient est un actif cosmétique largement utilisé dans les soins de la peau.

        ✅ **Avantages** :
        - Hydratation en profondeur
        - Amélioration de la texture de la peau
        - Compatible avec la plupart des types de peau
        - Résultats visibles rapidement

        ⚠️ **Précautions** :
        - Test patch recommandé pour les peaux sensibles
        - Éviter en cas d'allergie connue
        - Respecter les concentrations recommandées

        💡 **Conseils d'utilisation** :
        - Appliquer sur peau propre
        - Commencer par une utilisation progressive
        - Associer avec une protection solaire

        🔍 **Alternatives** : Si cet ingrédient ne vous convient pas, d'autres options similaires peuvent être recommandées selon votre profil.

        ⚠️ **Rappel** : Consultez un dermatologue en cas de doute ou de réaction.
        """
    
    def _generate_fallback_general_response(self, prompt: str) -> str:
        """Generate fallback general skincare advice response."""
        return """
        **Conseils Beauté Personnalisés**

        Voici mes recommandations basées sur votre profil :

        💡 **Conseils Généraux** :
        - Hydratez votre peau matin et soir
        - Protégez-vous du soleil quotidiennement
        - Adaptez votre routine selon les saisons
        - Écoutez votre peau et ajustez selon ses besoins

        🧴 **Produits Recommandés** :
        - Nettoyants doux et respectueux
        - Hydratants adaptés à votre type de peau
        - Actifs ciblés selon vos préoccupations
        - Protection solaire obligatoire

        ⚠️ **Points d'Attention** :
        - Évitez les produits trop agressifs
        - Testez les nouveaux produits progressivement
        - Consultez un professionnel en cas de problème
        - Respectez les dates de péremption

        🔄 **Évolution** : Votre routine peut évoluer selon l'âge, les saisons et les changements de votre peau.

        💬 **Questions Fréquentes** : N'hésitez pas à me poser des questions spécifiques sur vos produits ou préoccupations.
        """
    
    def _parse_ai_routine_response(self, ai_response: str, routine_type: str) -> Dict[str, Any]:
        """
        Parse AI response and extract structured routine data.
        
        Args:
            ai_response: Raw AI response text
            routine_type: Type of routine requested
            
        Returns:
            Dict containing structured routine data
        """
        try:
            # For fallback responses, create structured data from text
            routine_data = {
                'routine': {
                    'matin': [],
                    'soir': []
                }
            }
            
            # Extract products from the AI response text
            lines = ai_response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if 'matin' in line.lower() or '🌅' in line:
                    current_section = 'matin'
                    continue
                elif 'soir' in line.lower() or '🌙' in line:
                    current_section = 'soir'
                    continue
                
                # Extract product information
                if line.startswith(('1.', '2.', '3.', '4.', '5.')) and current_section:
                    product_info = self._extract_product_from_line(line)
                    if product_info:
                        routine_data['routine'][current_section].append(product_info)
            
            return routine_data
            
        except Exception as e:
            logger.error(f"Error parsing AI routine response: {str(e)}")
            return self._create_fallback_routine(routine_type)
    
    def _extract_product_from_line(self, line: str) -> Dict[str, Any]:
        """
        Extract product information from a line of text.
        
        Args:
            line: Line containing product information
            
        Returns:
            Dict containing product data
        """
        try:
            # Remove numbering
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                line = line[2:].strip()
            
            # Extract product name and brand
            if ' - ' in line:
                product_part, rest = line.split(' - ', 1)
                product_name = product_part.strip()
                
                # Extract brand and price
                if ' (' in rest and '€)' in rest:
                    brand_part = rest.split(' (')[0].strip()
                    price_part = rest.split('(')[1].split('€')[0].strip()
                    
                    return {
                        'type': 'produit',
                        'produit': product_name,
                        'marque': brand_part,
                        'prix': float(price_part),
                        'score': 85,  # Default score
                        'explication': f"Produit recommandé pour votre routine"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting product from line: {str(e)}")
            return None
    
    def _extract_explanation_from_ai_response(self, ai_response: str) -> str:
        """
        Extract explanation from AI response.
        
        Args:
            ai_response: Raw AI response text
            
        Returns:
            str: Extracted explanation
        """
        try:
            # Look for explanation section
            if 'Voici votre routine' in ai_response:
                lines = ai_response.split('\n')
                explanation_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(('1.', '2.', '3.', '4.', '5.')) and not '🌅' in line and not '🌙' in line:
                        if 'routine' in line.lower() and 'personnalisée' in line.lower():
                            explanation_lines.append(line)
                            break
                
                if explanation_lines:
                    return explanation_lines[0]
            
            return "Voici votre routine personnalisée adaptée à votre type de peau et vos besoins."
            
        except Exception as e:
            logger.error(f"Error extracting explanation: {str(e)}")
            return "Voici votre routine personnalisée."
    
    def _format_routine_as_text(self, routine_data: Dict[str, Any]) -> str:
        """Convert routine dictionary to text format for AI response."""
        text = ""
        
        if 'routine' in routine_data:
            routine = routine_data['routine']
            
            # Morning routine
            if 'matin' in routine and routine['matin']:
                text += "Routine du matin:\n"
                for i, product in enumerate(routine['matin'], 1):
                    text += f"{i}. {product['produit']} - {product['marque']} ({product['prix']}€)\n"
                    if product.get('explication'):
                        text += f"   {product['explication']}\n"
                text += "\n"
            
            # Evening routine
            if 'soir' in routine and routine['soir']:
                text += "Routine du soir:\n"
                for i, product in enumerate(routine['soir'], 1):
                    text += f"{i}. {product['produit']} - {product['marque']} ({product['prix']}€)\n"
                    if product.get('explication'):
                        text += f"   {product['explication']}\n"
                text += "\n"
        
        # Add global explanation
        if 'explication_globale' in routine_data:
            text += f"Explication: {routine_data['explication_globale']}\n\n"
        
        # Add tips
        if 'conseils' in routine_data:
            text += "Conseils d'application:\n"
            for i, conseil in enumerate(routine_data['conseils'], 1):
                text += f"{i}. {conseil}\n"
        
        return text

    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response when processing fails."""
        return {
            'type': 'error',
            'explanation': f"Désolé, une erreur s'est produite: {error_message}",
            'routine': {'matin': [], 'soir': []},
            'alternatives': [],
            'alerts': ["Une erreur technique s'est produite. Veuillez réessayer."],
            'suggested_questions': self.suggested_questions
        }


class PremiumRoutineManager:
    """
    Manager for Premium routine operations including saving, updating, and tracking.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.ai_service = PremiumAIService()
    
    def create_personalized_routine(
        self, 
        routine_type: str, 
        budget_filter: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create and save a personalized routine for the user.
        
        Args:
            routine_type: Type of routine (morning, evening, hair, body)
            budget_filter: Optional budget limit
            
        Returns:
            Dictionary with routine data and metadata
        """
        # Generate routine using AI service
        question = f"Routine {routine_type}"
        response = self.ai_service.process_premium_request(
            user=self.user,
            question=question,
            budget_filter=budget_filter
        )
        
        # Save routine to database
        if response.get('type') == 'routine' and response.get('routine'):
            routine_data = response['routine']
            saved_routine = self._save_routine_to_db(routine_type, routine_data)
            response['routine_id'] = saved_routine.id
        
        return response
    
    def _save_routine_to_db(self, routine_type: str, routine_data: Dict[str, Any]) -> 'Routine':
        """Save routine data to database."""
        from apps.ai_routines.models import Routine
        
        routine = Routine.objects.create(
            user=self.user,
            name=f"Routine {routine_type.title()} - {self.user.username}",
            routine_type=routine_type,
            description=routine_data.get('explication_globale', ''),
            steps=routine_data.get('routine', {}),
            is_active=True
        )
        
        return routine
    
    def get_user_routines(self, routine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's saved routines."""
        from apps.ai_routines.models import Routine
        
        queryset = Routine.objects.filter(user=self.user, is_active=True)
        if routine_type:
            queryset = queryset.filter(routine_type=routine_type)
        
        routines = []
        for routine in queryset.order_by('-created_at'):
            routines.append({
                'id': routine.id,
                'name': routine.name,
                'type': routine.routine_type,
                'description': routine.description,
                'steps': routine.steps,
                'created_at': routine.created_at.isoformat(),
                'is_active': routine.is_active
            })
        
        return routines
    
    def update_routine_budget(self, routine_id: int, new_budget: float) -> Dict[str, Any]:
        """Update routine with new budget constraints."""
        from apps.ai_routines.models import Routine
        
        try:
            routine = Routine.objects.get(id=routine_id, user=self.user)
            
            # Regenerate routine with new budget
            response = self.ai_service.process_premium_request(
                user=self.user,
                question=f"Routine {routine.routine_type}",
                budget_filter=new_budget
            )
            
            # Update existing routine
            if response.get('type') == 'routine' and response.get('routine'):
                routine.steps = response['routine']
                routine.save()
                response['routine_id'] = routine.id
            
            return response
            
        except Routine.DoesNotExist:
            return {'error': 'Routine non trouvée'}
    
    def log_routine_usage(self, routine_id: int, rating: Optional[int] = None, notes: str = "") -> bool:
        """Log routine usage for tracking and improvement."""
        from apps.ai_routines.models import Routine, UserRoutineLog
        
        try:
            routine = Routine.objects.get(id=routine_id, user=self.user)
            
            UserRoutineLog.objects.create(
                user=self.user,
                routine=routine,
                rating=rating,
                notes=notes
            )
            
            return True
            
        except Routine.DoesNotExist:
            return False
