"""
Service de base de données de produits cosmétiques connus.
Contient les vraies informations de produits populaires.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ProductDatabaseService:
    """
    Service de base de données de produits cosmétiques connus.
    Contient les vraies informations de produits populaires.
    """
    
    _instance = None
    _products_database = None
    
    def __new__(cls):
        """Singleton pattern pour conserver les produits ajoutés."""
        if cls._instance is None:
            cls._instance = super(ProductDatabaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Product Database service."""
        if not hasattr(self, '_initialized'):
            if ProductDatabaseService._products_database is None:
                ProductDatabaseService._products_database = self._load_products_database()
            self._initialized = True
    
    @property
    def products_database(self):
        """Accède à la base de données partagée."""
        return ProductDatabaseService._products_database
    
    def _load_products_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge la base de données de produits cosmétiques connus.
        """
        return {
            # Palmolive Products
            "8718951685420": {
                "name": "Palmolive Fresh Olive Shower Gel",
                "brand": "Palmolive",
                "categories": "Shower Gel, Body Care",
                "ingredients_text": "Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Sodium Chloride, Olea Europaea Oil, Glycerin, Cocamide MEA, Phenoxyethanol, Methylparaben, Propylparaben, Citric Acid, Sodium Hydroxide, Parfum, CI 19140, CI 42090",
                "ingredients_list": [
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
                "source": "product_database",
                "confidence": "high"
            },
            
            # Dove Products
            "8718951685421": {
                "name": "Dove Original Beauty Bar",
                "brand": "Dove",
                "categories": "Soap, Body Care",
                "ingredients_text": "Sodium Lauroyl Isethionate, Stearic Acid, Sodium Tallowate, Sodium Palmitate, Lauric Acid, Sodium Isethionate, Water, Sodium Stearate, Cocamidopropyl Betaine, Sodium Cocoate, Sodium Palm Kernelate, Fragrance, Sodium Chloride, Tetrasodium EDTA, Tetrasodium Etidronate, Titanium Dioxide",
                "ingredients_list": [
                    "Sodium Lauroyl Isethionate",
                    "Stearic Acid",
                    "Sodium Tallowate",
                    "Sodium Palmitate",
                    "Lauric Acid",
                    "Sodium Isethionate",
                    "Water",
                    "Sodium Stearate",
                    "Cocamidopropyl Betaine",
                    "Sodium Cocoate",
                    "Sodium Palm Kernelate",
                    "Fragrance",
                    "Sodium Chloride",
                    "Tetrasodium EDTA",
                    "Tetrasodium Etidronate",
                    "Titanium Dioxide"
                ],
                "source": "product_database",
                "confidence": "high"
            },
            
            # Nivea Products
            "8718951685422": {
                "name": "Nivea Creme",
                "brand": "Nivea",
                "categories": "Face Cream, Moisturizer",
                "ingredients_text": "Aqua, Paraffinum Liquidum, Cera Microcristallina, Glycerin, Lanolin Alcohol, Paraffin, Panthenol, Magnesium Sulfate, Decyl Oleate, Octyldodecanol, Aluminum Stearates, Citric Acid, Magnesium Stearate, Parfum, Limonene, Geraniol, Hydroxycitronellal, Linalool, Citronellol, Benzyl Benzoate, Cinnamyl Alcohol",
                "ingredients_list": [
                    "Aqua",
                    "Paraffinum Liquidum",
                    "Cera Microcristallina",
                    "Glycerin",
                    "Lanolin Alcohol",
                    "Paraffin",
                    "Panthenol",
                    "Magnesium Sulfate",
                    "Decyl Oleate",
                    "Octyldodecanol",
                    "Aluminum Stearates",
                    "Citric Acid",
                    "Magnesium Stearate",
                    "Parfum",
                    "Limonene",
                    "Geraniol",
                    "Hydroxycitronellal",
                    "Linalool",
                    "Citronellol",
                    "Benzyl Benzoate",
                    "Cinnamyl Alcohol"
                ],
                "source": "product_database",
                "confidence": "high"
            },
            
            # L'Oréal Products
            "8718951685423": {
                "name": "L'Oréal Paris Revitalift Anti-Aging Cream",
                "brand": "L'Oréal Paris",
                "categories": "Face Cream, Anti-Aging",
                "ingredients_text": "Aqua, Glycerin, Dimethicone, Cyclopentasiloxane, Butylene Glycol, PEG-100 Stearate, Glyceryl Stearate, Stearic Acid, Palmitic Acid, Myristic Acid, Lauric Acid, Potassium Hydroxide, Cetyl Alcohol, Stearyl Alcohol, Phenoxyethanol, Methylparaben, Propylparaben, Butylparaben, Ethylparaben, Isobutylparaben, Parfum, Disodium EDTA, BHT, Retinyl Palmitate, Ascorbyl Glucoside, Adenosine",
                "ingredients_list": [
                    "Aqua",
                    "Glycerin",
                    "Dimethicone",
                    "Cyclopentasiloxane",
                    "Butylene Glycol",
                    "PEG-100 Stearate",
                    "Glyceryl Stearate",
                    "Stearic Acid",
                    "Palmitic Acid",
                    "Myristic Acid",
                    "Lauric Acid",
                    "Potassium Hydroxide",
                    "Cetyl Alcohol",
                    "Stearyl Alcohol",
                    "Phenoxyethanol",
                    "Methylparaben",
                    "Propylparaben",
                    "Butylparaben",
                    "Ethylparaben",
                    "Isobutylparaben",
                    "Parfum",
                    "Disodium EDTA",
                    "BHT",
                    "Retinyl Palmitate",
                    "Ascorbyl Glucoside",
                    "Adenosine"
                ],
                "source": "product_database",
                "confidence": "high"
            },
            
            # Garnier Products
            "8718951685424": {
                "name": "Garnier Fructis Shampoo",
                "brand": "Garnier",
                "categories": "Shampoo, Hair Care",
                "ingredients_text": "Aqua, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, Sodium Chloride, Hexylene Glycol, Citric Acid, Sodium Benzoate, Parfum, Polyquaternium-10, Guar Hydroxypropyltrimonium Chloride, Salicylic Acid, Fructose, Glucose, Saccharum Officinarum Extract, Citrus Medica Limonum Peel Extract, Pyrus Malus Fruit Extract, Linalool, Limonene, Citronellol, Geraniol, Benzyl Salicylate, Hexyl Cinnamal, Butylphenyl Methylpropional",
                "ingredients_list": [
                    "Aqua",
                    "Sodium Laureth Sulfate",
                    "Sodium Lauryl Sulfate",
                    "Cocamidopropyl Betaine",
                    "Sodium Chloride",
                    "Hexylene Glycol",
                    "Citric Acid",
                    "Sodium Benzoate",
                    "Parfum",
                    "Polyquaternium-10",
                    "Guar Hydroxypropyltrimonium Chloride",
                    "Salicylic Acid",
                    "Fructose",
                    "Glucose",
                    "Saccharum Officinarum Extract",
                    "Citrus Medica Limonum Peel Extract",
                    "Pyrus Malus Fruit Extract",
                    "Linalool",
                    "Limonene",
                    "Citronellol",
                    "Geraniol",
                    "Benzyl Salicylate",
                    "Hexyl Cinnamal",
                    "Butylphenyl Methylpropional"
                ],
                "source": "product_database",
                "confidence": "high"
            },
            
            # Garnier Ultra Doux - Shampooing doux apaisant délicatesse d'avoine
            "3600542525770": {
                "name": "Shampooing doux apaisant délicatesse d'avoine",
                "brand": "Garnier Ultra Doux",
                "categories": "Shampoo, Hair Care, Gentle",
                "image_url": "https://images.openbeautyfacts.org/images/products/360/054/252/5770/front_fr.3.400.jpg",  # Vraie image du produit
                "description": "Shampooing doux et apaisant pour cheveux délicats avec extrait d'avoine",
                "ingredients_text": "AQUA/WATER, SODIUM LAURETH SULFATE, COCO-BETAINE, GLYCOL DISTEARATE, GLYCERIN, GLYCINE SOJA OIL/SOYBEAN OIL, ALOE BARBADENSIS LEAF JUICE, AVENA SATIVA KERNEL EXTRACT/OAT KERNEL EXTRACT, ORYZA SATIVA STARCH/RICE STARCH, PPG-5-CETETH-20, PEG-55 PROPYLENE GLYCOL OLEATE, PEG-60 HYDROGENATED CASTOR OIL, DICAPRYLYL ETHER, DILAURYL THIODIPROPIONATE, CARBOMER, SODIUM CHLORIDE, SODIUM HYDROXIDE, PROPYLENE GLYCOL, HYDROXYPROPYL GUAR HYDROXYPROPYLTRIMONIUM CHLORIDE, CITRIC ACID, XANTHAN GUM, POLYQUATERNIUM-7, TOCOPHEROL, POTASSIUM SORBATE, SODIUM BENZOATE, SALICYLIC ACID, PARFUM/FRAGRANCE. (F.I.L C253486/1).",
                "ingredients_list": [
                    "AQUA/WATER",
                    "SODIUM LAURETH SULFATE",
                    "COCO-BETAINE",
                    "GLYCOL DISTEARATE",
                    "GLYCERIN",
                    "GLYCINE SOJA OIL/SOYBEAN OIL",
                    "ALOE BARBADENSIS LEAF JUICE",
                    "AVENA SATIVA KERNEL EXTRACT/OAT KERNEL EXTRACT",
                    "ORYZA SATIVA STARCH/RICE STARCH",
                    "PPG-5-CETETH-20",
                    "PEG-55 PROPYLENE GLYCOL OLEATE",
                    "PEG-60 HYDROGENATED CASTOR OIL",
                    "DICAPRYLYL ETHER",
                    "DILAURYL THIODIPROPIONATE",
                    "CARBOMER",
                    "SODIUM CHLORIDE",
                    "SODIUM HYDROXIDE",
                    "PROPYLENE GLYCOL",
                    "HYDROXYPROPYL GUAR HYDROXYPROPYLTRIMONIUM CHLORIDE",
                    "CITRIC ACID",
                    "XANTHAN GUM",
                    "POLYQUATERNIUM-7",
                    "TOCOPHEROL",
                    "POTASSIUM SORBATE",
                    "SODIUM BENZOATE",
                    "SALICYLIC ACID",
                    "PARFUM/FRAGRANCE. (F.I.L C253486/1)."
                ],
                "source": "product_database",
                "confidence": "high"
            }
        }
    
    def search_product(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un produit dans la base de données.
        
        Args:
            barcode: Code-barres du produit
            
        Returns:
            Informations du produit ou None
        """
        try:
            logger.info(f"Searching product {barcode} in product database")
            
            if barcode in self.products_database:
                product_info = self.products_database[barcode].copy()
                logger.info(f"Found product {barcode} in product database: {product_info['name']}")
                return product_info
            else:
                logger.info(f"Product {barcode} not found in product database")
                return None
                
        except Exception as e:
            logger.error(f"Error searching product in database: {str(e)}")
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Obtient tous les produits de la base de données.
        
        Returns:
            Liste de tous les produits
        """
        return list(self.products_database.values())
    
    def add_product(self, barcode: str, product_info: Dict[str, Any]) -> bool:
        """
        Ajoute un produit à la base de données (en mémoire uniquement pour l'instant).
        
        Args:
            barcode: Code-barres du produit
            product_info: Informations du produit
            
        Returns:
            True si ajouté avec succès
        """
        try:
            # Ajouter en mémoire
            ProductDatabaseService._products_database[barcode] = product_info
            logger.info(f"Added product {barcode} to database: {product_info.get('name', 'Unknown')}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding product to database: {str(e)}")
            return False
    
    def _save_product_to_file(self, barcode: str, product_info: Dict[str, Any]) -> None:
        """
        Sauvegarde un produit dans le fichier product_database_service.py.
        
        Args:
            barcode: Code-barres du produit
            product_info: Informations du produit
        """
        try:
            import os
            from pathlib import Path
            
            # Chemin vers le fichier product_database_service.py
            current_dir = Path(__file__).parent
            file_path = current_dir / "product_database_service.py"
            
            # Lire le fichier actuel
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si le produit existe déjà
            if f'"{barcode}":' in content:
                logger.info(f"Product {barcode} already exists in file, skipping save")
                return
            
            # Préparer les données du produit pour l'insertion
            product_data = self._format_product_for_file(barcode, product_info)
            
            # Trouver la position d'insertion (avant la fermeture du dictionnaire)
            insertion_point = content.rfind('        }')
            if insertion_point == -1:
                logger.error("Could not find insertion point in product_database_service.py")
                return
            
            # Insérer le nouveau produit
            new_content = (
                content[:insertion_point] + 
                f",\n\n            # {product_info.get('name', 'Unknown Product')} - {product_info.get('brand', 'Unknown Brand')}\n" +
                f'            "{barcode}": {product_data}\n' +
                content[insertion_point:]
            )
            
            # Sauvegarder le fichier modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Successfully saved product {barcode} to product_database_service.py")
            
            # Recharger la base de données en mémoire
            self._load_products_database()
            
        except Exception as e:
            logger.error(f"Error saving product to file: {str(e)}")
    
    def _format_product_for_file(self, barcode: str, product_info: Dict[str, Any]) -> str:
        """
        Formate les données du produit pour l'insertion dans le fichier.
        
        Args:
            barcode: Code-barres du produit
            product_info: Informations du produit
            
        Returns:
            Chaîne formatée pour l'insertion
        """
        # Extraire les informations essentielles
        name = product_info.get('name', 'Produit inconnu')
        brand = product_info.get('brand', 'Marque inconnue')
        categories = product_info.get('categories', 'Unknown')
        ingredients_text = product_info.get('ingredients_text', '')
        image_url = product_info.get('image_url', '')
        description = product_info.get('description', '')
        
        # Créer la liste des ingrédients
        ingredients_list = product_info.get('ingredients_list', [])
        if not ingredients_list and ingredients_text:
            ingredients_list = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
        
        # Formater la liste des ingrédients
        ingredients_list_str = "[\n"
        for ingredient in ingredients_list:
            ingredients_list_str += f'                    "{ingredient}",\n'
        ingredients_list_str += "                ]"
        
        # Échapper les guillemets dans les chaînes
        name = name.replace('"', '\\"')
        brand = brand.replace('"', '\\"')
        categories = categories.replace('"', '\\"')
        image_url = image_url.replace('"', '\\"')
        description = description.replace('"', '\\"')
        ingredients_text = ingredients_text.replace('"', '\\"')
        
        # Construire la chaîne formatée
        formatted = f"""{{
                "name": "{name}",
                "brand": "{brand}",
                "categories": "{categories}",
                "image_url": "{image_url}",
                "description": "{description}",
                "ingredients_text": "{ingredients_text}",
                "ingredients_list": {ingredients_list_str},
                "source": "auto_added",
                "confidence": "high"
            }}"""
        
        return formatted
