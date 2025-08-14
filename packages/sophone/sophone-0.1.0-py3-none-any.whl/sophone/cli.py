#!/usr/bin/env python3
"""
Command-line interface for sophone - Somali phone number utilities.
"""

import sys
import argparse
from pathlib import Path
from typing import List

from .core import (
    is_valid_somali_mobile,
    normalize_e164,
    format_local,
    get_operator,
    format_international,
    get_operator_info,
    get_all_operators,
    validate_batch,
    SomaliPhoneError,
    _get_validation_error
)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='sophone',
        description='Somali phone number utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sophone validate "+252 61 123 4567"
  sophone format "0611234567"
  sophone e164 "0611234567"
  sophone international "0611234567"
  sophone operator "+252771234567"
  sophone info "0611234567"
  sophone operators
  sophone batch numbers.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a phone number')
    validate_parser.add_argument('number', help='Phone number to validate')
    
    # Format command
    format_parser = subparsers.add_parser('format', help='Format to local (0XXX XXX XXX)')
    format_parser.add_argument('number', help='Phone number to format')
    
    # E164 command
    e164_parser = subparsers.add_parser('e164', help='Format to E.164 (+252XXXXXXXXX)')
    e164_parser.add_argument('number', help='Phone number to format')
    
    # International command
    intl_parser = subparsers.add_parser('international', help='Format to international (+252 XX XXX XXXX)')
    intl_parser.add_argument('number', help='Phone number to format')
    
    # Operator command
    operator_parser = subparsers.add_parser('operator', help='Get operator name')
    operator_parser.add_argument('number', help='Phone number to check')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get detailed operator information')
    info_parser.add_argument('number', help='Phone number to check')
    
    # Operators command
    subparsers.add_parser('operators', help='List all operators')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Process numbers from file (one per line)')
    batch_parser.add_argument('file', help='File containing phone numbers')
    
    return parser


def handle_validate(number: str) -> int:
    """Handle validate command."""
    is_valid = is_valid_somali_mobile(number)
    print("✓ valid" if is_valid else "✗ invalid")
    
    if not is_valid:
        error = _get_validation_error(number)
        if error:
            print(f"  {error['message']}")
        return 1
    return 0


def handle_format(number: str) -> int:
    """Handle format command."""
    try:
        result = format_local(number)
        print(result)
        return 0
    except SomaliPhoneError as e:
        print(f"✗ {e}")
        return 1


def handle_e164(number: str) -> int:
    """Handle e164 command."""
    try:
        result = normalize_e164(number)
        print(result)
        return 0
    except SomaliPhoneError as e:
        print(f"✗ {e}")
        return 1


def handle_international(number: str) -> int:
    """Handle international command."""
    try:
        result = format_international(number)
        print(result)
        return 0
    except SomaliPhoneError as e:
        print(f"✗ {e}")
        return 1


def handle_operator(number: str) -> int:
    """Handle operator command."""
    try:
        result = get_operator(number)
        print(result if result else "Unknown")
        return 0
    except SomaliPhoneError as e:
        print(f"✗ {e}")
        return 1


def handle_info(number: str) -> int:
    """Handle info command."""
    try:
        info = get_operator_info(number)
        if info:
            print(f"Operator: {info['name']}")
            print(f"Prefixes: {', '.join(info['prefixes'])}")
            print(f"Type: {info['type']}")
            if info['website']:
                print(f"Website: {info['website']}")
        else:
            print("No operator information available")
        return 0
    except SomaliPhoneError as e:
        print(f"✗ {e}")
        return 1


def handle_operators() -> int:
    """Handle operators command."""
    operators = get_all_operators()
    print("Available Operators:")
    for op in operators:
        print(f"  {op['name']} ({', '.join(op['prefixes'])})")
        if op['website']:
            print(f"    Website: {op['website']}")
    return 0


def handle_batch(file_path: str) -> int:
    """Handle batch command."""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"✗ File not found: {file_path}")
            return 1
        
        content = path.read_text(encoding='utf-8')
        numbers = [line.strip() for line in content.split('\n') if line.strip()]
        results = validate_batch(numbers)
        
        print(f"Processing {len(numbers)} numbers from {file_path}:\n")
        
        for result in results:
            if result['ok']:
                operator = result['value']['operator'] or 'unknown'
                print(f"✓ {result['input']} → {result['value']['e164']} ({operator})")
            else:
                print(f"✗ {result['input']} → {result['error']['message']}")
        
        valid = sum(1 for r in results if r['ok'])
        invalid = len(results) - valid
        print(f"\nSummary: {valid} valid, {invalid} invalid")
        
        return 0
    except Exception as e:
        print(f"✗ Error processing file: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'validate':
            return handle_validate(args.number)
        elif args.command == 'format':
            return handle_format(args.number)
        elif args.command == 'e164':
            return handle_e164(args.number)
        elif args.command == 'international':
            return handle_international(args.number)
        elif args.command == 'operator':
            return handle_operator(args.number)
        elif args.command == 'info':
            return handle_info(args.number)
        elif args.command == 'operators':
            return handle_operators()
        elif args.command == 'batch':
            return handle_batch(args.file)
        else:
            print(f"✗ Unknown command '{args.command}'")
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n✗ Interrupted")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())