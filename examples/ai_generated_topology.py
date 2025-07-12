#!/usr/bin/env python3
"""
Example script demonstrating the use of LFT AI Topology Generator.
This script shows how to generate network topologies using the Llama-4-Scout-17B-16E-Instruct model.
"""

import os
import sys
from profissa_lft.ai_generator import AITopologyGenerator
from profissa_lft.exceptions import LFTException

def main():
    """Demonstrate AI topology generation."""
    
    # Check if Hugging Face token is available
    api_token = os.getenv('HF_TOKEN')
    if not api_token:
        print("Warning: HF_TOKEN environment variable not set.")
        print("You can either:")
        print("1. Set HF_TOKEN environment variable")
        print("2. Use --local flag to use local model")
        print("3. Pass api_token parameter to AITopologyGenerator")
        print()
        print("For this example, we'll use the local model (if available).")
        use_hf_api = False
    else:
        use_hf_api = True
    
    try:
        # Initialize AI generator
        print("Initializing AI Topology Generator...")
        generator = AITopologyGenerator(
            model_name="deepseek-ai/DeepSeek-R1-0528",
            use_hf_api=use_hf_api,
            api_token=api_token
        )
        
        # Example topology descriptions
        examples = [
            {
                "name": "Simple SDN Topology",
                "description": "Create a simple SDN topology with 2 hosts connected to a switch"
            },
            {
                "name": "4G Wireless Network", 
                "description": "Create a 4G wireless network with 2 UEs connected to an eNodeB and EPC"
            },
            {
                "name": "Multi-Switch SDN",
                "description": "Create an SDN topology with 3 switches, 1 controller, and 4 hosts"
            }
        ]
        
        print(f"AI Generator initialized successfully!")
        print(f"Using {'Hugging Face API' if use_hf_api else 'Local model'}")
        print()
        
        # Generate topologies for each example
        for i, example in enumerate(examples, 1):
            print(f"Example {i}: {example['name']}")
            print(f"Description: {example['description']}")
            print("-" * 60)
            
            try:
                # Generate topology
                print("Generating topology...")
                generated_code = generator.generate_topology(example['description'])
                
                # Validate the generated code
                if generator.validate_topology(generated_code):
                    print("✓ Generated code validation: PASSED")
                else:
                    print("⚠ Generated code validation: FAILED")
                
                # Save to file
                filename = f"ai_generated_{example['name'].lower().replace(' ', '_')}.py"
                generator.generate_and_save(example['description'], filename)
                print(f"✓ Topology saved to: {filename}")
                
                # Show first few lines of generated code
                print("\nGenerated code preview:")
                lines = generated_code.split('\n')
                for j, line in enumerate(lines[:10]):
                    print(f"  {line}")
                if len(lines) > 10:
                    print(f"  ... ({len(lines) - 10} more lines)")
                
                print("\n" + "="*80 + "\n")
                
            except LFTException as e:
                print(f"✗ Error generating topology: {str(e)}")
                print("\n" + "="*80 + "\n")
                continue
        
        print("AI topology generation demonstration completed!")
        print("\nGenerated files:")
        for example in examples:
            filename = f"ai_generated_{example['name'].lower().replace(' ', '_')}.py"
            if os.path.exists(filename):
                print(f"  - {filename}")
        
        print("\nYou can now run any of the generated topology files with:")
        print("  python3 <generated_file>.py")
        
    except LFTException as e:
        print(f"LFT Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 