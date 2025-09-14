"""
Unit tests for SafetyScore value object.

Tests the SafetyScore value object validation and business logic.
"""

import unittest
from decimal import Decimal
from core.value_objects.safety_score import SafetyScore, RiskLevel
from core.exceptions import InvalidSafetyScoreError


class TestSafetyScoreValueObject(unittest.TestCase):
    """Test cases for SafetyScore value object."""

    def test_valid_safety_scores(self):
        """Test valid safety scores."""
        valid_scores = [0, 25, 50, 75, 100, 85.5, 92.3]
        
        for score in valid_scores:
            safety_score = SafetyScore(score)
            self.assertEqual(safety_score.score, Decimal(str(score)))

    def test_invalid_negative_safety_score(self):
        """Test negative safety score raises exception."""
        with self.assertRaises(InvalidSafetyScoreError):
            SafetyScore(-1)

    def test_invalid_high_safety_score(self):
        """Test safety score above 100 raises exception."""
        with self.assertRaises(InvalidSafetyScoreError):
            SafetyScore(101)

    def test_safety_score_with_decimal(self):
        """Test safety score with decimal value."""
        safety_score = SafetyScore(85.5)
        self.assertEqual(safety_score.score, Decimal('85.5'))

    def test_safety_score_with_string(self):
        """Test safety score with string value."""
        safety_score = SafetyScore('85.5')
        self.assertEqual(safety_score.score, Decimal('85.5'))

    def test_low_risk_level(self):
        """Test low risk level calculation."""
        safety_score = SafetyScore(85)
        self.assertEqual(safety_score.risk_level, RiskLevel.LOW)

    def test_medium_risk_level(self):
        """Test medium risk level calculation."""
        safety_score = SafetyScore(65)
        self.assertEqual(safety_score.risk_level, RiskLevel.MEDIUM)

    def test_high_risk_level(self):
        """Test high risk level calculation."""
        safety_score = SafetyScore(25)
        self.assertEqual(safety_score.risk_level, RiskLevel.HIGH)

    def test_boundary_low_medium_risk(self):
        """Test boundary between low and medium risk."""
        safety_score = SafetyScore(70)
        self.assertEqual(safety_score.risk_level, RiskLevel.MEDIUM)

    def test_boundary_medium_high_risk(self):
        """Test boundary between medium and high risk."""
        safety_score = SafetyScore(40)
        self.assertEqual(safety_score.risk_level, RiskLevel.HIGH)

    def test_perfect_safety_score(self):
        """Test perfect safety score."""
        safety_score = SafetyScore(100)
        self.assertEqual(safety_score.score, Decimal('100'))
        self.assertEqual(safety_score.risk_level, RiskLevel.LOW)

    def test_zero_safety_score(self):
        """Test zero safety score."""
        safety_score = SafetyScore(0)
        self.assertEqual(safety_score.score, Decimal('0'))
        self.assertEqual(safety_score.risk_level, RiskLevel.HIGH)

    def test_safety_score_equality(self):
        """Test safety score equality."""
        safety_score1 = SafetyScore(85.5)
        safety_score2 = SafetyScore(85.5)
        self.assertEqual(safety_score1, safety_score2)

    def test_safety_score_inequality(self):
        """Test safety score inequality."""
        safety_score1 = SafetyScore(85.5)
        safety_score2 = SafetyScore(75.0)
        self.assertNotEqual(safety_score1, safety_score2)

    def test_safety_score_hash(self):
        """Test safety score hash."""
        safety_score1 = SafetyScore(85.5)
        safety_score2 = SafetyScore(85.5)
        self.assertEqual(hash(safety_score1), hash(safety_score2))

    def test_safety_score_string_representation(self):
        """Test safety score string representation."""
        safety_score = SafetyScore(85.5)
        self.assertEqual(str(safety_score), '85.5')

    def test_safety_score_repr(self):
        """Test safety score detailed string representation."""
        safety_score = SafetyScore(85.5)
        expected = "SafetyScore(85.5, RiskLevel.LOW)"
        self.assertEqual(repr(safety_score), expected)

    def test_risk_level_enum_values(self):
        """Test risk level enum values."""
        self.assertEqual(RiskLevel.LOW.value, 'low')
        self.assertEqual(RiskLevel.MEDIUM.value, 'medium')
        self.assertEqual(RiskLevel.HIGH.value, 'high')

    def test_risk_level_display_names(self):
        """Test risk level display names."""
        self.assertEqual(RiskLevel.LOW.display_name, 'Faible')
        self.assertEqual(RiskLevel.MEDIUM.display_name, 'Modéré')
        self.assertEqual(RiskLevel.HIGH.display_name, 'Élevé')

    def test_safety_score_immutability(self):
        """Test safety score is immutable."""
        safety_score = SafetyScore(85.5)
        with self.assertRaises(AttributeError):
            safety_score.score = Decimal('90.0')

    def test_safety_score_comparison(self):
        """Test safety score comparison."""
        safety_score1 = SafetyScore(85.5)
        safety_score2 = SafetyScore(75.0)
        
        self.assertGreater(safety_score1.score, safety_score2.score)
        self.assertLess(safety_score2.score, safety_score1.score)

    def test_safety_score_with_none(self):
        """Test safety score with None raises exception."""
        with self.assertRaises(InvalidSafetyScoreError):
            SafetyScore(None)

    def test_safety_score_with_invalid_string(self):
        """Test safety score with invalid string raises exception."""
        with self.assertRaises(InvalidSafetyScoreError):
            SafetyScore('invalid')

    def test_safety_score_precision(self):
        """Test safety score maintains precision."""
        safety_score = SafetyScore(85.123456)
        self.assertEqual(safety_score.score, Decimal('85.123456'))


if __name__ == '__main__':
    unittest.main()
