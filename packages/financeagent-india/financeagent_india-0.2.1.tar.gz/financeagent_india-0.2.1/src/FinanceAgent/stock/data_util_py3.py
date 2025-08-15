"""Minimal numeric formatting utilities for India NSE fetch.

Previously this module contained multi-market currency parsing, trie search,
and language utilities. For the India-only package we retain only the helper
needed by the NSE row mapper.
"""

def format_number_str(float_str: str) -> str:
    """Normalize a numeric string by removing commas and normalizing minus sign.

    Example: '1,234.50' -> '1234.50'
    """
    if float_str is None:
        return ""
    float_clean_str = str(float_str).replace(",", "")
    float_clean_str = float_clean_str.replace("−", "-")  # Unicode minus
    return float_clean_str

