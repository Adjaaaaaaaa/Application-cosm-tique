"""
Enhanced Routine Service for BeautyScan - Service GPT-4 Optimisé.

Ce service génère des routines de soins personnalisées en utilisant Azure OpenAI GPT-4
avec TOUTES les données du profil utilisateur.
"""

import json
import logging
import re
import requests
from typing import Dict, Any, List

# Configuration du logging
logger = logging.getLogger(__name__)

class EnhancedRoutineService:
    """
    Service de génération de routines utilisant Azure OpenAI GPT-4.
    
    Récupère TOUTES les données du profil utilisateur et génère des routines
    personnalisées et adaptées.
    """
    
    def __init__(self):
        """Initialise le service."""
        self.logger = logging.getLogger(__name__)
    
    def generate_routine(self, user_id: int, routine_type: str = "daily", 
                        budget: str = "medium", custom_question: str = "") -> Dict[str, Any]:
        """
        Génère une routine personnalisée avec GPT-4.
        Peut aussi répondre à des questions générales si routine_type est "general".
        
        Args:
            user_id: ID de l'utilisateur
            routine_type: Type de routine (daily, weekly, etc.) ou "general" pour questions
            budget: Niveau de budget (low, medium, high)
            custom_question: Question personnalisée pour l'IA
            
        Returns:
            Dict contenant la routine générée ou la réponse générale
        """
        try:
            # Récupérer TOUTES les données du profil
            profile_data = self._get_user_profile_data(user_id)
            
            # Vérifier que Azure OpenAI est disponible
            if not self._is_azure_openai_available():
                # Fallback spécifique pour les questions générales
                if routine_type == "general" or routine_type == "":
                    return {
                        "status": "success",
                        "type": "general_response",
                        "user_profile": profile_data,
                        "answer": self._create_fallback_general_answer(custom_question, profile_data),
                        "recommendations": [],
                        "tips": [],
                        "warnings": []
                    }
                # Sinon, retourner une routine de secours
                return self._generate_fallback_routine(profile_data, routine_type, budget)
            
            # Générer la routine avec GPT-4 UNIQUEMENT
            try:
                # Construire le prompt avec TOUTES les données
                prompt = self._build_gpt4_prompt(profile_data, routine_type, budget, custom_question)
                
                # Appeler GPT-4
                gpt4_response = self._call_gpt4_api(prompt)
                
                # Parser la réponse JSON
                routine_data = self._parse_gpt4_response(gpt4_response)
                
                # Construire la réponse finale selon le type
                if routine_type == "general":
                    # Réponse générale
                    # Normaliser la clé de réponse (gère 'réponse'/'reponse')
                    normalized_answer = routine_data.get("answer") or routine_data.get("réponse") or routine_data.get("reponse") or ""
                    routine = {
                        "status": "success",
                        "type": "general_response",
                        "user_profile": profile_data,
                        "answer": normalized_answer,
                        "recommendations": routine_data.get("recommendations", []),
                        "tips": routine_data.get("tips", []),
                        "warnings": routine_data.get("warnings", [])
                    }
                else:
                    # Routine structurée
                    routine = {
                        "status": "success",
                        "type": "comprehensive_routine",
                        "routine_type": routine_type,
                        "user_profile": profile_data,
                        "ai_routine": routine_data,
                        "product_recommendations": [],
                        "summary": {
                            "total_steps": len(routine_data.get("steps", [])),
                            "estimated_time": routine_data.get("estimated_time", "15-20 minutes"),
                            "difficulty": routine_data.get("difficulty", "beginner")
                        }
                    }
                
                self.logger.info(f"Réponse générée avec succès pour l'utilisateur {user_id}")
                self.logger.info(f"Données du profil utilisées: {profile_data}")
                return routine
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'appel à GPT-4: {e}")
                # Fallback: si question générale, renvoyer une réponse directe; sinon routine de base
                if routine_type == "general" or routine_type == "":
                    self.logger.info("Utilisation du fallback pour question générale")
                    return {
                        "status": "success",
                        "type": "general_response",
                        "user_profile": profile_data,
                        "answer": self._create_fallback_general_answer(custom_question, profile_data),
                        "recommendations": [],
                        "tips": [],
                        "warnings": []
                    }
                self.logger.info("Utilisation du fallback pour la routine")
                fallback_routine = self._generate_fallback_routine(profile_data, routine_type, budget)
                return fallback_routine
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de routine: {e}")
            return {
                "status": "error",
                "message": f"Échec de la génération: {str(e)}",
                "type": "error"
            }

    def _create_fallback_general_answer(self, question: str, profile: Dict[str, Any]) -> str:
        """Crée une réponse simple et utile pour les questions générales en fallback."""
        question_lower = (question or "").strip().lower()
        skin_type = profile.get('skin_type', 'normal')
        age_range = profile.get('age_range', '')
        allergies = ", ".join(profile.get('allergies', []))
        conditions = ", ".join(profile.get('dermatological_conditions', []))

        # Réponses rapides basées sur mots-clés simples
        if 'vaseline' in question_lower:
            base = "La vaseline (pétrolatum) est un occlusif qui réduit la perte d'eau et protège la barrière cutanée."
            advice = "Convient souvent aux peaux sèches ou irritées; appliquez en fine couche en fin de routine."
            caution = "Évitez sur zones très occluses si peau à tendance acnéique."
            specific = ""
            if 'fragrance' in allergies:
                specific = " La vaseline pure est généralement sans parfum, adaptée en cas d'allergie au parfum."
            return f"{base} {advice} {caution}{specific}"

        if 'vitamine c' in question_lower or 'vitamin c' in question_lower:
            return (
                "La vitamine C (acide L-ascorbique) est un antioxydant qui illumine le teint et stimule le collagène. "
                "Utilisez le matin sous une protection solaire. Si peau sensible, commencez à basse concentration (5-10%)."
            )

        # Générique par défaut
        tips = []
        if skin_type == 'sensitive':
            tips.append("privilégiez des formules sans parfum et testez sur une petite zone")
        if 'eczema' in conditions:
            tips.append("renforcez la barrière avec des émollients riches et évitez les irritants")
        suffix = f" (peau: {skin_type}{', allergies: ' + allergies if allergies else ''}{', conditions: ' + conditions if conditions else ''})"
        return (
            "Voici quelques conseils cosmétiques généraux: privilégiez une routine douce (nettoyant délicat, hydratant, SPF). "
            + ("Conseils spécifiques: " + "; ".join(tips) + "." if tips else "")
            + suffix
        )
    
    def _get_user_profile_data(self, user_id: int) -> Dict[str, Any]:
        """Récupère TOUTES les données du profil utilisateur."""
        try:
            import django
            if not django.conf.settings.configured:
                django.setup()
            
            from backend.services.user_service import UserService
            
            # Utiliser notre UserService mis à jour
            user_service = UserService()
            profile_data = user_service.get_user_profile(user_id)
            
            if not profile_data:
                raise Exception("Impossible de récupérer les données du profil")
            
            self.logger.info(f"Profil complet récupéré pour l'utilisateur {user_id}")
            return profile_data
            
        except Exception as e:
            self.logger.warning(f"Impossible de récupérer le profil: {e}")
            # Données par défaut
            return {
                'username': f'user_{user_id}',
                'skin_type': 'normal',
                'age_range': '26-35',
                'allergies': [],
                'skin_concerns': [],
                'dermatological_conditions': [],
                'objectives': [],
                'budget': 'medium'
            }
    
    def _build_gpt4_prompt(self, profile_data: Dict[str, Any], routine_type: str, 
                           budget: str, custom_question: str) -> str:
        """Construit le prompt pour GPT-4 avec TOUTES les données."""
        
        # Extraire TOUTES les données
        skin_type = profile_data.get('skin_type', 'normal')
        age_range = profile_data.get('age_range', '26-35')
        skin_concerns = profile_data.get('skin_concerns', [])
        allergies = profile_data.get('allergies', [])
        dermatological_conditions = profile_data.get('dermatological_conditions', [])
        objectives = profile_data.get('objectives', [])
        budget = profile_data.get('budget', budget)  # Utiliser le budget du profil ou celui passé en paramètre
        product_style = profile_data.get('product_style', 'standard')
        routine_frequency = profile_data.get('routine_frequency', 'standard')
        
        # Formater les données
        skin_concerns_text = ", ".join(skin_concerns) if skin_concerns else "aucun"
        allergies_text = ", ".join(allergies) if allergies else "aucune"
        dermatological_conditions_text = ", ".join(dermatological_conditions) if dermatological_conditions else "aucune"
        objectives_text = ", ".join(objectives) if objectives else "aucun"
        
        # Déterminer le type de demande
        if routine_type == "general" or routine_type == "":
            # Question générale - réponse directe et concise
            prompt = f"""
Tu es un expert en cosmétiques et soins de la peau. Réponds directement et de façon concise à la question de l'utilisateur.

## Profil Utilisateur
Type de peau: {skin_type} | Âge: {age_range} | Allergies: {allergies_text} | Conditions: {dermatological_conditions_text}

## Question
{custom_question if custom_question else "Je veux des conseils beauté personnalisés"}

## Instructions
- Réponds DIRECTEMENT à la question posée, sans ajouter d'informations non demandées
- Adapte ta réponse au profil utilisateur (allergies, type de peau, âge)
- Sois concis et précis
- Mentionne uniquement les précautions liées au profil si pertinentes
- Utilise un ton professionnel mais accessible
- Ne génère PAS de routine ou de conseils généraux sauf si explicitement demandé

Réponds comme si tu répondais à une question ponctuelle, de façon naturelle et directe.
            """
        elif routine_type == "ingredients":
            # Analyse d'ingrédient
            prompt = f"""
Tu es un expert en cosmétiques et soins de la peau avec 15 ans d'expérience. Analyse l'ingrédient demandé en donnant D'ABORD des informations générales, PUIS des conseils d'utilisation personnalisés.

Profil utilisateur COMPLET:
- Âge: {age_range}
- Type de peau: {skin_type}
- Préoccupations cutanées: {skin_concerns_text}
- Allergies: {allergies_text}
- Pathologies dermatologiques: {dermatological_conditions_text}
- Objectifs: {objectives_text}
- Budget: {budget}
- Style de produits: {product_style}

Question sur l'ingrédient: {custom_question if custom_question else "Analysez cet ingrédient"}

STRUCTURE OBLIGATOIRE - Réponds au format JSON suivant:

1. D'ABORD: Informations générales sur l'ingrédient (ce que c'est, d'où ça vient, propriétés)
2. ENSUITE: Conseils d'utilisation personnalisés pour CE profil spécifique
3. ENFIN: Recommandations de produits et marques précises

IMPORTANT: Réponds au format JSON suivant avec une analyse COMPLÈTE et PERSONNALISÉE:

{{
    "routine_name": "Analyse d'ingrédient personnalisée",
    "description": "Conseils personnalisés pour votre profil (âge: {age_range}, type: {skin_type}, allergies: {allergies_text}, conditions: {dermatological_conditions_text})",
    "total_budget": 0,
    "routine_type": "ingredients",
    "total_duration": "N/A",
    "average_tolerance_score": "N/A",
    "steps": [],
    "ingredient_info": {{
        "what_is_it": "Description détaillée de l'ingrédient (ce que c'est, origine, propriétés chimiques)",
        "how_it_works": "Comment l'ingrédient agit sur la peau (mécanisme d'action)",
        "common_uses": "Utilisations courantes en cosmétique",
        "concentrations": "Concentrations recommandées et efficaces"
    }},
    "personalized_advice": {{
        "safety_for_you": "Analyse de sécurité spécifique à votre profil (allergies: {allergies_text}, pathologies: {dermatological_conditions_text})",
        "benefits_for_you": "Bénéfices spécifiques pour votre type de peau {skin_type} et âge {age_range}",
        "risks_for_you": "Risques spécifiques selon votre profil",
        "how_to_use": "Conseils d'utilisation détaillés et personnalisés",
        "frequency": "Fréquence d'utilisation recommandée pour votre profil",
        "combinations": "Avec quels autres ingrédients l'associer (ou éviter)"
    }},
    "tips": [
        "Conseil PRATIQUE et SPÉCIFIQUE pour votre profil (âge {age_range}, type {skin_type})",
        "Précautions DÉTAILLÉES selon vos allergies {allergies_text} et pathologies {dermatological_conditions_text}",
        "Bénéfices SPÉCIFIQUES pour vos objectifs {objectives_text}",
        "Alternatives PRÉCISES si nécessaire pour votre profil"
    ],
    "faq": [
        {{
            "question": "Cet ingrédient est-il sûr pour moi avec mes allergies et pathologies ?",
            "answer": "Analyse DÉTAILLÉE de sécurité basée sur vos allergies {allergies_text} et pathologies {dermatological_conditions_text} - réponse minimum 100 mots"
        }},
        {{
            "question": "Comment l'utiliser efficacement avec mon type de peau et mon âge ?",
            "answer": "Conseils d'utilisation TRÈS DÉTAILLÉS et personnalisés pour peau {skin_type} et âge {age_range} - réponse minimum 120 mots"
        }},
        {{
            "question": "Quels produits contenant cet ingrédient me conviennent ?",
            "answer": "Recommandations de produits SPÉCIFIQUES adaptés à votre budget {budget} et style {product_style} - réponse minimum 100 mots"
        }}
    ],
    "warnings": [
        "⚠️ Avertissement CRITIQUE basé sur vos allergies {allergies_text}",
        "⚠️ Précautions SPÉCIFIQUES pour vos pathologies {dermatological_conditions_text}",
        "⚠️ Risques liés à votre âge {age_range} et type de peau {skin_type}"
    ],
    "recommendations": [
        "Recommandation ULTRA-PERSONNALISÉE pour votre profil exact (âge {age_range}, type {skin_type})",
        "Conseil SPÉCIFIQUE adapté à vos allergies {allergies_text} et conditions {dermatological_conditions_text}",
        "Suggestion PRÉCISE pour vos objectifs {objectives_text} et budget {budget}"
    ],
    "product_suggestions": [
        {{
            "category": "Produits contenant cet ingrédient",
            "recommendations": ["Marque et produit spécifique 1", "Marque et produit spécifique 2", "Marque et produit spécifique 3"],
            "reason": "Pourquoi ces produits vous conviennent PARFAITEMENT (budget {budget}, style {product_style}, profil {skin_type})"
        }}
    ]
}}

**IMPORTANT - STRUCTURE OBLIGATOIRE:** 
1. **D'ABORD** : Informations générales sur l'ingrédient (ce que c'est, origine, propriétés)
2. **ENSUITE** : Analyse de sécurité spécifique à votre profil (allergies, pathologies, âge)
3. **PUIS** : Conseils d'utilisation détaillés et personnalisés
4. **ENFIN** : Recommandations de produits et marques précises

**EXIGENCES CRITIQUES:**
- PERSONNALISE chaque conseil au profil EXACT (âge: {age_range}, type: {skin_type}, allergies: {allergies_text}, pathologies: {dermatological_conditions_text})
- Donne des informations GÉNÉRALES d'abord, puis des conseils PERSONNALISÉS
- Mentionne des marques et produits PRÉCIS adaptés à ce profil exact
- Explique le POURQUOI chaque recommandation est parfaite pour cette personne spécifique
- Adapte la fréquence d'utilisation selon l'âge {age_range} et les conditions {dermatological_conditions_text}
- Considère le budget {budget} et les préférences de style {product_style}
- Inclus des avertissements SPÉCIFIQUES basés sur les allergies et pathologies
- Suggère des alternatives si l'ingrédient n'est pas adapté au profil
- ÉVITE les répétitions dans les titres et descriptions
- Utilise un langage naturel et fluide
"""
        else:
            # Routine classique
            prompt = f"""
Tu es un expert en cosmétiques et soins de la peau. Génère une routine personnalisée COMPLÈTE et DÉTAILLÉE au format JSON.

Profil utilisateur COMPLET:
- Âge: {age_range}
- Type de peau: {skin_type}
- Préoccupations cutanées: {skin_concerns_text}
- Allergies: {allergies_text}
- Pathologies dermatologiques: {dermatological_conditions_text}
- Objectifs: {objectives_text}
- Budget: {budget}€

Type de routine: {routine_type}

Question personnalisée: {custom_question if custom_question else "Aucune"}

IMPORTANT: Réponds UNIQUEMENT au format JSON suivant avec des informations COMPLÈTES et PERSONNALISÉES:

{{
    "routine_name": "Nom de la routine personnalisée",
    "description": "Description détaillée de la routine adaptée au profil",
    "total_budget": 0,
    "routine_type": "{routine_type}",
    "total_duration": "15-20 minutes",
    "average_tolerance_score": "8/10",
    "steps": [
        {{
            "step_number": 1,
            "product_type": "Type de produit",
            "product_name": "Nom du produit",
            "description": "Description de l'étape",
            "duration": "Durée",
            "budget": 15,
            "tips": ["Conseil 1", "Conseil 2"],
            "recommended_products": ["Produit recommandé 1", "Produit recommandé 2"]
        }}
    ],
    "tips": [
        "Conseil général personnalisé",
        "Conseil basé sur votre type de peau",
        "Conseil pour éviter vos allergies"
    ],
    "faq": [
        {{
            "question": "Question fréquente pertinente",
            "answer": "Réponse détaillée et personnalisée"
        }}
    ],
    "warnings": ["Avertissement basé sur les allergies et pathologies"],
    "recommendations": ["Recommandation basée sur le profil complet"],
    "product_suggestions": [
        {{
            "category": "Catégorie de produit",
            "recommendations": ["Produit 1", "Produit 2"],
            "reason": "Pourquoi ces produits vous conviennent"
        }}
    ]
}}

**IMPORTANT:** 
- Adapte la routine aux pathologies dermatologiques spécifiques
- Évite les allergènes mentionnés
- Respecte le budget spécifié
- Sois précis et personnalisé selon TOUT le profil
- Inclus des produits recommandés adaptés
- Génère des questions fréquentes pertinentes
"""
        
        return prompt.strip()
    
    def _call_gpt4_api(self, prompt: str) -> str:
        """Appelle l'API GPT-4 via HTTP."""
        from config.env import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY
        import os
        
        azure_endpoint = AZURE_OPENAI_ENDPOINT
        if not azure_endpoint:
            raise Exception("AZURE_OPENAI_ENDPOINT non configuré")
        
        api_key = AZURE_OPENAI_KEY
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', os.getenv('OPENAI_MODEL', 'gpt-4'))
        
        if not api_key:
            raise Exception("AZURE_OPENAI_KEY non configuré")
        
        # Log pour debug
        self.logger.info(f"Appel Azure OpenAI - Endpoint: {azure_endpoint}, Déploiement: {deployment_name}")
        
        # URL de l'API
        url = f"{azure_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        
        # Headers et payload
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert conseiller en cosmétiques avec 15 ans d'expérience. Réponds UNIQUEMENT au format JSON demandé avec des réponses ULTRA-PERSONNALISÉES. PRIORITÉ ABSOLUE: - PERSONNALISE chaque conseil au profil EXACT de l'utilisateur (âge, type de peau, allergies, conditions) - ÉVITE les conseils généraux - Donne des conseils TRÈS SPÉCIFIQUES adaptés au profil unique - Mentionne des marques et ingrédients PRÉCIS adaptés au profil - Explique le POURQUOI chaque recommandation est parfaite pour CE profil spécifique - Adapte la fréquence d'utilisation selon l'âge et les conditions - Considère le budget et les préférences de style - Génère un JSON valide et complet - Assure-toi que TOUS les conseils sont 100% personnalisés au profil"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 3000,
            "temperature": 0.2
        }
        
        # Faire la requête avec timeout augmenté pour Azure OpenAI
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def _parse_gpt4_response(self, gpt4_response: str) -> Dict[str, Any]:
        """Parse la réponse de GPT-4 et extrait le JSON."""
        logger.info(f"Réponse brute de GPT-4: {gpt4_response}")
        
        try:
            # Essayer de parser directement d'abord
            routine_data = json.loads(gpt4_response)
            logger.info("Réponse JSON de GPT-4 parsée directement avec succès")
            return routine_data
        except json.JSONDecodeError:
            # Si ça échoue, essayer d'extraire le JSON avec regex
            json_match = re.search(r'\{.*\}', gpt4_response, re.DOTALL)
            if json_match:
                try:
                    routine_data = json.loads(json_match.group())
                    logger.info("Réponse JSON de GPT-4 extraite et parsée avec succès")
                    return routine_data
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur de parsing JSON extrait: {e}")
                    # Essayer de nettoyer la réponse
                    cleaned_response = self._clean_json_response(json_match.group())
                    routine_data = json.loads(cleaned_response)
                    logger.info("Réponse JSON de GPT-4 nettoyée et parsée avec succès")
                    return routine_data
            else:
                logger.error("Impossible d'extraire le JSON de la réponse de GPT-4")
                raise Exception("GPT-4 n'a pas retourné de JSON valide")
    
    def _clean_json_response(self, json_str: str) -> str:
        """Nettoie la réponse JSON pour corriger les erreurs communes."""
        try:
            logger.info(f"JSON brut à nettoyer: {json_str[:200]}...")
            
            # Remplacer les caractères problématiques
            cleaned = json_str.replace('\n', ' ').replace('\r', ' ')
            
            # Corriger les erreurs communes de virgules
            cleaned = re.sub(r',\s*}', '}', cleaned)  # Enlever les virgules trailing
            cleaned = re.sub(r',\s*]', ']', cleaned)  # Enlever les virgules trailing dans les arrays
            
            # Corriger les virgules avant } ou ] (erreur la plus commune)
            cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
            
            # Enlever l'espace à la fin
            cleaned = re.sub(r'}\s*$', '}', cleaned)
            
            # Corriger les guillemets non fermés
            cleaned = re.sub(r'([^"])\s*$', r'\1"', cleaned)
            
            # Corriger les catégories incomplètes (erreur spécifique observée)
            cleaned = re.sub(r'"category":\s*"([^"]*)$', r'"category": "\1"', cleaned)
            
            # Fermer les objets JSON incomplets
            if cleaned.count('{') > cleaned.count('}'):
                cleaned += '}'
            if cleaned.count('[') > cleaned.count(']'):
                cleaned += ']'
            
            logger.info(f"JSON nettoyé: {cleaned[:200]}...")
            return cleaned
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage JSON: {e}")
            return json_str
    
    def _generate_fallback_routine(self, profile_data: Dict[str, Any], routine_type: str, budget: str) -> Dict[str, Any]:
        """Génère une routine de fallback avec TOUTES les données."""
        try:
            # Extraire TOUTES les données
            skin_type = profile_data.get('skin_type', 'normal')
            age_range = profile_data.get('age_range', '26-35')
            skin_concerns = profile_data.get('skin_concerns', [])
            allergies = profile_data.get('allergies', [])
            dermatological_conditions = profile_data.get('dermatological_conditions', [])
            objectives = profile_data.get('objectives', [])
            
            # Générer des conseils personnalisés basés sur le profil
            tips = self._generate_personalized_tips(profile_data)
            faq = self._generate_personalized_faq(profile_data)
            product_suggestions = self._generate_product_suggestions(profile_data)
            
            # Créer la routine de fallback avec TOUTES les données
            routine = {
                "status": "success",
                "type": "fallback_routine",
                "routine_type": routine_type,
                "user_profile": profile_data,
                "ai_routine": {
                    "routine_name": f"Routine {routine_type} de base",
                    "description": f"Routine adaptée à votre type de peau {skin_type}",
                    "total_budget": 0,
                    "routine_type": routine_type,
                    "total_duration": "15-20 minutes",
                    "average_tolerance_score": "7/10",
                    "steps": [
                        {
                            "step_number": 1,
                            "product_type": "Nettoyant",
                            "product_name": "Nettoyant doux",
                            "description": "Nettoyez votre visage avec un produit doux",
                            "duration": "2-3 minutes",
                            "budget": 15,
                            "tips": ["Utilisez de l'eau tiède", "Évitez les frottements"],
                            "recommended_products": ["Nettoyant doux sans parfum", "Gel nettoyant apaisant"]
                        }
                    ],
                    "tips": tips,
                    "faq": faq,
                    "warnings": [f"Évitez les allergènes: {', '.join(allergies)}"] if allergies else [],
                    "recommendations": [f"Adapté à votre type de peau: {skin_type}"],
                    "product_suggestions": product_suggestions
                },
                "product_recommendations": [],
                "summary": {
                    "total_steps": 1,
                    "estimated_time": "15-20 minutes",
                    "difficulty": "beginner"
                }
            }
            
            self.logger.info("Routine de fallback générée avec TOUTES les données du profil")
            return routine
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de la routine de fallback: {e}")
            return {
                "status": "error",
                "message": f"Échec de la routine de fallback: {str(e)}",
                "type": "error"
            }
    
    def _generate_personalized_tips(self, profile_data: Dict[str, Any]) -> List[str]:
        """Génère des conseils personnalisés basés sur le profil."""
        tips = []
        skin_type = profile_data.get('skin_type', 'normal')
        age_range = profile_data.get('age_range', '26-35')
        allergies = profile_data.get('allergies', [])
        skin_concerns = profile_data.get('skin_concerns', [])
        
        # Conseils basés sur le type de peau
        if skin_type == 'sensitive':
            tips.append("Utilisez des produits sans parfum et hypoallergéniques")
            tips.append("Testez toujours sur une petite zone avant utilisation complète")
        elif skin_type == 'dry':
            tips.append("Hydratez votre peau matin et soir avec des crèmes riches")
            tips.append("Évitez les nettoyants trop dégraissants")
        elif skin_type == 'oily':
            tips.append("Utilisez des produits non comédogènes")
            tips.append("Nettoyez votre peau deux fois par jour")
        elif skin_type == 'combination':
            tips.append("Adaptez vos soins selon les zones de votre visage")
            tips.append("Utilisez des produits équilibrants")
        
        # Conseils basés sur l'âge
        if '18-25' in age_range:
            tips.append("Privilégiez la prévention et la protection solaire")
        elif '26-35' in age_range:
            tips.append("Commencez à intégrer des actifs anti-âge légers")
        elif '36-45' in age_range:
            tips.append("Intensifiez les soins anti-âge et l'hydratation")
        elif '46+' in age_range:
            tips.append("Privilégiez les soins nourrissants et régénérants")
        
        # Conseils basés sur les allergies
        if allergies:
            tips.append(f"Vérifiez toujours la composition pour éviter: {', '.join(allergies)}")
            tips.append("Préférez les produits dermo-cosmétiques testés")
        
        # Conseils basés sur les préoccupations
        if 'acne' in skin_concerns:
            tips.append("Nettoyez votre peau en douceur, évitez les frottements")
            tips.append("Utilisez des produits non comédogènes")
        if 'aging' in skin_concerns:
            tips.append("Protégez-vous du soleil avec un SPF 50+")
            tips.append("Intégrez des actifs comme le rétinol progressivement")
        
        return tips[:6]  # Limiter à 6 conseils
    
    def _generate_personalized_faq(self, profile_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère des questions fréquentes personnalisées basées sur le profil."""
        faq = []
        skin_type = profile_data.get('skin_type', 'normal')
        allergies = profile_data.get('allergies', [])
        skin_concerns = profile_data.get('skin_concerns', [])
        
        # FAQ basée sur le type de peau
        if skin_type == 'sensitive':
            faq.append({
                "question": "Comment savoir si un produit me convient ?",
                "answer": "Testez toujours sur une petite zone (cou ou bras) pendant 48h avant utilisation complète. Privilégiez les produits sans parfum et hypoallergéniques."
            })
        
        if skin_type == 'dry':
            faq.append({
                "question": "Combien de fois par jour dois-je hydrater ma peau ?",
                "answer": "Pour une peau sèche, hydratez matin et soir. En hiver ou climats secs, vous pouvez ajouter une hydratation en journée si nécessaire."
            })
        
        # FAQ basée sur les allergies
        if allergies:
            faq.append({
                "question": "Comment éviter mes allergies dans les cosmétiques ?",
                "answer": f"Lisez toujours la liste des ingrédients. Évitez les produits contenant: {', '.join(allergies)}. Privilégiez les produits dermo-cosmétiques testés."
            })
        
        # FAQ basée sur les préoccupations
        if 'acne' in skin_concerns:
            faq.append({
                "question": "Puis-je utiliser des gommages si j'ai de l'acné ?",
                "answer": "Oui, mais choisissez des gommages doux et non abrasifs. Évitez les gommages mécaniques, préférez les enzymes ou acides de fruits en faible concentration."
            })
        
        if 'aging' in skin_concerns:
            faq.append({
                "question": "À partir de quel âge commencer les soins anti-âge ?",
                "answer": "La prévention peut commencer dès 25-30 ans avec de la protection solaire. Les actifs anti-âge comme le rétinol peuvent être introduits progressivement à partir de 30-35 ans."
            })
        
        # FAQ générales
        faq.append({
            "question": "Quel est le bon ordre d'application des soins ?",
            "answer": "Nettoyant → Tonique → Sérum → Crème hydratante → Protection solaire (matin). Le soir, remplacez la protection solaire par une crème de nuit."
        })
        
        return faq[:5]  # Limiter à 5 questions
    
    def _generate_product_suggestions(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des suggestions de produits basées sur le profil."""
        suggestions = []
        skin_type = profile_data.get('skin_type', 'normal')
        skin_concerns = profile_data.get('skin_concerns', [])
        allergies = profile_data.get('allergies', [])
        
        # Suggestions de nettoyants
        if skin_type == 'sensitive':
            suggestions.append({
                "category": "Nettoyants",
                "recommendations": ["Lait démaquillant apaisant", "Gel nettoyant sans parfum"],
                "reason": "Formules douces et hypoallergéniques adaptées aux peaux sensibles"
            })
        elif skin_type == 'dry':
            suggestions.append({
                "category": "Nettoyants",
                "recommendations": ["Lait démaquillant nourrissant", "Huile nettoyante"],
                "reason": "Formules riches qui respectent le film hydrolipidique"
            })
        
        # Suggestions d'hydratants
        if 'aging' in skin_concerns:
            suggestions.append({
                "category": "Hydratants",
                "recommendations": ["Crème anti-âge avec peptides", "Sérum à l'acide hyaluronique"],
                "reason": "Actifs ciblés pour lutter contre le vieillissement cutané"
            })
        
        if 'acne' in skin_concerns:
            suggestions.append({
                "category": "Soins ciblés",
                "recommendations": ["Sérum à l'acide salicylique", "Crème matifiante non comédogène"],
                "reason": "Formules spécifiquement conçues pour les peaux à tendance acnéique"
            })
        
        # Suggestions de protection solaire
        suggestions.append({
            "category": "Protection solaire",
            "recommendations": ["SPF 50+ sans parfum", "Crème solaire teintée"],
            "reason": "Protection essentielle pour tous les types de peau, même en ville"
        })
        
        return suggestions[:4]  # Limiter à 4 catégories

    def _is_azure_openai_available(self) -> bool:
        """Vérifie si Azure OpenAI est disponible et configuré."""
        try:
            from config.env import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY
            import os
            
            # Vérifier que les variables d'environnement sont présentes
            azure_endpoint = AZURE_OPENAI_ENDPOINT
            api_key = AZURE_OPENAI_KEY
            
            if not azure_endpoint or not api_key:
                self.logger.warning("Variables d'environnement Azure OpenAI manquantes")
                return False
            
            # Vérifier que l'endpoint est accessible
            try:
                import requests
                test_url = f"{azure_endpoint}/openai/deployments/test/chat/completions?api-version=2024-02-15-preview"
                response = requests.get(test_url, timeout=5)
                # Même si on a une erreur 404, cela signifie que l'endpoint est accessible
                return True
            except Exception as e:
                self.logger.warning(f"Impossible de contacter Azure OpenAI: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification Azure OpenAI: {e}")
            return False
