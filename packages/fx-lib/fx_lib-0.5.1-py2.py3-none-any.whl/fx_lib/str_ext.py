
__all__ = ["StrExt", "S"]


class StrExt(str):
    """Extended string class with additional utility methods."""

    def __new__(cls, val: str = ""):
        """Create a new StrExt instance.
        
        Args:
            val: String value to initialize with
            
        Returns:
            StrExt instance
            
        Raises:
            TypeError: If val is not a string
        """
        if not isinstance(val, str):
            raise TypeError("StrExt must be initialized with a string. Got {}".format(type(val)))
        return super().__new__(cls, val)

    def is_empty(self) -> bool:
        """Check if string is empty (length is 0).
        
        Returns:
            bool: True if string has length 0, False otherwise
        """
        return len(self) == 0

    def is_blank(self) -> bool:
        """Check if string is blank (empty or contains only whitespace).
        
        Returns:
            bool: True if string is empty or contains only whitespace
        """
        return len(self.strip()) == 0


S = StrExt

