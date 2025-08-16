from __future__ import annotations
from datetime import datetime, timedelta


__all__ = ["Date", "Datetime"]


class Datetime(datetime):
    """Extended datetime class with additional formatting methods."""

    def __new__(cls, dt=None):
        """Create a new Datetime instance.
        
        Args:
            dt: datetime object to initialize with (default: current time)
            
        Returns:
            Datetime instance
            
        Raises:
            TypeError: If dt is not a datetime object
        """
        if dt is None:
            dt = datetime.now()
        if not isinstance(dt, datetime):
            raise TypeError("Wrong type. Should be datetime")
        return super().__new__(
            cls, dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)

    def __add__(self, other):
        """Override addition to return Datetime instance."""
        # Create a regular datetime to do the operation
        base_dt = datetime(self.year, self.month, self.day, 
                          self.hour, self.minute, self.second, self.microsecond, self.tzinfo)
        result = base_dt + other
        return Datetime(result)

    def __sub__(self, other):
        """Override subtraction to return Datetime instance or timedelta."""
        # Create a regular datetime to do the operation
        base_dt = datetime(self.year, self.month, self.day, 
                          self.hour, self.minute, self.second, self.microsecond, self.tzinfo)
        result = base_dt - other
        if isinstance(result, datetime):
            return Datetime(result)
        return result  # timedelta

    def to_yyyymmdd_hhmmss(self) -> str:
        """Format as YYYYMMDD_HHMMSS.
        
        Returns:
            str: Formatted datetime string
        """
        return self.strftime("%Y%m%d_%H%M%S")

    def to_iso_date_time(self) -> str:
        """Format as YYYY-MM-DD_HH:MM:SS.
        
        Returns:
            str: ISO-like formatted datetime string
        """
        return self.strftime("%Y-%m-%d_%H:%M:%S")

    # Backward compatibility methods (deprecated)
    def to_string_YYYYMMDD_hhmmss(self) -> str:
        """Deprecated: Use to_yyyymmdd_hhmmss instead."""
        return self.to_yyyymmdd_hhmmss()

    def to_string_YYYY_MM_DD_hhmmss(self) -> str:
        """Deprecated: Use to_iso_date_time instead."""
        return self.strftime("%Y-%m-%d_%H%M%S")

    def to_string_YYYY_MM_DD_hh_mm_ss(self) -> str:
        """Deprecated: Use to_iso_date_time instead."""
        return self.to_iso_date_time()


class Date(datetime):
    """Extended date class with additional utility methods."""

    def __new__(cls, dt=None):
        """Create a new Date instance.
        
        Args:
            dt: datetime object to initialize with (default: current date)
            
        Returns:
            Date instance
            
        Raises:
            TypeError: If dt is not a datetime object
        """
        if dt is None:
            dt = datetime.today()
        if not isinstance(dt, datetime):
            raise TypeError("Wrong type. Should be datetime")
        return super().__new__(cls, dt.year, dt.month, dt.day)

    def __add__(self, other):
        """Override addition to return Date instance."""
        # Create a regular datetime to do the operation
        base_dt = datetime(self.year, self.month, self.day)
        result = base_dt + other
        return Date(result)

    def __sub__(self, other):
        """Override subtraction to return Date instance or timedelta."""
        # Create a regular datetime to do the operation
        base_dt = datetime(self.year, self.month, self.day)
        result = base_dt - other
        if isinstance(result, datetime):
            return Date(result)
        return result  # timedelta

    def to_yyyy_mm_dd(self, delimiter="-") -> str:
        """Format date as YYYY-MM-DD with custom delimiter.
        
        Args:
            delimiter: String to use between date components
            
        Returns:
            str: Formatted date string
        """
        f = "%Y{0}%m{0}%d".format(delimiter)
        return self.strftime(f)

    def to_yyyymmdd(self) -> str:
        """Format date as YYYYMMDD.
        
        Returns:
            str: Formatted date string
        """
        return self.strftime("%Y%m%d")

    def to_yyyymm(self) -> str:
        """Format date as YYYYMM.
        
        Returns:
            str: Formatted year-month string
        """
        return self.strftime("%Y%m")

    def offset(self, days: int) -> Date:
        """Create new Date offset by specified days (immutable operation).
        
        Args:
            days: Number of days to offset (positive or negative)
            
        Returns:
            Date: New Date instance offset by specified days
        """
        new_dt = self + timedelta(days=days)
        return Date(new_dt)

    def next_days(self, days: int) -> Date:
        """Create new Date in the future by specified days.
        
        Args:
            days: Number of days in the future (must be positive)
            
        Returns:
            Date: New Date instance in the future
            
        Raises:
            ValueError: If days is zero or negative
        """
        if days <= 0:
            raise ValueError("Days must be positive. Current value is: {}".format(days))
        return self.offset(days)

    def before_days(self, days: int) -> Date:
        """Create new Date in the past by specified days.
        
        Args:
            days: Number of days in the past (must be positive)
            
        Returns:
            Date: New Date instance in the past
            
        Raises:
            ValueError: If days is zero or negative
        """
        if days <= 0:
            raise ValueError("Days must be positive. Current value is: {}".format(days))
        return self.offset(-days)

    def yesterday(self) -> Date:
        """Get yesterday's date.
        
        Returns:
            Date: New Date instance for yesterday
        """
        return self.before_days(1)

    def tomorrow(self) -> Date:
        """Get tomorrow's date.
        
        Returns:
            Date: New Date instance for tomorrow
        """
        return self.next_days(1)

    @staticmethod
    def today() -> Date:
        """Get today's date.
        
        Returns:
            Date: New Date instance for today
        """
        return Date(datetime.today())

    # Backward compatibility methods (deprecated)
    def to_string_YYYY_MM_DD(self, delimiter="-") -> str:
        """Deprecated: Use to_yyyy_mm_dd instead."""
        return self.to_yyyy_mm_dd(delimiter)

    def to_string_YYYYMMDD(self) -> str:
        """Deprecated: Use to_yyyymmdd instead."""
        return self.to_yyyymmdd()

    def to_string_YYYYMM(self) -> str:
        """Deprecated: Use to_yyyymm instead."""
        return self.to_yyyymm()
