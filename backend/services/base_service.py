"""
Base service class for BeautyScan backend services.

Provides common functionality and interface for all services.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional, List
from backend.core.exceptions import AIServiceException


class BaseService(ABC):
    """Abstract base class for all BeautyScan services."""
    
    def __init__(self, service_name: str):
        """
        Initialize base service.
        
        Args:
            service_name: Name of the service for logging
        """
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self.logger.info(f"Initializing {service_name} service")
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information and status.
        
        Returns:
            Dictionary with service information
        """
        pass
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle service errors consistently.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
        """
        error_msg = f"Error in {self.service_name}: {str(error)}"
        if context:
            error_msg += f" (Context: {context})"
        
        self.logger.error(error_msg)
        raise AIServiceException(error_msg)
    
    def log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log service operations consistently.
        
        Args:
            operation: Name of the operation
            details: Additional details about the operation
        """
        log_msg = f"{self.service_name} - {operation}"
        if details:
            log_msg += f" - {details}"
        
        self.logger.info(log_msg)
    
    def validate_input(self, data: Any, required_fields: List[str]) -> bool:
        """
        Validate input data.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            True if validation passes, False otherwise
        """
        if not data:
            return False
        
        if isinstance(data, dict):
            return all(field in data for field in required_fields)
        
        return True


class APIService(BaseService):
    """Abstract base class for API-based services."""
    
    def __init__(self, service_name: str, base_url: str):
        """
        Initialize API service.
        
        Args:
            service_name: Name of the service
            base_url: Base URL for the API
        """
        super().__init__(service_name)
        self.base_url = base_url
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """Initialize HTTP session with common headers."""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'BeautyScan/1.0 (https://github.com/beautyscan)',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            self.logger.info(f"Session initialized for {self.service_name}")
        except ImportError:
            self.logger.error("Requests library not available")
            self.session = None
    
    def is_available(self) -> bool:
        """Check if API service is available."""
        return self.session is not None
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get API service information."""
        return {
            'name': self.service_name,
            'base_url': self.base_url,
            'available': self.is_available(),
            'type': 'api'
        }
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data or None if failed
        """
        if not self.is_available():
            self.logger.error(f"{self.service_name} is not available")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            
            self.log_operation(f"{method} {endpoint}", {'status_code': response.status_code})
            return response.json()
            
        except Exception as e:
            self.handle_error(e, f"API request to {endpoint}")
            return None


class CacheableService(APIService):
    """Abstract base class for services with caching capability."""
    
    def __init__(self, service_name: str, base_url: str, cache_ttl: int = 3600):
        """
        Initialize cacheable service.
        
        Args:
            service_name: Name of the service
            base_url: Base URL for the API
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(service_name, base_url)
        self.cache_ttl = cache_ttl
        self._cache = {}
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if key in self._cache:
            data, timestamp = self._cache[key]
            if self._is_cache_valid(timestamp):
                self.logger.debug(f"Cache hit for key: {key}")
                return data
            else:
                del self._cache[key]
        
        return None
    
    def set_cached_data(self, key: str, data: Any) -> None:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        import time
        self._cache[key] = (data, time.time())
        self.logger.debug(f"Cached data for key: {key}")
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            timestamp: Cache timestamp
            
        Returns:
            True if cache is valid, False otherwise
        """
        import time
        return (time.time() - timestamp) < self.cache_ttl
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self.logger.info(f"Cache cleared for {self.service_name}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information."""
        return {
            'cache_size': len(self._cache),
            'cache_ttl': self.cache_ttl,
            'cached_keys': list(self._cache.keys())
        }
