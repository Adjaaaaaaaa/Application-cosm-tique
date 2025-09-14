#!/usr/bin/env python
"""
Test runner script for BeautyScan application.

This script provides convenient commands to run different types of tests
for the Clean Architecture refactored BeautyScan application.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
from django.conf import settings
from django.test.utils import get_runner

# Configure Django
django.setup()


def run_command(command, description):
    """
    Run a command and display the result.
    
    Args:
        command: Command to run
        description: Description of what the command does
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_unit_tests():
    """Run unit tests for domain entities, value objects, and use cases."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/unit/', 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "Unit Tests (Domain, Use Cases, Infrastructure)")


def run_integration_tests():
    """Run integration tests for Django apps."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/integration/', 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "Integration Tests (Django Apps)")


def run_domain_tests():
    """Run tests for domain layer (entities and value objects)."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/unit/core/', 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "Domain Layer Tests (Entities & Value Objects)")


def run_usecase_tests():
    """Run tests for use cases."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/unit/usecases/', 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "Use Case Tests")


def run_infrastructure_tests():
    """Run tests for infrastructure layer."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/unit/infrastructure/', 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "Infrastructure Tests (Django Repositories)")


def run_all_tests():
    """Run all tests."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/', 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "All Tests")


def run_django_tests():
    """Run tests using Django's test runner."""
    command = [
        sys.executable, 'manage.py', 'test', 
        '--verbosity=2',
        '--keepdb'
    ]
    return run_command(command, "Django Test Runner")


def run_coverage_tests():
    """Run tests with coverage reporting."""
    command = [
        sys.executable, '-m', 'pytest', 
        'tests/', 
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-exclude=venv/*',
        '--cov-exclude=migrations/*',
        '--cov-exclude=staticfiles/*',
        '--cov-exclude=static/*',
        '--cov-exclude=templates/*',
        '--cov-exclude=*.pyc',
        '--cov-exclude=__pycache__/*',
        '--disable-warnings'
    ]
    return run_command(command, "Tests with Coverage Report")


def run_specific_test(test_path):
    """Run a specific test file or test function."""
    command = [
        sys.executable, '-m', 'pytest', 
        test_path, 
        '-v', 
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, f"Specific Test: {test_path}")


def check_django_setup():
    """Check if Django is properly configured."""
    try:
        from django.core.management import execute_from_command_line
        print("✓ Django is properly configured")
        return True
    except Exception as e:
        print(f"✗ Django configuration error: {e}")
        return False


def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description='BeautyScan Test Runner')
    parser.add_argument(
        'test_type', 
        nargs='?', 
        default='all',
        choices=[
            'all', 'unit', 'integration', 'domain', 'usecase', 
            'infrastructure', 'django', 'coverage', 'check'
        ],
        help='Type of tests to run'
    )
    parser.add_argument(
        '--specific', 
        type=str, 
        help='Run a specific test file or function'
    )
    
    args = parser.parse_args()
    
    print("BeautyScan Test Runner")
    print("=" * 60)
    
    # Check Django setup first
    if not check_django_setup():
        sys.exit(1)
    
    success = True
    
    if args.specific:
        success = run_specific_test(args.specific)
    elif args.test_type == 'all':
        success = run_all_tests()
    elif args.test_type == 'unit':
        success = run_unit_tests()
    elif args.test_type == 'integration':
        success = run_integration_tests()
    elif args.test_type == 'domain':
        success = run_domain_tests()
    elif args.test_type == 'usecase':
        success = run_usecase_tests()
    elif args.test_type == 'infrastructure':
        success = run_infrastructure_tests()
    elif args.test_type == 'django':
        success = run_django_tests()
    elif args.test_type == 'coverage':
        success = run_coverage_tests()
    elif args.test_type == 'check':
        print("✓ Django setup check completed")
        return
    
    if success:
        print(f"\n{'='*60}")
        print("✓ All tests completed successfully!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("✗ Some tests failed!")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == '__main__':
    main()
