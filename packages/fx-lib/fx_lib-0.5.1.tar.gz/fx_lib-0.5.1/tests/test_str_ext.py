#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.str_ext module."""

import unittest
from fx_lib.str_ext import StrExt, S


class TestStrExt(unittest.TestCase):
    """Test cases for StrExt class."""

    def test_str_ext_inherits_from_str(self):
        """Test StrExt properly inherits from str."""
        s = StrExt("hello")
        self.assertIsInstance(s, str)
        self.assertIsInstance(s, StrExt)

    def test_str_ext_behaves_like_string(self):
        """Test StrExt behaves like a normal string."""
        s = StrExt("hello")
        self.assertEqual(str(s), "hello")
        self.assertEqual(len(s), 5)
        self.assertEqual(s[0], "h")
        self.assertEqual(s.upper(), "HELLO")

    def test_is_empty_with_empty_string(self):
        """Test is_empty returns True for empty string."""
        s = StrExt("")
        self.assertTrue(s.is_empty())

    def test_is_empty_with_non_empty_string(self):
        """Test is_empty returns False for non-empty string."""
        s = StrExt("hello")
        self.assertFalse(s.is_empty())

    def test_is_empty_with_whitespace_only(self):
        """Test is_empty returns False for whitespace-only strings."""
        s = StrExt("   ")
        self.assertFalse(s.is_empty())  # Only truly empty strings are empty

    def test_is_blank_with_empty_string(self):
        """Test is_blank returns True for empty string."""
        s = StrExt("")
        self.assertTrue(s.is_blank())

    def test_is_blank_with_whitespace_only(self):
        """Test is_blank returns True for whitespace-only strings."""
        s = StrExt("   ")
        self.assertTrue(s.is_blank())
        s = StrExt("\t\n  ")
        self.assertTrue(s.is_blank())

    def test_is_blank_with_non_blank_string(self):
        """Test is_blank returns False for non-blank strings."""
        s = StrExt("hello")
        self.assertFalse(s.is_blank())
        s = StrExt("  hello  ")
        self.assertFalse(s.is_blank())

    def test_constructor_with_non_string_raises_error(self):
        """Test constructor raises TypeError for non-string input."""
        with self.assertRaises(TypeError):
            StrExt(123)
        with self.assertRaises(TypeError):
            StrExt(None)
        with self.assertRaises(TypeError):
            StrExt([1, 2, 3])

    def test_s_alias_works(self):
        """Test S alias works the same as StrExt."""
        s1 = StrExt("hello")
        s2 = S("hello")
        self.assertEqual(s1, s2)
        self.assertIsInstance(s2, StrExt)
        self.assertTrue(s2.is_empty() == s1.is_empty())

    def test_string_concatenation(self):
        """Test StrExt works with string concatenation."""
        s = StrExt("hello")
        result = s + " world"
        # Result should be regular string, not StrExt
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, str)

    def test_string_multiplication(self):
        """Test StrExt works with string multiplication."""
        s = StrExt("hi")
        result = s * 3
        self.assertEqual(result, "hihihi")

    def test_string_slicing(self):
        """Test StrExt works with slicing."""
        s = StrExt("hello")
        self.assertEqual(s[1:4], "ell")
        self.assertEqual(s[:3], "hel")
        self.assertEqual(s[3:], "lo")

    def test_string_formatting(self):
        """Test StrExt works with string formatting."""
        s = StrExt("Hello {}")
        result = s.format("world")
        self.assertEqual(result, "Hello world")

    def test_repr_and_str(self):
        """Test string representation methods."""
        s = StrExt("hello")
        self.assertEqual(str(s), "hello")
        self.assertEqual(repr(s), "'hello'")


if __name__ == '__main__':
    unittest.main()