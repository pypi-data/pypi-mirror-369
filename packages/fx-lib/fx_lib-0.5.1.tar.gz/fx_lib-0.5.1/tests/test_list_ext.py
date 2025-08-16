#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.list_ext module."""

import unittest
from fx_lib.list_ext import ListExt


class TestListExt(unittest.TestCase):
    """Test cases for ListExt class."""

    def test_list_ext_inherits_from_list(self):
        """Test ListExt properly inherits from list."""
        lst = ListExt([1, 2, 3])
        self.assertIsInstance(lst, list)
        self.assertIsInstance(lst, ListExt)

    def test_list_ext_behaves_like_list(self):
        """Test ListExt behaves like a normal list."""
        lst = ListExt([1, 2, 3])
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0], 1)
        self.assertEqual(lst[-1], 3)
        lst.append(4)
        self.assertEqual(len(lst), 4)

    def test_constructor_with_empty_list(self):
        """Test constructor with empty list."""
        lst = ListExt([])
        self.assertEqual(len(lst), 0)
        self.assertIsInstance(lst, ListExt)

    def test_constructor_with_no_arguments(self):
        """Test constructor with no arguments creates empty list."""
        lst = ListExt()
        self.assertEqual(len(lst), 0)
        self.assertIsInstance(lst, ListExt)

    def test_constructor_with_various_iterables(self):
        """Test constructor works with various iterables."""
        # From list
        lst1 = ListExt([1, 2, 3])
        self.assertEqual(list(lst1), [1, 2, 3])
        
        # From tuple
        lst2 = ListExt((4, 5, 6))
        self.assertEqual(list(lst2), [4, 5, 6])
        
        # From string
        lst3 = ListExt("abc")
        self.assertEqual(list(lst3), ['a', 'b', 'c'])

    def test_join_with_default_delimiter(self):
        """Test join method with default comma delimiter."""
        lst = ListExt([1, 2, 3])
        result = lst.join()
        self.assertEqual(result, "1,2,3")

    def test_join_with_custom_delimiter(self):
        """Test join method with custom delimiter."""
        lst = ListExt([1, 2, 3])
        result = lst.join(" - ")
        self.assertEqual(result, "1 - 2 - 3")

    def test_join_with_mixed_types(self):
        """Test join method converts all elements to strings."""
        lst = ListExt([1, "hello", 3.14, True])
        result = lst.join(", ")
        self.assertEqual(result, "1, hello, 3.14, True")

    def test_join_with_empty_list(self):
        """Test join method with empty list."""
        lst = ListExt([])
        result = lst.join()
        self.assertEqual(result, "")

    def test_join_with_single_element(self):
        """Test join method with single element."""
        lst = ListExt([42])
        result = lst.join()
        self.assertEqual(result, "42")

    def test_repr_uses_join(self):
        """Test __repr__ method uses join functionality."""
        lst = ListExt([1, 2, 3])
        repr_str = repr(lst)
        self.assertEqual(repr_str, "[1, 2, 3]")

    def test_repr_with_empty_list(self):
        """Test __repr__ with empty list."""
        lst = ListExt([])
        repr_str = repr(lst)
        self.assertEqual(repr_str, "[]")

    def test_list_operations_preserve_type(self):
        """Test that list operations return appropriate types."""
        lst = ListExt([1, 2, 3, 4])
        
        # Slicing should return regular list (Python default behavior)
        sliced = lst[1:3]
        self.assertEqual(sliced, [2, 3])
        self.assertIsInstance(sliced, list)
        
        # Addition with another list
        result = lst + [5, 6]
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

    def test_list_methods_work(self):
        """Test that inherited list methods work correctly."""
        lst = ListExt([3, 1, 4, 1, 5])
        
        # Test sort
        lst.sort()
        self.assertEqual(list(lst), [1, 1, 3, 4, 5])
        
        # Test count
        self.assertEqual(lst.count(1), 2)
        
        # Test index
        self.assertEqual(lst.index(3), 2)

    def test_join_with_none_values(self):
        """Test join handles None values properly."""
        lst = ListExt([1, None, 3])
        result = lst.join(", ")
        self.assertEqual(result, "1, None, 3")


if __name__ == '__main__':
    unittest.main()