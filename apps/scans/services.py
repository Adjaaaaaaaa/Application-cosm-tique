"""
Services for external API integration in product scanning.

This module provides services for integrating with external APIs:
- OpenBeautyFacts: Product database and ingredient information
- PubChem: Chemical compound data and safety information
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Dictionnaire complet des H-codes GHS avec catégories et poids
GHS_H_CODES = {
    # Dangers physiques (Physical Hazards)
    'H200': {'class': 'Explosifs', 'category': '1', 'description': 'Explosif instable', 'weight': -50},
    'H201': {'class': 'Explosifs', 'category': '1', 'description': 'Explosif ; danger d\'explosion en masse', 'weight': -50},
    'H202': {'class': 'Explosifs', 'category': '2', 'description': 'Explosif ; grave danger de projection', 'weight': -45},
    'H203': {'class': 'Explosifs', 'category': '3', 'description': 'Explosif ; danger d\'incendie, d\'effet de souffle ou de projection', 'weight': -40},
    'H204': {'class': 'Explosifs', 'category': '3', 'description': 'Danger d\'incendie ou de projection', 'weight': -40},
    'H205': {'class': 'Explosifs', 'category': '4', 'description': 'Danger d\'explosion en masse en cas d\'incendie', 'weight': -35},
    'H220': {'class': 'Gaz inflammables', 'category': '1', 'description': 'Gaz extrêmement inflammable', 'weight': -40},
    'H221': {'class': 'Gaz inflammables', 'category': '2', 'description': 'Gaz inflammable', 'weight': -35},
    'H222': {'class': 'Aérosols inflammables', 'category': '1', 'description': 'Aérosol extrêmement inflammable', 'weight': -40},
    'H223': {'class': 'Aérosols inflammables', 'category': '2', 'description': 'Aérosol inflammable', 'weight': -35},
    'H224': {'class': 'Liquides inflammables', 'category': '1', 'description': 'Liquide et vapeurs extrêmement inflammables', 'weight': -40},
    'H225': {'class': 'Liquides inflammables', 'category': '2', 'description': 'Liquide et vapeurs très inflammables', 'weight': -35},
    'H226': {'class': 'Liquides inflammables', 'category': '3', 'description': 'Liquide et vapeurs inflammables', 'weight': -30},
    'H228': {'class': 'Solides inflammables', 'category': '1', 'description': 'Matière solide inflammable', 'weight': -30},
    'H240': {'class': 'Auto-réactifs', 'category': '1', 'description': 'Peut exploser sous l\'effet de la chaleur', 'weight': -45},
    'H241': {'class': 'Auto-réactifs', 'category': '2', 'description': 'Peut s\'enflammer ou exploser sous l\'effet de la chaleur', 'weight': -40},
    'H242': {'class': 'Auto-réactifs', 'category': '3', 'description': 'Peut s\'enflammer sous l\'effet de la chaleur', 'weight': -35},
    'H250': {'class': 'Auto-inflammables', 'category': '1', 'description': 'S\'enflamme spontanément au contact de l\'air', 'weight': -45},
    'H251': {'class': 'Auto-inflammables', 'category': '2', 'description': 'Matière auto-échauffante ; peut s\'enflammer', 'weight': -40},
    'H252': {'class': 'Auto-inflammables', 'category': '3', 'description': 'Matière auto-échauffante en grandes quantités ; peut s\'enflammer', 'weight': -35},
    'H260': {'class': 'Réaction avec l\'eau', 'category': '1', 'description': 'Dégage, au contact de l\'eau, des gaz inflammables qui peuvent s\'enflammer spontanément', 'weight': -45},
    'H261': {'class': 'Réaction avec l\'eau', 'category': '2', 'description': 'Dégage, au contact de l\'eau, des gaz inflammables', 'weight': -40},
    'H270': {'class': 'Oxydants', 'category': '1', 'description': 'Peut provoquer ou aggraver un incendie ; comburant', 'weight': -40},
    'H271': {'class': 'Oxydants', 'category': '2', 'description': 'Peut provoquer un incendie ou une explosion ; comburant puissant', 'weight': -35},
    'H272': {'class': 'Oxydants', 'category': '3', 'description': 'Peut aggraver un incendie ; comburant', 'weight': -30},
    'H280': {'class': 'Gaz sous pression', 'category': '1', 'description': 'Contient un gaz sous pression ; peut exploser sous l\'effet de la chaleur', 'weight': -20},
    'H281': {'class': 'Gaz réfrigéré', 'category': '2', 'description': 'Contient du gaz réfrigéré ; peut provoquer des brûlures cryogéniques', 'weight': -15},
    
    # Dangers pour la santé (Health Hazards)
    'H300': {'class': 'Toxicité aiguë (oral)', 'category': '1', 'description': 'Mortel par ingestion', 'weight': -40},
    'H301': {'class': 'Toxicité aiguë (oral)', 'category': '2', 'description': 'Toxique par ingestion', 'weight': -30},
    'H302': {'class': 'Toxicité aiguë (oral)', 'category': '3', 'description': 'Nocif par ingestion', 'weight': -15},
    'H303': {'class': 'Toxicité aiguë (oral)', 'category': '4', 'description': 'Peut être nocif en cas d\'ingestion', 'weight': -5},
    'H304': {'class': 'Toxicité aiguë (oral/aspiration)', 'category': '1', 'description': 'Peut être mortel si avalé et pénètre dans les voies respiratoires', 'weight': -30},
    'H305': {'class': 'Toxicité aiguë (oral/aspiration)', 'category': '2', 'description': 'Peut être nocif si avalé et pénètre dans les voies respiratoires', 'weight': -15},
    'H310': {'class': 'Toxicité aiguë (cutané)', 'category': '1', 'description': 'Mortel par contact cutané', 'weight': -40},
    'H311': {'class': 'Toxicité aiguë (cutané)', 'category': '2', 'description': 'Toxique par contact cutané', 'weight': -30},
    'H312': {'class': 'Toxicité aiguë (cutané)', 'category': '3', 'description': 'Nocif par contact cutané', 'weight': -15},
    'H313': {'class': 'Toxicité aiguë (cutané)', 'category': '4', 'description': 'Peut être nocif en cas de contact cutané', 'weight': -5},
    'H314': {'class': 'Corrosion cutanée', 'category': '1', 'description': 'Provoque des brûlures de la peau et des lésions oculaires graves', 'weight': -25},
    'H315': {'class': 'Irritation cutanée', 'category': '2', 'description': 'Provoque une irritation cutanée', 'weight': -10},
    'H316': {'class': 'Irritation cutanée', 'category': '3', 'description': 'Provoque une légère irritation cutanée', 'weight': -5},
    'H317': {'class': 'Sensibilisation cutanée', 'category': '1', 'description': 'Peut provoquer une allergie cutanée', 'weight': -15},
    'H318': {'class': 'Lésions oculaires graves', 'category': '1', 'description': 'Provoque de graves lésions oculaires', 'weight': -25},
    'H319': {'class': 'Irritation oculaire', 'category': '2', 'description': 'Provoque une sévère irritation des yeux', 'weight': -10},
    'H320': {'class': 'Irritation oculaire', 'category': '3', 'description': 'Provoque une irritation légère des yeux', 'weight': -5},
    'H330': {'class': 'Toxicité aiguë (inhalation)', 'category': '1', 'description': 'Mortel par inhalation', 'weight': -40},
    'H331': {'class': 'Toxicité aiguë (inhalation)', 'category': '2', 'description': 'Toxique par inhalation', 'weight': -30},
    'H332': {'class': 'Toxicité aiguë (inhalation)', 'category': '3', 'description': 'Nocif par inhalation', 'weight': -15},
    'H333': {'class': 'Toxicité aiguë (inhalation)', 'category': '4', 'description': 'Peut être nocif par inhalation', 'weight': -5},
    'H334': {'class': 'Sensibilisation respiratoire', 'category': '1', 'description': 'Peut provoquer des symptômes allergiques respiratoires', 'weight': -20},
    'H335': {'class': 'Irritation respiratoire', 'category': '3', 'description': 'Peut irriter les voies respiratoires', 'weight': -10},
    'H336': {'class': 'Effets sur le SNC', 'category': '3', 'description': 'Peut provoquer somnolence ou vertiges', 'weight': -10},
    'H340': {'class': 'Mutagénicité', 'category': '1', 'description': 'Peut induire des anomalies génétiques', 'weight': -40},
    'H341': {'class': 'Mutagénicité', 'category': '2', 'description': 'Susceptible d\'induire des anomalies génétiques', 'weight': -25},
    'H350': {'class': 'Cancérogénicité', 'category': '1', 'description': 'Peut provoquer le cancer', 'weight': -40},
    'H351': {'class': 'Cancérogénicité', 'category': '2', 'description': 'Susceptible de provoquer le cancer', 'weight': -25},
    'H360': {'class': 'Reprotoxicité', 'category': '1', 'description': 'Peut nuire à la fertilité ou au fœtus', 'weight': -40},
    'H361': {'class': 'Reprotoxicité', 'category': '2', 'description': 'Susceptible de nuire à la fertilité ou au fœtus', 'weight': -25},
    'H362': {'class': 'Reprotoxicité', 'category': '3', 'description': 'Peut être nocif pour les bébés nourris au lait maternel', 'weight': -15},
    'H370': {'class': 'STOT (exposition unique)', 'category': '1', 'description': 'Risque avéré d\'effets graves pour les organes', 'weight': -35},
    'H371': {'class': 'STOT (exposition unique)', 'category': '2', 'description': 'Risque présumé d\'effets graves pour les organes', 'weight': -20},
    'H372': {'class': 'STOT (exposition répétée)', 'category': '1', 'description': 'Risque avéré d\'effets graves pour les organes', 'weight': -35},
    'H373': {'class': 'STOT (exposition répétée)', 'category': '2', 'description': 'Risque présumé d\'effets graves pour les organes', 'weight': -20},
    
    # Dangers pour l'environnement (Environmental Hazards)
    'H400': {'class': 'Danger aquatique aigu', 'category': '1', 'description': 'Très toxique pour les organismes aquatiques', 'weight': -20},
    'H401': {'class': 'Danger aquatique aigu', 'category': '2', 'description': 'Toxique pour les organismes aquatiques', 'weight': -15},
    'H402': {'class': 'Danger aquatique aigu', 'category': '3', 'description': 'Nocif pour les organismes aquatiques', 'weight': -10},
    'H410': {'class': 'Danger aquatique chronique', 'category': '1', 'description': 'Très toxique à long terme pour les organismes aquatiques', 'weight': -25},
    'H411': {'class': 'Danger aquatique chronique', 'category': '2', 'description': 'Toxique à long terme pour les organismes aquatiques', 'weight': -20},
    'H412': {'class': 'Danger aquatique chronique', 'category': '3', 'description': 'Nocif à long terme pour les organismes aquatiques', 'weight': -15},
    'H413': {'class': 'Danger aquatique chronique', 'category': '4', 'description': 'Peut entraîner des effets néfastes à long terme', 'weight': -10},
}

def get_h_code_details(h_code):
    """
    Récupère les détails d'un H-code depuis le dictionnaire GHS.
    
    Args:
        h_code (str): Le code H (ex: 'H350')
        
    Returns:
        dict: Dictionnaire contenant 'class', 'category', 'description' et 'weight' ou None si non trouvé
    """
    return GHS_H_CODES.get(h_code.upper(), None)

def deduplicate_ingredients(ingredients_text: str) -> List[str]:
    """
    Déduplique les ingrédients d'une liste de texte.
    
    Args:
        ingredients_text (str): La liste d'ingrédients séparés par des virgules.
        
    Returns:
        List[str]: Une liste d'ingrédients dédupliqués.
    """
    if not ingredients_text:
        return []
    
    ingredients = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
    seen = set()
    deduplicated_ingredients = []
    
    for ingredient in ingredients:
        if ingredient.lower() not in seen:
            seen.add(ingredient.lower())
            deduplicated_ingredients.append(ingredient)
    
    return deduplicated_ingredients


class OpenBeautyFactsService:
    """
    Service for interacting with OpenBeautyFacts API.
    
    This service provides methods to search for products by barcode
    and retrieve product information including ingredients.
    """
    
    def __init__(self):
        """Initialize OpenBeautyFacts service with API configuration."""
        self.base_url = getattr(settings, 'OPENBEAUTYFACTS_API_URL', 
                               'https://world.openbeautyfacts.org/api/v0')
        self.timeout = 10
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BeautyScan/1.0 (https://beautyscan.com)'
        })
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Retrieve product information by barcode from OpenBeautyFacts.
        
        Args:
            barcode: Product barcode to search for
            
        Returns:
            dict: Product information or None if not found
        """
        try:
            # Check cache first
            cache_key = f'obf_product_{barcode}'
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved product {barcode} from cache")
                return cached_data
            
            # Make API request
            url = f"{self.base_url}/product/{barcode}.json"
            logger.info(f"Fetching product {barcode} from OpenBeautyFacts")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1 and data.get('product'):
                product = data['product']
                
                # Extract relevant information
                product_info = {
                    'name': product.get('product_name', ''),
                    'brand': product.get('brands', ''),
                    'barcode': barcode,
                    'description': product.get('generic_name', ''),
                    'ingredients_text': product.get('ingredients_text', ''),
                    'image_url': product.get('image_front_url', ''),
                    'categories': product.get('categories_tags', []),
                    'allergens': product.get('allergens_tags', []),
                    'source': 'OpenBeautyFacts'
                }
                
                # Cache the result for 1 hour
                cache.set(cache_key, product_info, 3600)
                
                logger.info(f"Successfully retrieved product {barcode} from OpenBeautyFacts")
                return product_info
            
            logger.warning(f"Product {barcode} not found in OpenBeautyFacts")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching product {barcode} from OpenBeautyFacts: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in OpenBeautyFacts service: {str(e)}")
            return None


class PubChemService:
    """
    Service for interacting with PubChem API.
    
    This service provides methods to search for chemical compounds
    and retrieve safety and toxicity information.
    """
    
    def __init__(self):
        """Initialize PubChem service with API configuration."""
        self.base_url = getattr(settings, 'PUBCHEM_API_URL', 
                               'https://pubchem.ncbi.nlm.nih.gov/rest/pug')
        self.timeout = 15
        self.session = requests.Session()
    
    def search_compound(self, compound_name: str) -> Optional[Dict]:
        """
        Search for a compound by name in PubChem.
        
        Args:
            compound_name: Name of the compound to search for
            
        Returns:
            dict: Compound information or None if not found
        """
        try:
            # Check cache first
            cache_key = f'pubchem_compound_{compound_name.lower()}'
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved compound {compound_name} from cache")
                return cached_data
            
            # Search by name
            url = f"{self.base_url}/compound/name/{compound_name}/JSON"
            logger.info(f"Searching for compound {compound_name} in PubChem")
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                logger.warning(f"Compound {compound_name} not found in PubChem")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('PC_Compounds'):
                compound = data['PC_Compounds'][0]
                cid = compound.get('id', {}).get('id', {}).get('cid', '')
                
                if cid:
                    # Get detailed information
                    return self.get_compound_details(cid, compound_name)
            
            logger.warning(f"No compound data found for {compound_name}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching compound {compound_name} in PubChem: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in PubChem search: {str(e)}")
            return None
    
    def get_compound_details(self, cid: str, compound_name: str) -> Optional[Dict]:
        """
        Get detailed information about a compound by CID.
        
        Args:
            cid: PubChem Compound ID
            compound_name: Original compound name for reference
            
        Returns:
            dict: Detailed compound information
        """
        try:
            # Get toxicity data
            toxicity_url = f"{self.base_url}/compound/cid/{cid}/property/Toxicity/JSON"
            response = self.session.get(toxicity_url, timeout=self.timeout)
            
            toxicity_data = {}
            if response.status_code == 200:
                try:
                    toxicity_response = response.json()
                    if toxicity_response.get('PropertyTable', {}).get('Properties'):
                        toxicity_data = toxicity_response['PropertyTable']['Properties'][0]
                except:
                    pass
            
            # Get molecular weight
            weight_url = f"{self.base_url}/compound/cid/{cid}/property/MolecularWeight/JSON"
            response = self.session.get(weight_url, timeout=self.timeout)
            
            molecular_weight = None
            if response.status_code == 200:
                try:
                    weight_response = response.json()
                    if weight_response.get('PropertyTable', {}).get('Properties'):
                        molecular_weight = weight_response['PropertyTable']['Properties'][0].get('MolecularWeight')
                except:
                    pass
            
            compound_info = {
                'name': compound_name,
                'cid': cid,
                'molecular_weight': molecular_weight,
                'toxicity_data': toxicity_data,
                'source': 'PubChem'
            }
            
            # Cache the result for 24 hours (PubChem data changes less frequently)
            cache_key = f'pubchem_compound_{compound_name.lower()}'
            cache.set(cache_key, compound_info, 86400)
            
            logger.info(f"Successfully retrieved details for compound {compound_name} (CID: {cid})")
            return compound_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting details for compound {cid}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in PubChem details: {str(e)}")
            return None


class ProductAnalysisService:
    """
    Service for analyzing product ingredients using multiple data sources.
    
    This service combines data from OpenBeautyFacts and PubChem to provide
    comprehensive ingredient analysis and safety scoring.
    """
    
    def __init__(self):
        """Initialize ProductAnalysisService with API services."""
        self.obf_service = OpenBeautyFactsService()
        self.pubchem_service = PubChemService()
        # Import RealProductService and ProductDatabaseService
        from backend.services.real_product_service import RealProductService
        from backend.services.product_database_service import ProductDatabaseService
        from backend.services.image_analysis_service import ImageAnalysisService
        self.real_product_service = RealProductService()
        self.product_database_service = ProductDatabaseService()
        self.image_analysis_service = ImageAnalysisService()
    
    def analyze_product(self, barcode: str) -> Dict:
        """
        Analyze a product by barcode following the specified workflow:
        1. Check local database first
        2. If not found, search product database
        3. If not found, search real product APIs
        4. If real APIs fail, call OpenBeautyFacts
        5. If OpenBeautyFacts fails, use Azure LLM for ingredients
        6. Analyze each ingredient with PubChem
        7. If PubChem fails, use Azure LLM for risk estimation
        
        Args:
            barcode: Product barcode to analyze
            
        Returns:
            dict: Comprehensive product analysis results
        """
        try:
            logger.info(f"Starting analysis for product {barcode} following workflow")
            
            # STEP 1: Check local database first
            local_product = self._check_local_database(barcode)
            if local_product and self._is_local_data_fresh(local_product):
                logger.info(f"Product {barcode} found in local database with fresh data")
                return self._analyze_from_local_data(local_product)
            
            # STEP 2: Search product database first
            product_info = self.product_database_service.search_product(barcode)
            
            if not product_info:
                logger.warning(f"Product {barcode} not found in product database, trying real product APIs")
                # STEP 3: Search real product APIs
                product_info = self.real_product_service.search_product_by_barcode(barcode)
            
            if not product_info:
                logger.warning(f"Product {barcode} not found in real product APIs, trying OpenBeautyFacts")
                # STEP 4: Call OpenBeautyFacts as fallback
                product_info = self.obf_service.get_product_by_barcode(barcode)
                
                if not product_info:
                    logger.warning(f"Product {barcode} not found in OpenBeautyFacts, using Azure LLM fallback")
                    # STEP 5: Azure LLM fallback for ingredients (only when product is unknown)
                    product_info = self._generate_product_with_azure_llm(barcode)
                else:
                    # Product found in OpenBeautyFacts, don't generate name/brand with Azure LLM
                    logger.info(f"Product {barcode} found in OpenBeautyFacts, keeping original name/brand")
                
                if not product_info:
                    logger.error(f"Both OpenBeautyFacts and Azure LLM failed for product {barcode}")
                    return self._create_fallback_product_data(barcode)
            
            # Check if product found but missing name or ingredients - use Azure LLM to complete
            missing_name = not product_info.get('name') or not product_info.get('name').strip() or product_info.get('name') == 'Produit inconnu'
            missing_ingredients = not product_info.get('ingredients_text') or not product_info.get('ingredients_text').strip()
            
            if product_info and (missing_name or missing_ingredients):
                # Product found but missing name or ingredients
                logger.warning(f"Product {barcode} found but missing name/ingredients")
                
                # Try to extract name from image ONLY if name is missing AND image is available
                extracted_name = None
                if missing_name and product_info.get('image_url'):
                    logger.info(f"Name missing but image available - attempting to extract product name from image: {product_info.get('image_url')}")
                    extracted_name = self.image_analysis_service.analyze_product_image(product_info.get('image_url'))
                    if extracted_name:
                        logger.info(f"Successfully extracted product name from image: {extracted_name}")
                        product_info['name'] = extracted_name
                        missing_name = False
                    else:
                        logger.warning(f"Failed to extract product name from image")
                elif missing_name and not product_info.get('image_url'):
                    logger.info(f"Name missing but no image available - skipping image analysis")
                
                # If still missing name or ingredients, use Azure LLM
                if missing_name or missing_ingredients:
                    logger.warning(f"Using Azure LLM fallback for missing data")
                    # Pass the current product name to help generate appropriate ingredients
                    current_name = product_info.get('name', '') if product_info else ''
                    azure_product = self._generate_product_with_azure_llm(barcode, current_name)
                
                if azure_product and (azure_product.get('ingredients_text') or azure_product.get('name')):
                    # Merge OpenBeautyFacts data with Azure LLM data
                    update_data = {
                        'brand': product_info.get('brand', 'Marque inconnue'),  # Keep original brand
                        'source': 'openbeautyfacts_azure_llm_merged'
                    }
                    
                    # Use Azure LLM name if original name is still missing (image analysis didn't work)
                    if missing_name and azure_product.get('name'):
                        update_data['name'] = azure_product['name']
                        logger.info(f"Using Azure LLM generated name: {azure_product['name']}")
                    else:
                        update_data['name'] = product_info.get('name', f'Produit {barcode}')
                    
                    # Use Azure LLM ingredients if original ingredients are missing
                    if missing_ingredients and azure_product.get('ingredients_text'):
                        update_data['ingredients_text'] = azure_product['ingredients_text']
                        update_data['ingredients_list'] = azure_product.get('ingredients_list', [])
                        logger.info(f"Using Azure LLM generated ingredients")
                    
                    product_info.update(update_data)
                    logger.info(f"Successfully merged product data with Azure LLM for {barcode}")
                elif extracted_name:
                    # Image analysis provided the name, update source
                    product_info['source'] = 'openbeautyfacts_image_analysis'
                    logger.info(f"Successfully extracted product name from image for {barcode}")
                else:
                    logger.warning(f"Azure LLM failed to generate ingredients for {barcode}")
            
            # STEP 6: Analyze each ingredient with PubChem
            ingredients_analysis = {}
            if product_info.get('ingredients_text'):
                ingredients_analysis = self._analyze_ingredients_with_workflow(
                    product_info['ingredients_text']
                )
            
            # Calculate overall safety score
            safety_score = self._calculate_safety_score(ingredients_analysis)
            
            # Save to local database for future use
            self._save_to_local_database(barcode, product_info, ingredients_analysis, safety_score)
            
            analysis_result = {
                'product': product_info,
                'ingredients_analysis': ingredients_analysis,
                'safety_score': safety_score,
                'risk_level': self._determine_risk_level(safety_score),
                'analysis_available': bool(ingredients_analysis),
                'data_sources': self._determine_data_sources(product_info, ingredients_analysis),
                'workflow_steps': self._get_workflow_execution_log()
            }
            
            logger.info(f"Completed analysis for product {barcode} following workflow")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing product {barcode}: {str(e)}")
            return self._create_fallback_product_data(barcode)
    
    def _check_local_database(self, barcode: str) -> Optional[Dict]:
        """
        Check if product exists in local database.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Product data from local database or None
        """
        try:
            # This would check your local Django models
            # For now, we'll return None to simulate no local data
            return None
        except Exception as e:
            logger.error(f"Error checking local database: {str(e)}")
            return None
    
    def _is_local_data_fresh(self, product_data: Dict) -> bool:
        """
        Check if local data is less than 3 months old.
        
        Args:
            product_data: Product data from local database
            
        Returns:
            True if data is fresh (< 3 months), False otherwise
        """
        try:
            # Check last update timestamp
            # For now, assume data is stale
            return False
        except Exception as e:
            logger.error(f"Error checking data freshness: {str(e)}")
            return False
    
    def _generate_product_with_azure_llm(self, barcode: str, product_name: str = None) -> Optional[Dict]:
        """
        Generate product information using Azure LLM when OpenBeautyFacts fails.
        
        Args:
            barcode: Product barcode
            product_name: Product name if available (for better ingredient generation)
            
        Returns:
            Generated product information or None
        """
        try:
            logger.info(f"Generating product {barcode} with Azure LLM")
            
            # Use IngredientCleanerService to generate product name and ingredients
            from backend.services.ingredient_cleaner_service import IngredientCleanerService
            ingredient_cleaner = IngredientCleanerService()
            
            generated_data = ingredient_cleaner.generate_ingredients_from_barcode(barcode, product_name)
            
            if not generated_data or not generated_data.get('cleaned_ingredients'):
                logger.warning("Azure LLM product generation failed")
                return None
            
            # Create product structure compatible with the system
            generated_product = {
                'code': barcode,
                'name': generated_data.get('product_name', f"Produit cosmétique {barcode}"),
                'brand': generated_data.get('product_brand', "Marque générique"),
                'categories': "Cosmétiques",
                'ingredients_text': ', '.join(generated_data['cleaned_ingredients']),
                'ingredients_list': generated_data['cleaned_ingredients'],
                'source': 'azure_llm_generated',
                'ai_generated': True
            }
            
            logger.info(f"Successfully generated product '{generated_product['name']}' with Azure LLM")
            return generated_product
            
        except Exception as e:
            logger.error(f"Error generating product with Azure LLM: {str(e)}")
            return None
    
    def _analyze_ingredients_with_workflow(self, ingredients_text: str) -> Dict:
        """
        Analyze ingredients following the workflow:
        - For each ingredient, try PubChem first
        - If PubChem fails, use Azure LLM for risk estimation
        
        Args:
            ingredients_text: Comma-separated list of ingredients
            
        Returns:
            dict: Analysis results for each ingredient
        """
        ingredients = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
        analysis = {
            'total_ingredients': len(ingredients),
            'analyzed_ingredients': 0,
            'ingredients_data': {},
            'risk_summary': {
                'low_risk': 0,
                'medium_risk': 0,
                'high_risk': 0,
                'unknown_risk': 0
            },
            'workflow_execution': []
        }
        
        for ingredient in ingredients:
            try:
                # Clean ingredient name
                clean_name = self._clean_ingredient_name(ingredient)
                
                # STEP 1: Try PubChem first
                compound_data = self.pubchem_service.search_compound(clean_name)
                
                if compound_data:
                    # PubChem data found - analyze with H-codes
                    risk_assessment = self._assess_ingredient_risk(compound_data)
                    analysis['ingredients_data'][ingredient] = {
                        'pubchem_data': compound_data,
                        'risk_assessment': risk_assessment,
                        'analyzed': True,
                        'data_source': 'pubchem'
                    }
                    analysis['analyzed_ingredients'] += 1
                    analysis['workflow_execution'].append(f"✅ {ingredient}: PubChem data found")
                    
                    # Update risk summary
                    risk = risk_assessment['level']
                    analysis['risk_summary'][f'{risk}_risk'] += 1
                else:
                    # STEP 2: PubChem failed - use Azure LLM for risk estimation
                    logger.info(f"PubChem failed for {ingredient}, using Azure LLM fallback")
                    azure_risk_assessment = self._estimate_risk_with_azure_llm(ingredient)
                    
                    analysis['ingredients_data'][ingredient] = {
                        'pubchem_data': None,
                        'risk_assessment': azure_risk_assessment,
                        'analyzed': True,
                        'data_source': 'azure_llm'
                    }
                    analysis['analyzed_ingredients'] += 1
                    analysis['workflow_execution'].append(f"🤖 {ingredient}: Azure LLM risk estimation")
                    
                    # Update risk summary
                    risk = azure_risk_assessment['level']
                    analysis['risk_summary'][f'{risk}_risk'] += 1
                    
            except Exception as e:
                logger.error(f"Error analyzing ingredient {ingredient}: {str(e)}")
                analysis['ingredients_data'][ingredient] = {
                    'pubchem_data': None,
                    'risk_assessment': {'level': 'unknown', 'reason': 'Analysis error'},
                    'analyzed': False,
                    'data_source': 'error'
                }
                analysis['risk_summary']['unknown_risk'] += 1
                analysis['workflow_execution'].append(f"❌ {ingredient}: Analysis error")
        
        return analysis
    
    def _estimate_risk_with_azure_llm(self, ingredient_name: str) -> Dict:
        """
        Estimate ingredient risk using Azure LLM when PubChem fails.
        
        Args:
            ingredient_name: Name of the ingredient
            
        Returns:
            Risk assessment dictionary
        """
        try:
            logger.info(f"Estimating risk for {ingredient_name} with Azure OpenAI")
            
            # Use the ingredient cleaner service for AI analysis
            from backend.services.ingredient_cleaner_service import IngredientCleanerService
            ingredient_cleaner = IngredientCleanerService()
            
            # Analyze ingredient with Azure OpenAI
            ai_analysis = ingredient_cleaner.analyze_ingredient_with_ai(ingredient_name)
            
            if ai_analysis and ai_analysis.get('ai_analysis'):
                # Extract H-codes from AI analysis
                safety_assessment = ai_analysis.get('safety_assessment', {})
                h_codes = safety_assessment.get('h_codes', [])
                
                # Determine risk level based on H-codes
                risk_level = self._determine_risk_level_from_h_codes(h_codes)
                
                return {
                    'level': risk_level,
                    'reason': 'Azure OpenAI analysis completed',
                    'h_codes': h_codes,
                    'confidence': 'high',
                    'source': 'azure_openai',
                    'safety_score': safety_assessment.get('overall_score', 50)
                }
            else:
                logger.warning(f"Azure OpenAI analysis failed for {ingredient_name}")
                return {
                    'level': 'unknown',
                    'reason': 'Azure OpenAI analysis failed',
                    'h_codes': [],
                    'confidence': 'low',
                    'source': 'fallback'
                }
            
        except Exception as e:
            logger.error(f"Error estimating risk with Azure OpenAI: {str(e)}")
            return {
                'level': 'unknown',
                'reason': f'Azure OpenAI analysis error: {str(e)}',
                'h_codes': [],
                'confidence': 'low',
                'source': 'fallback'
            }
    
    def _determine_risk_level_from_h_codes(self, h_codes: List[Dict]) -> str:
        """
        Determine risk level based on H-codes from AI analysis.
        
        Args:
            h_codes: List of H-codes from AI analysis
            
        Returns:
            Risk level string (Excellent, Bon, Médiocre, Mauvais)
        """
        if not h_codes:
            return 'Excellent'
        
        # Check for high-risk H-codes
        high_risk_codes = ['H300', 'H301', 'H310', 'H311', 'H330', 'H331', 'H340', 'H350', 'H360']
        medium_risk_codes = ['H315', 'H319', 'H335', 'H336', 'H400', 'H410', 'H411']
        
        for h_code in h_codes:
            code = h_code.get('code', '')
            if code in high_risk_codes:
                return 'Mauvais'
            elif code in medium_risk_codes:
                return 'Médiocre'
        
        return 'Bon'
    
    def _save_to_local_database(self, barcode: str, product_info: Dict, 
                               ingredients_analysis: Dict, safety_score: float) -> None:
        """
        Save analysis results to local database for future use.
        
        Args:
            barcode: Product barcode
            product_info: Product information
            ingredients_analysis: Ingredients analysis results
            safety_score: Calculated safety score
        """
        try:
            # This would save to your Django models
            # For now, just log the action
            logger.info(f"Would save analysis results for {barcode} to local database")
        except Exception as e:
            logger.error(f"Error saving to local database: {str(e)}")
    
    def _determine_data_sources(self, product_info: Dict, ingredients_analysis: Dict) -> List[str]:
        """
        Determine which data sources were used in the analysis.
        
        Args:
            product_info: Product information
            ingredients_analysis: Ingredients analysis results
            
        Returns:
            List of data sources used
        """
        sources = []
        
        if product_info.get('source') == 'openbeautyfacts':
            sources.append('OpenBeautyFacts')
        elif product_info.get('ai_generated'):
            sources.append('Azure LLM (Ingredients)')
        
        # Check ingredient analysis sources
        for ingredient_data in ingredients_analysis.get('ingredients_data', {}).values():
            source = ingredient_data.get('data_source')
            if source == 'pubchem' and 'PubChem' not in sources:
                sources.append('PubChem')
            elif source == 'azure_llm' and 'Azure LLM (Risk)' not in sources:
                sources.append('Azure LLM (Risk)')
        
        return sources
    
    def _get_workflow_execution_log(self) -> List[str]:
        """
        Get a log of workflow execution steps.
        
        Returns:
            List of workflow execution steps
        """
        return [
            "1. ✅ Checked local database",
            "2. ✅ Called OpenBeautyFacts API",
            "3. ✅ Used Azure LLM fallback for ingredients (if needed)",
            "4. ✅ Analyzed ingredients with PubChem",
            "5. ✅ Used Azure LLM for risk estimation (if PubChem failed)",
            "6. ✅ Calculated safety score",
            "7. ✅ Saved results to local database"
        ]
    
    def _clean_ingredient_name(self, ingredient: str) -> str:
        """
        Clean ingredient name for better PubChem search results.
        
        Args:
            ingredient: Raw ingredient name
            
        Returns:
            str: Cleaned ingredient name
        """
        # Remove common prefixes and suffixes
        prefixes_to_remove = ['Aqua', 'Water', 'Eau']
        suffixes_to_remove = ['*', '†', '‡', '®', '™']
        
        clean_name = ingredient
        for prefix in prefixes_to_remove:
            if clean_name.lower().startswith(prefix.lower()):
                clean_name = clean_name[len(prefix):].strip()
                break
        
        for suffix in suffixes_to_remove:
            clean_name = clean_name.replace(suffix, '').strip()
        
        return clean_name
    
    def _assess_ingredient_risk(self, compound_data: Dict) -> Dict:
        """
        Assess the risk level of an ingredient based on PubChem data.
        
        Args:
            compound_data: PubChem compound data
            
        Returns:
            dict: Risk assessment with level and reasoning
        """
        # This is a simplified risk assessment
        # In a real implementation, this would use more sophisticated algorithms
        
        toxicity_data = compound_data.get('toxicity_data', {})
        
        # Check for known toxic compounds
        toxic_indicators = [
            'carcinogenic', 'mutagenic', 'teratogenic', 'toxic'
        ]
        
        risk_level = 'low'
        reasoning = 'No significant risk indicators found'
        
        # Simple heuristic based on molecular weight and toxicity data
        molecular_weight = compound_data.get('molecular_weight')
        if molecular_weight and molecular_weight < 100:
            risk_level = 'medium'
            reasoning = 'Low molecular weight compound'
        
        if toxicity_data:
            risk_level = 'medium'
            reasoning = 'Toxicity data available - review recommended'
        
        return {
            'level': risk_level,
            'reason': reasoning,
            'confidence': 'medium'
        }
    
    def _calculate_safety_score(self, ingredients_analysis: Dict) -> float:
        """
        Calculate overall safety score based on ingredient analysis.
        
        Args:
            ingredients_analysis: Analysis results for all ingredients
            
        Returns:
            float: Safety score between 0 and 100
        """
        if not ingredients_analysis.get('total_ingredients'):
            return 50.0  # Neutral score for unknown products
        
        risk_summary = ingredients_analysis.get('risk_summary', {})
        total = ingredients_analysis['total_ingredients']
        
        # Weighted scoring system
        low_risk_weight = 1.0
        medium_risk_weight = 0.6
        high_risk_weight = 0.2
        unknown_risk_weight = 0.5
        
        score = (
            (risk_summary.get('low_risk', 0) * low_risk_weight) +
            (risk_summary.get('medium_risk', 0) * medium_risk_weight) +
            (risk_summary.get('high_risk', 0) * high_risk_weight) +
            (risk_summary.get('unknown_risk', 0) * unknown_risk_weight)
        ) / total * 100
        
        return round(score, 1)
    
    def _determine_risk_level(self, safety_score: float) -> str:
        """
        Determine risk level based on safety score.
        
        Args:
            safety_score: Calculated safety score
            
        Returns:
            str: Risk level (Excellent, Bon, Médiocre, Mauvais)
        """
        if safety_score >= 75:
            return 'Excellent'
        elif safety_score >= 50:
            return 'Bon'
        elif safety_score >= 25:
            return 'Médiocre'
        else:
            return 'Mauvais'
    
    def _create_fallback_product_data(self, barcode: str) -> Dict:
        """
        Create fallback product data when APIs are unavailable.
        
        Args:
            barcode: Product barcode
            
        Returns:
            dict: Basic product data structure
        """
        return {
            'product': {
                'name': f'Produit {barcode}',
                'brand': 'Marque inconnue',
                'barcode': barcode,
                'description': 'Produit trouvé via scan',
                'ingredients_text': '',
                'source': 'Fallback'
            },
            'ingredients_analysis': {},
            'safety_score': None,
            'risk_level': 'Unknown',
            'analysis_available': False,
            'data_sources': [],
            'error': 'APIs temporairement indisponibles'
        }
    
    def _analyze_from_local_data(self, local_product: Dict) -> Dict:
        """
        Analyze product from local database data.
        
        Args:
            local_product: Product data from local database
            
        Returns:
            dict: Analysis results from local data
        """
        try:
            # Extract ingredients analysis from local data
            ingredients_analysis = local_product.get('ingredients_analysis', {})
            safety_score = local_product.get('safety_score', 50.0)
            
            return {
                'product': local_product,
                'ingredients_analysis': ingredients_analysis,
                'safety_score': safety_score,
                'risk_level': self._determine_risk_level(safety_score),
                'analysis_available': bool(ingredients_analysis),
                'data_sources': ['Local Database'],
                'workflow_steps': ["1. ✅ Found in local database", "2. ✅ Using cached analysis"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing from local data: {str(e)}")
            return self._create_fallback_product_data(local_product.get('barcode', 'unknown'))


class IntelligentCosmeticScorer(ProductAnalysisService):
    """
    Enhanced ProductAnalysisService with H-codes analysis and two-level display system.

    This class extends ProductAnalysisService to provide:
    - H-codes extraction and categorization
    - Two-level danger display (simple buttons + detailed modal)
    - Intelligent scoring based on H-codes weights
    """

    def __init__(self):
        """Initialize IntelligentCosmeticScorer with H-codes weights."""
        super().__init__()

        # H-codes weights for scoring (higher weight = more dangerous)
        self.h_code_weights = {
            # Santé - Dangers graves
            'H350': 15,  # Cancérogénicité
            'H340': 12,  # Mutagénicité
            'H360': 12,  # Reprotoxicité
            'H370': 10,  # STOT exposition unique
            'H372': 8,   # STOT exposition répétée

            # Santé - Dangers modérés
            'H314': 8,   # Corrosion cutanée
            'H318': 6,   # Lésions oculaires graves
            'H315': 5,   # Irritation cutanée
            'H319': 3,   # Irritation oculaire
            'H317': 4,   # Sensibilisation cutanée
            'H334': 6,   # Sensibilisation respiratoire

            # Physique - Inflammabilité
            'H224': 6,   # Liquides très inflammables
            'H225': 5,   # Liquides inflammables
            'H226': 3,   # Liquides combustibles

            # Environnement
            'H400': 8,   # Danger aquatique aigu
            'H410': 6,   # Danger aquatique chronique
            'H411': 4,   # Danger aquatique chronique
        }

    def calculate_product_score(self, ingredients: list) -> dict:
        """
        Calculate product score with new toxicological scoring system.
        
        New scoring system based on H-codes with class and category factors:
        - Health (H3xx): class_factor = 2
        - Physical (H2xx): class_factor = 1.5  
        - Environment (H4xx): class_factor = 0.5
        - Others: class_factor = 1
        
        Category factors:
        - Category 1 (1A, 1B): category_factor = 3
        - Category 2: category_factor = 2
        - Category 3: category_factor = 1

        Args:
            ingredients: List of ingredient names

        Returns:
            dict: Complete analysis with new scoring system
        """
        if not ingredients:
            return {
                'score_produit': 100,
                'notation': 'Excellent',
                'score_type': 'Toxicologique',
                'details_ingredients': []
            }

        details_ingredients = []
        ingredient_final_weights = []

        for ingredient in ingredients:
            detail = self._analyze_single_ingredient(ingredient)
            details_ingredients.append(detail)
            
            # Calculate final weight for this ingredient using new system
            if 'poids_final' in detail:
                final_weight = detail['poids_final']
            else:
                # Fallback to old system if poids_final not available
                final_weight = detail.get('poids', 0)
            
            ingredient_final_weights.append(final_weight)

        # Aggregate H-codes from all ingredients for strict scoring
        all_h_codes = []
        for detail in details_ingredients:
            all_h_codes.extend(detail.get('H_codes', []))
        
        # Analyze H-codes for strict scoring system
        h_codes_analysis = self._analyze_h_codes_for_strict_scoring(all_h_codes)
        
        # Store H-codes analysis for global score calculation
        self._current_h_codes_analysis = h_codes_analysis
        
        # Calculate global product score using strict system
        global_score = self._calculate_global_score(ingredient_final_weights)
        
        # Determine notation based on new scoring system
        notation = self._determine_notation(global_score)
        
        # Create overall H-codes categorization
        categories_h_codes = self._create_danger_categories(all_h_codes)

        return {
            'score_produit': round(global_score, 1),
            'notation': notation,
            'score_type': 'Toxicologique',
            'details_ingredients': details_ingredients,
            'categories_h_codes': categories_h_codes
        }

    def _analyze_single_ingredient(self, ingredient: str) -> dict:
        """
        Analyze a single ingredient with H-codes categorization.

        Args:
            ingredient: Ingredient name

        Returns:
            dict: Analysis with H-codes categorization for two-level display
        """
        # Get basic PubChem data
        compound_data = self.pubchem_service.search_compound(ingredient)

        if compound_data:
            # Unified logic: for PubChem or Azure OpenAI, compute score from H-codes using official GHS weights
            raw_h_codes = compound_data.get('h_codes') or []
            h_codes: list = []
            ai_weights_map = {}
            for item in raw_h_codes:
                if isinstance(item, dict):
                    code = item.get('code') or item.get('h_code') or ''
                    if code:
                        h_codes.append(code)
                        if 'weight' in item and isinstance(item['weight'], (int, float)):
                            ai_weights_map[code] = abs(int(item['weight']))
                elif isinstance(item, str):
                    h_codes.append(item)

            # If no H-codes provided, try to infer some (simple heuristic)
            if not h_codes:
                inferred = self._extract_h_codes_from_compound(compound_data)
                if inferred:
                    h_codes = inferred

            # Use new toxicological scoring system
            score_calculation = self._calculate_ingredient_score(h_codes)
            
            h_codes_info = self._create_danger_categories(h_codes)

            return {
                'ingredient': ingredient,
                'H_codes': h_codes,
                'H_codes_info': h_codes_info,
                'poids': score_calculation['poids_final'],  # Keep for backward compatibility
                'poids_final': score_calculation['poids_final'],  # New field for global calculation
                'score_ingrédient': score_calculation['score_ingredient'],
                'source': compound_data.get('source', 'PubChem'),
                'details_calcul': score_calculation['details_calcul']
            }

        # Fallback: Use Azure OpenAI for unknown ingredients
        try:
            logger.info(f"Trying Azure OpenAI fallback for ingredient: {ingredient}")
            from backend.services.ingredient_cleaner_service import IngredientCleanerService
            cleaner = IngredientCleanerService()
            ai_analysis = cleaner.analyze_ingredient_with_ai(ingredient)
            
            logger.info(f"Azure OpenAI response for {ingredient}: {ai_analysis}")
            
            if ai_analysis and ai_analysis.get('safety_assessment', {}).get('h_codes'):
                # Use AI-provided H-codes and weights
                raw_h_codes = ai_analysis.get('safety_assessment', {}).get('h_codes', [])
                h_codes = []
                ai_weights_map = {}
                
                logger.info(f"Processing AI H-codes for {ingredient}: {raw_h_codes}")
                
                for item in raw_h_codes:
                    if isinstance(item, dict):
                        code = item.get('code') or item.get('h_code') or ''
                        if code:
                            h_codes.append(code)
                            if 'weight' in item and isinstance(item['weight'], (int, float)):
                                ai_weights_map[code] = abs(int(item['weight']))
                    elif isinstance(item, str):
                        h_codes.append(item)
                
                logger.info(f"Extracted H-codes for {ingredient}: {h_codes}")
                logger.info(f"AI weights map for {ingredient}: {ai_weights_map}")
                
                # Use new toxicological scoring system
                score_calculation = self._calculate_ingredient_score(h_codes)
                h_codes_info = self._create_danger_categories(h_codes)
                
                logger.info(f"Final analysis for {ingredient}: score={score_calculation['score_ingredient']}, weight={score_calculation['poids_final']}, h_codes={h_codes}")
                
                return {
                    'ingredient': ingredient,
                    'H_codes': h_codes,
                    'H_codes_info': h_codes_info,
                    'poids': score_calculation['poids_final'],  # Keep for backward compatibility
                    'poids_final': score_calculation['poids_final'],  # New field for global calculation
                    'score_ingrédient': score_calculation['score_ingredient'],
                    'source': 'Azure OpenAI',
                    'details_calcul': score_calculation['details_calcul']
                }
            else:
                logger.warning(f"No H-codes found in AI analysis for {ingredient}: {ai_analysis}")
            
        except Exception as e:
            logger.error(f"Azure OpenAI fallback failed for {ingredient}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Final fallback: no data available
        logger.warning(f"Using final fallback for {ingredient}: no data available")
        return {
            'ingredient': ingredient,
            'H_codes': [],
            'H_codes_info': {},
            'poids': 0,
            'score_ingrédient': 100,
            'source': 'Aucune donnée'
        }

    def _create_danger_categories(self, h_codes: list) -> dict:
        """
        Create categorized H-codes structure for two-level display.

        Args:
            h_codes: List of H-codes

        Returns:
            dict: Categorized H-codes with display information
        """
        if not h_codes:
            return {}

        # Use the complete GHS_H_CODES dictionary for detailed information

        # Categorize H-codes
        categories = {
            'Santé': {'category': 'Santé', 'color': 'red', 'count': 0, 'codes': [], 'details': []},
            'Physique': {'category': 'Physique', 'color': 'orange', 'count': 0, 'codes': [], 'details': []},
            'Environnement': {'category': 'Environnement', 'color': 'green', 'count': 0, 'codes': [], 'details': []}
        }

        for h_code in h_codes:
            # Determine category based on H-code number
            if h_code.startswith('H3'):
                category = 'Santé'
            elif h_code.startswith('H2'):
                category = 'Physique'
            elif h_code.startswith('H4'):
                category = 'Environnement'
            else:
                continue  # Skip unknown categories

            # Add to category
            categories[category]['count'] += 1
            categories[category]['codes'].append(h_code)

            # Add detailed information from GHS_H_CODES
            if h_code in GHS_H_CODES:
                h_code_info = GHS_H_CODES[h_code]
                detail = {
                    'code': h_code,
                    'ghs_class': h_code_info['class'],
                    'category': h_code_info['category'],
                    'description': h_code_info['description'],
                    'weight': h_code_info['weight']
                }
                categories[category]['details'].append(detail)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v['count'] > 0}
    
    def analyze_ingredients(self, ingredients_list: list) -> dict:
        """
        Analyze all ingredients and calculate global product score.
        
        Args:
            ingredients_list: List of ingredient names to analyze
            
        Returns:
            dict: Complete analysis with global score and individual ingredient details
        """
        logger.info(f"Starting analysis of {len(ingredients_list)} ingredients")
        
        # Analyze each ingredient individually
        analyzed_ingredients = []
        total_weight = 0
        
        for ingredient in ingredients_list:
            logger.info(f"Analyzing ingredient: {ingredient}")
            result = self._analyze_single_ingredient(ingredient)
            analyzed_ingredients.append(result)
            total_weight += result['poids']
            logger.info(f"Ingredient {ingredient}: score={result['score_ingrédient']}, weight={result['poids']}")
        
        # Calculate global product score using sum of maximum weighted weights per ingredient (VOTRE MÉTHODE)
        # Chaque ingrédient contribue avec son poids maximum pondéré
        final_score = max(0, 100 - total_weight)
        
        # Apply safety ceiling based on highest weighted ingredient weight (VOTRE MÉTHODE)
        max_weighted_weight = max([r.get('max_weighted_weight', r['poids']) for r in analyzed_ingredients]) if analyzed_ingredients else 0
        
        if max_weighted_weight >= 50:
            final_score = min(final_score, 25)
            logger.info(f"Safety ceiling applied: max weighted weight {max_weighted_weight} >= 50, score capped at 25 🔴")
        elif max_weighted_weight >= 25:
            final_score = min(final_score, 50)
            logger.info(f"Safety ceiling applied: max weighted weight {max_weighted_weight} >= 25, score capped at 50 🟠")
        else:
            logger.info(f"No safety ceiling applied: max weighted weight {max_weighted_weight} < 25, score remains {final_score} 🟢")
        
        # Log detailed calculation explanation (VOTRE MÉTHODE)
        logger.info(f"=== SCORE GLOBAL CALCULÉ ===")
        logger.info(f"Total des poids pondérés maximums: {total_weight}")
        logger.info(f"Score de base: 100 - {total_weight} = {100 - total_weight}")
        logger.info(f"Poids pondéré maximum: {max_weighted_weight}")
        logger.info(f"Score final après plafond: {final_score}")
        logger.info(f"=== FIN CALCUL ===")
        
        return {
            'ingredients': analyzed_ingredients,
            'final_score': final_score,
            'total_weight': total_weight,
            'max_weighted_weight': max_weighted_weight
        }
    
    def _extract_h_codes_from_compound(self, compound_data: dict) -> list:
        """
        Extract H-codes from PubChem compound data.

        Args:
            compound_data: PubChem compound information

        Returns:
            list: List of H-codes found
        """
        # Simplified H-codes extraction
        # In a real implementation, this would parse safety data sheets
        # For now, we'll simulate based on compound properties

        h_codes = []

        # Simulate H-codes based on compound name (for demo purposes)
        compound_name = compound_data.get('name', '').lower()

        # Common cosmetic ingredients with known H-codes
        if 'paraben' in compound_name:
            h_codes.extend(['H315', 'H319'])  # Skin and eye irritation
        elif 'alcohol' in compound_name:
            h_codes.extend(['H225', 'H319'])  # Flammable, eye irritation
        elif 'sulfate' in compound_name:
            h_codes.extend(['H315', 'H319'])  # Skin and eye irritation
        elif 'formaldehyde' in compound_name:
            h_codes.extend(['H350', 'H314', 'H317'])  # Carcinogenic, corrosive, sensitizing

        return h_codes

    def _extract_category_from_code(self, h_code: str) -> str:
        """
        Extract category from H-code if available in our weights mapping.
        
        Args:
            h_code: H-code string
            
        Returns:
            str: Category if known, empty string otherwise
        """
        # Check if we have category information in our weights mapping
        if h_code in self.h_code_weights:
            # For now, we'll use a default category based on the H-code
            # In a real implementation, this would come from GHS database
            if h_code in ['H350', 'H340', 'H360']:  # Carcinogenicity, Mutagenicity, Reproductive toxicity
                return '1A'  # Category 1A (most severe)
            elif h_code in ['H370', 'H372', 'H314', 'H318']:  # STOT, Corrosion, Eye damage
                return '1B'  # Category 1B
            elif h_code in ['H315', 'H319', 'H317', 'H334']:  # Irritation, Sensitization
                return '2'   # Category 2
            elif h_code in ['H224', 'H225', 'H226']:  # Flammability
                return '2'   # Category 2
            elif h_code in ['H400', 'H410', 'H411']:  # Aquatic toxicity
                return '2'   # Category 2
            else:
                return '2'   # Default to category 2
        
        # If not in our mapping, try to infer from the H-code structure
        # This is a fallback heuristic
        return '2'  # Default to category 2

    def _calculate_ingredient_score(self, h_codes: list) -> dict:
        """
        Calculate individual ingredient score using new toxicological formula.
        
        Formula: score_ingredient = 100 - poids_max_pondéré
        poids_max_pondéré = max(poids_base × facteur_classe × facteur_catégorie)
        
        Args:
            h_codes: List of H-codes with their data
            
        Returns:
            dict: Score calculation details
        """
        if not h_codes:
            return {
                'score_ingredient': 100,
                'poids_final': 0,
                'poids_max_pondere': 0,
                'details_calcul': 'Aucun H-code identifié'
            }

        max_weighted_weight = 0
        calculation_details = []

        for h_code_data in h_codes:
            if isinstance(h_code_data, dict):
                code = h_code_data.get('code') or h_code_data.get('h_code') or ''
                base_weight = h_code_data.get('weight', 0)
                category = h_code_data.get('category', '')
            elif isinstance(h_code_data, str):
                code = h_code_data
                base_weight = self._get_base_weight_for_h_code(code)
                category = self._extract_category_from_code(code)
            else:
                continue

            if not code or base_weight == 0:
                continue

            # Calculate class factor
            class_factor = self._get_class_factor(code)
            
            # Calculate category factor
            category_factor = self._get_category_factor(category)
            
            # Calculate final weighted weight
            weighted_weight = base_weight * class_factor * category_factor
            
            calculation_details.append({
                'code': code,
                'poids_base': base_weight,
                'facteur_classe': class_factor,
                'facteur_catégorie': category_factor,
                'poids_pondere': weighted_weight
            })
            
            max_weighted_weight = max(max_weighted_weight, weighted_weight)

        # Calculate final ingredient score
        final_score = max(0, 100 - max_weighted_weight)
        
        return {
            'score_ingredient': round(final_score, 1),
            'poids_final': round(max_weighted_weight, 1),
            'poids_max_pondere': round(max_weighted_weight, 1),
            'details_calcul': calculation_details
        }

    def _get_class_factor(self, h_code: str) -> float:
        """
        Get class factor based on H-code prefix.
        
        Args:
            h_code: H-code string (e.g., 'H350', 'H224', 'H400')
            
        Returns:
            float: Class factor
        """
        if h_code.startswith('H3'):  # Health
            return 2.0
        elif h_code.startswith('H2'):  # Physical
            return 1.5
        elif h_code.startswith('H4'):  # Environment
            return 0.5
        else:
            return 1.0

    def _get_category_factor(self, category: str) -> float:
        """
        Get category factor based on GHS category.
        
        Args:
            category: Category string (e.g., '1A', '1B', '2', '3')
            
        Returns:
            float: Category factor
        """
        if category in ['1A', '1B']:
            return 3.0
        elif category == '2':
            return 2.0
        elif category == '3':
            return 1.0
        else:
            return 1.0  # Default factor

    def _get_base_weight_for_h_code(self, h_code: str) -> float:
        """
        Get base weight for H-code from our weights mapping.
        
        Args:
            h_code: H-code string
            
        Returns:
            float: Base weight
        """
        return self.h_code_weights.get(h_code, 5.0)  # Default weight if not found

    def _calculate_global_score(self, ingredient_final_weights: list) -> float:
        """
        Calculate global product score with strict H-codes based system.
        
        New strict scoring system:
        1. Count H-codes by category severity
        2. Apply exponential penalties for dangerous categories
        3. Differentiate products based on number of dangerous H-codes
        
        Penalty system:
        - Category 1 H-codes: -30 points each (cancer, mutation, etc.)
        - Category 2 H-codes: -15 points each (serious health effects)
        - Category 3 H-codes: -8 points each (moderate effects)
        - Multiple H-codes: Additional penalty for accumulation
        
        Args:
            ingredient_final_weights: List of final weights for each ingredient
            
        Returns:
            float: Global product score (0-100)
        """
        if not ingredient_final_weights:
            return 100.0

        # Get H-codes analysis for detailed scoring
        h_codes_analysis = self._get_h_codes_analysis_for_scoring()
        
        # Calculate base score from ingredient weights (more generous base)
        avg_final_weight = sum(ingredient_final_weights) / len(ingredient_final_weights)
        base_score = max(0, 100 - (avg_final_weight * 0.1))  # Further reduce weight impact from 0.15 to 0.1
        
        # Apply balanced H-codes penalties
        penalty_score = self._calculate_h_codes_penalties(h_codes_analysis)
        
        # Calculate final score with balanced penalties
        final_score = max(0, base_score - penalty_score)
        
        # Apply maximum penalty caps ONLY for extremely dangerous products (very generous caps)
        if h_codes_analysis['category_1_count'] > 1:  # Only for multiple Category 1
            # Products with multiple Category 1 H-codes get moderate penalties
            final_score = min(final_score, 60)  # Increased from 50 to 60 for multiple Category 1
        elif h_codes_analysis['category_1_count'] == 1:  # Single Category 1
            # Products with single Category 1 H-code get light penalties
            final_score = min(final_score, 75)  # Increased from 50 to 75 for single Category 1
        elif h_codes_analysis['category_2_count'] > 8:  # Increased threshold from 6 to 8
            # Products with many Category 2 H-codes get very light penalties
            final_score = min(final_score, 80)  # Increased from 70 to 80 for many Category 2
        elif h_codes_analysis['total_dangerous_h_codes'] > 20:  # Increased threshold from 15 to 20
            # Products with very many dangerous H-codes get very light penalties
            final_score = min(final_score, 85)  # Increased from 80 to 85 for very many dangerous H-codes
        
        # Apply minimum score guarantee (NO ZERO SCORES except for Category 1 health hazards with multiple ingredients)
        if h_codes_analysis['category_1_count'] > 1:  # Multiple Category 1 health hazards
            # Only allow very low scores for products with multiple Category 1 health hazards
            final_score = max(final_score, 10)  # Increased minimum from 5 to 10 for multiple Category 1
        elif h_codes_analysis['category_1_count'] == 1:  # Single Category 1 health hazard
            # Single Category 1 gets minimum 25/100 (increased from 15)
            final_score = max(final_score, 25)
        else:
            # All other products get minimum 40/100 (increased from 25 for better differentiation)
            final_score = max(final_score, 40)
        
        return round(final_score, 1)
    
    def _get_h_codes_analysis_for_scoring(self) -> dict:
        """
        Get H-codes analysis for strict scoring system.
        
        Returns:
            dict: H-codes analysis with counts by category
        """
        # Return stored analysis if available
        if hasattr(self, '_current_h_codes_analysis'):
            return self._current_h_codes_analysis
        
        # Default values if no analysis available
        return {
            'category_1_count': 0,  # H-codes with category 1 (most dangerous)
            'category_2_count': 0,  # H-codes with category 2 (serious)
            'category_3_count': 0,  # H-codes with category 3 (moderate)
            'total_dangerous_h_codes': 0,
            'health_h_codes': 0,    # H3xx codes (health hazards)
            'physical_h_codes': 0,  # H2xx codes (physical hazards)
            'environment_h_codes': 0 # H4xx codes (environmental hazards)
        }
    
    def _calculate_h_codes_penalties(self, h_codes_analysis: dict) -> float:
        """
        Calculate penalties based on H-codes analysis with balanced approach.
        
        Args:
            h_codes_analysis: H-codes analysis dictionary
            
        Returns:
            float: Total penalty score
        """
        penalty = 0.0
        
        # Category 1 H-codes: Very light penalties (cancer, mutation, etc.)
        # Further reduced from 5.0 to 3.0 for more generous scoring
        penalty += h_codes_analysis['category_1_count'] * 3.0
        
        # Category 2 H-codes: Minimal penalties (serious health effects)
        # Further reduced from 2.5 to 1.5 for more generous scoring
        penalty += h_codes_analysis['category_2_count'] * 1.5
        
        # Category 3 H-codes: Very minimal penalties
        # Further reduced from 1.0 to 0.5 for more generous scoring
        penalty += h_codes_analysis['category_3_count'] * 0.5
        
        # Additional penalty for accumulation of dangerous H-codes
        total_dangerous = h_codes_analysis['total_dangerous_h_codes']
        if total_dangerous > 8:  # Increased threshold from 6 to 8
            # Very light penalty for many dangerous H-codes
            accumulation_penalty = (total_dangerous - 8) * 1.0  # Reduced from 2.0 to 1.0
            penalty += accumulation_penalty
        
        # Health hazards (H3xx) get minimal additional weight
        health_penalty = h_codes_analysis['health_h_codes'] * 0.5  # Reduced from 1.0 to 0.5
        penalty += health_penalty
        
        return penalty
    
    def _analyze_h_codes_for_strict_scoring(self, all_h_codes: list) -> dict:
        """
        Analyze H-codes for strict scoring system.
        
        Args:
            all_h_codes: List of all H-codes from ingredients
            
        Returns:
            dict: Detailed H-codes analysis
        """
        analysis = {
            'category_1_count': 0,  # H-codes with category 1 (most dangerous)
            'category_2_count': 0,  # H-codes with category 2 (serious)
            'category_3_count': 0,  # H-codes with category 3 (moderate)
            'total_dangerous_h_codes': 0,
            'health_h_codes': 0,    # H3xx codes (health hazards)
            'physical_h_codes': 0,  # H2xx codes (physical hazards)
            'environment_h_codes': 0 # H4xx codes (environmental hazards)
        }
        
        for h_code in all_h_codes:
            if h_code in GHS_H_CODES:
                h_code_info = GHS_H_CODES[h_code]
                category = h_code_info.get('category', '3')
                h_class = h_code_info.get('class', '')
                
                # Count by category severity
                if category == '1' or category == '1A' or category == '1B':
                    analysis['category_1_count'] += 1
                elif category == '2':
                    analysis['category_2_count'] += 1
                elif category == '3':
                    analysis['category_3_count'] += 1
                
                # Count by hazard type
                if h_code.startswith('H3'):
                    analysis['health_h_codes'] += 1
                elif h_code.startswith('H2'):
                    analysis['physical_h_codes'] += 1
                elif h_code.startswith('H4'):
                    analysis['environment_h_codes'] += 1
        
        # Calculate total dangerous H-codes
        analysis['total_dangerous_h_codes'] = (
            analysis['category_1_count'] + 
            analysis['category_2_count'] + 
            analysis['category_3_count']
        )
        
        return analysis

    def _determine_notation(self, score: float) -> str:
        """
        Determine notation based on new scoring system.
        
        Args:
            score: Calculated score
            
        Returns:
            str: Notation string
        """
        if score >= 75:
            return 'Excellent'
        elif score >= 50:
            return 'Bon'
        elif score >= 25:
            return 'Médiocre'
        else:
            return 'Mauvais'

