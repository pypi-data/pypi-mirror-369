"""
Sophone - Professional Somali phone number validation, formatting & operator detection.

A comprehensive Python library for validating, formatting, and analyzing Somali phone numbers
with support for all major operators and beautiful error handling.
"""

from .core import (
    # Constants
    ERROR_CODES,
    SomaliPhoneError,
    OPERATOR_INFO,
    
    # Core functions
    to_nsn,
    is_valid_somali_mobile,
    validate,
    
    # Throwing functions
    normalize_e164,
    format_local,
    get_operator,
    format_international,
    get_operator_info,
    
    # Safe functions (non-throwing)
    normalize_e164_safe,
    format_local_safe,
    get_operator_safe,
    format_international_safe,
    get_operator_info_safe,
    
    # Utility functions
    get_all_operators,
    get_operator_by_prefix,
    
    # Batch processing
    validate_batch,
    normalize_batch,
)

__version__ = "0.1.0"
__author__ = "Jeedaal"
__email__ = "you@example.com"

__all__ = [
    # Constants
    "ERROR_CODES",
    "SomaliPhoneError",
    "OPERATOR_INFO",
    
    # Core functions
    "to_nsn",
    "is_valid_somali_mobile",
    "validate",
    
    # Throwing functions
    "normalize_e164",
    "format_local",
    "get_operator",
    "format_international",
    "get_operator_info",
    
    # Safe functions
    "normalize_e164_safe",
    "format_local_safe",
    "get_operator_safe",
    "format_international_safe",
    "get_operator_info_safe",
    
    # Utility functions
    "get_all_operators",
    "get_operator_by_prefix",
    
    # Batch processing
    "validate_batch",
    "normalize_batch",
]