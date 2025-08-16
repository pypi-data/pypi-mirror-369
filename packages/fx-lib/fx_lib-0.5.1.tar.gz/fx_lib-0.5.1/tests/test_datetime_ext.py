#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fx_lib.datetime_ext module."""

import unittest
from datetime import datetime, timedelta
from fx_lib.datetime_ext import Datetime, Date


class TestDatetime(unittest.TestCase):
    """Test cases for Datetime class."""

    def test_datetime_inherits_from_datetime(self):
        """Test Datetime properly inherits from datetime."""
        dt = Datetime(datetime(2023, 1, 15, 10, 30, 45))
        self.assertIsInstance(dt, datetime)
        self.assertIsInstance(dt, Datetime)

    def test_datetime_creation_with_datetime_object(self):
        """Test creating Datetime with datetime object."""
        source_dt = datetime(2023, 1, 15, 10, 30, 45)
        dt = Datetime(source_dt)
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 15)
        self.assertEqual(dt.hour, 10)
        self.assertEqual(dt.minute, 30)
        self.assertEqual(dt.second, 45)

    def test_datetime_creation_with_no_arguments_uses_now(self):
        """Test creating Datetime with no arguments uses current time."""
        dt = Datetime()
        now = datetime.now()
        # Allow for small time difference in test execution
        self.assertLessEqual(abs((dt - now).total_seconds()), 1)

    def test_datetime_creation_with_invalid_type_raises_error(self):
        """Test creating Datetime with invalid type raises TypeError."""
        with self.assertRaises(TypeError):
            Datetime("2023-01-15")
        with self.assertRaises(TypeError):
            Datetime(20230115)

    def test_to_yyyymmdd_hhmmss(self):
        """Test to_yyyymmdd_hhmmss method."""
        dt = Datetime(datetime(2023, 1, 15, 10, 30, 45))
        result = dt.to_yyyymmdd_hhmmss()
        self.assertEqual(result, "20230115_103045")

    def test_to_iso_date_time(self):
        """Test to_iso_date_time method."""
        dt = Datetime(datetime(2023, 1, 15, 10, 30, 45))
        result = dt.to_iso_date_time()
        self.assertEqual(result, "2023-01-15_10:30:45")

    def test_to_iso_date_time_with_microseconds(self):
        """Test to_iso_date_time handles microseconds correctly."""
        dt = Datetime(datetime(2023, 1, 15, 10, 30, 45, 123456))
        result = dt.to_iso_date_time()
        self.assertEqual(result, "2023-01-15_10:30:45")  # Microseconds should be ignored

    def test_datetime_operations_work(self):
        """Test that datetime operations work correctly."""
        dt = Datetime(datetime(2023, 1, 15, 10, 30, 45))
        
        # Addition
        future = dt + timedelta(days=1, hours=2)
        self.assertEqual(future.day, 16)
        self.assertEqual(future.hour, 12)
        
        # Subtraction
        past = dt - timedelta(days=1)
        self.assertEqual(past.day, 14)


class TestDate(unittest.TestCase):
    """Test cases for Date class."""

    def test_date_inherits_from_datetime(self):
        """Test Date properly inherits from datetime."""
        d = Date(datetime(2023, 1, 15))
        self.assertIsInstance(d, datetime)
        self.assertIsInstance(d, Date)

    def test_date_creation_with_datetime_object(self):
        """Test creating Date with datetime object."""
        source_dt = datetime(2023, 1, 15, 10, 30, 45)  # Time should be ignored
        d = Date(source_dt)
        self.assertEqual(d.year, 2023)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.hour, 0)  # Time components should be zero
        self.assertEqual(d.minute, 0)
        self.assertEqual(d.second, 0)

    def test_date_creation_with_no_arguments_uses_today(self):
        """Test creating Date with no arguments uses current date."""
        d = Date()
        today = datetime.today().date()
        self.assertEqual(d.date(), today)

    def test_date_creation_with_invalid_type_raises_error(self):
        """Test creating Date with invalid type raises TypeError."""
        with self.assertRaises(TypeError):
            Date("2023-01-15")
        with self.assertRaises(TypeError):
            Date(20230115)

    def test_to_yyyy_mm_dd_with_default_delimiter(self):
        """Test to_yyyy_mm_dd with default delimiter."""
        d = Date(datetime(2023, 1, 15))
        result = d.to_yyyy_mm_dd()
        self.assertEqual(result, "2023-01-15")

    def test_to_yyyy_mm_dd_with_custom_delimiter(self):
        """Test to_yyyy_mm_dd with custom delimiter."""
        d = Date(datetime(2023, 1, 15))
        result = d.to_yyyy_mm_dd("/")
        self.assertEqual(result, "2023/01/15")

    def test_to_yyyymmdd(self):
        """Test to_yyyymmdd method."""
        d = Date(datetime(2023, 1, 15))
        result = d.to_yyyymmdd()
        self.assertEqual(result, "20230115")

    def test_to_yyyymm(self):
        """Test to_yyyymm method."""
        d = Date(datetime(2023, 1, 15))
        result = d.to_yyyymm()
        self.assertEqual(result, "202301")

    def test_offset_creates_new_instance(self):
        """Test offset method creates new Date instance without mutating original."""
        d = Date(datetime(2023, 1, 15))
        new_date = d.offset(5)
        
        # Original should be unchanged
        self.assertEqual(d.day, 15)
        # New date should be offset
        self.assertEqual(new_date.day, 20)
        self.assertIsInstance(new_date, Date)
        self.assertIsNot(d, new_date)  # Should be different objects

    def test_offset_with_negative_days(self):
        """Test offset with negative days."""
        d = Date(datetime(2023, 1, 15))
        new_date = d.offset(-5)
        self.assertEqual(new_date.day, 10)

    def test_next_days(self):
        """Test next_days method."""
        d = Date(datetime(2023, 1, 15))
        future = d.next_days(5)
        self.assertEqual(future.day, 20)
        self.assertIsInstance(future, Date)

    def test_next_days_with_zero_or_negative_raises_error(self):
        """Test next_days raises ValueError for zero or negative values."""
        d = Date(datetime(2023, 1, 15))
        with self.assertRaises(ValueError):
            d.next_days(0)
        with self.assertRaises(ValueError):
            d.next_days(-1)

    def test_before_days(self):
        """Test before_days method."""
        d = Date(datetime(2023, 1, 15))
        past = d.before_days(5)
        self.assertEqual(past.day, 10)
        self.assertIsInstance(past, Date)

    def test_before_days_with_zero_or_negative_raises_error(self):
        """Test before_days raises ValueError for zero or negative values."""
        d = Date(datetime(2023, 1, 15))
        with self.assertRaises(ValueError):
            d.before_days(0)
        with self.assertRaises(ValueError):
            d.before_days(-1)

    def test_yesterday(self):
        """Test yesterday method."""
        d = Date(datetime(2023, 1, 15))
        yesterday = d.yesterday()
        self.assertEqual(yesterday.day, 14)
        self.assertIsInstance(yesterday, Date)

    def test_tomorrow(self):
        """Test tomorrow method."""
        d = Date(datetime(2023, 1, 15))
        tomorrow = d.tomorrow()
        self.assertEqual(tomorrow.day, 16)
        self.assertIsInstance(tomorrow, Date)

    def test_today_static_method(self):
        """Test today static method."""
        today = Date.today()
        expected_today = datetime.today().date()
        self.assertEqual(today.date(), expected_today)
        self.assertIsInstance(today, Date)

    def test_month_boundary_operations(self):
        """Test date operations across month boundaries."""
        d = Date(datetime(2023, 1, 31))
        tomorrow = d.tomorrow()
        self.assertEqual(tomorrow.month, 2)
        self.assertEqual(tomorrow.day, 1)

    def test_year_boundary_operations(self):
        """Test date operations across year boundaries."""
        d = Date(datetime(2022, 12, 31))
        tomorrow = d.tomorrow()
        self.assertEqual(tomorrow.year, 2023)
        self.assertEqual(tomorrow.month, 1)
        self.assertEqual(tomorrow.day, 1)


if __name__ == '__main__':
    unittest.main()