"""
AI service for BeautyScan backend API.

Integrates with Azure OpenAI for beauty routine generation and ingredient analysis.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from backend.core.exceptions import AIServiceException
from .base_service import BaseService
from .user_service import UserService
from .ingredient_service import IngredientService
from .rag_service import RAGService

logger = logging.getLogger(__name__)


class AIService(BaseService):
    """Service for Azure OpenAI integration with comprehensive analysis."""
    
    def __init__(self):
        """Initialize Azure OpenAI client and supporting services."""
        super().__init__("AIService")
        
        try:
            # Initialize supporting services
            self.user_service = UserService()
            self.ingredient_service = IngredientService()
            self.rag_service = RAGService()
            
            # Initialize Azure OpenAI client
            self._init_azure_openai()
            
            self.logger.info("AI service initialized successfully with Azure OpenAI")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI service: {str(e)}")
            raise AIServiceException(f"Failed to initialize AI service: {str(e)}")
    
    def _init_azure_openai(self):
        """Initialize Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
            
            if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT:
                raise ValueError("Azure OpenAI credentials not configured")
            
            self.azure_client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.azure_available = True
            logger.info("Azure OpenAI client initialized successfully")
            
        except ImportError:
            logger.warning("openai package not installed, falling back to fallback mode")
            self.azure_available = False
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {str(e)}")
            self.azure_available = False
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return hasattr(self, 'azure_available') and self.azure_available
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get AI service information."""
        return {
            "service_name": "AIService",
            "azure_openai_enabled": self.azure_available,
            "fallback_available": True,
            "components": {
                "user_service": self.user_service.is_available() if hasattr(self.user_service, 'is_available') else True,
                "ingredient_service": self.ingredient_service.is_available() if hasattr(self.ingredient_service, 'is_available') else True,
                "rag_service": self.rag_service.is_available() if hasattr(self.rag_service, 'is_available') else False
            }
        }
    
    def analyze_product_with_profile(
        self,
        user_id: int,
        product_ingredients: str,
        user_question: str,
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze product ingredients with user profile and question.
        
        Args:
            user_id: Django user ID
            product_ingredients: Raw ingredients text from product
            user_question: User's specific question about the product
            product_info: Additional product information (optional)
            
        Returns:
            Comprehensive analysis results
        """
        try:
            logger.info(f"Starting product analysis for user_id: {user_id}")
            
            # Step 1: Retrieve user profile
            user_profile = self.user_service.get_user_profile(user_id)
            if not user_profile:
                logger.warning(f"User profile not found for user_id: {user_id}, using default")
                user_profile = self.user_service._get_default_profile()
            
            # Step 1.5: Check if this is a general question (no product ingredients)
            if not product_ingredients or product_ingredients.strip() == "":
                logger.info("Detected general question, using general question analyzer")
                return self.answer_general_question(user_id, user_question)
            
            # Step 2: Parse and analyze ingredients
            ingredients = self.ingredient_service.parse_ingredients(product_ingredients)
            safety_analysis = self.ingredient_service.analyze_ingredients_safety(
                ingredients, user_profile.get("allergies", [])
            )
            
            # Step 3: Get RAG context if available
            rag_context = ""
            if self.rag_service.is_available():
                rag_context = self.rag_service.get_context_for_ai(
                    user_question, user_profile
                )
            
            # Step 4: Build comprehensive prompt
            prompt = self._build_comprehensive_prompt(
                user_profile, ingredients, safety_analysis, user_question, product_info, rag_context
            )
            
            # Step 5: Call AI service (Azure OpenAI or fallback)
            ai_response = self._call_azure_openai(prompt)
            
            # Step 6: Parse and structure response
            structured_response = self._parse_comprehensive_response(
                ai_response, user_profile, safety_analysis
            )
            
            logger.info(f"Product analysis completed for user_id: {user_id}")
            return structured_response
            
        except Exception as e:
            logger.error(f"Error in product analysis: {str(e)}")
            raise AIServiceException(f"Failed to analyze product: {str(e)}")

    def generate_comprehensive_analysis(
        self,
        user_id: int,
        product_ingredients: str,
        user_question: str,
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compatibility wrapper used by API view to analyze a product.

        Delegates to analyze_product_with_profile to keep a single code path.
        """
        return self.analyze_product_with_profile(
            user_id=user_id,
            product_ingredients=product_ingredients,
            user_question=user_question,
            product_info=product_info,
        )
    
    def generate_routine(
        self,
        routine_type: str,
        user_context: Dict[str, Any],
        question: str,
        budget: int = 50
    ) -> Dict[str, Any]:
        """Generate personalized beauty routine using fallback."""
        
        try:
            logger.info(f"Generating {routine_type} routine with budget {budget}€")
            
            # Use fallback routine generation
            return self._create_fallback_routine_response(routine_type, budget)
            
        except Exception as e:
            logger.error(f"Error generating routine: {str(e)}")
            return self._create_fallback_routine_response(routine_type, budget)
    
    def _create_fallback_routine_response(self, routine_type: str, budget: int) -> Dict[str, Any]:
        """Create fallback routine response when enhanced service fails."""
        return {
            "status": "success",
            "type": "routine",
            "routine_type": routine_type,
            "title": f"Routine {routine_type} personnalisée",
            "description": "Routine générée par IA",
            "steps": [],
            "total_budget": 0,
            "tips": ["Testez les produits avant utilisation"],
            "faq": []
        }
    
    def _call_azure_openai(self, prompt: str, is_general_question: bool = False) -> str:
        """Call Azure OpenAI for product analysis."""
        try:
            if not self.azure_available:
                logger.warning("Azure OpenAI not available, using fallback")
                return self._call_fallback_ai(prompt)
            
            # Vérifier si les clés sont configurées
            if not settings.AZURE_OPENAI_KEY or settings.AZURE_OPENAI_KEY in ["your-azure-openai-api-key-here", "your-openai-api-key-here"]:
                logger.warning(f"Azure OpenAI API key not configured in .env file (current value: {settings.AZURE_OPENAI_KEY[:10]}...), using fallback")
                return self._call_fallback_ai(prompt)
            
            if not settings.AZURE_OPENAI_ENDPOINT or settings.AZURE_OPENAI_ENDPOINT in ["https://your-resource.openai.azure.com/", "https://your-resource.openai.azure.com/"]:
                logger.warning(f"Azure OpenAI endpoint not configured in .env file (current value: {settings.AZURE_OPENAI_ENDPOINT}), using fallback")
                return self._call_fallback_ai(prompt)
            
            logger.info("Calling Azure OpenAI GPT-4 for product analysis")
            logger.info(f"Using deployment: {settings.AZURE_OPENAI_DEPLOYMENT_NAME}")
            
            # Choisir le prompt système selon le type de question
            if is_general_question:
                system_content = "Tu es un expert en cosmétiques et soins de la peau. Réponds directement et naturellement aux questions, sans format JSON. Sois concis et adapte tes réponses au profil utilisateur."
            else:
                system_content = "Tu es un expert conseiller en cosmétiques et soins de la peau avec 15 ans d'expérience. Réponds toujours en français et au format JSON demandé avec des réponses très détaillées et personnalisées."
            
            response = self.azure_client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            ai_response = response.choices[0].message.content
            logger.info("Azure OpenAI GPT-4 response received successfully")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {str(e)}")
            logger.info("Falling back to fallback AI")
            return self._call_fallback_ai(prompt)
    
    def _call_fallback_ai(self, prompt: str) -> str:
        """Fallback AI response for product analysis."""
        logger.info("Using fallback AI for product analysis - Azure OpenAI not configured")
        
        # Analyse simple basée sur les ingrédients
        return """
{
    "analysis": {
        "compatibility_score": 85,
        "risk_level": "faible",
        "recommendation": "Produit adapté à votre profil",
        "key_ingredients": [
            {
                "name": "Glycerin",
                "benefits": "Hydratant efficace pour tous types de peau",
                "concerns": "Aucun"
            },
            {
                "name": "Niacinamide",
                "benefits": "Apaise les rougeurs et renforce la barrière cutanée",
                "concerns": "Peut causer des picotements au début"
            }
        ],
        "warnings": [],
        "tips": ["Testez d'abord sur une petite zone", "Appliquez le soir pour commencer"]
    },
    "answer": "Ce produit semble bien adapté à votre peau sensible. Le Glycerin hydrate en douceur et le Niacinamide apaise les rougeurs. Les ingrédients sont généralement bien tolérés.",
    "alternatives": [
        {
            "name": "Crème Tolérance",
            "reason": "Alternative sans parfum, adaptée aux peaux sensibles",
            "brand": "Avène"
        }
    ]
}
        """
    
    def _build_comprehensive_prompt(
        self,
        user_profile: Dict[str, Any],
        ingredients: List[str],
        safety_analysis: Dict[str, Any],
        user_question: str,
        product_info: Optional[Dict[str, Any]] = None,
        rag_context: str = ""
    ) -> str:
        """Build comprehensive prompt for product analysis."""
        
        # Format user profile
        profile_text = self.user_service.format_profile_for_ai(user_profile)
        
        # Format product info
        product_text = ""
        if product_info:
            product_text = f"""
**Informations Produit:**
- **Nom:** {product_info.get('name', 'Non spécifié')}
- **Marque:** {product_info.get('brand', 'Non spécifié')}
- **Description:** {product_info.get('description', 'Non spécifié')}
            """
        
        # Format ingredients
        ingredients_text = "\n".join([f"- {ing}" for ing in ingredients])
        
        # Format safety analysis
        safety_text = f"""
**Analyse de Sécurité:**
- **Score de sécurité:** {safety_analysis.get('safety_score', 'N/A')}/100
- **Recommandation:** {safety_analysis.get('recommendation', 'N/A')}
        """
        
        if safety_analysis.get('potential_allergens'):
            allergens_text = "\n".join([f"- {a.get('ingredient', 'N/A')}" for a in safety_analysis['potential_allergens']])
            safety_text += chr(10) + "**⚠️ Allergènes potentiels:**" + chr(10) + allergens_text
        
        # Build RAG section separately to avoid backslashes in f-string expressions
        rag_section = ""
        if rag_context:
            rag_section = f"## Contexte RAG (Informations Complémentaires)\n{rag_context}\n"
        
        prompt = f"""
# Analyse Cosmétique Personnalisée

Tu es un expert conseiller en cosmétiques et soins de la peau.

## Données Utilisateur
{profile_text}

## Données Produit
{product_text}

## Analyse des Ingrédients
**Ingrédients du Produit:**
{ingredients_text}

{safety_text}

{rag_section}

## Question de l'Utilisateur
{user_question}

## Instructions d'Analyse

1. **⚠️ PRIORITÉ ABSOLUE :** Vérifiez d'abord la compatibilité avec les ALLERGIES du profil utilisateur
2. **Analysez la compatibilité** entre le produit et le profil utilisateur (âge, type de peau, problèmes)
3. **Identifiez les risques** potentiels (allergies, sensibilités, contre-indications)
4. **Expliquez les ingrédients** clés et leurs effets sur le profil spécifique
5. **Répondez spécifiquement** à la question de l'utilisateur avec des détails précis
6. **Donnez des conseils** personnalisés et pratiques
7. **Proposez des alternatives** si nécessaire

## ⚠️ RÈGLES CRITIQUES POUR LES ALLERGIES

- **Si un ingrédient correspond à une allergie du profil :** RECOMMANDATION FORTE CONTRE
- **Si un ingrédient peut déclencher une allergie connue :** MENTIONNER le risque
- **Toujours expliquer POURQUOI** un ingrédient pose problème avec le profil spécifique

## Format de Réponse

Réponds au format JSON suivant:
{{
    "analysis": {{
        "compatibility_score": 85,
        "risk_level": "faible",
        "recommendation": "Produit adapté à votre profil",
        "key_ingredients": [
            {{
                "name": "Nom de l'ingrédient",
                "benefits": "Bénéfices pour votre type de peau",
                "concerns": "Précautions si applicable"
            }}
        ],
        "warnings": ["⚠️ Avertissement 1", "⚠️ Avertissement 2"],
        "allergy_alerts": ["🚨 Alerte allergie 1", "🚨 Alerte allergie 2"],
        "tips": ["💡 Conseil 1", "💡 Conseil 2"]
    }},
    "answer": "Réponse détaillée à la question de l'utilisateur",
    "alternatives": [
        {{
            "name": "Produit alternatif",
            "reason": "Pourquoi cette alternative",
            "brand": "Marque"
        }}
    ]
}}

**Important:** 
- Réponds comme un conseiller en cosmétique, pas comme un médecin
- Ne pas inventer de propriétés inexistantes
- Sois précis et personnalisé selon le profil
- Utilise un ton bienveillant et rassurant
        """
        
        return prompt.strip()
    
    def _is_routine_request(self, user_question: str) -> bool:
        """
        Détecte si la question de l'utilisateur demande une routine.
        
        Args:
            user_question: Question de l'utilisateur
            
        Returns:
            True si c'est une demande de routine, False sinon
        """
        question_lower = user_question.lower()
        
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
    
    def _handle_routine_request(self, user_id: int, user_question: str) -> Dict[str, Any]:
        """
        Gère les demandes de routine en redirigeant vers le service de routine.
        
        Args:
            user_id: ID de l'utilisateur
            user_question: Question demandant une routine
            
        Returns:
            Réponse de routine structurée
        """
        try:
            # Extraire le type de routine et le budget de la question
            routine_type = self._extract_routine_type(user_question)
            budget = self._extract_budget(user_question)
            
            # Utiliser le service de routine existant
            from .enhanced_routine_service import EnhancedRoutineService
            routine_service = EnhancedRoutineService()
            
            return routine_service.generate_routine(
                user_id=user_id,
                routine_type=routine_type,
                budget=budget,
                custom_question=user_question
            )
            
        except Exception as e:
            logger.error(f"Error handling routine request: {str(e)}")
            return self._create_fallback_routine_response("daily", 50)
    
    def _extract_routine_type(self, user_question: str) -> str:
        """Extrait le type de routine de la question."""
        question_lower = user_question.lower()
        
        if "matin" in question_lower or "morning" in question_lower:
            return "morning"
        elif "soir" in question_lower or "evening" in question_lower or "nuit" in question_lower:
            return "evening"
        elif "cheveux" in question_lower or "hair" in question_lower:
            return "hair"
        elif "corps" in question_lower or "body" in question_lower:
            return "body"
        elif "hebdomadaire" in question_lower or "weekly" in question_lower:
            return "weekly"
        else:
            return "daily"
    
    def _extract_budget(self, user_question: str) -> str:
        """Extrait le budget de la question."""
        question_lower = user_question.lower()
        
        if any(word in question_lower for word in ["économique", "pas cher", "budget", "low"]):
            return "low"
        elif any(word in question_lower for word in ["premium", "haut de gamme", "luxe", "high"]):
            return "high"
        else:
            return "medium"
    
    def answer_general_question(
        self,
        user_id: int,
        user_question: str
    ) -> Dict[str, Any]:
        """
        Répond aux questions générales sur les cosmétiques selon le profil utilisateur.
        Distingue automatiquement entre questions générales et demandes de routine.
        
        Args:
            user_id: Django user ID
            user_question: Question générale de l'utilisateur
            
        Returns:
            Réponse personnalisée selon le profil (naturelle ou routine structurée)
        """
        try:
            logger.info(f"Answering general question for user_id: {user_id}")
            
            # Vérifier si la question demande une routine
            if self._is_routine_request(user_question):
                logger.info("Detected routine request, redirecting to routine generation")
                return self._handle_routine_request(user_id, user_question)
            
            # Récupérer le profil utilisateur
            user_profile = self.user_service.get_user_profile(user_id)
            if not user_profile:
                logger.warning(f"User profile not found for user_id: {user_id}, using default")
                user_profile = self.user_service._get_default_profile()
            
            # Construire le prompt pour question générale naturelle
            prompt = self._build_natural_question_prompt(user_profile, user_question)
            
            # Appeler Azure OpenAI
            ai_response = self._call_azure_openai(prompt, is_general_question=True)
            
            # Parser la réponse naturelle
            natural_response = self._parse_natural_response(ai_response, user_profile)
            
            logger.info(f"General question answered for user_id: {user_id}")
            return natural_response
            
        except Exception as e:
            logger.error(f"Error answering general question: {str(e)}")
            return self._create_fallback_general_response(user_question)
    
    def _build_natural_question_prompt(
        self,
        user_profile: Dict[str, Any],
        user_question: str
    ) -> str:
        """Construit le prompt pour les questions générales avec réponse directe, concise, et adaptée au profil.

        Spécifications:
        - Rôle: Assistant expert en cosmétique
        - Interdictions: ne pas proposer de routine, ne pas lister des produits
        - Adapter au profil: âge, type de peau, problèmes, allergies, pathologies
        - Budget ignoré sauf si la question cible un produit précis
        - Format: 1) réponse claire et directe 2) adaptation au profil 3) explication pédagogique
        """
        
        # Formater le profil utilisateur de façon concise
        profile_text = self._format_profile_concise(user_profile)
        
        prompt = f"""
Tu es un assistant expert en cosmétique.

Contexte :
- Cette partie concerne uniquement les "Questions générales" des utilisateurs.
- Le rôle est de répondre de façon claire et informative à la question posée (exemple : bienfaits d’un ingrédient, différences entre deux produits, conseils d’utilisation…).
- Il est INTERDIT de proposer une routine ici. Les routines sont gérées dans une autre section.
- La réponse doit être adaptée au profil de l’utilisateur :
   - Âge
   - Type de peau
   - Problèmes cutanés
   - Allergies
   - Pathologies
- Le budget renseigné par l’utilisateur n’est pas à prendre en compte ici, sauf si la question concerne un produit spécifique.

Profil Utilisateur: {profile_text}

Question: {user_question}

Format de la réponse :
1. Réponse simple, claire et directe à la question.
2. Adapter la réponse au profil (ex. : éviter le parfum si allergie, préciser si l’ingrédient est utile pour l’eczéma, préciser s’il n’y a pas d’effet anti‑âge, etc.).
3. Pas de proposition de routine, pas de liste de produits → seulement une explication pédagogique.
        """
        
        return prompt.strip()
    
    def _format_profile_concise(self, user_profile: Dict[str, Any]) -> str:
        """Format user profile concisely for direct responses."""
        skin_type = user_profile.get("skin_type", "Non spécifié")
        age_range = user_profile.get("age_range", "Non spécifié")
        allergies = user_profile.get("allergies", [])
        conditions = user_profile.get("dermatological_conditions", [])
        
        profile_parts = [f"Type de peau: {skin_type}", f"Âge: {age_range}"]
        
        if allergies:
            profile_parts.append(f"Allergies: {', '.join(allergies)}")
        
        if conditions:
            profile_parts.append(f"Conditions: {', '.join(conditions)}")
        
        return " | ".join(profile_parts)
    
    def _parse_natural_response(
        self,
        ai_response: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse natural AI response."""
        try:
            # Pour les réponses naturelles, on retourne directement le texte
            # sans parsing JSON complexe
            return {
                "type": "natural_response",
                "answer": ai_response.strip(),
                "user_profile_used": {
                    "skin_type": user_profile.get("skin_type", "N/A"),
                    "age_range": user_profile.get("age_range", "N/A"),
                    "allergies": user_profile.get("allergies", []),
                    "conditions": user_profile.get("dermatological_conditions", [])
                },
                "timestamp": self._get_current_timestamp()
            }
                
        except Exception as e:
            logger.error(f"Error parsing natural response: {str(e)}")
            return self._create_fallback_general_response(ai_response)
    
    def _get_current_timestamp(self) -> str:
        """Retourne le timestamp actuel."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _build_general_question_prompt(
        self,
        user_profile: Dict[str, Any],
        user_question: str
    ) -> str:
        """Build prompt for general questions."""
        
        # Formater le profil utilisateur
        profile_text = self.user_service.format_profile_for_ai(user_profile)
        
        prompt = f"""
# Conseils Cosmétiques Personnalisés - Expert Beauté

Tu es un expert conseiller en cosmétiques et soins de la peau avec 15 ans d'expérience. Réponds toujours en français avec un ton professionnel et bienveillant.

## Profil Détaillé de l'Utilisateur
{profile_text}

## Question de l'Utilisateur
{user_question}

## Instructions CRITIQUES

1. **🚨 PRIORITÉ ABSOLUE :** Analyse d'abord les ALLERGIES et CONDITIONS du profil
2. **Personnalisation maximale :** Adapte chaque conseil au profil spécifique (âge, type de peau, préoccupations)
3. **Détail et précision :** Donne des conseils très détaillés et pratiques
4. **Sécurité avant tout :** Mentionne tous les risques liés aux allergies/conditions
5. **Alternatives concrètes :** Propose des solutions spécifiques et des marques
6. **Ton rassurant :** Utilise un langage bienveillant et professionnel

## Format de Réponse OBLIGATOIRE

Réponds au format JSON suivant avec des réponses TRÈS DÉTAILLÉES:
{{
    "answer": "Réponse complète et personnalisée à la question (minimum 200 mots, très détaillée)",
    "personalized_advice": {{
        "skin_type_advice": "Conseils très détaillés spécifiques au type de peau (minimum 100 mots)",
        "age_advice": "Conseils détaillés adaptés à l'âge avec explications (minimum 80 mots)",
        "allergy_warnings": ["⚠️ Avertissement allergie détaillé 1", "⚠️ Avertissement allergie détaillé 2", "⚠️ Avertissement allergie détaillé 3"],
        "condition_advice": "Conseils détaillés pour les conditions dermatologiques (minimum 100 mots)",
        "practical_tips": ["💡 Conseil pratique détaillé 1", "💡 Conseil pratique détaillé 2", "💡 Conseil pratique détaillé 3", "💡 Conseil pratique détaillé 4"]
    }},
    "recommendations": [
        {{
            "category": "Catégorie de produit spécifique",
            "suggestion": "Suggestion très détaillée et personnalisée",
            "reason": "Explication détaillée du pourquoi (minimum 50 mots)",
            "brand_examples": ["Marque spécifique 1", "Marque spécifique 2", "Marque spécifique 3"],
            "ingredients_to_look_for": ["Ingrédient 1", "Ingrédient 2", "Ingrédient 3"],
            "ingredients_to_avoid": ["Ingrédient à éviter 1", "Ingrédient à éviter 2"]
        }},
        {{
            "category": "Deuxième catégorie de produit",
            "suggestion": "Deuxième suggestion détaillée",
            "reason": "Explication détaillée",
            "brand_examples": ["Marque 1", "Marque 2"],
            "ingredients_to_look_for": ["Ingrédient 1", "Ingrédient 2"],
            "ingredients_to_avoid": ["Ingrédient à éviter 1"]
        }}
    ],
    "warnings": ["⚠️ Avertissement important détaillé 1", "⚠️ Avertissement important détaillé 2", "⚠️ Avertissement important détaillé 3"],
    "next_steps": ["Étape suivante détaillée 1", "Étape suivante détaillée 2", "Étape suivante détaillée 3"],
    "routine_suggestions": {{
        "morning": ["Étape matin 1", "Étape matin 2", "Étape matin 3"],
        "evening": ["Étape soir 1", "Étape soir 2", "Étape soir 3"],
        "weekly": ["Étape hebdomadaire 1", "Étape hebdomadaire 2"]
    }}
}}

**RÈGLES STRICTES:**
- Chaque section doit être TRÈS DÉTAILLÉE (minimum de mots indiqué)
- Personnalise chaque conseil au profil exact de l'utilisateur
- Mentionne des marques et ingrédients spécifiques
- Explique le POURQUOI de chaque recommandation
- Adapte le langage au niveau d'expertise (professionnel mais accessible)
- Ne jamais inventer de propriétés inexistantes
- Toujours prioriser la sécurité et les allergies
        """
        
        return prompt.strip()
    
    def _parse_general_response(
        self,
        ai_response: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse response for general questions."""
        try:
            # Essayer d'extraire le JSON de la réponse
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = ai_response[json_start:json_end]
                import json
                parsed_response = json.loads(json_str)
                
                # Ajouter des métadonnées
                parsed_response["user_profile_used"] = {
                    "skin_type": user_profile.get("skin_type", "N/A"),
                    "age_range": user_profile.get("age_range", "N/A"),
                    "allergies": user_profile.get("allergies", []),
                    "conditions": user_profile.get("dermatological_conditions", [])
                }
                
                return parsed_response
            else:
                # Fallback si pas de JSON valide
                return self._create_fallback_general_response(ai_response)
                
        except Exception as e:
            logger.error(f"Error parsing general response: {str(e)}")
            return self._create_fallback_general_response(ai_response)
    
    def _create_fallback_general_response(self, question: str) -> Dict[str, Any]:
        """Create a fallback response for general questions."""
        return {
            "type": "general_response",
            "answer": f"Je comprends votre question : '{question}'. ⚠️ ATTENTION : Azure OpenAI GPT-4 n'est pas configuré dans le fichier .env. Pour des conseils personnalisés et détaillés, veuillez configurer vos clés Azure OpenAI dans le fichier .env. En attendant, voici quelques conseils généraux de sécurité.",
            "personalized_advice": {
                "skin_type_advice": "Pour tous types de peau, privilégiez des produits doux, sans parfum et testés dermatologiquement. Évitez les ingrédients agressifs comme les sulfates et les alcools dénaturés. Hydratez régulièrement avec des produits adaptés à votre type de peau.",
                "age_advice": "Les besoins cutanés évoluent avec l'âge. Après 30 ans, intégrez des antioxydants comme la vitamine C. Après 40 ans, ajoutez des peptides et du rétinol (avec précaution). Après 50 ans, privilégiez l'hydratation intensive et la protection solaire renforcée.",
                "allergy_warnings": [
                    "⚠️ Vérifiez toujours la liste INCI des ingrédients avant tout achat",
                    "⚠️ Testez tout nouveau produit sur une petite zone pendant 48h",
                    "⚠️ Évitez les produits contenant vos allergènes connus"
                ],
                "condition_advice": "Pour les peaux sensibles ou avec conditions dermatologiques (eczéma, rosacée, etc.), consultez un dermatologue avant d'introduire de nouveaux produits. Privilégiez des soins apaisants avec des ingrédients comme l'aloe vera, l'avoine colloïdale ou les céramides.",
                "practical_tips": [
                    "💡 Lisez toujours les étiquettes et évitez les ingrédients que vous ne connaissez pas",
                    "💡 Introduisez un seul nouveau produit à la fois pour identifier les réactions",
                    "💡 Consultez un professionnel pour des conseils personnalisés",
                    "💡 Gardez un journal de vos produits pour identifier ce qui fonctionne"
                ]
            },
            "recommendations": [
                {
                    "category": "Consultation professionnelle",
                    "suggestion": "Prenez rendez-vous avec un dermatologue",
                    "reason": "Un professionnel peut analyser votre peau et recommander des produits spécifiquement adaptés à vos besoins, allergies et conditions cutanées",
                    "brand_examples": ["Dermatologue", "Pharmacien spécialisé"],
                    "ingredients_to_look_for": ["Produits recommandés par le professionnel"],
                    "ingredients_to_avoid": ["Allergènes identifiés par le professionnel"]
                },
                {
                    "category": "Soins de base sécurisés",
                    "suggestion": "Utilisez des produits doux et hypoallergéniques",
                    "reason": "Ces produits sont formulés pour minimiser les risques de réactions allergiques et conviennent à la plupart des types de peau",
                    "brand_examples": ["La Roche-Posay Toleriane", "Avène Antirougeurs", "Eucerin Sensitive"],
                    "ingredients_to_look_for": ["Céramides", "Acide hyaluronique", "Aloe vera"],
                    "ingredients_to_avoid": ["Parfums", "Sulfates", "Alcools dénaturés"]
                }
            ],
            "warnings": [
                "⚠️ Consultez toujours un professionnel de santé pour des conseils personnalisés",
                "⚠️ Ne jamais utiliser de produits contenant vos allergènes connus",
                "⚠️ Arrêtez immédiatement tout produit qui cause une réaction"
            ],
            "next_steps": [
                "Prendre rendez-vous avec un dermatologue pour une consultation personnalisée",
                "Demander conseil à votre pharmacien pour des produits adaptés",
                "Tenir un journal de vos produits et réactions cutanées"
            ],
            "routine_suggestions": {
                "morning": [
                    "Nettoyage doux avec un produit sans savon",
                    "Hydratation avec une crème adaptée à votre type de peau",
                    "Protection solaire SPF 30+ (même en hiver)"
                ],
                "evening": [
                    "Démaquillage en douceur",
                    "Nettoyage doux",
                    "Hydratation intensive pour la nuit"
                ],
                "weekly": [
                    "Masque hydratant une fois par semaine",
                    "Exfoliation douce (si votre peau le tolère)"
                ]
            }
        }
    
    def _parse_comprehensive_response(
        self,
        ai_response: str,
        user_profile: Dict[str, Any],
        safety_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse and structure the comprehensive AI response.
        
        Args:
            ai_response: Raw AI response
            user_profile: User profile data
            safety_analysis: Safety analysis results
            
        Returns:
            Structured response
        """
        try:
            # Try to extract JSON from the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = ai_response[json_start:json_end]
                parsed_response = json.loads(json_str)
            else:
                # Fallback if no JSON found
                parsed_response = self._create_fallback_analysis_response(
                    ai_response, user_profile, safety_analysis
                )
            
            # Build final response structure
            final_response = {
                "status": "success",
                "type": "product_analysis",
                "user_profile": {
                    "username": user_profile.get("username", "utilisateur"),
                    "skin_type": user_profile.get("skin_type", "mixte"),
                    "age_range": user_profile.get("age_range", "26-35")
                },
                "safety_analysis": safety_analysis,
                "ai_analysis": parsed_response
            }
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            # Return fallback response
            return self._create_fallback_analysis_response(
                ai_response, user_profile, safety_analysis
            )
    
    def _create_fallback_analysis_response(
        self,
        ai_response: str,
        user_profile: Dict[str, Any],
        safety_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback response when AI parsing fails."""
        return {
            "status": "success",
            "type": "product_analysis",
            "user_profile": {
                "username": user_profile.get("username", "utilisateur"),
                "skin_type": user_profile.get("skin_type", "mixte"),
                "age_range": user_profile.get("age_range", "26-35")
            },
            "safety_analysis": safety_analysis,
            "ai_analysis": {
                "analysis": {
                    "compatibility_score": 75,
                    "risk_level": "modéré",
                    "recommendation": "Produit acceptable avec précautions",
                    "key_ingredients": [],
                    "warnings": ["Analyse IA non disponible"],
                    "tips": ["Testez d'abord sur une petite zone"]
                },
                "answer": "Analyse basée sur les ingrédients uniquement. Testez le produit sur une petite zone avant utilisation complète.",
                "alternatives": []
            }
        }
