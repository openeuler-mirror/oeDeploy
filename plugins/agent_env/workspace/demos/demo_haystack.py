#!/usr/bin/env python3
"""
Haystack AI demo script
Tests basic Haystack functionality
"""

print("Testing Haystack AI installation...")

try:
    # Import Haystack modules
    from haystack import Pipeline, Document
    
    print("✓ Successfully imported haystack core modules")
    
    # Test basic document creation
    doc = Document(content="This is a test document")
    print("✓ Created Document successfully")
    
    # Test pipeline creation
    pipeline = Pipeline()
    print("✓ Created Pipeline successfully")
    
    print("\n=== Haystack AI Installation Verification ===")
    print("Status: SUCCESS")
    print("Haystack AI is installed and working!")
    print("==========================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if haystack-ai package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


