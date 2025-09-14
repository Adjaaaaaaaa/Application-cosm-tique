"""
Ingredient value object for BeautyScan domain.

Represents cosmetic ingredients with validation and business rules.
"""

from typing import List, Optional
from core.exceptions import InvalidIngredientError


class Ingredient:
    """
    Value object representing a cosmetic ingredient.
    
    An ingredient is defined by its name and may have additional properties
    like INCI name, safety information, etc.
    """
    
    def __init__(self, name: str, inci_name: Optional[str] = None):
        """
        Initialize ingredient.
        
        Args:
            name: Common name of the ingredient
            inci_name: INCI (International Nomenclature of Cosmetic Ingredients) name
            
        Raises:
            InvalidIngredientError: If ingredient name is invalid
        """
        if not name or not name.strip():
            raise InvalidIngredientError("Ingredient name cannot be empty")
        
        self._name = name.strip()
        self._inci_name = inci_name.strip() if inci_name else None
    
    @property
    def name(self) -> str:
        """Get ingredient name."""
        return self._name
    
    @property
    def inci_name(self) -> Optional[str]:
        """Get INCI name if available."""
        return self._inci_name
    
    def get_display_name(self) -> str:
        """
        Get display name for the ingredient.
        
        Returns:
            INCI name if available, otherwise common name
        """
        return self._inci_name or self._name
    
    def is_inci_standardized(self) -> bool:
        """
        Check if ingredient has INCI name.
        
        Returns:
            True if INCI name is available, False otherwise
        """
        return self._inci_name is not None
    
    def __eq__(self, other) -> bool:
        """Check equality based on name."""
        if not isinstance(other, Ingredient):
            return False
        return self._name.lower() == other._name.lower()
    
    def __hash__(self) -> int:
        """Hash based on name."""
        return hash(self._name.lower())
    
    def __str__(self) -> str:
        """String representation."""
        return self.get_display_name()
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Ingredient(name='{self._name}', inci_name='{self._inci_name}')"


class IngredientList:
    """
    Value object representing a list of ingredients.
    
    Provides methods for ingredient list manipulation and validation.
    """
    
    def __init__(self, ingredients: List[Ingredient]):
        """
        Initialize ingredient list.
        
        Args:
            ingredients: List of Ingredient objects
        """
        self._ingredients = list(ingredients)
        self._validate_ingredients()
    
    def _validate_ingredients(self) -> None:
        """Validate that all items are Ingredient objects."""
        for ingredient in self._ingredients:
            if not isinstance(ingredient, Ingredient):
                raise InvalidIngredientError(
                    f"All items must be Ingredient objects, got {type(ingredient)}"
                )
    
    @classmethod
    def from_string_list(cls, ingredient_strings: List[str]) -> "IngredientList":
        """
        Create IngredientList from list of strings.
        
        Args:
            ingredient_strings: List of ingredient name strings
            
        Returns:
            IngredientList object
        """
        ingredients = []
        for ingredient_str in ingredient_strings:
            if ingredient_str and ingredient_str.strip():
                ingredients.append(Ingredient(ingredient_str.strip()))
        
        return cls(ingredients)
    
    @property
    def ingredients(self) -> List[Ingredient]:
        """Get list of ingredients."""
        return self._ingredients.copy()
    
    def count(self) -> int:
        """Get number of ingredients."""
        return len(self._ingredients)
    
    def is_empty(self) -> bool:
        """Check if ingredient list is empty."""
        return len(self._ingredients) == 0
    
    def contains(self, ingredient: Ingredient) -> bool:
        """
        Check if ingredient list contains a specific ingredient.
        
        Args:
            ingredient: Ingredient to search for
            
        Returns:
            True if ingredient is found, False otherwise
        """
        return ingredient in self._ingredients
    
    def contains_by_name(self, ingredient_name: str) -> bool:
        """
        Check if ingredient list contains an ingredient by name.
        
        Args:
            ingredient_name: Name of ingredient to search for
            
        Returns:
            True if ingredient is found, False otherwise
        """
        ingredient_name_lower = ingredient_name.lower().strip()
        return any(
            ingredient.name.lower() == ingredient_name_lower 
            for ingredient in self._ingredients
        )
    
    def get_names(self) -> List[str]:
        """
        Get list of ingredient names.
        
        Returns:
            List of ingredient names
        """
        return [ingredient.name for ingredient in self._ingredients]
    
    def get_display_names(self) -> List[str]:
        """
        Get list of ingredient display names.
        
        Returns:
            List of ingredient display names
        """
        return [ingredient.get_display_name() for ingredient in self._ingredients]
    
    def __len__(self) -> int:
        """Get number of ingredients."""
        return len(self._ingredients)
    
    def __iter__(self):
        """Iterate over ingredients."""
        return iter(self._ingredients)
    
    def __getitem__(self, index):
        """Get ingredient by index."""
        return self._ingredients[index]
    
    def __str__(self) -> str:
        """String representation."""
        return ", ".join(self.get_display_names())
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"IngredientList({self._ingredients})"
