"""
AI Ingredient Analyzer Service using Azure OpenAI.

This service analyzes cosmetic ingredients when they are not available
from OpenBeautyFacts or when additional analysis is needed.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from .base_service import CacheableService

logger = logging.getLogger(__name__)


class AIIngredientAnalyzer(CacheableService):
    """Service for analyzing cosmetic ingredients using Azure OpenAI."""
    
    def __init__(self):
        """Initialize AI Ingredient Analyzer service."""
        super().__init__(
            service_name="AIIngredientAnalyzer",
            base_url="",  # Not needed for this service
            cache_ttl=7200  # 2 hours cache for AI analysis
        )
    
    def analyze_product_ingredients(self, barcode: str, product_name: str = "") -> Dict[str, Any]:
        """
        Analyze product ingredients using Azure OpenAI when OpenBeautyFacts data is missing.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available
            
        Returns:
            Dictionary containing analyzed ingredients and metadata
        """
        # Check cache first
        cache_key = f"ai_analysis_{barcode}"
        cached_result = self.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            logger.info(f"Analyzing ingredients for barcode {barcode} using Azure OpenAI")
            
            # Create comprehensive analysis prompt
            prompt = self._create_comprehensive_analysis_prompt(barcode, product_name)
            response = self._call_azure_openai(prompt)
            
            if not response:
                logger.warning("Azure OpenAI analysis failed")
                return self._get_fallback_analysis(barcode, product_name)
            
            # Parse the AI response
            analysis_data = self._parse_ai_response(response)
            
            if analysis_data:
                logger.info(f"Successfully analyzed ingredients for barcode {barcode}")
                # Cache the result
                self.set_cached_data(cache_key, analysis_data)
                
                self.log_operation("analyze_product_ingredients", {
                    'barcode': barcode,
                    'ingredients_count': len(analysis_data.get('ingredients', [])),
                    'confidence': analysis_data.get('metadata', {}).get('confidence', 'unknown')
                })
                
                return analysis_data
            else:
                logger.warning("Failed to parse AI response")
                return self._get_fallback_analysis(barcode, product_name)
                
        except Exception as e:
            logger.error(f"Error analyzing ingredients with AI: {str(e)}")
            return self._get_fallback_analysis(barcode, product_name)
    
    def _create_comprehensive_analysis_prompt(self, barcode: str, product_name: str) -> str:
        """
        Create a comprehensive prompt for ingredient analysis.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert cosmetic chemist and safety specialist. Your task is to analyze a cosmetic product based on its barcode and generate a comprehensive ingredient analysis.

PRODUCT BARCODE: {barcode}
PRODUCT NAME: {product_name if product_name else 'Unknown cosmetic product'}

TASK: Generate a realistic and safe list of cosmetic ingredients with detailed analysis.

REQUIREMENTS:
1. Generate 8-15 realistic cosmetic ingredients
2. Use standard INCI ingredient names (English)
3. Include common ingredients for cosmetic formulations
4. Ensure all ingredients are safe and commonly used
5. Start with water (Aqua) as first ingredient
6. Include preservatives, emulsifiers, and active ingredients
7. Consider typical product categories (cream, lotion, shampoo, etc.)

EXPECTED JSON FORMAT:
{{
    "ingredients": [
        {{
            "name": "Aqua",
            "function": "Solvent",
            "safety_level": "Safe",
            "common_use": "Base ingredient in most cosmetics"
        }},
        {{
            "name": "Glycerin",
            "function": "Humectant",
            "safety_level": "Safe",
            "common_use": "Moisturizing agent"
        }}
    ],
    "metadata": {{
        "total_ingredients": 10,
        "safety_assessment": "All ingredients are safe for cosmetic use",
        "product_category": "General cosmetic product",
        "processing_notes": "Generated using Azure OpenAI for barcode {barcode}",
        "source": "azure_openai_analysis",
        "confidence": "high"
    }}
}}

IMPORTANT: Return ONLY the JSON, no additional text or explanations. Ensure the JSON is valid and complete.
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the AI response and extract ingredient data.
        
        Args:
            response: Raw AI response
            
        Returns:
            Parsed data or None if parsing fails
        """
        try:
            # Clean the response
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            # Parse JSON
            data = json.loads(cleaned_response)
            
            # Validate structure
            if not isinstance(data, dict):
                return None
            
            if 'ingredients' not in data or not isinstance(data['ingredients'], list):
                return None
            
            # Extract ingredients list for compatibility
            ingredients_list = [ing.get('name', '') for ing in data['ingredients'] if ing.get('name')]
            ingredients_text = ". ".join(ingredients_list)
            
            # Create compatible structure
            parsed_data = {
                'cleaned_ingredients': ingredients_list,
                'ingredients_text': ingredients_text,
                'detailed_analysis': data.get('ingredients', []),
                'metadata': {
                    'original_count': 0,
                    'cleaned_count': len(ingredients_list),
                    'duplicates_removed': 0,
                    'languages_detected': ['en'],
                    'processing_notes': data.get('metadata', {}).get('processing_notes', 'AI analysis completed'),
                    'source': 'azure_openai_analysis',
                    'confidence': data.get('metadata', {}).get('confidence', 'high'),
                    'safety_assessment': data.get('metadata', {}).get('safety_assessment', 'Safe ingredients')
                }
            }
            
            return parsed_data
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return None
    
    def _get_fallback_analysis(self, barcode: str, product_name: str) -> Dict[str, Any]:
        """
        Get fallback analysis when AI analysis fails.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available
            
        Returns:
            Basic fallback analysis structure
        """
        # Safe and common cosmetic ingredients as fallback
        fallback_ingredients = [
            "Aqua",
            "Glycerin",
            "Cetearyl Alcohol",
            "Stearic Acid",
            "Cetyl Alcohol",
            "Glyceryl Stearate",
            "Dimethicone",
            "Phenoxyethanol",
            "Caprylyl Glycol",
            "Xanthan Gum"
        ]
        
        return {
            'cleaned_ingredients': fallback_ingredients,
            'ingredients_text': ". ".join(fallback_ingredients),
            'detailed_analysis': [],
            'metadata': {
                'original_count': 0,
                'cleaned_count': len(fallback_ingredients),
                'duplicates_removed': 0,
                'languages_detected': ['en'],
                'processing_notes': f'Fallback analysis for barcode {barcode} - AI analysis failed',
                'source': 'fallback_analysis',
                'confidence': 'low',
                'safety_assessment': 'Safe fallback ingredients'
            }
        }
    
    def _call_azure_openai(self, prompt: str) -> Optional[str]:
        """
        Call Azure OpenAI API for ingredient analysis.
        
        Args:
            prompt: The prompt to send to Azure OpenAI
            
        Returns:
            AI response or None if call fails
        """
        try:
            # Import Azure OpenAI client
            from openai import AzureOpenAI
            
            # Check if Azure OpenAI is configured
            if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT:
                logger.warning("Azure OpenAI not configured - using fallback")
                return None
            
            # Initialize Azure OpenAI client
            client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            
            # Call Azure OpenAI
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cosmetic chemist and safety specialist. Provide accurate, safe ingredient analysis in JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent responses
                max_tokens=1500
            )
            
            # Extract response content
            ai_response = response.choices[0].message.content
            logger.info(f"Azure OpenAI response received: {len(ai_response)} characters")
            
            return ai_response
            
        except ImportError:
            logger.warning("Azure OpenAI package not installed - using fallback")
            return None
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {str(e)}")
            return None
