"""
Service pour rechercher les vraies informations de produits par code-barres.
Utilise plusieurs APIs pour obtenir les données réelles des produits.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from backend.core.config import settings
from .base_service import CacheableService

logger = logging.getLogger(__name__)


class RealProductService(CacheableService):
    """
    Service pour rechercher les vraies informations de produits par code-barres.
    Utilise plusieurs APIs pour obtenir les données réelles.
    """
    
    def __init__(self):
        """Initialize Real Product service."""
        super().__init__(
            service_name="RealProductService",
            base_url="",
            cache_ttl=86400  # 24 hours cache for product data
        )
    
    def search_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Recherche les vraies informations d'un produit par code-barres.
        
        Args:
            barcode: Code-barres du produit
            
        Returns:
            Informations réelles du produit ou None
        """
        try:
            logger.info(f"Searching real product information for barcode: {barcode}")
            
            # Essayer plusieurs APIs dans l'ordre
            apis = [
                self._search_openfoodfacts,
                self._search_upcitemdb,
                self._search_barcodelookup,
                self._search_products_api
            ]
            
            for api_func in apis:
                try:
                    result = api_func(barcode)
                    if result and result.get('name'):
                        logger.info(f"Found product information using {api_func.__name__}")
                        return result
                except Exception as e:
                    logger.warning(f"API {api_func.__name__} failed: {str(e)}")
                    continue
            
            logger.warning(f"No real product information found for barcode: {barcode}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching product by barcode: {str(e)}")
            return None
    
    def _search_openfoodfacts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Recherche dans OpenFoodFacts (inclut les cosmétiques).
        """
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 1 and data.get('product'):
                product = data['product']
                
                return {
                    'name': product.get('product_name', ''),
                    'brand': product.get('brands', ''),
                    'categories': product.get('categories', ''),
                    'ingredients_text': product.get('ingredients_text', ''),
                    'ingredients_list': product.get('ingredients', []),
                    'image_url': product.get('image_url', ''),
                    'source': 'openfoodfacts',
                    'confidence': 'high'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"OpenFoodFacts search failed: {str(e)}")
            return None
    
    def _search_upcitemdb(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Recherche dans UPCItemDB.
        """
        try:
            url = f"https://api.upcitemdb.com/prod/trial/lookup"
            params = {'upc': barcode}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 'OK' and data.get('items'):
                item = data['items'][0]
                
                return {
                    'name': item.get('title', ''),
                    'brand': item.get('brand', ''),
                    'categories': item.get('category', ''),
                    'ingredients_text': '',  # UPCItemDB ne fournit pas d'ingrédients
                    'ingredients_list': [],
                    'image_url': item.get('images', [''])[0] if item.get('images') else '',
                    'source': 'upcitemdb',
                    'confidence': 'medium'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"UPCItemDB search failed: {str(e)}")
            return None
    
    def _search_barcodelookup(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Recherche dans BarcodeLookup (nécessite une clé API).
        """
        try:
            # Vérifier si une clé API est configurée
            api_key = getattr(settings, 'BARCODE_LOOKUP_API_KEY', None)
            if not api_key:
                logger.info("BarcodeLookup API key not configured, skipping")
                return None
            
            url = f"https://api.barcodelookup.com/v3/products"
            params = {
                'barcode': barcode,
                'formatted': 'y',
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('products'):
                product = data['products'][0]
                
                return {
                    'name': product.get('title', ''),
                    'brand': product.get('brand', ''),
                    'categories': product.get('category', ''),
                    'ingredients_text': '',  # BarcodeLookup ne fournit pas d'ingrédients
                    'ingredients_list': [],
                    'image_url': product.get('images', [''])[0] if product.get('images') else '',
                    'source': 'barcodelookup',
                    'confidence': 'medium'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"BarcodeLookup search failed: {str(e)}")
            return None
    
    def _search_products_api(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Recherche dans Products API (nécessite une clé API).
        """
        try:
            # Vérifier si une clé API est configurée
            api_key = getattr(settings, 'PRODUCTS_API_KEY', None)
            if not api_key:
                logger.info("Products API key not configured, skipping")
                return None
            
            url = f"https://api.products.com/v1/products"
            headers = {'Authorization': f'Bearer {api_key}'}
            params = {'barcode': barcode}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('products'):
                product = data['products'][0]
                
                return {
                    'name': product.get('name', ''),
                    'brand': product.get('brand', ''),
                    'categories': product.get('category', ''),
                    'ingredients_text': product.get('ingredients', ''),
                    'ingredients_list': product.get('ingredients_list', []),
                    'image_url': product.get('image_url', ''),
                    'source': 'products_api',
                    'confidence': 'high'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Products API search failed: {str(e)}")
            return None
    
    def get_product_suggestions(self, barcode: str) -> List[Dict[str, Any]]:
        """
        Obtient des suggestions de produits basées sur le code-barres.
        """
        try:
            # Analyser le code-barres pour extraire des informations
            suggestions = []
            
            # Codes-barres EAN-13 (13 chiffres)
            if len(barcode) == 13:
                country_code = barcode[:3]
                manufacturer_code = barcode[3:7]
                
                # Suggestions basées sur le code pays
                country_suggestions = {
                    '871': 'Pays-Bas (Unilever, etc.)',
                    '871': 'Pays-Bas (Palmolive, etc.)',
                    '301': 'France (L\'Oréal, etc.)',
                    '400': 'Allemagne (Nivea, etc.)',
                    '500': 'Royaume-Uni (Unilever, etc.)',
                    '690': 'Chine (produits cosmétiques)',
                }
                
                if country_code in country_suggestions:
                    suggestions.append({
                        'type': 'country_hint',
                        'description': country_suggestions[country_code],
                        'confidence': 'low'
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting product suggestions: {str(e)}")
            return []
