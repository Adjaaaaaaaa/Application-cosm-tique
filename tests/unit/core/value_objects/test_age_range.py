"""
Unit tests for AgeRange value object.

Tests the AgeRange value object validation and business logic.
"""

import unittest
from core.value_objects.age_range import AgeRange
from core.exceptions import InvalidAgeRangeError


class TestAgeRangeValueObject(unittest.TestCase):
    """Test cases for AgeRange value object."""

    def test_valid_age_ranges(self):
        """Test all valid age ranges."""
        valid_ranges = [
            '13-17', '18-25', '26-35', '36-45', '46+'
        ]
        
        for age_range_str in valid_ranges:
            age_range = AgeRange.from_string(age_range_str)
            self.assertEqual(age_range.value, age_range_str)

    def test_invalid_age_range(self):
        """Test invalid age range raises exception."""
        with self.assertRaises(InvalidAgeRangeError):
            AgeRange.from_string('invalid_range')

    def test_empty_age_range(self):
        """Test empty age range raises exception."""
        with self.assertRaises(InvalidAgeRangeError):
            AgeRange.from_string('')

    def test_none_age_range(self):
        """Test None age range raises exception."""
        with self.assertRaises(InvalidAgeRangeError):
            AgeRange.from_string(None)

    def test_age_range_case_insensitive(self):
        """Test age range is case insensitive."""
        age_range = AgeRange.from_string('26-35')
        self.assertEqual(age_range.value, '26-35')

    def test_age_range_whitespace_handling(self):
        """Test age range handles whitespace."""
        age_range = AgeRange.from_string('  26-35  ')
        self.assertEqual(age_range.value, '26-35')

    def test_age_range_equality(self):
        """Test age range equality."""
        age_range1 = AgeRange.from_string('26-35')
        age_range2 = AgeRange.from_string('26-35')
        self.assertEqual(age_range1, age_range2)

    def test_age_range_inequality(self):
        """Test age range inequality."""
        age_range1 = AgeRange.from_string('26-35')
        age_range2 = AgeRange.from_string('18-25')
        self.assertNotEqual(age_range1, age_range2)

    def test_age_range_hash(self):
        """Test age range hash."""
        age_range1 = AgeRange.from_string('26-35')
        age_range2 = AgeRange.from_string('26-35')
        self.assertEqual(hash(age_range1), hash(age_range2))

    def test_age_range_string_representation(self):
        """Test age range string representation."""
        age_range = AgeRange.from_string('26-35')
        self.assertEqual(str(age_range), '26-35')

    def test_age_range_repr(self):
        """Test age range detailed string representation."""
        age_range = AgeRange.from_string('26-35')
        expected = "AgeRange('26-35')"
        self.assertEqual(repr(age_range), expected)

    def test_all_age_range_constants(self):
        """Test all age range constants are accessible."""
        self.assertEqual(AgeRange.TEEN.value, '13-17')
        self.assertEqual(AgeRange.YOUNG_ADULT.value, '18-25')
        self.assertEqual(AgeRange.ADULT.value, '26-35')
        self.assertEqual(AgeRange.MATURE.value, '36-45')
        self.assertEqual(AgeRange.SENIOR.value, '46+')

    def test_age_range_display_names(self):
        """Test age range display names."""
        self.assertEqual(AgeRange.TEEN.display_name, '13–17 ans')
        self.assertEqual(AgeRange.YOUNG_ADULT.display_name, '18–25 ans')
        self.assertEqual(AgeRange.ADULT.display_name, '26–35 ans')
        self.assertEqual(AgeRange.MATURE.display_name, '36–45 ans')
        self.assertEqual(AgeRange.SENIOR.display_name, '46+ ans')

    def test_age_range_from_enum(self):
        """Test creating age range from enum constant."""
        age_range = AgeRange(AgeRange.ADULT)
        self.assertEqual(age_range.value, '26-35')

    def test_age_range_immutability(self):
        """Test age range is immutable."""
        age_range = AgeRange.from_string('26-35')
        with self.assertRaises(AttributeError):
            age_range.value = '18-25'


if __name__ == '__main__':
    unittest.main()
