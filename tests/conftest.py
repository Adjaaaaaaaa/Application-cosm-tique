"""
Pytest configuration for BeautyScan tests.

This file contains pytest fixtures and configuration for the test suite.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
from django.conf import settings
from django.test.utils import get_runner

# Configure Django
django.setup()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Set up Django database for tests.
    
    This fixture ensures that the Django database is properly configured
    for testing with the Clean Architecture refactored code.
    """
    with django_db_blocker.unblock():
        # Any additional database setup can go here
        pass


@pytest.fixture
def sample_user():
    """
    Create a sample user for testing.
    
    Returns:
        User: A sample user entity for testing
    """
    from core.entities.user import User
    
    return User(
        user_id=1,
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        is_active=True,
        is_staff=False,
        is_superuser=False
    )


@pytest.fixture
def sample_profile(sample_user):
    """
    Create a sample user profile for testing.
    
    Args:
        sample_user: The user entity to create a profile for
        
    Returns:
        UserProfile: A sample user profile entity for testing
    """
    from core.entities.profile import UserProfile
    from core.value_objects.skin_type import SkinType
    from core.value_objects.age_range import AgeRange
    
    return UserProfile(
        user=sample_user,
        subscription_type='free',
        skin_type=SkinType.COMBINATION,
        age_range=AgeRange.ADULT,
        skin_concerns=['acne', 'aging'],
        dermatological_conditions=['eczema'],
        dermatological_other='psoriasis',
        allergies=['paraben', 'sulfate'],
        allergies_other='fragrance',
        product_style='pharmacy',
        routine_frequency='standard',
        objectives=['anti-aging', 'hydration'],
        budget='moderate'
    )


@pytest.fixture
def sample_scan(sample_user):
    """
    Create a sample scan for testing.
    
    Args:
        sample_user: The user entity to create a scan for
        
    Returns:
        Scan: A sample scan entity for testing
    """
    from core.entities.scan import Scan
    from core.value_objects.safety_score import SafetyScore
    from datetime import datetime
    
    return Scan(
        scan_id=1,
        user=sample_user,
        scan_type='barcode',
        barcode='123456789',
        image_path='/media/scans/scan1.jpg',
        scanned_at=datetime.now(),
        notes='Test scan',
        product_name='Test Product',
        product_brand='Test Brand',
        product_description='A test product',
        product_ingredients_text='Water, Glycerin, Paraben',
        safety_score=SafetyScore(85.5),
        analysis_available=True
    )


@pytest.fixture
def mock_user_repository():
    """
    Create a mock user repository for testing.
    
    Returns:
        Mock: A mock user repository
    """
    from unittest.mock import Mock
    return Mock()


@pytest.fixture
def mock_profile_repository():
    """
    Create a mock profile repository for testing.
    
    Returns:
        Mock: A mock profile repository
    """
    from unittest.mock import Mock
    return Mock()


@pytest.fixture
def mock_scan_repository():
    """
    Create a mock scan repository for testing.
    
    Returns:
        Mock: A mock scan repository
    """
    from unittest.mock import Mock
    return Mock()


@pytest.fixture
def django_user():
    """
    Create a Django user for testing.
    
    Returns:
        User: A Django user instance
    """
    from django.contrib.auth.models import User
    
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def django_profile(django_user):
    """
    Create a Django user profile for testing.
    
    Args:
        django_user: The Django user to create a profile for
        
    Returns:
        UserProfile: A Django user profile instance
    """
    from apps.accounts.models import UserProfile
    
    profile = django_user.profile
    profile.skin_type = 'combination'
    profile.age_range = '26-35'
    profile.set_skin_concerns_list(['acne', 'aging'])
    profile.set_allergies_list(['paraben'])
    profile.allergies_other = 'fragrance'
    profile.save()
    
    return profile


@pytest.fixture
def django_scan(django_user):
    """
    Create a Django scan for testing.
    
    Args:
        django_user: The Django user to create a scan for
        
    Returns:
        Scan: A Django scan instance
    """
    from apps.scans.models import Scan
    
    return Scan.objects.create(
        user=django_user,
        scan_type='barcode',
        barcode='123456789',
        product_name='Test Product',
        product_brand='Test Brand',
        product_score=85.5,
        product_risk_level='low',
        analysis_available=True
    )


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest for Django testing.
    
    Args:
        config: Pytest configuration object
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection for Django testing.
    
    Args:
        config: Pytest configuration object
        items: List of test items
    """
    # Add markers based on test file location
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
