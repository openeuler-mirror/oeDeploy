#!/usr/bin/env python3
"""
Agno demo script
Tests basic Agno functionality
"""

print("Testing Agno installation...")

try:
    # Import Agno modules
    import agno
    
    print("✓ Successfully imported agno module")
    
    # Get version info
    if hasattr(agno, '__version__'):
        print(f"✓ Agno version: {agno.__version__}")
    else:
        print("✓ Agno module loaded successfully")
    
    print("\n=== Agno Installation Verification ===")
    print("Status: SUCCESS")
    print("Agno is installed and importable!")
    print("======================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if agno package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


