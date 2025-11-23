#!/usr/bin/env python3
"""
LangChain demo script
Tests basic LangChain functionality
"""

print("Testing LangChain installation...")

try:
    # Import core LangChain modules
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    
    print("✓ Successfully imported langchain_core modules")
    
    # Test basic prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])
    
    print("✓ Created ChatPromptTemplate successfully")
    
    # Test output parser
    parser = StrOutputParser()
    print("✓ Created StrOutputParser successfully")
    
    print("\n=== LangChain Installation Verification ===")
    print("Status: SUCCESS")
    print("All LangChain core components are working properly!")
    print("==========================================\n")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please check if langchain packages are installed correctly.")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)


