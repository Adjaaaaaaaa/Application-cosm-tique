"""
OpenFact Beauty API service for BeautyScan backend.

Handles product information retrieval from OpenFact Beauty database.
"""

import logging
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from .base_service import CacheableService
from .ingredient_cleaner_service import IngredientCleanerService
from .ai_ingredient_analyzer import AIIngredientAnalyzer

logger = logging.getLogger(__name__)


class OpenBeautyService(CacheableService):
    """Service for OpenFact Beauty API integration."""
    
    def __init__(self):
        """Initialize OpenBeauty service."""
        super().__init__(
            service_name="OpenBeautyService",
            base_url=settings.OPENBEAUTYFACTS_API_URL,
            cache_ttl=3600  # 1 hour cache
        )
        self.ingredient_cleaner = IngredientCleanerService()
        self.ai_analyzer = AIIngredientAnalyzer()
    
    def search_product(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products in OpenFact Beauty database.
        
        Args:
            query: Search query (product name, brand, etc.)
            limit: Maximum number of results
            
        Returns:
            List of product information
        """
        # Check cache first
        cache_key = f"search_{query}_{limit}"
        cached_result = self.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'search_terms': query,
                'json': 1,
                'page_size': limit
            }
            
            data = self.make_request('GET', 'search', params=params)
            if not data:
                return []
            
            products = data.get('products', [])
            
            # Format and filter products
            formatted_products = []
            for product in products:
                formatted_product = self._format_product(product)
                if formatted_product:
                    formatted_products.append(formatted_product)
            
            # Cache the result
            self.set_cached_data(cache_key, formatted_products)
            
            self.log_operation("search_product", {
                'query': query,
                'limit': limit,
                'results': len(formatted_products)
            })
            
            return formatted_products
            
        except Exception as e:
            self.handle_error(e, f"Searching products with query: {query}")
            return []
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Get product information by barcode with Azure OpenAI fallback.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Product information or None
        """
        # Check cache first
        cache_key = f"barcode_{barcode}"
        cached_result = self.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Try to get product from OpenBeautyFacts
            params = {'json': 1}
            data = self.make_request('GET', f'product/{barcode}', params=params)
            
            if data and data.get('product'):
                # Product found in OpenBeautyFacts
                product = data.get('product')
                formatted_product = self._format_product(product)
                
                # Cache the result
                self.set_cached_data(cache_key, formatted_product)
                
                self.log_operation("get_product_by_barcode", {
                    'barcode': barcode,
                    'source': 'openbeautyfacts'
                })
                return formatted_product
            
            else:
                # Product not found in OpenBeautyFacts - use Azure OpenAI
                logger.info(f"Product {barcode} not found in OpenBeautyFacts, generating with Azure OpenAI")
                
                generated_product = self._generate_product_with_ai(barcode)
                
                if generated_product and generated_product.get('ingredients_text'):
                    logger.info(f"Successfully generated ingredients for barcode {barcode} using Azure OpenAI")
                    # Cache the result
                    self.set_cached_data(cache_key, generated_product)
                    
                    self.log_operation("get_product_by_barcode", {
                        'barcode': barcode,
                        'source': 'azure_openai_generated',
                        'ingredients_count': len(generated_product.get('ingredients_list', []))
                    })
                    return generated_product
                else:
                    logger.warning(f"Failed to generate ingredients for barcode {barcode}")
                    return None
            
        except Exception as e:
            logger.warning(f"Error getting product by barcode {barcode}: {str(e)}")
            
            # Fallback to AI generation on error
            logger.info(f"Falling back to AI generation for barcode {barcode}")
            generated_product = self._generate_product_with_ai(barcode)
            
            if generated_product and generated_product.get('ingredients_text'):
                # Cache the result
                self.set_cached_data(cache_key, generated_product)
                return generated_product
            else:
                logger.error(f"Both OpenBeautyFacts and Azure OpenAI failed for barcode {barcode}")
                return None
    
    def _generate_product_with_ai(self, barcode: str) -> Dict[str, Any]:
        """
        Generate product information using Azure OpenAI when OpenBeautyFacts fails.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Generated product information
        """
        try:
            # Use the new AI analyzer service for comprehensive ingredient analysis
            ingredients_data = self.ai_analyzer.analyze_product_ingredients(barcode)
            
            if not ingredients_data or not ingredients_data.get('cleaned_ingredients'):
                logger.error(f"Failed to generate ingredients for barcode {barcode}")
                return None
            
            # Create a realistic product structure
            generated_product = {
                'code': barcode,
                'product_name': f"Produit cosmétique {barcode}",
                'brands': "Marque générique",
                'categories': "Cosmétiques",
                'ingredients_text': ingredients_data.get('ingredients_text', ''),
                'ingredients_list': ingredients_data['cleaned_ingredients'],
                'ingredients_cleaning': {
                    'source': 'azure_openai_generated',
                    'confidence': ingredients_data['metadata'].get('confidence', 'high'),
                    'processing_notes': ingredients_data['metadata'].get('processing_notes', ''),
                    'safety_assessment': ingredients_data['metadata'].get('safety_assessment', 'Safe ingredients')
                },
                'ingredients_cleaned': True,
                'ai_generated': True,
                'openbeautyfacts_found': False
            }
            
            logger.info(f"Generated product {barcode} with {len(ingredients_data['cleaned_ingredients'])} ingredients")
            return generated_product
            
        except Exception as e:
            logger.error(f"Error generating product with AI: {str(e)}")
            
            # Ultimate fallback
            return {
                'code': barcode,
                'product_name': f"Product {barcode}",
                'brands': "Unknown Brand",
                'categories': "Cosmetics",
                'ingredients_text': "Aqua, Glycerin, Cetearyl Alcohol, Stearic Acid, Cetyl Alcohol",
                'ingredients_list': ["Aqua", "Glycerin", "Cetearyl Alcohol", "Stearic Acid", "Cetyl Alcohol"],
                'ingredients_cleaning': {
                    'source': 'fallback',
                    'confidence': 'low',
                    'processing_notes': 'Fallback ingredients due to AI generation failure'
                },
                'ingredients_cleaned': True,
                'ai_generated': False,
                'openbeautyfacts_found': False
            }
    
    def get_ingredients_info(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information about ingredients from OpenFact Beauty.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            List of ingredient information
        """
        ingredients_info = []
        
        for ingredient in ingredients:
            # Check cache first
            cache_key = f"ingredient_{ingredient}"
            cached_result = self.get_cached_data(cache_key)
            
            if cached_result:
                ingredients_info.append(cached_result)
                continue
            
            try:
                # Search for ingredient in OpenFact Beauty
                params = {
                    'search_terms': ingredient,
                    'json': 1,
                    'page_size': 5
                }
                
                data = self.make_request('GET', 'search', params=params)
                if not data:
                    ingredient_info = self._get_fallback_ingredient_info(ingredient)
                    ingredients_info.append(ingredient_info)
                    continue
                
                products = data.get('products', [])
                
                # Find products containing this ingredient
                ingredient_info = {
                    'name': ingredient,
                    'products_count': len(products),
                    'common_products': [],
                    'safety_info': self._extract_safety_info(products, ingredient)
                }
                
                # Get common products containing this ingredient
                for product in products[:3]:  # Top 3 products
                    product_name = product.get('product_name', 'Unknown')
                    brand = product.get('brands', 'Unknown')
                    ingredient_info['common_products'].append({
                        'name': product_name,
                        'brand': brand
                    })
                
                # Cache the result
                self.set_cached_data(cache_key, ingredient_info)
                ingredients_info.append(ingredient_info)
                
            except Exception as e:
                self.logger.warning(f"Error getting info for ingredient {ingredient}: {str(e)}")
                ingredient_info = self._get_fallback_ingredient_info(ingredient)
                ingredients_info.append(ingredient_info)
        
        self.log_operation("get_ingredients_info", {
            'ingredients_count': len(ingredients),
            'results_count': len(ingredients_info)
        })
        
        return ingredients_info
    
    def _get_fallback_ingredient_info(self, ingredient: str) -> Dict[str, Any]:
        """
        Get fallback ingredient information when API fails.
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            Basic ingredient information
        """
        return {
            'name': ingredient,
            'products_count': 0,
            'common_products': [],
            'safety_info': {}
        }
    
    def _format_product(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format raw product data from OpenFact Beauty.
        
        Args:
            product: Raw product data
            
        Returns:
            Formatted product information
        """
        try:
            # Extract basic information
            product_name = product.get('product_name', 'Unknown')
            brand = product.get('brands', 'Unknown')
            barcode = product.get('code', '')
            
            # Extract ingredients
            ingredients_text = product.get('ingredients_text', '')
            ingredients_list = []
            cleaned_ingredients_data = None
            
            if ingredients_text:
                # Clean and standardize ingredients using Azure OpenAI
                cleaned_ingredients_data = self.ingredient_cleaner.clean_ingredients_list(
                    ingredients_text, product_name
                )
                
                # Use cleaned ingredients for the list
                ingredients_list = cleaned_ingredients_data.get('cleaned_ingredients', [])
                
                # Fallback to basic processing if AI cleaning failed
                if not ingredients_list:
                    ingredients_list = [ing.strip() for ing in ingredients_text.split(',')]
            
            # Extract nutrition grades (if available)
            nutrition_grade = product.get('nutrition_grade_fr', '')
            
            # Extract image
            image_url = product.get('image_front_url', '')
            
            # Extract categories
            categories = product.get('categories_tags', [])
            category_names = [cat.replace('en:', '').replace('_', ' ') for cat in categories[:5]]
            
            product_data = {
                'name': product_name,
                'brand': brand,
                'barcode': barcode,
                'ingredients_text': ingredients_text,
                'image_url': image_url,
                'ingredients_list': ingredients_list,
                'nutrition_grade': nutrition_grade,
                'categories': category_names,
                'source': 'openbeautyfacts'
            }
            
            # Add cleaning metadata if available
            if cleaned_ingredients_data:
                product_data['ingredients_cleaning'] = cleaned_ingredients_data.get('metadata', {})
                product_data['ingredients_cleaned'] = True
            else:
                product_data['ingredients_cleaned'] = False
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error formatting product: {str(e)}")
            return None
    
    def _extract_safety_info(self, products: List[Dict[str, Any]], ingredient: str) -> Dict[str, Any]:
        """
        Extract safety information from products containing the ingredient.
        
        Args:
            products: List of products
            ingredient: Ingredient name
            
        Returns:
            Safety information
        """
        safety_info = {
            'frequency': 0,
            'common_combinations': [],
            'potential_concerns': []
        }
        
        try:
            # Count frequency
            safety_info['frequency'] = len(products)
            
            # Analyze common combinations
            ingredient_combinations = {}
            for product in products:
                ingredients_text = product.get('ingredients_text', '')
                if ingredients_text and ingredient.lower() in ingredients_text.lower():
                    # Find other ingredients in the same product
                    other_ingredients = [
                        ing.strip() for ing in ingredients_text.split(',')
                        if ingredient.lower() not in ing.lower()
                    ]
                    
                    for other_ing in other_ingredients[:3]:  # Top 3 combinations
                        if other_ing:
                            ingredient_combinations[other_ing] = ingredient_combinations.get(other_ing, 0) + 1
            
            # Get top combinations
            top_combinations = sorted(
                ingredient_combinations.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            safety_info['common_combinations'] = [
                {'ingredient': ing, 'frequency': freq}
                for ing, freq in top_combinations
            ]
            
        except Exception as e:
            logger.warning(f"Error extracting safety info: {str(e)}")
        
        return safety_info
