"""
PubChem API service for BeautyScan backend.

Handles chemical information retrieval from PubChem database.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from .base_service import CacheableService
from .ingredient_cleaner_service import IngredientCleanerService

logger = logging.getLogger(__name__)


class PubChemService(CacheableService):
    """Service for PubChem API integration."""
    
    def __init__(self):
        """Initialize PubChem service."""
        super().__init__(
            service_name="PubChemService",
            base_url=settings.PUBCHEM_API_URL,
            cache_ttl=86400  # 24 hours cache for scientific data
        )
        self.ingredient_cleaner = IngredientCleanerService()
    
    def search_compound(self, compound_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a compound in PubChem database with Azure OpenAI fallback.
        
        Args:
            compound_name: Name of the compound/ingredient
            
        Returns:
            Compound information or None
        """
        try:
            # Search by name in PubChem
            url = f"{self.base_url}/compound/name/{compound_name}/JSON"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pc_compound = data.get('PC_Compounds', [{}])[0]
            
            if pc_compound:
                compound_info = self._extract_compound_info(pc_compound, compound_name)
                logger.info(f"Found compound in PubChem: {compound_name}")
                return compound_info
            
            # Compound not found in PubChem - use Azure OpenAI
            logger.info(f"Compound {compound_name} not found in PubChem, analyzing with Azure OpenAI")
            return self._analyze_ingredient_with_ai(compound_name)
            
        except requests.RequestException as e:
            logger.warning(f"Error searching compound {compound_name} in PubChem: {str(e)}")
            # Fallback to Azure OpenAI on PubChem error
            logger.info(f"Falling back to Azure OpenAI analysis for {compound_name}")
            return self._analyze_ingredient_with_ai(compound_name)
            
        except Exception as e:
            logger.error(f"Unexpected error searching compound: {str(e)}")
            # Fallback to Azure OpenAI on any error
            return self._analyze_ingredient_with_ai(compound_name)
    
    def _analyze_ingredient_with_ai(self, ingredient_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyze ingredient using Azure OpenAI when PubChem data is unavailable.
        
        Args:
            ingredient_name: Name of the ingredient to analyze
            
        Returns:
            AI-generated compound information
        """
        try:
            logger.info(f"Analyzing ingredient {ingredient_name} with Azure OpenAI")
            
            # Use the ingredient cleaner service for AI analysis
            ai_analysis = self.ingredient_cleaner.analyze_ingredient_with_ai(ingredient_name)
            
            if ai_analysis and ai_analysis.get('ai_analysis'):
                # Convert AI analysis to PubChem-like format
                compound_info = self._convert_ai_analysis_to_pubchem_format(ingredient_name, ai_analysis)
                logger.info(f"AI analysis completed for {ingredient_name} with {len(ai_analysis.get('safety_assessment', {}).get('h_codes', []))} H-codes")
                return compound_info
            else:
                logger.warning(f"Azure OpenAI analysis failed for {ingredient_name}, using fallback")
                return self._get_fallback_compound_info(ingredient_name)
                
        except Exception as e:
            logger.error(f"Error in Azure OpenAI analysis for {ingredient_name}: {str(e)}")
            # Try to provide more specific error information
            if "Azure OpenAI not configured" in str(e):
                logger.error("Azure OpenAI is not properly configured. Check your .env file.")
            elif "timeout" in str(e).lower():
                logger.error("Azure OpenAI request timed out. Check your internet connection.")
            else:
                logger.error(f"Unexpected error in Azure OpenAI analysis: {str(e)}")
            return self._get_fallback_compound_info(ingredient_name)
    
    def _convert_ai_analysis_to_pubchem_format(self, ingredient_name: str, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert AI analysis to PubChem-like format for consistency.
        
        Args:
            ingredient_name: Name of the ingredient
            ai_analysis: AI analysis data
            
        Returns:
            PubChem-like compound information
        """
        safety_assessment = ai_analysis.get('safety_assessment', {})
        h_codes = safety_assessment.get('h_codes', [])
        
        # Convert H-codes to PubChem-like format
        pubchem_h_codes = []
        for h_code in h_codes:
            pubchem_h_codes.append({
                'code': h_code.get('code', ''),
                'description': h_code.get('description', ''),
                'category': h_code.get('category', ''),
                'weight': h_code.get('weight', 0)
            })
        
        return {
            'name': ingredient_name,
            'molecular_weight': ai_analysis.get('chemical_properties', {}).get('molecular_weight', 'Unknown'),
            'molecular_formula': 'Unknown',  # AI doesn't provide this
            'iupac_name': ingredient_name,
            'h_codes': pubchem_h_codes,
            'safety_score': safety_assessment.get('overall_score', 50),
            'risk_factors': safety_assessment.get('risk_factors', []),
            'precautions': safety_assessment.get('precautions', []),
            'cosmetic_uses': ai_analysis.get('cosmetic_uses', []),
            'regulatory_status': ai_analysis.get('regulatory_status', 'Unknown'),
            'source': 'azure_openai',
            'ai_analysis': True,
            'confidence': ai_analysis.get('confidence', 'medium')
        }
    
    def _get_fallback_compound_info(self, ingredient_name: str) -> Dict[str, Any]:
        """
        Get fallback compound information when all methods fail.
        
        Args:
            ingredient_name: Name of the ingredient
            
        Returns:
            Basic compound information
        """
        return {
            'name': ingredient_name,
            'molecular_weight': 'Unknown',
            'molecular_formula': 'Unknown',
            'iupac_name': ingredient_name,
            'h_codes': [],
            'safety_score': 50,
            'risk_factors': ['Unknown'],
            'precautions': ['Use with caution'],
            'cosmetic_uses': ['Unknown'],
            'regulatory_status': 'Unknown',
            'source': 'fallback',
            'ai_analysis': False,
            'confidence': 'low'
        }
    
    def get_compound_properties(self, cid: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed properties for a compound by CID.
        
        Args:
            cid: PubChem Compound ID
            
        Returns:
            Compound properties or None
        """
        try:
            # Get properties
            properties = [
                'MolecularWeight', 'XLogP', 'TPSA', 'Complexity',
                'Charge', 'HBondDonorCount', 'HBondAcceptorCount',
                'RotatableBondCount', 'HeavyAtomCount'
            ]
            
            url = f"{self.base_url}/compound/cid/{cid}/property/{','.join(properties)}/JSON"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            properties_data = data.get('PropertyTable', {}).get('Properties', [{}])[0]
            
            if properties_data:
                return self._format_properties(properties_data)
            
            return None
            
        except requests.RequestException as e:
            logger.warning(f"Error getting properties for CID {cid}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting properties: {str(e)}")
            return None
    
    def get_compound_safety(self, cid: int) -> Optional[Dict[str, Any]]:
        """
        Get safety information for a compound.
        
        Args:
            cid: PubChem Compound ID
            
        Returns:
            Safety information or None
        """
        try:
            # Get toxicity data
            url = f"{self.base_url}/compound/cid/{cid}/property/Toxicity/JSON"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            toxicity_data = data.get('PropertyTable', {}).get('Properties', [{}])[0]
            
            # Get hazard data
            hazard_url = f"{self.base_url}/compound/cid/{cid}/property/Hazard/JSON"
            hazard_response = self.session.get(hazard_url, timeout=10)
            
            hazard_data = {}
            if hazard_response.status_code == 200:
                hazard_json = hazard_response.json()
                hazard_data = hazard_json.get('PropertyTable', {}).get('Properties', [{}])[0]
            
            return self._format_safety_data(toxicity_data, hazard_data)
            
        except requests.RequestException as e:
            logger.warning(f"Error getting safety for CID {cid}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting safety: {str(e)}")
            return None
    
    def analyze_ingredients_safety(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze safety of multiple ingredients using PubChem.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            List of safety analysis results
        """
        safety_results = []
        
        for ingredient in ingredients:
            try:
                # Search for compound
                compound_info = self.search_compound(ingredient)
                
                if compound_info and compound_info.get('cid'):
                    cid = compound_info['cid']
                    
                    # Get properties and safety
                    properties = self.get_compound_properties(cid)
                    safety = self.get_compound_safety(cid)
                    
                    safety_result = {
                        'ingredient': ingredient,
                        'compound_info': compound_info,
                        'properties': properties,
                        'safety': safety,
                        'risk_assessment': self._assess_risk(properties, safety)
                    }
                else:
                    # No compound found
                    safety_result = {
                        'ingredient': ingredient,
                        'compound_info': None,
                        'properties': None,
                        'safety': None,
                        'risk_assessment': {
                            'level': 'unknown',
                            'description': 'Ingrédient non trouvé dans PubChem'
                        }
                    }
                
                safety_results.append(safety_result)
                
            except Exception as e:
                logger.warning(f"Error analyzing ingredient {ingredient}: {str(e)}")
                safety_results.append({
                    'ingredient': ingredient,
                    'compound_info': None,
                    'properties': None,
                    'safety': None,
                    'risk_assessment': {
                        'level': 'error',
                        'description': f'Erreur lors de l\'analyse: {str(e)}'
                    }
                })
        
        return safety_results
    
    def _extract_compound_info(self, pc_compound: Dict[str, Any], compound_name: str) -> Dict[str, Any]:
        """
        Extract basic compound information from PubChem response.
        
        Args:
            pc_compound: PubChem compound data
            compound_name: Original compound name
            
        Returns:
            Formatted compound information
        """
        try:
            # Extract CID - handle different response structures
            cid = None
            if isinstance(pc_compound, dict):
                # Try different possible structures for CID
                if 'id' in pc_compound:
                    id_data = pc_compound['id']
                    if isinstance(id_data, dict):
                        if 'id' in id_data:
                            inner_id = id_data['id']
                            if isinstance(inner_id, dict) and 'cid' in inner_id:
                                cid = inner_id['cid']
                            elif isinstance(inner_id, (int, str)):
                                cid = inner_id
                        elif 'cid' in id_data:
                            cid = id_data['cid']
                    elif isinstance(id_data, (int, str)):
                        cid = id_data
                
                # If still no CID, try to find it in other fields
                if cid is None and 'cid' in pc_compound:
                    cid = pc_compound['cid']
            
            # Extract molecular formula
            molecular_formula = ""
            atoms = pc_compound.get('atoms', {})
            if atoms and isinstance(atoms, dict):
                # Try to reconstruct formula from atoms
                atom_counts = {}
                aid_list = atoms.get('aid', [])
                if isinstance(aid_list, list):
                    for atom in aid_list:
                        if isinstance(atom, dict):
                            element = atom.get('element', '')
                            if element:
                                atom_counts[element] = atom_counts.get(element, 0) + 1
                
                if atom_counts:
                    molecular_formula = ''.join([f"{element}{count}" for element, count in atom_counts.items()])
            
            # Extract IUPAC name
            iupac_name = ""
            props = pc_compound.get('props', [])
            if isinstance(props, list):
                for prop in props:
                    if isinstance(prop, dict):
                        urn = prop.get('urn', {})
                        if isinstance(urn, dict) and urn.get('label') == 'IUPAC Name':
                            value = prop.get('value', {})
                            if isinstance(value, dict):
                                iupac_name = value.get('sval', '')
                                break
            
            return {
                'cid': cid,
                'name': compound_name,
                'iupac_name': iupac_name,
                'molecular_formula': molecular_formula,
                'source': 'pubchem'
            }
            
        except Exception as e:
            logger.error(f"Error extracting compound info: {str(e)}")
            return {
                'cid': None,
                'name': compound_name,
                'iupac_name': '',
                'molecular_formula': '',
                'source': 'pubchem'
            }
    
    def _format_properties(self, properties_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format compound properties.
        
        Args:
            properties_data: Raw properties data
            
        Returns:
            Formatted properties
        """
        return {
            'molecular_weight': properties_data.get('MolecularWeight', {}).get('value', {}).get('sval', ''),
            'xlogp': properties_data.get('XLogP', {}).get('value', {}).get('sval', ''),
            'tpsa': properties_data.get('TPSA', {}).get('value', {}).get('sval', ''),
            'complexity': properties_data.get('Complexity', {}).get('value', {}).get('sval', ''),
            'charge': properties_data.get('Charge', {}).get('value', {}).get('sval', ''),
            'h_bond_donors': properties_data.get('HBondDonorCount', {}).get('value', {}).get('sval', ''),
            'h_bond_acceptors': properties_data.get('HBondAcceptorCount', {}).get('value', {}).get('sval', ''),
            'rotatable_bonds': properties_data.get('RotatableBondCount', {}).get('value', {}).get('sval', ''),
            'heavy_atoms': properties_data.get('HeavyAtomCount', {}).get('value', {}).get('sval', '')
        }
    
    def _format_safety_data(self, toxicity_data: Dict[str, Any], hazard_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format safety and toxicity data.
        
        Args:
            toxicity_data: Toxicity information
            hazard_data: Hazard information
            
        Returns:
            Formatted safety data
        """
        safety_info = {
            'toxicity': {},
            'hazards': [],
            'safety_summary': 'Données de sécurité limitées'
        }
        
        try:
            # Extract toxicity data
            if toxicity_data:
                safety_info['toxicity'] = {
                    'data': toxicity_data,
                    'summary': 'Données de toxicité disponibles'
                }
            
            # Extract hazard data
            if hazard_data:
                safety_info['hazards'] = [
                    hazard_data.get('Hazard', {}).get('value', {}).get('sval', '')
                ]
                safety_info['safety_summary'] = 'Données de sécurité disponibles'
            
        except Exception as e:
            logger.warning(f"Error formatting safety data: {str(e)}")
        
        return safety_info
    
    def _assess_risk(self, properties: Optional[Dict[str, Any]], safety: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess risk level based on properties and safety data.
        
        Args:
            properties: Compound properties
            safety: Safety data
            
        Returns:
            Risk assessment
        """
        risk_level = 'low'
        description = 'Risque faible basé sur les propriétés chimiques'
        
        try:
            if properties:
                # Assess based on molecular weight
                mw = properties.get('molecular_weight')
                if mw and mw != '':
                    try:
                        mw_float = float(mw)
                        if mw_float > 500:
                            risk_level = 'medium'
                            description = 'Masse moléculaire élevée - absorption limitée'
                    except ValueError:
                        pass
                
                # Assess based on XLogP (lipophilicity)
                xlogp = properties.get('xlogp')
                if xlogp and xlogp != '':
                    try:
                        xlogp_float = float(xlogp)
                        if xlogp_float > 3:
                            risk_level = 'medium'
                            description = 'Lipophilie élevée - peut s\'accumuler'
                        elif xlogp_float < -1:
                            risk_level = 'low'
                            description = 'Lipophilie faible - élimination rapide'
                    except ValueError:
                        pass
            
            if safety and safety.get('hazards'):
                risk_level = 'high'
                description = 'Hazards identifiés - prudence recommandée'
            
        except Exception as e:
            logger.warning(f"Error assessing risk: {str(e)}")
            risk_level = 'unknown'
            description = 'Évaluation du risque non disponible'
        
        return {
            'level': risk_level,
            'description': description
        }
