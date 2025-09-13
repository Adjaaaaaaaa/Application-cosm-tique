"""
Unit tests for domain entities.

Tests the core business logic in domain entities without any framework dependencies.
"""

import unittest
from datetime import datetime
from decimal import Decimal

from core.entities.user import User
from core.entities.profile import UserProfile
from core.entities.scan import Scan, ScanType
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.value_objects.safety_score import SafetyScore, RiskLevel
from core.exceptions import (
    UserNotFoundError, ProfileNotFoundError, ScanNotFoundError,
    InvalidSkinTypeError, InvalidAgeRangeError, InvalidSafetyScoreError
)


class TestUserEntity(unittest.TestCase):
    """Test User domain entity."""
    
    def test_create_user_with_valid_data(self):
        """Test creating user with valid data."""
        user = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.is_active)
    
    def test_create_user_with_invalid_id(self):
        """Test creating user with invalid ID."""
        with self.assertRaises(UserNotFoundError):
            User(user_id=0, username="test", email="test@example.com")
        
        with self.assertRaises(UserNotFoundError):
            User(user_id=-1, username="test", email="test@example.com")
    
    def test_create_user_with_empty_username(self):
        """Test creating user with empty username."""
        with self.assertRaises(UserNotFoundError):
            User(user_id=1, username="", email="test@example.com")
        
        with self.assertRaises(UserNotFoundError):
            User(user_id=1, username="   ", email="test@example.com")
    
    def test_create_user_with_empty_email(self):
        """Test creating user with empty email."""
        with self.assertRaises(UserNotFoundError):
            User(user_id=1, username="test", email="")
    
    def test_get_full_name(self):
        """Test getting user's full name."""
        user = User(user_id=1, username="test", email="test@example.com")
        self.assertEqual(user.get_full_name(), "test")
        
        user = User(user_id=1, username="test", email="test@example.com", first_name="John")
        self.assertEqual(user.get_full_name(), "John")
        
        user = User(user_id=1, username="test", email="test@example.com", first_name="John", last_name="Doe")
        self.assertEqual(user.get_full_name(), "John Doe")
    
    def test_user_equality(self):
        """Test user equality based on ID."""
        user1 = User(user_id=1, username="user1", email="user1@example.com")
        user2 = User(user_id=1, username="user2", email="user2@example.com")
        user3 = User(user_id=2, username="user1", email="user1@example.com")
        
        self.assertEqual(user1, user2)
        self.assertNotEqual(user1, user3)


class TestUserProfileEntity(unittest.TestCase):
    """Test UserProfile domain entity."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User(user_id=1, username="testuser", email="test@example.com")
    
    def test_create_profile_with_valid_data(self):
        """Test creating profile with valid data."""
        profile = UserProfile(
            user=self.user,
            skin_type=SkinType.COMBINATION,
            age_range=AgeRange.AGE_26_35,
            skin_concerns=["acne", "aging"],
            allergies=["paraben"]
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.skin_type, SkinType.COMBINATION)
        self.assertEqual(profile.age_range, AgeRange.AGE_26_35)
        self.assertEqual(profile.skin_concerns, ["acne", "aging"])
        self.assertEqual(profile.allergies, ["paraben"])
        self.assertFalse(profile.is_premium())
    
    def test_create_profile_with_invalid_user(self):
        """Test creating profile with invalid user."""
        with self.assertRaises(ProfileNotFoundError):
            UserProfile(user="invalid", skin_type=SkinType.COMBINATION)
    
    def test_premium_access(self):
        """Test premium access checking."""
        profile = UserProfile(user=self.user, subscription_type="free")
        self.assertFalse(profile.is_premium())
        
        profile = UserProfile(user=self.user, subscription_type="premium")
        self.assertTrue(profile.is_premium())
        
        profile = UserProfile(user=self.user, subscription_type="pro")
        self.assertTrue(profile.is_premium())
        self.assertTrue(profile.is_pro())
    
    def test_add_remove_allergies(self):
        """Test adding and removing allergies."""
        profile = UserProfile(user=self.user)
        
        profile.add_allergy("paraben")
        self.assertIn("paraben", profile.allergies)
        
        profile.add_allergy("sulfate")
        self.assertIn("sulfate", profile.allergies)
        
        profile.remove_allergy("paraben")
        self.assertNotIn("paraben", profile.allergies)
        self.assertIn("sulfate", profile.allergies)
    
    def test_get_all_allergies(self):
        """Test getting all allergies including other allergies."""
        profile = UserProfile(
            user=self.user,
            allergies=["paraben", "sulfate"],
            allergies_other="fragrance"
        )
        
        all_allergies = profile.get_all_allergies()
        self.assertIn("paraben", all_allergies)
        self.assertIn("sulfate", all_allergies)
        self.assertIn("fragrance", all_allergies)
    
    def test_format_for_ai(self):
        """Test formatting profile for AI prompts."""
        profile = UserProfile(
            user=self.user,
            skin_type=SkinType.COMBINATION,
            age_range=AgeRange.AGE_26_35,
            skin_concerns=["acne"],
            allergies=["paraben"],
            objectives=["anti-aging"]
        )
        
        formatted = profile.format_for_ai()
        self.assertIn("testuser", formatted)
        self.assertIn("Mixte", formatted)
        self.assertIn("26–35 ans", formatted)
        self.assertIn("🚨", formatted)  # Allergy warning
        self.assertIn("paraben", formatted)
        self.assertIn("acne", formatted)
        self.assertIn("anti-aging", formatted)


class TestScanEntity(unittest.TestCase):
    """Test Scan domain entity."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User(user_id=1, username="testuser", email="test@example.com")
    
    def test_create_barcode_scan(self):
        """Test creating barcode scan."""
        scan = Scan(
            scan_id=1,
            user=self.user,
            scan_type=ScanType.BARCODE,
            barcode="123456789"
        )
        
        self.assertEqual(scan.id, 1)
        self.assertEqual(scan.user, self.user)
        self.assertEqual(scan.scan_type, ScanType.BARCODE)
        self.assertEqual(scan.barcode, "123456789")
        self.assertFalse(scan.is_new())
    
    def test_create_new_scan(self):
        """Test creating new scan (not yet persisted)."""
        scan = Scan(
            scan_id=None,
            user=self.user,
            scan_type=ScanType.MANUAL
        )
        
        self.assertIsNone(scan.id)
        self.assertTrue(scan.is_new())
    
    def test_create_scan_with_invalid_type(self):
        """Test creating scan with invalid type."""
        with self.assertRaises(ScanNotFoundError):
            Scan(scan_id=1, user=self.user, scan_type="invalid")
    
    def test_create_barcode_scan_without_barcode(self):
        """Test creating barcode scan without barcode."""
        with self.assertRaises(ScanNotFoundError):
            Scan(scan_id=1, user=self.user, scan_type=ScanType.BARCODE)
    
    def test_update_product_info(self):
        """Test updating product information."""
        scan = Scan(scan_id=1, user=self.user, scan_type=ScanType.MANUAL)
        
        scan.update_product_info(
            name="Test Product",
            brand="Test Brand",
            description="Test Description"
        )
        
        self.assertEqual(scan.product_name, "Test Product")
        self.assertEqual(scan.product_brand, "Test Brand")
        self.assertEqual(scan.product_description, "Test Description")
        self.assertTrue(scan.has_product_info())
    
    def test_update_analysis(self):
        """Test updating analysis results."""
        scan = Scan(scan_id=1, user=self.user, scan_type=ScanType.MANUAL)
        safety_score = SafetyScore(Decimal("85.0"))
        
        scan.update_analysis(safety_score)
        
        self.assertEqual(scan.safety_score, safety_score)
        self.assertTrue(scan.analysis_available)
        self.assertTrue(scan.has_analysis())
    
    def test_get_ingredients_list(self):
        """Test getting ingredients as list."""
        scan = Scan(
            scan_id=1,
            user=self.user,
            scan_type=ScanType.MANUAL,
            product_ingredients_text="Water, Glycerin, Hyaluronic Acid"
        )
        
        ingredients = scan.get_ingredients_list()
        self.assertEqual(len(ingredients), 3)
        self.assertIn("Water", ingredients)
        self.assertIn("Glycerin", ingredients)
        self.assertIn("Hyaluronic Acid", ingredients)


class TestValueObjects(unittest.TestCase):
    """Test value objects."""
    
    def test_skin_type_validation(self):
        """Test skin type validation."""
        # Valid skin types
        self.assertEqual(SkinType.from_string("normal"), SkinType.NORMAL)
        self.assertEqual(SkinType.from_string("combination"), SkinType.COMBINATION)
        self.assertEqual(SkinType.from_string(""), SkinType.UNSPECIFIED)
        
        # Invalid skin type
        with self.assertRaises(InvalidSkinTypeError):
            SkinType.from_string("invalid")
    
    def test_age_range_validation(self):
        """Test age range validation."""
        # Valid age ranges
        self.assertEqual(AgeRange.from_string("26-35"), AgeRange.AGE_26_35)
        self.assertEqual(AgeRange.from_string("under18"), AgeRange.UNDER_18)
        self.assertEqual(AgeRange.from_string(""), AgeRange.UNSPECIFIED)
        
        # Invalid age range
        with self.assertRaises(InvalidAgeRangeError):
            AgeRange.from_string("invalid")
    
    def test_safety_score_validation(self):
        """Test safety score validation."""
        # Valid scores
        score1 = SafetyScore(Decimal("85.0"))
        self.assertEqual(score1.score, Decimal("85.0"))
        self.assertEqual(score1.risk_level, RiskLevel.LOW)
        self.assertTrue(score1.is_safe())
        
        score2 = SafetyScore(Decimal("45.0"))
        self.assertEqual(score2.risk_level, RiskLevel.HIGH)
        self.assertTrue(score2.is_high_risk())
        
        # Invalid scores
        with self.assertRaises(InvalidSafetyScoreError):
            SafetyScore(Decimal("150.0"))
        
        with self.assertRaises(InvalidSafetyScoreError):
            SafetyScore(Decimal("-10.0"))


if __name__ == '__main__':
    unittest.main()
