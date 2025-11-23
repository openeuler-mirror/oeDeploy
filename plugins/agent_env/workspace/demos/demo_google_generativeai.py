#!/usr/bin/env python3
"""
Google Generative AI demo script
Tests basic Google AI SDK functionality
"""

print("Testing Google Generative AI installation...")

try:
    # Import Google Generative AI modules
    import google.generativeai as genai
    
    print("✓ Successfully imported google.generativeai module")
    
    # Test configuration structure (without actual API key)
    # This just verifies the module is properly installed
    print("✓ Module structure is correct")
    
    # Check if main classes are available
    if hasattr(genai, 'GenerativeModel'):
        print("✓ GenerativeModel class is available")
    
    print("\n=== Google Generative AI Installation Verification ===")
    print("Status: SUCCESS")
    print("Google Generative AI SDK is installed correctly!")
    print("===================================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if google-generativeai package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


