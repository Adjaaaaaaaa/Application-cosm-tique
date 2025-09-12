"""
Ingredient Cleaner Service using Azure OpenAI.

This service cleans and standardizes ingredient lists from OpenBeautyFacts
to eliminate duplicates, translate to English, and create clean JSON format.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from .base_service import CacheableService

logger = logging.getLogger(__name__)


class IngredientCleanerService(CacheableService):
    """Service for cleaning and standardizing ingredient lists using Azure OpenAI."""
    
    def __init__(self):
        """Initialize Ingredient Cleaner service."""
        super().__init__(
            service_name="IngredientCleanerService",
            base_url="",  # Not needed for this service
            cache_ttl=7200  # 2 hours cache for cleaned ingredients
        )
        # Azure OpenAI configuration will be done in _call_azure_openai method
    
    def clean_ingredients_list(self, ingredients_text: str, product_name: str = "") -> Dict[str, Any]:
        """
        Clean and standardize ingredient list using Azure OpenAI.
        
        Args:
            ingredients_text: Raw ingredients text from OpenBeautyFacts
            product_name: Name of the product (for context)
            
        Returns:
            Dictionary containing cleaned ingredients and metadata
        """
        # Check cache first
        cache_key = f"cleaned_ingredients_{hash(ingredients_text)}"
        cached_result = self.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Use Azure OpenAI for ingredient cleaning
            logger.info("Using Azure OpenAI for ingredient cleaning")
            
            # Create the prompt
            prompt = self._create_cleaning_prompt(ingredients_text, product_name)
            logger.info(f"Prompt créé: {len(prompt)} caractères")
            
            # Call Azure OpenAI
            response = self._call_azure_openai(prompt)
            logger.info(f"Réponse Azure OpenAI reçue: {len(response)} caractères")
            logger.debug(f"Réponse complète: {response}")
            
            # Parse the response
            cleaned_data = self._parse_ai_response(response)
            
            if cleaned_data:
                logger.info("Azure OpenAI processing successful")
                # Add source information to metadata
                cleaned_data['metadata']['source'] = 'azure_openai'
                cleaned_data['metadata']['confidence'] = 'high'
            else:
                logger.warning("Azure OpenAI processing failed, using fallback")
                cleaned_data = self._get_fallback_cleaned_ingredients(ingredients_text)
            
            # Cache the result
            self.set_cached_data(cache_key, cleaned_data)
            
            self.log_operation("clean_ingredients_list", {
                'original_count': len(ingredients_text.split(',')),
                'cleaned_count': len(cleaned_data.get('cleaned_ingredients', [])),
                'product_name': product_name,
                'ai_processing': cleaned_data.get('metadata', {}).get('processing_notes', '').startswith('Enhanced fallback')
            })
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error in Azure OpenAI processing: {str(e)}")
            # Use fallback if AI processing fails
            cleaned_data = self._get_fallback_cleaned_ingredients(ingredients_text)
            self.set_cached_data(cache_key, cleaned_data)
            return cleaned_data
    
    def _create_cleaning_prompt(self, ingredients_text: str, product_name: str) -> str:
        """
        Create a prompt for Azure OpenAI to clean ingredients.
        
        Args:
            ingredients_text: Raw ingredients text
            product_name: Product name for context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert cosmetic chemist and ingredient specialist. Your task is to clean and standardize a list of cosmetic ingredients.

PRODUCT: {product_name if product_name else 'Unknown cosmetic product'}

ORIGINAL INGREDIENTS TEXT:
{ingredients_text}

TASK: Clean and standardize this ingredient list by:
1. Removing duplicates (e.g., "aqua" and "water" are the same)
2. Translating all ingredients to English
3. Standardizing ingredient names to INCI format
4. Removing unnecessary words, numbers, or symbols
5. Organizing ingredients in a logical order

REQUIREMENTS:
- Return ONLY valid JSON format
- Use standard INCI ingredient names
- Remove duplicates completely
- Ensure all ingredients are in English
- Maintain the original meaning and safety information

EXPECTED JSON FORMAT:
{{
    "cleaned_ingredients": [
        "Aqua",
        "Glycerin",
        "Cetearyl Alcohol",
        "Stearic Acid"
    ],
    "metadata": {{
        "original_count": 15,
        "cleaned_count": 12,
        "duplicates_removed": 3,
        "languages_detected": ["en", "fr"],
        "processing_notes": "Removed duplicate 'aqua/water', standardized alcohol names"
    }}
}}

IMPORTANT: Return ONLY the JSON, no additional text or explanations.
"""
        return prompt
    
    def _call_azure_openai(self, prompt: str) -> str:
        """
        Call Azure OpenAI API to clean ingredients.
        
        Args:
            prompt: The prompt to send to Azure OpenAI
            
        Returns:
            Response from Azure OpenAI
        """
        try:
            # Check if Azure OpenAI is configured
            if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT:
                raise ValueError("Azure OpenAI not configured")
            
            # Create Azure OpenAI client
            from openai import AzureOpenAI
            
            try:
                # Try basic client creation first
                client = AzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
                logger.info("Azure OpenAI client created with basic configuration")
                
            except TypeError as e:
                if "proxies" in str(e):
                    # Use custom httpx client to avoid proxy issues
                    logger.info("Proxy issue detected, using custom httpx client")
                    import httpx
                    
                    http_client = httpx.Client(
                        timeout=30.0,
                        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                    )
                    
                    client = AzureOpenAI(
                        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        api_key=settings.AZURE_OPENAI_KEY,
                        api_version=settings.AZURE_OPENAI_API_VERSION,
                        http_client=http_client
                    )
                    logger.info("Azure OpenAI client created with custom httpx client")
                else:
                    raise e
            
            # Call the API
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert cosmetic chemist and ingredient specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=1000
            )
            
            # Extract the response content
            ai_response = response.choices[0].message.content
            logger.info(f"Azure OpenAI response received: {len(ai_response)} characters")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {str(e)}")
            raise e
    
    def _parse_ai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the response from Azure OpenAI.
        
        Args:
            response: Raw response from Azure OpenAI
            
        Returns:
            Parsed dictionary or None if parsing fails
        """
        try:
            # Clean the response to extract JSON
            cleaned_response = self._extract_json_from_response(response)
            
            if not cleaned_response:
                return None
            
            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            
            # Try to validate as ingredient analysis first (new format)
            if self._validate_ingredient_analysis_data(parsed_data):
                logger.info("Valid ingredient analysis data structure detected")
                return parsed_data
            
            # Fallback to old cleaned ingredients validation
            if self._validate_cleaned_data(parsed_data):
                logger.info("Valid cleaned ingredients data structure detected")
                return parsed_data
            
            logger.warning("Invalid structure in AI response data")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return None
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract JSON from Azure OpenAI response.
        
        Args:
            response: Raw response string
            
        Returns:
            Cleaned JSON string or None
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    return response[start:end].strip()
            
            # Look for JSON-like content
            start = response.find("{")
            end = response.rfind("}") + 1
            
            if start != -1 and end > start:
                json_content = response[start:end]
                # Validate it's valid JSON
                json.loads(json_content)
                return json_content
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return None
    
    def _validate_ingredient_analysis_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate the structure of ingredient analysis data.
        
        Args:
            data: Parsed data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required keys for ingredient analysis
            if 'ingredient_name' not in data:
                return False
            
            if 'safety_assessment' not in data:
                return False
            
            if 'ai_analysis' not in data:
                return False
            
            # Check safety_assessment structure
            safety = data['safety_assessment']
            if not isinstance(safety, dict):
                return False
            
            if 'h_codes' not in safety:
                return False
            
            # Check that h_codes is a list and has at least one item
            if not isinstance(safety['h_codes'], list) or len(safety['h_codes']) == 0:
                return False
            
            # Check each H-code has required fields
            for h_code in safety['h_codes']:
                if not isinstance(h_code, dict):
                    return False
                if 'code' not in h_code or 'weight' not in h_code:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ingredient analysis validation error: {str(e)}")
            return False
    
    def _validate_cleaned_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate the structure of cleaned ingredients data.
        
        Args:
            data: Parsed data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required keys
            if 'cleaned_ingredients' not in data:
                return False
            
            if 'metadata' not in data:
                return False
            
            # Check that cleaned_ingredients is a list
            if not isinstance(data['cleaned_ingredients'], list):
                return False
            
            # Check that all ingredients are strings
            for ingredient in data['cleaned_ingredients']:
                if not isinstance(ingredient, str) or not ingredient.strip():
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False
    
    def _get_fallback_cleaned_ingredients(self, ingredients_text: str) -> Dict[str, Any]:
        """
        Get fallback cleaned ingredients when AI processing fails.
        
        Args:
            ingredients_text: Original ingredients text
            
        Returns:
            Basic cleaned ingredients structure
        """
        try:
            # Enhanced ingredient separation
            ingredients_list = self._smart_split_ingredients(ingredients_text)
            
            # Remove obvious duplicates (case-insensitive)
            seen = set()
            cleaned_ingredients = []
            
            for ingredient in ingredients_list:
                ingredient_lower = ingredient.lower()
                if ingredient_lower not in seen:
                    seen.add(ingredient_lower)
                    cleaned_ingredients.append(ingredient)
            
            return {
                "cleaned_ingredients": cleaned_ingredients,
                "metadata": {
                    "original_count": len(ingredients_list),
                    "cleaned_count": len(cleaned_ingredients),
                    "duplicates_removed": len(ingredients_list) - len(cleaned_ingredients),
                    "languages_detected": ["unknown"],
                    "processing_notes": "Enhanced fallback processing - smart ingredient separation",
                    "source": "fallback_smart_split",
                    "confidence": "medium"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fallback processing: {str(e)}")
            return {
                "cleaned_ingredients": [ingredients_text],
                "metadata": {
                    "original_count": 1,
                    "cleaned_count": 1,
                    "duplicates_removed": 0,
                    "languages_detected": ["unknown"],
                    "processing_notes": "Error in processing - using original text"
                }
            }
    
    def _smart_split_ingredients(self, ingredients_text: str) -> List[str]:
        """
        Smart splitting of ingredients text using multiple separators and patterns.
        
        Args:
            ingredients_text: Raw ingredients text
            
        Returns:
            List of individual ingredients
        """
        import re
        
        # Clean the text first
        cleaned_text = ingredients_text.strip()
        
        # Common separators in order of preference
        separators = [
            r'\.\s*',           # Period (most common in your example)
            r',\s*',            # Comma
            r';\s*',            # Semicolon
            r'\s+et\s+',        # French "et"
            r'\s+and\s+',       # English "and"
            r'\s*\*\s*',        # Asterisk
            r'\s*•\s*',         # Bullet point
            r'\s*\-\s*',        # Dash
        ]
        
        # Try to find the best separator
        best_separator = None
        max_ingredients = 1
        
        for separator in separators:
            if re.search(separator, cleaned_text):
                split_result = re.split(separator, cleaned_text)
                if len(split_result) > max_ingredients:
                    max_ingredients = len(split_result)
                    best_separator = separator
        
        # If no good separator found, try to split by common patterns
        if not best_separator:
            # Look for patterns like "INGREDIENT (DESCRIPTION)" or "INGREDIENT. NEXT_INGREDIENT"
            ingredients = []
            current_ingredient = ""
            
            # Split by periods and look for ingredient patterns
            parts = cleaned_text.split('.')
            for part in parts:
                part = part.strip()
                if part:
                    # Check if this looks like an ingredient
                    if self._looks_like_ingredient(part):
                        if current_ingredient:
                            ingredients.append(current_ingredient.strip())
                        current_ingredient = part
                    else:
                        # This might be a continuation of the previous ingredient
                        if current_ingredient:
                            current_ingredient += ". " + part
                        else:
                            current_ingredient = part
            
            if current_ingredient:
                ingredients.append(current_ingredient.strip())
            
            return ingredients
        
        # Use the best separator found
        ingredients = re.split(best_separator, cleaned_text)
        return [ing.strip() for ing in ingredients if ing.strip()]
    
    def _looks_like_ingredient(self, text: str) -> bool:
        """
        Check if a text fragment looks like an ingredient name.
        
        Args:
            text: Text to check
            
        Returns:
            True if it looks like an ingredient
        """
        import re
        
        # Common ingredient patterns
        ingredient_patterns = [
            r'^[A-Z][A-Z\s]+$',  # All caps (like "MINERAL OIL")
            r'^[A-Z][a-z\s]+$',  # Title case (like "Bees Wax")
            r'\([A-Z\s]+\)',      # Parentheses with caps (like "(PARAF - FINUM LIQUIDUM)")
            r'[A-Z]{2,}',         # Multiple caps (like "BHT", "C20-40")
        ]
        
        for pattern in ingredient_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def get_ingredients_for_pubchem(self, cleaned_data: Dict[str, Any]) -> List[str]:
        """
        Extract ingredients list ready for PubChem analysis.
        
        Args:
            cleaned_data: Cleaned ingredients data from Azure OpenAI
            
        Returns:
            List of ingredient names ready for PubChem
        """
        try:
            ingredients = cleaned_data.get('cleaned_ingredients', [])
            
            # Filter out common non-chemical ingredients
            excluded_ingredients = {
                'aqua', 'water', 'eau', 'agua', 'voda', 'wasser',
                'parfum', 'fragrance', 'aroma', 'scent',
                'colorant', 'color', 'couleur', 'farbe',
                'preservative', 'conservateur', 'konservierungsmittel'
            }
            
            filtered_ingredients = []
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                if ingredient_lower not in excluded_ingredients:
                    filtered_ingredients.append(ingredient)
            
            return filtered_ingredients
            
        except Exception as e:
            logger.error(f"Error preparing ingredients for PubChem: {str(e)}")
            return cleaned_data.get('cleaned_ingredients', [])
    
    def generate_ingredients_from_barcode(self, barcode: str, product_name: str = "") -> Dict[str, Any]:
        """
        Generate ingredients list from barcode when OpenBeautyFacts doesn't have data.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available
            
        Returns:
            Dictionary containing generated ingredients and metadata
        """
        try:
            logger.info(f"Generating ingredients for barcode {barcode} using Azure OpenAI")
            
            prompt = self._create_barcode_ingredients_prompt(barcode, product_name)
            response = self._call_azure_openai(prompt)
            generated_data = self._parse_ai_response(response)
            
            if not generated_data:
                logger.warning("Azure OpenAI ingredient generation failed")
                return self._get_fallback_generated_ingredients(barcode, product_name)
            
            # Cache the result
            cache_key = f"generated_ingredients_{barcode}"
            self.set_cached_data(cache_key, generated_data)
            
            return generated_data
            
        except Exception as e:
            logger.error(f"Error generating ingredients from barcode: {str(e)}")
            return self._get_fallback_generated_ingredients(barcode, product_name)
    
    def _analyze_product_type(self, product_name: str) -> str:
        """
        Analyze product type from product name to generate appropriate ingredients.
        
        Args:
            product_name: Product name to analyze
            
        Returns:
            Product type analysis string
        """
        if not product_name:
            return "Unknown product type - use generic cosmetic ingredients"
        
        product_name_lower = product_name.lower()
        
        # Define product type patterns
        product_types = {
            "petroleum jelly": {
                "keywords": ["vaseline", "petroleum", "jelly", "pommade"],
                "description": "Petroleum jelly product - Original versions should be 100% Petrolatum, enriched versions can have additional ingredients"
            },
            "shower gel": {
                "keywords": ["shower", "gel", "douche", "bain"],
                "description": "Shower gel product - should contain surfactants like Sodium Laureth Sulfate, Cocamidopropyl Betaine"
            },
            "shampoo": {
                "keywords": ["shampoo", "shampoing"],
                "description": "Shampoo product - should contain surfactants and conditioning agents"
            },
            "cream": {
                "keywords": ["cream", "crème", "moisturizer", "hydratant"],
                "description": "Cream product - should contain emollients, humectants, and emulsifiers"
            },
            "lotion": {
                "keywords": ["lotion", "body", "corps"],
                "description": "Lotion product - should contain lighter emollients and humectants"
            },
            "soap": {
                "keywords": ["soap", "savon", "bar"],
                "description": "Soap product - should contain saponified oils and fats"
            },
            "lip balm": {
                "keywords": ["lip", "lèvre", "balm", "baume"],
                "description": "Lip balm product - should contain waxes, oils, and emollients"
            },
            "deodorant": {
                "keywords": ["deodorant", "déodorant", "antiperspirant"],
                "description": "Deodorant product - should contain aluminum compounds and antimicrobial agents"
            }
        }
        
        # Find matching product type
        for product_type, info in product_types.items():
            for keyword in info["keywords"]:
                if keyword in product_name_lower:
                    return info["description"]
        
        # Default analysis
        return f"Generic cosmetic product - analyze name '{product_name}' to determine appropriate ingredients"
    
    def _get_appropriate_fallback_ingredients(self, product_name: str) -> List[str]:
        """
        Get appropriate fallback ingredients based on product type.
        
        Args:
            product_name: Product name to analyze
            
        Returns:
            List of appropriate ingredients for the product type
        """
        if not product_name:
            return self._get_generic_fallback_ingredients()
        
        product_name_lower = product_name.lower()
        
        # Petroleum jelly products
        if any(keyword in product_name_lower for keyword in ["vaseline", "petroleum", "jelly", "pommade"]):
            # Check if it's "original" or "classic" version
            if any(keyword in product_name_lower for keyword in ["original", "classic", "pure", "100%"]):
                # Original Vaseline should be 100% Petrolatum
                return ["Petrolatum"]
            else:
                # Enriched versions can have additional ingredients
                return [
                    "Petrolatum",
                    "Paraffin",
                    "Mineral Oil",
                    "Microcrystalline Wax"
                ]
        
        # Shower gel products
        elif any(keyword in product_name_lower for keyword in ["shower", "gel", "douche", "bain"]):
            return [
                "Aqua",
                "Sodium Laureth Sulfate",
                "Cocamidopropyl Betaine",
                "Sodium Chloride",
                "Glycerin",
                "Cocamide MEA",
                "Parfum",
                "Citric Acid",
                "Sodium Benzoate",
                "Tetrasodium EDTA"
            ]
        
        # Shampoo products
        elif any(keyword in product_name_lower for keyword in ["shampoo", "shampoing"]):
            return [
                "Aqua",
                "Sodium Laureth Sulfate",
                "Cocamidopropyl Betaine",
                "Glycerin",
                "Cocamide MEA",
                "Guar Hydroxypropyltrimonium Chloride",
                "Parfum",
                "Citric Acid",
                "Sodium Benzoate",
                "Tetrasodium EDTA"
            ]
        
        # Cream products
        elif any(keyword in product_name_lower for keyword in ["cream", "crème", "moisturizer", "hydratant"]):
            return [
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
        
        # Soap products
        elif any(keyword in product_name_lower for keyword in ["soap", "savon", "bar"]):
            return [
                "Sodium Palmate",
                "Sodium Palm Kernelate",
                "Aqua",
                "Glycerin",
                "Sodium Chloride",
                "Tocopherol",
                "Parfum"
            ]
        
        # Default fallback
        return self._get_generic_fallback_ingredients()
    
    def _get_generic_fallback_ingredients(self) -> List[str]:
        """
        Get generic fallback ingredients for unknown product types.
        
        Returns:
            List of safe, commonly used cosmetic ingredients
        """
        return [
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
    
    def _create_barcode_ingredients_prompt(self, barcode: str, product_name: str) -> str:
        """
        Create prompt for generating ingredients from barcode.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available
            
        Returns:
            Formatted prompt string
        """
        # Analyze product type from name
        product_type_analysis = self._analyze_product_type(product_name)
        
        prompt = f"""
You are an expert cosmetic chemist and ingredient specialist. Your task is to generate a realistic product name and ingredients list for a cosmetic product based on its barcode.

PRODUCT BARCODE: {barcode}
PRODUCT NAME: {product_name if product_name else 'Unknown cosmetic product'}

PRODUCT TYPE ANALYSIS: {product_type_analysis}

TASK: Generate a realistic product name and list of cosmetic ingredients that would typically be found in this SPECIFIC type of product.

IMPORTANT CONTEXT:
- This is a real product that exists in stores but is not found in the OpenBeautyFacts database
- The barcode {barcode} corresponds to a real cosmetic product
- Generate realistic information that matches the actual product type and brand
- The product type has been analyzed from the name: {product_type_analysis}
- Use realistic brand names and product names that could exist

REQUIREMENTS:
- Generate a realistic product name that matches the barcode and product type
- Generate a realistic brand name (not generic names like "BeautyCare")
- Generate 8-15 realistic cosmetic ingredients SPECIFIC to the product type
- Use standard INCI ingredient names (English)
- Include ONLY ingredients that are commonly found in this specific product type
- Ensure ingredients are safe and commonly used
- Consider the product category: {product_type_analysis}
- Use ingredients that are appropriate for this specific product type
- DO NOT use ingredients from other product types (e.g., don't use shower gel ingredients for a petroleum jelly)
- For "Original" or "Classic" versions: use minimal, simple ingredients (e.g., Original Vaseline = 100% Petrolatum)
- For "Enriched" or "Advanced" versions: can include additional beneficial ingredients

EXPECTED JSON FORMAT:
{{
    "product_name": "Gel Douche Fraîcheur Olive",
    "product_brand": "Palmolive",
    "cleaned_ingredients": [
        "Aqua",
        "Sodium Laureth Sulfate",
        "Cocamidopropyl Betaine",
        "Sodium Chloride",
        "Olea Europaea Oil",
        "Glycerin",
        "Cocamide MEA",
        "Phenoxyethanol",
        "Methylparaben",
        "Propylparaben",
        "Citric Acid",
        "Sodium Hydroxide",
        "Parfum",
        "CI 19140",
        "CI 42090"
    ],
    "metadata": {{
        "original_count": 0,
        "cleaned_count": 15,
        "duplicates_removed": 0,
        "languages_detected": ["en"],
        "processing_notes": "Generated realistic product name and ingredients list for barcode {barcode} using Azure OpenAI",
        "source": "azure_openai_generated",
        "confidence": "high"
    }}
}}

IMPORTANT: Return ONLY the JSON, no additional text or explanations. Ensure the JSON is valid and complete.
"""
        return prompt
    
    def _get_fallback_generated_ingredients(self, barcode: str, product_name: str) -> Dict[str, Any]:
        """
        Get fallback generated ingredients when AI generation fails.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available
            
        Returns:
            Basic generated ingredients structure
        """
        # Analyze product type to get appropriate fallback ingredients
        product_type_analysis = self._analyze_product_type(product_name)
        
        # Get appropriate fallback ingredients based on product type
        fallback_ingredients = self._get_appropriate_fallback_ingredients(product_name)
        
        # Generate a realistic product name if not provided
        if product_name:
            generated_name = product_name
            generated_brand = "Marque Inconnue"
        else:
            # Generate realistic names based on barcode patterns
            last_digits = barcode[-4:]
            product_types = ["Gel Douche", "Shampooing", "Crème Hydratante", "Lotion", "Savon", "Déodorant"]
            brands = ["Palmolive", "Dove", "Nivea", "L'Oréal", "Garnier", "Sanex", "Fa", "Axe"]
            
            # Use barcode digits to select consistent names
            type_index = int(last_digits[:2]) % len(product_types)
            brand_index = int(last_digits[2:]) % len(brands)
            
            generated_name = f"{product_types[type_index]} {brands[brand_index]}"
            generated_brand = brands[brand_index]
        
        return {
            'product_name': generated_name,
            'product_brand': generated_brand,
            'cleaned_ingredients': fallback_ingredients,
            'metadata': {
                'original_count': 0,
                'cleaned_count': len(fallback_ingredients),
                'duplicates_removed': 0,
                'languages_detected': ['en'],
                'processing_notes': f'Fallback product name and ingredients generated for barcode {barcode} - AI generation failed',
                'source': 'fallback_generated',
                'confidence': 'low'
            }
        }

    
    def analyze_ingredient_with_ai(self, ingredient_name: str, pubchem_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze ingredient with Azure OpenAI when PubChem data is incomplete or missing.
        
        Args:
            ingredient_name: Name of the ingredient to analyze
            pubchem_data: Existing PubChem data if available
            
        Returns:
            Dictionary containing AI-enhanced ingredient analysis
        """
        try:
            logger.info(f"Analyzing ingredient {ingredient_name} with Azure OpenAI")
            
            prompt = self._create_ingredient_analysis_prompt(ingredient_name, pubchem_data)
            response = self._call_azure_openai(prompt)
            analysis_data = self._parse_ai_response(response)
            
            if not analysis_data:
                logger.warning("Azure OpenAI ingredient analysis failed")
                return self._get_fallback_ingredient_analysis(ingredient_name, pubchem_data)
            
            # Cache the result
            cache_key = f"ai_analysis_{ingredient_name.lower().replace(' ', '_')}"
            self.set_cached_data(cache_key, analysis_data)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error analyzing ingredient with AI: {str(e)}")
            return self._get_fallback_ingredient_analysis(ingredient_name, pubchem_data)
    
    def _create_ingredient_analysis_prompt(self, ingredient_name: str, pubchem_data: Dict[str, Any] = None) -> str:
        """
        Create prompt for analyzing ingredient with AI.
        
        Args:
            ingredient_name: Name of the ingredient to analyze
            pubchem_data: Existing PubChem data if available
            
        Returns:
            Formatted prompt string
        """
        pubchem_info = ""
        if pubchem_data:
            pubchem_info = f"""
EXISTING PUBCHEM DATA:
- Molecular Weight: {pubchem_data.get('molecular_weight', 'Unknown')}
- Formula: {pubchem_data.get('molecular_formula', 'Unknown')}
- IUPAC Name: {pubchem_data.get('iupac_name', 'Unknown')}
"""
        
        prompt = f"""
You are a cosmetic safety expert and toxicologist. Analyze this cosmetic ingredient and provide comprehensive H-codes for any known hazards.

INGREDIENT: {ingredient_name}
{pubchem_info}

TASK: Analyze the ingredient for potential health and environmental hazards based on its chemical properties and known toxicological data.

REQUIREMENTS:
1. You MUST provide at least 2-3 H-codes if the ingredient has known risks
2. Consider skin irritation, eye irritation, toxicity, environmental impact
3. Use specific H-codes from the GHS classification system
4. If no specific risks are known, use H400 (harmful to aquatic life) as a precaution
5. Provide realistic weight values (10-50) based on risk severity

COMMON H-CODES TO CONSIDER:
- H315: Causes skin irritation
- H319: Causes serious eye irritation  
- H335: May cause respiratory irritation
- H400: Very toxic to aquatic life
- H410: Very toxic to aquatic life with long lasting effects
- H411: Toxic to aquatic life with long lasting effects
- H302: Harmful if swallowed
- H312: Harmful in contact with skin

REQUIRED JSON FORMAT:
{{
    "ingredient_name": "{ingredient_name}",
    "safety_assessment": {{
        "overall_score": 75,
        "h_codes": [
            {{
                "code": "H315",
                "description": "Causes skin irritation",
                "weight": 25
            }},
            {{
                "code": "H400", 
                "description": "Very toxic to aquatic life",
                "weight": 15
            }}
        ]
    }},
    "ai_analysis": true
}}

IMPORTANT: Return ONLY valid JSON with at least 2 H-codes. Base your analysis on cosmetic ingredient safety knowledge.
"""
        return prompt
    
    def _get_fallback_ingredient_analysis(self, ingredient_name: str, pubchem_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get fallback ingredient analysis when AI analysis fails.
        
        Args:
            ingredient_name: Name of the ingredient to analyze
            pubchem_data: Existing PubChem data if available
            
        Returns:
            Basic ingredient analysis structure
        """
        return {
            "ingredient_name": ingredient_name,
            "chemical_properties": {
                "classification": "Unknown",
                "molecular_weight": pubchem_data.get('molecular_weight', 'Unknown') if pubchem_data else 'Unknown',
                "solubility": "Unknown"
            },
            "safety_assessment": {
                "overall_score": 50,
                "h_codes": [],
                "risk_factors": ["Unknown"],
                "precautions": ["Use with caution"]
            },
            "cosmetic_uses": ["Unknown"],
            "regulatory_status": "Unknown",
            "ai_analysis": False,
            "confidence": "low"
        }
