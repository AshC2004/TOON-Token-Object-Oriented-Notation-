#!/usr/bin/env python3
"""Example script demonstrating TOON conversion."""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toon import TOONConverter


def main():
    """Convert example.py to TOON format."""
    # Create converter
    converter = TOONConverter(max_docstring_length=60)

    # Convert the example file
    example_file = Path(__file__).parent / "example.py"

    print("="*60)
    print("TOON CONVERSION EXAMPLE")
    print("="*60)
    print(f"\nConverting: {example_file.name}\n")

    # Convert to TOON
    toon_module = converter.convert_file(example_file)

    # Get TOON output
    toon_output = toon_module.to_toon()

    print("TOON OUTPUT:")
    print("-"*60)
    print(toon_output)
    print("-"*60)

    # Show statistics
    stats = toon_module.get_stats()
    print("\nMODULE STATISTICS:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Show compression stats
    with open(example_file, 'r') as f:
        original_code = f.read()

    compression = converter.estimate_compression(original_code, toon_output)
    print("\nCOMPRESSION STATISTICS:")
    for key, value in compression.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60)
    print(f"Token Savings: {compression['token_savings_percent']}%")
    print("="*60)


if __name__ == "__main__":
    main()
