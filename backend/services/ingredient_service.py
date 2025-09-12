"""
Ingredient analysis service for BeautyScan backend API.

Handles ingredient parsing, formatting, and safety analysis.
"""

import re
import logging
from typing import Dict, Any, List, Set
from backend.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class IngredientService:
    """Service for ingredient analysis and formatting."""
    
    def __init__(self):
        """Initialize ingredient service."""
        # Common allergens and potentially problematic ingredients
        self.allergens = {
            'parabens': ['methylparaben', 'ethylparaben', 'propylparaben', 'butylparaben'],
            'sulfates': ['sodium lauryl sulfate', 'sodium laureth sulfate', 'ammonium lauryl sulfate'],
            'alcohols': ['alcohol denat', 'ethanol', 'isopropyl alcohol'],
            'fragrances': ['parfum', 'fragrance', 'perfume'],
            'preservatives': ['phenoxyethanol', 'formaldehyde', 'imidazolidinyl urea'],
            'retinoids': ['retinol', 'retinal', 'retinyl palmitate', 'tretinoin'],
            'acids': ['salicylic acid', 'glycolic acid', 'lactic acid', 'citric acid'],
            'vitamins': ['vitamin c', 'ascorbic acid', 'vitamin e', 'tocopherol'],
            'oils': ['coconut oil', 'olive oil', 'almond oil', 'argan oil'],
            'extracts': ['aloe vera', 'chamomile', 'lavender', 'tea tree']
        }
    
    def parse_ingredients(self, ingredients_text: str) -> List[str]:
        """
        Parse ingredients text into a structured list.
        
        Args:
            ingredients_text: Raw ingredients text from product
            
        Returns:
            List of individual ingredients
        """
        if not ingredients_text:
            return []
        
        try:
            # Clean the text
            cleaned_text = self._clean_ingredients_text(ingredients_text)
            
            # Split by common separators
            ingredients = self._split_ingredients(cleaned_text)
            
            # Clean individual ingredients
            cleaned_ingredients = [self._clean_ingredient(ing) for ing in ingredients]
            
            # Remove empty ingredients
            filtered_ingredients = [ing for ing in cleaned_ingredients if ing.strip()]
            
            logger.info(f"Parsed {len(filtered_ingredients)} ingredients from text")
            return filtered_ingredients
            
        except Exception as e:
            logger.error(f"Error parsing ingredients: {str(e)}")
            return []
    
    def _clean_ingredients_text(self, text: str) -> str:
        """
        Clean ingredients text by removing common artifacts.
        
        Args:
            text: Raw ingredients text
            
        Returns:
            Cleaned text
        """
        # Remove common prefixes and suffixes
        text = re.sub(r'^ingredients?[:\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^composants?[:\s]*', '', text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common artifacts
        text = re.sub(r'[•\-\*]\s*', '', text)
        
        return text.strip()
    
    def _split_ingredients(self, text: str) -> List[str]:
        """
        Split ingredients text into individual ingredients.
        
        Args:
            text: Cleaned ingredients text
            
        Returns:
            List of ingredient strings
        """
        # Common separators in ingredients lists
        separators = [
            r',\s*',           # Comma
            r'\.\s*',          # Period
            r';\s*',           # Semicolon
            r'\s+et\s+',       # French "et"
            r'\s+and\s+',      # English "and"
            r'\s*\*\s*',       # Asterisk
            r'\s*•\s*',        # Bullet point
        ]
        
        # Try different separators
        for separator in separators:
            if re.search(separator, text):
                ingredients = re.split(separator, text)
                if len(ingredients) > 1:
                    return ingredients
        
        # If no separator found, return as single ingredient
        return [text]
    
    def _clean_ingredient(self, ingredient: str) -> str:
        """
        Clean individual ingredient string.
        
        Args:
            ingredient: Raw ingredient string
            
        Returns:
            Cleaned ingredient string
        """
        # Remove extra whitespace
        ingredient = re.sub(r'\s+', ' ', ingredient.strip())
        
        # Remove common artifacts
        ingredient = re.sub(r'^[•\-\*]\s*', '', ingredient)
        ingredient = re.sub(r'\s*[•\-\*]$', '', ingredient)
        
        # Remove concentration indicators (e.g., "5%", "0.1%")
        ingredient = re.sub(r'\s*\d+%?\s*$', '', ingredient)
        
        return ingredient.strip()
    
    def analyze_ingredients_safety(
        self,
        ingredients: List[str],
        user_allergies: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze ingredients for safety and allergy concerns.
        
        Args:
            ingredients: List of product ingredients
            user_allergies: List of user allergies
            
        Returns:
            Safety analysis results
        """
        try:
            # Convert to lowercase for comparison
            ingredients_lower = [ing.lower() for ing in ingredients]
            allergies_lower = [allergy.lower() for allergy in user_allergies]
            
            # Check for direct allergy matches
            direct_matches = self._find_allergy_matches(ingredients_lower, allergies_lower)
            
            # Check for potential allergen categories
            potential_allergens = self._find_potential_allergens(ingredients_lower)
            
            # Check for potentially problematic ingredients
            problematic_ingredients = self._find_problematic_ingredients(ingredients_lower)
            
            # Calculate overall safety score
            safety_score = self._calculate_safety_score(
                direct_matches, potential_allergens, problematic_ingredients
            )
            
            return {
                "safety_score": safety_score,
                "direct_allergy_matches": direct_matches,
                "potential_allergens": potential_allergens,
                "problematic_ingredients": problematic_ingredients,
                "recommendation": self._get_safety_recommendation(safety_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing ingredients safety: {str(e)}")
            return {
                "safety_score": 50,
                "direct_allergy_matches": [],
                "potential_allergens": [],
                "problematic_ingredients": [],
                "recommendation": "Analyse de sécurité non disponible"
            }
    
    def _find_allergy_matches(
        self,
        ingredients: List[str],
        allergies: List[str]
    ) -> List[Dict[str, str]]:
        """
        Find direct matches between ingredients and user allergies.
        
        Args:
            ingredients: List of ingredients (lowercase)
            allergies: List of user allergies (lowercase)
            
        Returns:
            List of matched ingredients with severity
        """
        matches = []
        
        for ingredient in ingredients:
            for allergy in allergies:
                if allergy in ingredient or ingredient in allergy:
                    matches.append({
                        "ingredient": ingredient,
                        "allergy": allergy,
                        "severity": "high"  # Direct match is always high severity
                    })
        
        return matches
    
    def _find_potential_allergens(self, ingredients: List[str]) -> List[Dict[str, str]]:
        """
        Find ingredients that belong to common allergen categories.
        
        Args:
            ingredients: List of ingredients (lowercase)
            
        Returns:
            List of potential allergens
        """
        potential_allergens = []
        
        for category, category_ingredients in self.allergens.items():
            for ingredient in ingredients:
                for category_ingredient in category_ingredients:
                    if category_ingredient in ingredient:
                        potential_allergens.append({
                            "ingredient": ingredient,
                            "category": category,
                            "severity": "medium"
                        })
                        break
        
        return potential_allergens
    
    def _find_problematic_ingredients(self, ingredients: List[str]) -> List[Dict[str, str]]:
        """
        Find ingredients that might be problematic for sensitive skin.
        
        Args:
            ingredients: List of ingredients (lowercase)
            
        Returns:
            List of problematic ingredients
        """
        problematic = []
        
        # High-risk ingredients for sensitive skin
        high_risk = [
            'alcohol denat', 'ethanol', 'isopropyl alcohol',
            'sodium lauryl sulfate', 'sodium laureth sulfate',
            'retinol', 'tretinoin', 'salicylic acid', 'glycolic acid'
        ]
        
        for ingredient in ingredients:
            for risk_ingredient in high_risk:
                if risk_ingredient in ingredient:
                    problematic.append({
                        "ingredient": ingredient,
                        "risk_type": "sensitive_skin",
                        "severity": "high"
                    })
                    break
        
        return problematic
    
    def _calculate_safety_score(
        self,
        direct_matches: List[Dict[str, str]],
        potential_allergens: List[Dict[str, str]],
        problematic_ingredients: List[Dict[str, str]]
    ) -> int:
        """
        Calculate overall safety score (0-100).
        
        Args:
            direct_matches: Direct allergy matches
            potential_allergens: Potential allergen matches
            problematic_ingredients: Problematic ingredients
            
        Returns:
            Safety score (0-100, higher is safer)
        """
        score = 100
        
        # Deduct points for direct allergy matches (high severity)
        score -= len(direct_matches) * 30
        
        # Deduct points for potential allergens (medium severity)
        score -= len(potential_allergens) * 15
        
        # Deduct points for problematic ingredients (high severity)
        score -= len(problematic_ingredients) * 20
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _get_safety_recommendation(self, safety_score: int) -> str:
        """
        Get safety recommendation based on score.
        
        Args:
            safety_score: Safety score (0-100)
            
        Returns:
            Safety recommendation
        """
        if safety_score >= 75:
            return "Produit excellent pour votre profil"
        elif safety_score >= 50:
            return "Produit bon pour votre profil"
        elif safety_score >= 25:
            return "Produit médiocre, surveillez les réactions"
        else:
            return "Produit déconseillé pour votre profil"
    
    def format_ingredients_for_ai(
        self,
        ingredients: List[str],
        safety_analysis: Dict[str, Any]
    ) -> str:
        """
        Format ingredients and safety analysis for AI prompt.
        
        Args:
            ingredients: List of product ingredients
            safety_analysis: Safety analysis results
            
        Returns:
            Formatted ingredients section for AI
        """
        if not ingredients:
            return "**Ingrédients:** Non disponibles"
        
        # Format ingredients list
        ingredients_text = "\n".join([f"- {ing}" for ing in ingredients])
        
        # Format safety information
        safety_text = f"""
**Analyse de Sécurité:**
- **Score de sécurité:** {safety_analysis.get('safety_score', 50)}/100
- **Recommandation:** {safety_analysis.get('recommendation', 'Non disponible')}
        """.strip()
        
        # Format allergy matches if any
        allergy_matches = safety_analysis.get('direct_allergy_matches', [])
        if allergy_matches:
            allergy_text = "\n**⚠️ Allergies détectées:**\n"
            for match in allergy_matches:
                allergy_text += f"- {match['ingredient']} (allergie: {match['allergy']})\n"
        else:
            allergy_text = ""
        
        # Format potential allergens if any
        potential_allergens = safety_analysis.get('potential_allergens', [])
        if potential_allergens:
            allergen_text = "\n**⚠️ Allergènes potentiels:**\n"
            for allergen in potential_allergens:
                allergen_text += f"- {allergen['ingredient']} (catégorie: {allergen['category']})\n"
        else:
            allergen_text = ""
        
        return f"""
**Ingrédients du Produit:**
{ingredients_text}

{safety_text}{allergy_text}{allergen_text}
        """.strip()
