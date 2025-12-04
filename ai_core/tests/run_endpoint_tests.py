"""
Quick test runner to validate nutrition endpoint tests.
This script verifies the test structure without running full Django test suite.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')

import django
django.setup()

# Now import and run tests
from ai_core.tests.test_nutrition_endpoint import NutritionPredictionViewTestCase
import unittest

if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(NutritionPredictionViewTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
