#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.math module."""

import unittest
from fx_lib.math import modable


class TestMathModule(unittest.TestCase):
    """Test cases for math utilities."""

    def test_modable_with_divisible_numbers(self):
        """Test modable returns True when number is divisible."""
        # RED: This test will fail with current implementation
        self.assertTrue(modable(10, 5))  # 10 % 5 == 0, should be True
        self.assertTrue(modable(8, 4))   # 8 % 4 == 0, should be True
        self.assertTrue(modable(12, 3))  # 12 % 3 == 0, should be True
        self.assertTrue(modable(0, 5))   # 0 % 5 == 0, should be True

    def test_modable_with_non_divisible_numbers(self):
        """Test modable returns False when number is not divisible."""
        # RED: This test will fail with current implementation
        self.assertFalse(modable(10, 3))  # 10 % 3 == 1, should be False
        self.assertFalse(modable(7, 4))   # 7 % 4 == 3, should be False
        self.assertFalse(modable(5, 2))   # 5 % 2 == 1, should be False

    def test_modable_edge_cases(self):
        """Test modable with edge cases."""
        # Test with 1 (everything is divisible by 1)
        self.assertTrue(modable(5, 1))
        self.assertTrue(modable(0, 1))
        
        # Test with same numbers
        self.assertTrue(modable(5, 5))
        self.assertTrue(modable(1, 1))

    def test_modable_with_negative_numbers(self):
        """Test modable with negative numbers."""
        self.assertTrue(modable(-10, 5))   # -10 % 5 == 0
        self.assertTrue(modable(10, -5))   # 10 % -5 == 0
        self.assertTrue(modable(-10, -5))  # -10 % -5 == 0
        self.assertFalse(modable(-7, 5))   # -7 % 5 != 0

    def test_modable_with_zero_dividend(self):
        """Test modable when dividend is zero."""
        self.assertTrue(modable(0, 5))   # 0 is divisible by any non-zero number
        self.assertTrue(modable(0, -3))
        self.assertTrue(modable(0, 1))

    def test_modable_with_zero_divisor_raises_error(self):
        """Test modable raises ZeroDivisionError when divisor is zero."""
        with self.assertRaises(ZeroDivisionError):
            modable(5, 0)

    def test_modable_function_name_and_docstring(self):
        """Test function has proper name and documentation."""
        self.assertEqual(modable.__name__, 'modable')
        self.assertIsNotNone(modable.__doc__)
        # Function should be properly documented
        self.assertIn('divisible', modable.__doc__.lower())


if __name__ == '__main__':
    unittest.main()