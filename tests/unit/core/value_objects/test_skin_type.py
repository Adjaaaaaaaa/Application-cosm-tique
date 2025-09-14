"""
Unit tests for SkinType value object.

Tests the SkinType value object validation and business logic.
"""

import unittest
from core.value_objects.skin_type import SkinType
from core.exceptions import InvalidSkinTypeError


class TestSkinTypeValueObject(unittest.TestCase):
    """Test cases for SkinType value object."""

    def test_valid_skin_types(self):
        """Test all valid skin types."""
        valid_types = [
            'normal', 'dry', 'oily', 'combination', 
            'sensitive', 'mature'
        ]
        
        for skin_type_str in valid_types:
            skin_type = SkinType.from_string(skin_type_str)
            self.assertEqual(skin_type.value, skin_type_str)

    def test_invalid_skin_type(self):
        """Test invalid skin type raises exception."""
        with self.assertRaises(InvalidSkinTypeError):
            SkinType.from_string('invalid_type')

    def test_empty_skin_type(self):
        """Test empty skin type raises exception."""
        with self.assertRaises(InvalidSkinTypeError):
            SkinType.from_string('')

    def test_none_skin_type(self):
        """Test None skin type raises exception."""
        with self.assertRaises(InvalidSkinTypeError):
            SkinType.from_string(None)

    def test_skin_type_case_insensitive(self):
        """Test skin type is case insensitive."""
        skin_type = SkinType.from_string('NORMAL')
        self.assertEqual(skin_type.value, 'normal')

    def test_skin_type_whitespace_handling(self):
        """Test skin type handles whitespace."""
        skin_type = SkinType.from_string('  normal  ')
        self.assertEqual(skin_type.value, 'normal')

    def test_skin_type_equality(self):
        """Test skin type equality."""
        skin_type1 = SkinType.from_string('normal')
        skin_type2 = SkinType.from_string('normal')
        self.assertEqual(skin_type1, skin_type2)

    def test_skin_type_inequality(self):
        """Test skin type inequality."""
        skin_type1 = SkinType.from_string('normal')
        skin_type2 = SkinType.from_string('dry')
        self.assertNotEqual(skin_type1, skin_type2)

    def test_skin_type_hash(self):
        """Test skin type hash."""
        skin_type1 = SkinType.from_string('normal')
        skin_type2 = SkinType.from_string('normal')
        self.assertEqual(hash(skin_type1), hash(skin_type2))

    def test_skin_type_string_representation(self):
        """Test skin type string representation."""
        skin_type = SkinType.from_string('normal')
        self.assertEqual(str(skin_type), 'normal')

    def test_skin_type_repr(self):
        """Test skin type detailed string representation."""
        skin_type = SkinType.from_string('normal')
        expected = "SkinType('normal')"
        self.assertEqual(repr(skin_type), expected)

    def test_all_skin_type_constants(self):
        """Test all skin type constants are accessible."""
        self.assertEqual(SkinType.NORMAL.value, 'normal')
        self.assertEqual(SkinType.DRY.value, 'dry')
        self.assertEqual(SkinType.OILY.value, 'oily')
        self.assertEqual(SkinType.COMBINATION.value, 'combination')
        self.assertEqual(SkinType.SENSITIVE.value, 'sensitive')
        self.assertEqual(SkinType.MATURE.value, 'mature')

    def test_skin_type_display_names(self):
        """Test skin type display names."""
        self.assertEqual(SkinType.NORMAL.display_name, 'Normal')
        self.assertEqual(SkinType.DRY.display_name, 'Sèche')
        self.assertEqual(SkinType.OILY.display_name, 'Grasse')
        self.assertEqual(SkinType.COMBINATION.display_name, 'Mixte')
        self.assertEqual(SkinType.SENSITIVE.display_name, 'Sensible')
        self.assertEqual(SkinType.MATURE.display_name, 'Mature')

    def test_skin_type_from_enum(self):
        """Test creating skin type from enum constant."""
        skin_type = SkinType(SkinType.NORMAL)
        self.assertEqual(skin_type.value, 'normal')

    def test_skin_type_immutability(self):
        """Test skin type is immutable."""
        skin_type = SkinType.from_string('normal')
        with self.assertRaises(AttributeError):
            skin_type.value = 'dry'


if __name__ == '__main__':
    unittest.main()
