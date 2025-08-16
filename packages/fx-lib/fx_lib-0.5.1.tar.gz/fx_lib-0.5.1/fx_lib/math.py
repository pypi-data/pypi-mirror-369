
__all__ = ["modable"]


def modable(n, v):
    """Check if n is divisible by v (i.e., n % v == 0).
    
    Args:
        n: The dividend (number to be divided)
        v: The divisor (number to divide by)
        
    Returns:
        bool: True if n is divisible by v, False otherwise
        
    Raises:
        ZeroDivisionError: If v is zero
    """
    return n % v == 0
