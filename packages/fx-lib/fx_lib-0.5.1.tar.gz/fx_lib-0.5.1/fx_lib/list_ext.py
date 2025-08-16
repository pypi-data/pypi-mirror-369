__all__ = ["ListExt"]


class ListExt(list):
    """Extended list class with additional utility methods."""

    def __init__(self, iterable=()):
        """Initialize ListExt with an iterable.
        
        Args:
            iterable: Any iterable to initialize the list with (default: empty)
        """
        super().__init__(iterable)

    def __repr__(self):
        """Return string representation using join method."""
        return "[{}]".format(self.join(", "))

    def join(self, delimiter=","):
        """Join all elements into a string with specified delimiter.
        
        Args:
            delimiter: String to use as separator between elements (default: ",")
            
        Returns:
            str: String representation with elements joined by delimiter
        """
        return delimiter.join(str(x) for x in self)
