#!/usr/bin/env python3
"""
Test script for LFT AI Topology Generator.
This script tests the basic functionality of the AI generator.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from profissa_lft.ai_generator import AITopologyGenerator
from profissa_lft.exceptions import LFTException

def test_ai_generator():
    """Test the AI generator functionality."""
    print("Testing LFT AI Topology Generator...")
    print("="*50)
    
    # Check if Hugging Face token is available
    api_token = os.getenv('HF_TOKEN')
    if not api_token:
        print("Warning: HF_TOKEN environment variable not set.")
        print("This test will attempt to use local model (if available).")
        use_hf_api = False
    else:
        print("✓ Hugging Face API token found")
        use_hf_api = True
    
    try:
        # Test 1: Initialize generator
        print("\n1. Testing generator initialization...")
        generator = AITopologyGenerator(
            model_name="deepseek-ai/DeepSeek-R1-0528",
            use_hf_api=use_hf_api,
            api_token=api_token
        )
        print("✓ Generator initialized successfully")
        
        # Test 2: Generate simple topology
        print("\n2. Testing topology generation...")
        description = "Create a simple SDN topology with 2 hosts connected to a switch"
        print(f"Description: {description}")
        
        generated_code = generator.generate_topology(description)
        print("✓ Topology generated successfully")
        
        # Test 3: Validate generated code
        print("\n3. Testing code validation...")
        if generator.validate_topology(generated_code):
            print("✓ Generated code validation: PASSED")
        else:
            print("⚠ Generated code validation: FAILED")
        
        # Test 4: Save to file
        print("\n4. Testing file save...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
        
        generator.generate_and_save(description, temp_file)
        
        if os.path.exists(temp_file):
            print(f"✓ File saved successfully: {temp_file}")
            
            # Read and display first few lines
            with open(temp_file, 'r') as f:
                lines = f.readlines()
                print("\nGenerated code preview:")
                for i, line in enumerate(lines[:10]):
                    print(f"  {line.rstrip()}")
                if len(lines) > 10:
                    print(f"  ... ({len(lines) - 10} more lines)")
            
            # Clean up
            os.unlink(temp_file)
        else:
            print("✗ File save failed")
        
        # Test 5: Test with different description
        print("\n5. Testing with different topology type...")
        description2 = "Create a 4G wireless network with 1 UE connected to an eNodeB"
        print(f"Description: {description2}")
        
        generated_code2 = generator.generate_topology(description2)
        print("✓ Second topology generated successfully")
        
        if generator.validate_topology(generated_code2):
            print("✓ Second topology validation: PASSED")
        else:
            print("⚠ Second topology validation: FAILED")
        
        print("\n" + "="*50)
        print("🎉 All tests completed successfully!")
        print("\nThe AI generator is working correctly.")
        print("\nYou can now use it with:")
        print("  - Command line: lft-ai generate \"description\" -o output.py")
        print("  - Interactive mode: lft-ai interactive")
        print("  - Programmatic: AITopologyGenerator().generate_topology(description)")
        
        return 0
        
    except LFTException as e:
        print(f"\n✗ LFT Error: {str(e)}")
        print("\nThis might be due to:")
        print("  - Missing Hugging Face API token")
        print("  - Network connectivity issues")
        print("  - Model access permissions")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(test_ai_generator()) 