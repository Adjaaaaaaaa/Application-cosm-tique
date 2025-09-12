"""
RAG Service for BeautyScan - Azure Cognitive Search Integration

Provides Retrieval Augmented Generation capabilities for enhanced AI responses
with ingredient analysis, product recommendations, and safety information.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, 
    ComplexField, SearchFieldDataType
)
from backend.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG (Retrieval Augmented Generation) with Azure Cognitive Search."""
    
    def __init__(self):
        """Initialize Azure Cognitive Search client."""
        try:
            # Check if Azure Search is configured
            if not hasattr(settings, 'AZURE_SEARCH_ENDPOINT') or not settings.AZURE_SEARCH_ENDPOINT:
                logger.warning("Azure Search not configured - RAG Service will be disabled")
                self.search_client = None
                self.index_client = None
                return
            
            # Azure Cognitive Search configuration
            self.endpoint = settings.AZURE_SEARCH_ENDPOINT
            self.key = settings.AZURE_SEARCH_KEY
            self.index_name = settings.AZURE_SEARCH_INDEX_NAME
            
            # Validate configuration
            if not self.endpoint or not self.key or not self.index_name:
                logger.warning("Azure Search configuration incomplete - RAG Service will be disabled")
                self.search_client = None
                self.index_client = None
                return
            
            # Initialize clients
            self.credential = AzureKeyCredential(self.key)
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=self.credential
            )
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=self.credential
            )
            
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize RAG Service: {str(e)} - Service will be disabled")
            self.search_client = None
            self.index_client = None
    
    def create_index(self) -> bool:
        """Create the search index if it doesn't exist."""
        try:
            if not self.index_client:
                logger.error("Index client not initialized")
                return False
            
            # Check if index exists
            try:
                self.index_client.get_index(self.index_name)
                logger.info(f"Index {self.index_name} already exists")
                return True
            except:
                pass
            
            # Create index definition
            index = SearchIndex(
                name=self.index_name,
                fields=[
                    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                    SearchableField(name="title", type=SearchFieldDataType.String),
                    SearchableField(name="content", type=SearchFieldDataType.String),
                    SearchableField(name="ingredients", type=SearchFieldDataType.String),
                    SearchableField(name="category", type=SearchFieldDataType.String),
                    SearchableField(name="brand", type=SearchFieldDataType.String),
                    SimpleField(name="safety_score", type=SearchFieldDataType.Int32),
                    SearchableField(name="benefits", type=SearchFieldDataType.String),
                    SearchableField(name="warnings", type=SearchFieldDataType.String),
                    SearchableField(name="skin_types", type=SearchFieldDataType.String),
                    SearchableField(name="tags", type=SearchFieldDataType.String),
                    SimpleField(name="price_range", type=SearchFieldDataType.String),
                    SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset)
                ]
            )
            
            # Create the index
            self.index_client.create_index(index)
            logger.info(f"Index {self.index_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the search index."""
        try:
            if not self.search_client:
                logger.error("Search client not initialized")
                return False
            
            # Upload documents
            result = self.search_client.upload_documents(documents)
            
            # Check for errors
            failed_docs = [doc for doc in result if doc.succeeded is False]
            if failed_docs:
                logger.error(f"Failed to upload {len(failed_docs)} documents")
                return False
            
            logger.info(f"Successfully uploaded {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            return False
    
    def search_ingredients(self, query: str, top: int = 5) -> List[Dict[str, Any]]:
        """Search for ingredient information."""
        try:
            if not self.search_client:
                logger.error("Search client not initialized")
                return []
            
            # Search in ingredients field
            search_results = self.search_client.search(
                search_text=query,
                search_fields=["ingredients", "title", "content"],
                top=top,
                include_total_count=True
            )
            
            results = []
            for result in search_results:
                results.append({
                    "id": result["id"],
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "ingredients": result.get("ingredients", ""),
                    "category": result.get("category", ""),
                    "brand": result.get("brand", ""),
                    "safety_score": result.get("safety_score", 0),
                    "benefits": result.get("benefits", ""),
                    "warnings": result.get("warnings", ""),
                    "skin_types": result.get("skin_types", ""),
                    "tags": result.get("tags", ""),
                    "price_range": result.get("price_range", ""),
                    "score": result.get("@search.score", 0)
                })
            
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search ingredients: {str(e)}")
            return []
    
    def search_products(self, query: str, skin_type: str = None, budget: int = None, top: int = 5) -> List[Dict[str, Any]]:
        """Search for product recommendations."""
        try:
            if not self.search_client:
                logger.error("Search client not initialized")
                return []
            
            # Build search query
            search_text = query
            if skin_type:
                search_text += f" {skin_type}"
            
            # Search with filters
            search_results = self.search_client.search(
                search_text=search_text,
                search_fields=["title", "content", "benefits", "skin_types"],
                filter=f"price_range eq '{self._get_price_range(budget)}'" if budget else None,
                top=top,
                include_total_count=True
            )
            
            results = []
            for result in search_results:
                results.append({
                    "id": result["id"],
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "brand": result.get("brand", ""),
                    "safety_score": result.get("safety_score", 0),
                    "benefits": result.get("benefits", ""),
                    "price_range": result.get("price_range", ""),
                    "score": result.get("@search.score", 0)
                })
            
            logger.info(f"Found {len(results)} product recommendations for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            return []
    
    def search_safety_info(self, ingredient_name: str) -> Dict[str, Any]:
        """Search for safety information about an ingredient."""
        try:
            if not self.search_client:
                logger.error("Search client not initialized")
                return {}
            
            # Search for safety information
            search_results = self.search_client.search(
                search_text=ingredient_name,
                search_fields=["title", "content", "warnings"],
                filter="category eq 'safety'",
                top=3,
                include_total_count=True
            )
            
            safety_info = {}
            for result in search_results:
                safety_info = {
                    "ingredient": ingredient_name,
                    "safety_score": result.get("safety_score", 0),
                    "warnings": result.get("warnings", ""),
                    "benefits": result.get("benefits", ""),
                    "content": result.get("content", ""),
                    "score": result.get("@search.score", 0)
                }
                break  # Take the first (most relevant) result
            
            logger.info(f"Found safety info for ingredient: {ingredient_name}")
            return safety_info
            
        except Exception as e:
            logger.error(f"Failed to search safety info: {str(e)}")
            return {}
    
    def get_context_for_ai(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Get relevant context for AI response generation."""
        try:
            context_parts = []
            
            # Search for ingredient information
            ingredient_results = self.search_ingredients(query, top=3)
            if ingredient_results:
                context_parts.append("## Informations sur les ingrédients:")
                for result in ingredient_results:
                    context_parts.append(f"- {result['title']}: {result['content'][:200]}...")
            
            # Search for product recommendations
            skin_type = user_profile.get("skin_type", "") if user_profile else ""
            product_results = self.search_products(query, skin_type=skin_type, top=3)
            if product_results:
                context_parts.append("\n## Recommandations de produits:")
                for result in product_results:
                    context_parts.append(f"- {result['title']} ({result['brand']}): {result['benefits'][:150]}...")
            
            # Search for safety information
            safety_results = self.search_safety_info(query)
            if safety_results:
                context_parts.append("\n## Informations de sécurité:")
                context_parts.append(f"- Score de sécurité: {safety_results['safety_score']}/100")
                if safety_results['warnings']:
                    context_parts.append(f"- Avertissements: {safety_results['warnings']}")
            
            context = "\n".join(context_parts)
            logger.info(f"Generated context for query: {query[:50]}...")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context for AI: {str(e)}")
            return ""
    
    def _get_price_range(self, budget: int) -> str:
        """Convert budget to price range category."""
        if budget <= 20:
            return "low"
        elif budget <= 50:
            return "medium"
        else:
            return "high"
    
    def is_available(self) -> bool:
        """Check if RAG service is available."""
        return self.search_client is not None and self.index_client is not None
