#!/usr/bin/env python3
"""Verify DeepSeek-R1 is now the default model."""
import sys
sys.path.insert(0, '.')

print("Checking default LLM configuration...")
print("=" * 60)

# Check the code
with open('profissa_lft/ai_generator.py', 'r') as f:
    content = f.read()
    
    # Find the default model_name parameter
    if 'model_name: str = "deepseek-r1"' in content:
        print("✓ Default model changed to: deepseek-r1")
    else:
        print("✗ Default model not updated")
    
    # Check if deepseek-r1 is in SUPPORTED_MODELS
    if '"deepseek-r1": "deepseek-ai/DeepSeek-R1-0528"' in content:
        print("✓ DeepSeek-R1-0528 added to SUPPORTED_MODELS")
    else:
        print("✗ DeepSeek-R1-0528 not in SUPPORTED_MODELS")

print("\n" + "=" * 60)
print("Instantiating generator with default settings...")
print("(This will take time as DeepSeek is larger than Stable Code)")
print("=" * 60)

