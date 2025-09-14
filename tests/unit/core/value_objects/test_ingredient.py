"""
Unit tests for Ingredient value object.

Tests the Ingredient value object validation and business logic.
"""

import unittest
from core.value_objects.ingredient import Ingredient
from core.exceptions import InvalidIngredientError


class TestIngredientValueObject(unittest.TestCase):
    """Test cases for Ingredient value object."""

    def test_create_ingredient_with_valid_name(self):
        """Test creating ingredient with valid name."""
        ingredient = Ingredient('Water')
        self.assertEqual(ingredient.name, 'Water')

    def test_create_ingredient_with_empty_name(self):
        """Test creating ingredient with empty name raises exception."""
        with self.assertRaises(InvalidIngredientError):
            Ingredient('')

    def test_create_ingredient_with_none_name(self):
        """Test creating ingredient with None name raises exception."""
        with self.assertRaises(InvalidIngredientError):
            Ingredient(None)

    def test_create_ingredient_with_whitespace_name(self):
        """Test creating ingredient with whitespace name raises exception."""
        with self.assertRaises(InvalidIngredientError):
            Ingredient('   ')

    def test_ingredient_name_trimming(self):
        """Test ingredient name is trimmed."""
        ingredient = Ingredient('  Water  ')
        self.assertEqual(ingredient.name, 'Water')

    def test_ingredient_equality(self):
        """Test ingredient equality."""
        ingredient1 = Ingredient('Water')
        ingredient2 = Ingredient('Water')
        self.assertEqual(ingredient1, ingredient2)

    def test_ingredient_inequality(self):
        """Test ingredient inequality."""
        ingredient1 = Ingredient('Water')
        ingredient2 = Ingredient('Glycerin')
        self.assertNotEqual(ingredient1, ingredient2)

    def test_ingredient_hash(self):
        """Test ingredient hash."""
        ingredient1 = Ingredient('Water')
        ingredient2 = Ingredient('Water')
        self.assertEqual(hash(ingredient1), hash(ingredient2))

    def test_ingredient_string_representation(self):
        """Test ingredient string representation."""
        ingredient = Ingredient('Water')
        self.assertEqual(str(ingredient), 'Water')

    def test_ingredient_repr(self):
        """Test ingredient detailed string representation."""
        ingredient = Ingredient('Water')
        expected = "Ingredient('Water')"
        self.assertEqual(repr(ingredient), expected)

    def test_ingredient_immutability(self):
        """Test ingredient is immutable."""
        ingredient = Ingredient('Water')
        with self.assertRaises(AttributeError):
            ingredient.name = 'Glycerin'

    def test_ingredient_case_sensitivity(self):
        """Test ingredient names are case sensitive."""
        ingredient1 = Ingredient('Water')
        ingredient2 = Ingredient('water')
        self.assertNotEqual(ingredient1, ingredient2)

    def test_ingredient_with_special_characters(self):
        """Test ingredient with special characters."""
        ingredient = Ingredient('Sodium Lauryl Sulfate')
        self.assertEqual(ingredient.name, 'Sodium Lauryl Sulfate')

    def test_ingredient_with_numbers(self):
        """Test ingredient with numbers."""
        ingredient = Ingredient('Vitamin C (Ascorbic Acid)')
        self.assertEqual(ingredient.name, 'Vitamin C (Ascorbic Acid)')

    def test_ingredient_with_very_long_name(self):
        """Test ingredient with very long name."""
        long_name = 'A' * 1000
        ingredient = Ingredient(long_name)
        self.assertEqual(ingredient.name, long_name)

    def test_ingredient_with_unicode_characters(self):
        """Test ingredient with unicode characters."""
        ingredient = Ingredient('Acide Hyaluronique')
        self.assertEqual(ingredient.name, 'Acide Hyaluronique')


if __name__ == '__main__':
    unittest.main()
