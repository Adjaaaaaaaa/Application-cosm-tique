"""
Service d'analyse d'image pour extraire le nom du produit depuis les images OpenBeautyFacts.
"""

import base64
import logging
import requests
from typing import Optional, Dict, Any
from openai import AzureOpenAI
import httpx
from backend.core.config import settings

logger = logging.getLogger(__name__)

class ImageAnalysisService:
    """Service pour analyser les images de produits et extraire le nom."""
    
    def __init__(self):
        """Initialise le service d'analyse d'image."""
        self.azure_config = {
            'api_key': settings.AZURE_OPENAI_KEY,
            'azure_endpoint': settings.AZURE_OPENAI_ENDPOINT,
            'api_version': settings.AZURE_OPENAI_API_VERSION,
            'deployment_name': settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            'use_proxy': True,  # Enable proxy support
            'proxy_url': 'http://proxy.univ-lille.fr:3128'  # Configure as needed
        }
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client Azure OpenAI avec gestion du proxy."""
        try:
            # Configuration du client avec gestion du proxy
            if self.azure_config.get('use_proxy', False):
                # Utiliser httpx avec proxy
                proxy_url = self.azure_config.get('proxy_url')
                if proxy_url:
                    transport = httpx.HTTPTransport(proxy=proxy_url)
                    http_client = httpx.Client(transport=transport)
                    logger.info("Proxy issue detected, using custom httpx client")
                else:
                    http_client = httpx.Client()
                    logger.info("Using standard httpx client")
                
                self.client = AzureOpenAI(
                    api_key=self.azure_config['api_key'],
                    api_version=self.azure_config['api_version'],
                    azure_endpoint=self.azure_config['azure_endpoint'],
                    http_client=http_client
                )
                logger.info("Azure OpenAI client created with custom httpx client")
            else:
                self.client = AzureOpenAI(
                    api_key=self.azure_config['api_key'],
                    api_version=self.azure_config['api_version'],
                    azure_endpoint=self.azure_config['azure_endpoint']
                )
                logger.info("Azure OpenAI client created with standard client")
                
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            self.client = None
    
    def analyze_product_image(self, image_url: str) -> Optional[str]:
        """
        Analyse une image de produit et extrait le nom du produit.
        
        Args:
            image_url: URL de l'image du produit
            
        Returns:
            Nom du produit extrait de l'image, ou None si échec
        """
        if not self.client:
            logger.error("Azure OpenAI client not initialized")
            return None
            
        try:
            # Télécharger l'image
            image_data = self._download_image(image_url)
            if not image_data:
                logger.error(f"Failed to download image from {image_url}")
                return None
            
            # Encoder l'image en base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Analyser l'image avec Azure OpenAI Vision
            product_name = self._extract_product_name_from_image(image_base64)
            
            if product_name:
                logger.info(f"Successfully extracted product name from image: {product_name}")
                return product_name
            else:
                logger.warning("Failed to extract product name from image")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing product image: {str(e)}")
            return None
    
    def _download_image(self, image_url: str) -> Optional[bytes]:
        """
        Télécharge une image depuis une URL.
        
        Args:
            image_url: URL de l'image
            
        Returns:
            Données binaires de l'image, ou None si échec
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {str(e)}")
            return None
    
    def _extract_product_name_from_image(self, image_base64: str) -> Optional[str]:
        """
        Extrait le nom du produit depuis une image encodée en base64.
        
        Args:
            image_base64: Image encodée en base64
            
        Returns:
            Nom du produit extrait, ou None si échec
        """
        try:
            # Prompt optimisé pour l'extraction du nom de produit
            prompt = """
            Analyse cette image de produit cosmétique et extrais le nom exact du produit visible sur l'emballage.
            
            Instructions:
            - Retourne UNIQUEMENT le nom du produit (ex: "Shower Gel Fresh", "Moisturizing Cream")
            - Ne pas inclure la marque
            - Ne pas inclure de texte marketing ou descriptif
            - Si le nom n'est pas clairement visible, retourne "Non identifiable"
            - Réponds en français si possible
            
            Nom du produit:
            """
            
            response = self.client.chat.completions.create(
                model=self.azure_config['deployment_name'],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            product_name = response.choices[0].message.content.strip()
            
            # Nettoyer le résultat
            if product_name and product_name.lower() not in ['non identifiable', 'non identifié', 'non visible']:
                return product_name
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting product name from image: {str(e)}")
            return None
    
    def is_image_available(self, image_url: str) -> bool:
        """
        Vérifie si une image est disponible et accessible.
        
        Args:
            image_url: URL de l'image
            
        Returns:
            True si l'image est disponible, False sinon
        """
        try:
            response = requests.head(image_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
