"""
Unit tests for Scan domain entity.

Tests the Scan entity validation, properties, and business logic.
"""

import unittest
from datetime import datetime
from core.entities.user import User
from core.entities.scan import Scan
from core.value_objects.safety_score import SafetyScore, RiskLevel
from core.exceptions import InvalidInputException


class TestScanEntity(unittest.TestCase):
    """Test cases for Scan domain entity."""

    def setUp(self):
        """Set up test data."""
        self.user = User(
            user_id=1,
            username='testuser',
            email='test@example.com'
        )
        
        self.safety_score = SafetyScore(85.5)
        
        self.valid_scan_data = {
            'scan_id': 1,
            'user': self.user,
            'scan_type': 'barcode',
            'barcode': '123456789',
            'image_path': '/media/scans/scan1.jpg',
            'scanned_at': datetime.now(),
            'notes': 'Test scan',
            'product_name': 'Test Product',
            'product_brand': 'Test Brand',
            'product_description': 'A test product',
            'product_ingredients_text': 'Water, Glycerin, Paraben',
            'safety_score': self.safety_score,
            'analysis_available': True
        }

    def test_create_scan_with_valid_data(self):
        """Test creating scan with valid data."""
        scan = Scan(**self.valid_scan_data)
        
        self.assertEqual(scan.id, 1)
        self.assertEqual(scan.user, self.user)
        self.assertEqual(scan.scan_type, 'barcode')
        self.assertEqual(scan.barcode, '123456789')
        self.assertEqual(scan.image_path, '/media/scans/scan1.jpg')
        self.assertEqual(scan.scanned_at, self.valid_scan_data['scanned_at'])
        self.assertEqual(scan.notes, 'Test scan')
        self.assertEqual(scan.product_name, 'Test Product')
        self.assertEqual(scan.product_brand, 'Test Brand')
        self.assertEqual(scan.product_description, 'A test product')
        self.assertEqual(scan.product_ingredients_text, 'Water, Glycerin, Paraben')
        self.assertEqual(scan.safety_score, self.safety_score)
        self.assertTrue(scan.analysis_available)

    def test_create_new_scan(self):
        """Test creating new scan (not yet persisted)."""
        new_scan_data = self.valid_scan_data.copy()
        new_scan_data['scan_id'] = None
        scan = Scan(**new_scan_data)
        
        self.assertIsNone(scan.id)
        self.assertEqual(scan.scan_type, 'barcode')
        self.assertEqual(scan.product_name, 'Test Product')

    def test_create_barcode_scan(self):
        """Test creating barcode scan."""
        barcode_data = self.valid_scan_data.copy()
        barcode_data['scan_type'] = 'barcode'
        barcode_data['barcode'] = '987654321'
        scan = Scan(**barcode_data)
        
        self.assertEqual(scan.scan_type, 'barcode')
        self.assertEqual(scan.barcode, '987654321')

    def test_create_barcode_scan_without_barcode(self):
        """Test creating barcode scan without barcode."""
        barcode_data = self.valid_scan_data.copy()
        barcode_data['scan_type'] = 'barcode'
        barcode_data['barcode'] = None
        scan = Scan(**barcode_data)
        
        self.assertEqual(scan.scan_type, 'barcode')
        self.assertIsNone(scan.barcode)

    def test_create_scan_with_invalid_type(self):
        """Test creating scan with invalid type."""
        invalid_data = self.valid_scan_data.copy()
        invalid_data['scan_type'] = 'invalid_type'
        
        with self.assertRaises(InvalidInputException):
            Scan(**invalid_data)

    def test_create_scan_with_invalid_user(self):
        """Test creating scan with invalid user."""
        invalid_data = self.valid_scan_data.copy()
        invalid_data['user'] = None
        
        with self.assertRaises(InvalidInputException):
            Scan(**invalid_data)

    def test_get_ingredients_list(self):
        """Test getting ingredients as list."""
        scan = Scan(**self.valid_scan_data)
        ingredients = scan.get_ingredients_list()
        
        expected = ['Water', 'Glycerin', 'Paraben']
        self.assertEqual(ingredients, expected)

    def test_get_ingredients_list_empty(self):
        """Test getting ingredients list when empty."""
        data = self.valid_scan_data.copy()
        data['product_ingredients_text'] = ''
        scan = Scan(**data)
        ingredients = scan.get_ingredients_list()
        
        self.assertEqual(ingredients, [])

    def test_get_ingredients_list_with_commas(self):
        """Test getting ingredients list with comma separation."""
        data = self.valid_scan_data.copy()
        data['product_ingredients_text'] = 'Water, Glycerin, Paraben, Fragrance'
        scan = Scan(**data)
        ingredients = scan.get_ingredients_list()
        
        expected = ['Water', 'Glycerin', 'Paraben', 'Fragrance']
        self.assertEqual(ingredients, expected)

    def test_update_product_info(self):
        """Test updating product information."""
        scan = Scan(**self.valid_scan_data)
        
        new_info = {
            'product_name': 'Updated Product',
            'product_brand': 'Updated Brand',
            'product_description': 'Updated description',
            'product_ingredients_text': 'New ingredients'
        }
        
        scan.update_product_info(**new_info)
        
        self.assertEqual(scan.product_name, 'Updated Product')
        self.assertEqual(scan.product_brand, 'Updated Brand')
        self.assertEqual(scan.product_description, 'Updated description')
        self.assertEqual(scan.product_ingredients_text, 'New ingredients')

    def test_update_analysis(self):
        """Test updating analysis results."""
        scan = Scan(**self.valid_scan_data)
        
        new_safety_score = SafetyScore(92.0)
        scan.update_analysis(
            safety_score=new_safety_score,
            analysis_available=True
        )
        
        self.assertEqual(scan.safety_score, new_safety_score)
        self.assertTrue(scan.analysis_available)

    def test_update_analysis_without_safety_score(self):
        """Test updating analysis without safety score."""
        scan = Scan(**self.valid_scan_data)
        
        scan.update_analysis(
            safety_score=None,
            analysis_available=False
        )
        
        self.assertIsNone(scan.safety_score)
        self.assertFalse(scan.analysis_available)

    def test_scan_equality(self):
        """Test scan equality based on ID."""
        scan1 = Scan(**self.valid_scan_data)
        scan2_data = self.valid_scan_data.copy()
        scan2_data['product_name'] = 'Different Product'
        scan2 = Scan(**scan2_data)
        
        self.assertEqual(scan1, scan2)

    def test_scan_inequality(self):
        """Test scan inequality with different IDs."""
        scan1 = Scan(**self.valid_scan_data)
        scan2_data = self.valid_scan_data.copy()
        scan2_data['scan_id'] = 2
        scan2 = Scan(**scan2_data)
        
        self.assertNotEqual(scan1, scan2)

    def test_scan_hash(self):
        """Test scan hash based on ID."""
        scan1 = Scan(**self.valid_scan_data)
        scan2_data = self.valid_scan_data.copy()
        scan2_data['product_name'] = 'Different Product'
        scan2 = Scan(**scan2_data)
        
        self.assertEqual(hash(scan1), hash(scan2))

    def test_scan_string_representation(self):
        """Test scan string representation."""
        scan = Scan(**self.valid_scan_data)
        expected = "Scan(id=1, scan_type='barcode', product_name='Test Product')"
        self.assertEqual(str(scan), expected)

    def test_scan_repr(self):
        """Test scan detailed string representation."""
        scan = Scan(**self.valid_scan_data)
        repr_str = repr(scan)
        self.assertIn('Scan(', repr_str)
        self.assertIn('scan_id=1', repr_str)
        self.assertIn("scan_type='barcode'", repr_str)
        self.assertIn("product_name='Test Product'", repr_str)

    def test_scan_with_no_safety_score(self):
        """Test scan without safety score."""
        data = self.valid_scan_data.copy()
        data['safety_score'] = None
        scan = Scan(**data)
        
        self.assertIsNone(scan.safety_score)
        self.assertTrue(scan.analysis_available)

    def test_scan_with_high_risk_score(self):
        """Test scan with high risk safety score."""
        high_risk_score = SafetyScore(25.0)
        data = self.valid_scan_data.copy()
        data['safety_score'] = high_risk_score
        scan = Scan(**data)
        
        self.assertEqual(scan.safety_score, high_risk_score)
        self.assertEqual(scan.safety_score.risk_level, RiskLevel.HIGH)

    def test_scan_with_medium_risk_score(self):
        """Test scan with medium risk safety score."""
        medium_risk_score = SafetyScore(65.0)
        data = self.valid_scan_data.copy()
        data['safety_score'] = medium_risk_score
        scan = Scan(**data)
        
        self.assertEqual(scan.safety_score, medium_risk_score)
        self.assertEqual(scan.safety_score.risk_level, RiskLevel.MEDIUM)

    def test_scan_with_low_risk_score(self):
        """Test scan with low risk safety score."""
        low_risk_score = SafetyScore(85.0)
        data = self.valid_scan_data.copy()
        data['safety_score'] = low_risk_score
        scan = Scan(**data)
        
        self.assertEqual(scan.safety_score, low_risk_score)
        self.assertEqual(scan.safety_score.risk_level, RiskLevel.LOW)


if __name__ == '__main__':
    unittest.main()
