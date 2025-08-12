#!/usr/bin/python3
"""
Test runner for Emmett KiCad Plugin

This script runs all tests in the tests directory.
"""

import sys
import os
import subprocess
import unittest

# Add the src/plugins directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'plugins'))

# Import test modules
from test_trace_segment_factory import (
    test_basic_calculations,
    test_serpentine_pattern,
    test_parameter_variations,
    test_arc_adjustment_factors,
    test_polymorphism,
    test_factory_pattern
)


def run_tests():
    """Run all tests and report results."""
    print("Running Emmett Plugin Tests")
    print("=" * 40)
    
    # Collect all test functions
    test_functions = [
        test_basic_calculations,
        test_serpentine_pattern,
        test_parameter_variations,
        test_arc_adjustment_factors,
        test_polymorphism,
        test_factory_pattern
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"\nRunning {test_func.__name__}...")
            test_func()
            print(f"✓ {test_func.__name__} passed")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1


def run_with_pytest():
    """Run tests using pytest if available."""
    try:
        import pytest
        print("Running tests with pytest...")
        return pytest.main([__file__])
    except ImportError:
        print("pytest not available, running with built-in test runner...")
        return run_tests()


if __name__ == "__main__":
    # Try to use pytest if available, otherwise use our custom runner
    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        exit_code = run_with_pytest()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
