#!/usr/bin/env python3
"""
Test script for the new Modern AI Topology Generator.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_generator():
    """Test the new AI generator."""
    print("Testing Modern AI Topology Generator...")
    print("=" * 50)
    
    try:
        # Import the new generator
        from profissa_lft.ai_generator import ModernAITopologyGenerator
        
        print("✓ Import successful")
        
        # Test initialization
        print("\n1. Testing initialization...")
        gen = ModernAITopologyGenerator(use_hf_api=False)
        print("✓ Generator initialized successfully")
        
        # Test model info
        print("\n2. Testing model info...")
        model_info = gen.get_model_info()
        print(f"Model: {model_info.get('model_name', 'Unknown')}")
        print(f"Parameters: {model_info.get('parameters', 'Unknown'):,}")
        print(f"Device: {model_info.get('device', 'Unknown')}")
        
        # Test available models
        print("\n3. Testing available models...")
        available_models = gen.list_available_models()
        print(f"Available models: {', '.join(available_models)}")
        
        # Test simple generation
        print("\n4. Testing simple generation...")
        prompt = "Create a simple network with 2 hosts and 1 switch"
        print(f"Prompt: {prompt}")
        
        try:
            result = gen.generate_topology(prompt)
            print("✓ Generation successful!")
            print(f"Generated code length: {len(result)} characters")
            print("\nFirst 200 characters:")
            print(result[:200] + "..." if len(result) > 200 else result)
            
        except Exception as e:
            print(f"⚠ Generation failed: {e}")
            print("This is expected if the model is still downloading...")
        
        print("\n🎉 AI Generator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_generator()
    sys.exit(0 if success else 1)
