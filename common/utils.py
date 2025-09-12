"""
Common utility functions for the BeautyScan project.
"""

import re
from typing import List, Dict, Any
from django.core.exceptions import ValidationError


def clean_inci_name(inci_name: str) -> str:
    """Clean and standardize INCI ingredient names."""
    if not inci_name:
        return ""
    
    # Remove extra whitespace and convert to title case
    cleaned = re.sub(r'\s+', ' ', inci_name.strip()).title()
    
    # Handle common INCI naming conventions
    cleaned = re.sub(r'\b(And|Or|Of|The|In|To|For|With|By)\b', lambda m: m.group(1).lower(), cleaned)
    
    return cleaned


def validate_barcode(barcode: str) -> bool:
    """Validate barcode format."""
    if not barcode:
        return False
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', barcode)
    
    # Check if it's a valid length (8, 12, 13, or 14 digits)
    if len(digits) not in [8, 12, 13, 14]:
        return False
    
    return True


def calculate_product_score(ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate product safety score based on ingredients."""
    if not ingredients:
        return {
            'score': 0,
            'risk_level': 'Unknown',
            'hazard_count': 0,
            'safe_count': 0
        }
    
    hazard_count = 0
    safe_count = 0
    
    for ingredient in ingredients:
        hazard_level = ingredient.get('hazard_level', 'Unknown')
        if hazard_level in ['High', 'Medium']:
            hazard_count += 1
        elif hazard_level == 'Low':
            safe_count += 1
    
    total_ingredients = len(ingredients)
    if total_ingredients == 0:
        score = 0
    else:
        score = int((safe_count / total_ingredients) * 100)
    
    # Determine risk level
    if score >= 75:
        risk_level = 'Excellent'
    elif score >= 50:
        risk_level = 'Bon'
    elif score >= 25:
        risk_level = 'Médiocre'
    else:
        risk_level = 'Mauvais'
    
    return {
        'score': score,
        'risk_level': risk_level,
        'hazard_count': hazard_count,
        'safe_count': safe_count,
        'total_ingredients': total_ingredients
    }


class RiskLevel:
    """Constants for risk levels."""
    EXCELLENT = "Excellent"
    BON = "Bon"
    MEDIOCRE = "Médiocre"
    MAUVAIS = "Mauvais"
    UNKNOWN = "Unknown"


def get_risk_level(score: int) -> str:
    """Return risk level for a given product score."""
    if score >= 75:
        return RiskLevel.EXCELLENT
    elif score >= 50:
        return RiskLevel.BON
    elif score >= 25:
        return RiskLevel.MEDIOCRE
    return RiskLevel.MAUVAIS
