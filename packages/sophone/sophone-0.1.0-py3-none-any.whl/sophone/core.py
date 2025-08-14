"""
Core functionality for Somali phone number validation and formatting.
"""

import re
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass


# Error codes constants
class ERROR_CODES:
    INVALID_LENGTH = 'INVALID_LENGTH'
    INVALID_PREFIX = 'INVALID_PREFIX'
    UNKNOWN = 'UNKNOWN'
    INVALID_INPUT = 'INVALID_INPUT'


class SomaliPhoneError(Exception):
    """Custom exception for Somali phone number validation errors."""
    
    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


# Mobile prefixes and operator mappings
MOBILE_PREFIXES: Set[str] = {
    "61", "62", "63", "64", "65", "66", "68", "69", "71", "77"
}

OPERATOR_BY_PREFIX: Dict[str, str] = {
    "61": "Hormuud",
    "77": "Hormuud", 
    "62": "Somtel",
    "65": "Somtel",
    "66": "Somtel",
    "63": "Telesom",
    "64": "SomLink",
    "68": "SomNet",
    "69": "NationLink",
    "71": "Amtel",
}

# Operator information
OPERATOR_INFO: Dict[str, Dict[str, Any]] = {
    "Hormuud": {
        "name": "Hormuud Telecom Somalia",
        "prefixes": ["61", "77"],
        "website": "https://hormuud.com",
        "type": "GSM"
    },
    "Somtel": {
        "name": "Somtel Network", 
        "prefixes": ["62", "65", "66"],
        "website": "https://somtel.com",
        "type": "GSM"
    },
    "Telesom": {
        "name": "Telesom",
        "prefixes": ["63"],
        "website": "https://telesom.net",
        "type": "GSM"
    },
    "SomLink": {
        "name": "SomLink",
        "prefixes": ["64"],
        "website": None,
        "type": "GSM"
    },
    "SomNet": {
        "name": "SomNet",
        "prefixes": ["68"],
        "website": None,
        "type": "GSM"
    },
    "NationLink": {
        "name": "NationLink Telecom",
        "prefixes": ["69"],
        "website": None,
        "type": "GSM"
    },
    "Amtel": {
        "name": "Amtel",
        "prefixes": ["71"],
        "website": None,
        "type": "GSM"
    }
}


@dataclass
class ValidationResult:
    """Result of phone number validation."""
    ok: bool
    value: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


def _digits(s: str) -> str:
    """Extract digits and plus sign from string."""
    if not isinstance(s, str):
        return ""
    return re.sub(r'[^\d+]', '', s)


def to_nsn(input_number: str) -> str:
    """Convert input to National Significant Number (NSN)."""
    s = _digits(input_number)
    
    if s.startswith("+"):
        s = s[1:]
    if s.startswith("00252"):
        s = s[5:]
    elif s.startswith("252"):
        s = s[3:]
    if s.startswith("0"):
        s = s[1:]
    
    return s


def is_valid_somali_mobile(input_number: str) -> bool:
    """Check if input is a valid Somali mobile number."""
    if not input_number or not isinstance(input_number, str):
        return False
    
    nsn = to_nsn(input_number)
    if not re.match(r'^\d{9}$', nsn):
        return False
    
    return nsn[:2] in MOBILE_PREFIXES


def _get_validation_error(input_number: str) -> Optional[Dict[str, Any]]:
    """Get validation error details if number is invalid."""
    if not input_number or not isinstance(input_number, str):
        return {
            "code": ERROR_CODES.INVALID_INPUT,
            "message": "Phone number is required and must be a string",
            "details": {"input": input_number, "type": type(input_number).__name__}
        }
    
    nsn = to_nsn(input_number)
    
    if not nsn or len(nsn) == 0:
        return {
            "code": ERROR_CODES.INVALID_INPUT,
            "message": f'"{input_number}" contains no valid digits',
            "details": {"input": input_number, "nsn": nsn}
        }
    
    if len(nsn) < 9:
        return {
            "code": ERROR_CODES.INVALID_LENGTH,
            "message": f'"{input_number}" is too short ({len(nsn)} digits). Somali mobile numbers need 9 digits',
            "details": {
                "input": input_number,
                "nsn": nsn,
                "actual_length": len(nsn),
                "expected_length": 9
            }
        }
    
    if len(nsn) > 9:
        return {
            "code": ERROR_CODES.INVALID_LENGTH,
            "message": f'"{input_number}" is too long ({len(nsn)} digits). Somali mobile numbers need exactly 9 digits',
            "details": {
                "input": input_number,
                "nsn": nsn,
                "actual_length": len(nsn),
                "expected_length": 9
            }
        }
    
    prefix = nsn[:2]
    if prefix not in MOBILE_PREFIXES:
        valid_prefixes = sorted(list(MOBILE_PREFIXES))
        return {
            "code": ERROR_CODES.INVALID_PREFIX,
            "message": f'"{input_number}" has invalid prefix "{prefix}". Valid prefixes are: {", ".join(valid_prefixes)}',
            "details": {
                "input": input_number,
                "nsn": nsn,
                "prefix": prefix,
                "valid_prefixes": valid_prefixes
            }
        }
    
    return None


# Throwing functions
def normalize_e164(input_number: str) -> str:
    """Convert to E.164 format (+252XXXXXXXXX). Raises SomaliPhoneError if invalid."""
    error = _get_validation_error(input_number)
    if error:
        raise SomaliPhoneError(error["message"], error["code"], error["details"])
    return f"+252{to_nsn(input_number)}"


def format_local(input_number: str) -> str:
    """Format to local format (0XXX XXX XXX). Raises SomaliPhoneError if invalid."""
    error = _get_validation_error(input_number)
    if error:
        raise SomaliPhoneError(error["message"], error["code"], error["details"])
    
    nsn = to_nsn(input_number)
    return f"0{nsn[:3]} {nsn[3:6]} {nsn[6:9]}"


def get_operator(input_number: str) -> str:
    """Get operator name. Raises SomaliPhoneError if invalid."""
    error = _get_validation_error(input_number)
    if error:
        raise SomaliPhoneError(error["message"], error["code"], error["details"])
    
    nsn = to_nsn(input_number)
    return OPERATOR_BY_PREFIX.get(nsn[:2])


def format_international(input_number: str) -> str:
    """Format to international format (+252 XX XXX XXXX). Raises SomaliPhoneError if invalid."""
    error = _get_validation_error(input_number)
    if error:
        raise SomaliPhoneError(error["message"], error["code"], error["details"])
    
    nsn = to_nsn(input_number)
    return f"+252 {nsn[:2]} {nsn[2:5]} {nsn[5:9]}"


def get_operator_info(input_number: str) -> Optional[Dict[str, Any]]:
    """Get detailed operator information. Raises SomaliPhoneError if invalid."""
    error = _get_validation_error(input_number)
    if error:
        raise SomaliPhoneError(error["message"], error["code"], error["details"])
    
    operator = get_operator(input_number)
    return OPERATOR_INFO.get(operator) if operator else None


# Safe functions (non-throwing)
def normalize_e164_safe(input_number: str) -> Optional[str]:
    """Convert to E.164 format. Returns None if invalid."""
    try:
        return normalize_e164(input_number)
    except SomaliPhoneError:
        return None


def format_local_safe(input_number: str) -> Optional[str]:
    """Format to local format. Returns None if invalid."""
    try:
        return format_local(input_number)
    except SomaliPhoneError:
        return None


def get_operator_safe(input_number: str) -> Optional[str]:
    """Get operator name. Returns None if invalid."""
    try:
        return get_operator(input_number)
    except SomaliPhoneError:
        return None


def format_international_safe(input_number: str) -> Optional[str]:
    """Format to international format. Returns None if invalid."""
    try:
        return format_international(input_number)
    except SomaliPhoneError:
        return None


def get_operator_info_safe(input_number: str) -> Optional[Dict[str, Any]]:
    """Get detailed operator information. Returns None if invalid."""
    try:
        return get_operator_info(input_number)
    except SomaliPhoneError:
        return None


# Validate function that returns result object
def validate(input_number: str) -> ValidationResult:
    """Validate phone number and return detailed result."""
    error = _get_validation_error(input_number)
    if error:
        return ValidationResult(
            ok=False,
            error={
                "code": error["code"],
                "message": error["message"],
                "details": error["details"]
            }
        )
    
    nsn = to_nsn(input_number)
    operator = OPERATOR_BY_PREFIX.get(nsn[:2])
    
    return ValidationResult(
        ok=True,
        value={
            "input": input_number,
            "nsn": nsn,
            "e164": f"+252{nsn}",
            "local": f"0{nsn[:3]} {nsn[3:6]} {nsn[6:9]}",
            "operator": operator,
            "operator_info": OPERATOR_INFO.get(operator) if operator else None
        }
    )


# Utility functions
def get_all_operators() -> List[Dict[str, Any]]:
    """Get list of all operators with their information."""
    return [
        {"name": name, **info}
        for name, info in OPERATOR_INFO.items()
    ]


def get_operator_by_prefix(prefix: str) -> Optional[str]:
    """Get operator name by prefix."""
    return OPERATOR_BY_PREFIX.get(prefix)


# Batch processing functions
def validate_batch(numbers: List[str]) -> List[Dict[str, Any]]:
    """Validate a batch of phone numbers."""
    return [
        {"input": number, **validate(number).__dict__}
        for number in numbers
    ]


def normalize_batch(numbers: List[str]) -> List[Dict[str, Any]]:
    """Normalize a batch of phone numbers to E.164 format."""
    return [
        {"input": number, "result": normalize_e164_safe(number)}
        for number in numbers
    ]