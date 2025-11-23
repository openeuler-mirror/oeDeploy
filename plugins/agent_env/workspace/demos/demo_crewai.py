#!/usr/bin/env python3
"""
CrewAI demo script
Tests basic CrewAI functionality
"""

print("Testing CrewAI installation...")

try:
    # Import CrewAI modules
    from crewai import Agent, Task, Crew
    
    print("✓ Successfully imported crewai core modules")
    
    # Test crewai-tools
    try:
        import crewai_tools
        print("✓ Successfully imported crewai_tools")
    except ImportError:
        print("⚠ crewai_tools not found (optional)")
    
    # Test basic agent creation structure
    print("✓ Agent, Task, and Crew classes are available")
    
    print("\n=== CrewAI Installation Verification ===")
    print("Status: SUCCESS")
    print("CrewAI is installed and ready to use!")
    print("========================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if crewai package is installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


