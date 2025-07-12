# Copyright (C) 2024 Alexandre Mitsuru Kaihara
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS for a PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import os
import logging
from pathlib import Path
from .ai_generator import AITopologyGenerator
from .exceptions import LFTException

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LFT AI Topology Generator - Generate network topologies using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a simple SDN topology
  lft-ai generate "Create a simple SDN topology with 2 hosts connected to a switch" -o topology.py
  
  # Generate a 4G wireless network
  lft-ai generate "Create a 4G wireless network with 3 UEs connected to an eNodeB and EPC" -o wireless_network.py
  
  # Use local model instead of API
  lft-ai generate "Create a complex SDN topology with multiple switches and controllers" -o complex_topology.py --local
  
  # Interactive mode
  lft-ai interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate topology from description')
    gen_parser.add_argument('description', help='Natural language description of the desired topology')
    gen_parser.add_argument('-o', '--output', help='Output file path (default: generated_topology.py)')
    gen_parser.add_argument('--local', action='store_true', help='Use local model instead of Hugging Face API')
    gen_parser.add_argument('--model', default='deepseek-ai/DeepSeek-R1-0528', 
                           help='Model name (default: deepseek-ai/DeepSeek-R1-0528)')
    gen_parser.add_argument('--token', help='Hugging Face API token (or set HF_TOKEN env var)')
    gen_parser.add_argument('--validate', action='store_true', help='Validate generated code')
    gen_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive topology generation')
    interactive_parser.add_argument('--local', action='store_true', help='Use local model instead of Hugging Face API')
    interactive_parser.add_argument('--model', default='deepseek-ai/DeepSeek-R1-0528', 
                                   help='Model name (default: deepseek-ai/DeepSeek-R1-0528)')
    interactive_parser.add_argument('--token', help='Hugging Face API token (or set HF_TOKEN env var)')
    interactive_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # List examples command
    examples_parser = subparsers.add_parser('examples', help='Show example topology descriptions')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        if args.command == 'generate':
            return handle_generate(args, logger)
        elif args.command == 'interactive':
            return handle_interactive(args, logger)
        elif args.command == 'examples':
            return handle_examples()
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

def handle_generate(args, logger):
    """Handle the generate command."""
    try:
        # Initialize AI generator
        generator = AITopologyGenerator(
            model_name=args.model,
            use_hf_api=not args.local,
            api_token=args.token
        )
        
        # Generate topology
        logger.info("Generating topology...")
        generated_code = generator.generate_topology(args.description)
        
        # Validate if requested
        if args.validate:
            if generator.validate_topology(generated_code):
                logger.info("Generated code validation: PASSED")
            else:
                logger.warning("Generated code validation: FAILED")
        
        # Output the result
        if args.output:
            output_file = args.output
            generator.generate_and_save(args.description, output_file)
            print(f"Topology generated and saved to: {output_file}")
        else:
            print("\n" + "="*50)
            print("GENERATED TOPOLOGY CODE")
            print("="*50)
            print(generated_code)
            print("="*50)
        
        return 0
        
    except LFTException as e:
        logger.error(f"LFT Error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

def handle_interactive(args, logger):
    """Handle the interactive command."""
    try:
        # Initialize AI generator
        generator = AITopologyGenerator(
            model_name=args.model,
            use_hf_api=not args.local,
            api_token=args.token
        )
        
        print("LFT AI Topology Generator - Interactive Mode")
        print("="*50)
        print("Type 'quit' to exit, 'help' for examples, 'clear' to clear screen")
        print()
        
        while True:
            try:
                description = input("Describe your topology: ").strip()
                
                if description.lower() == 'quit':
                    print("Goodbye!")
                    break
                elif description.lower() == 'help':
                    handle_examples()
                    continue
                elif description.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif not description:
                    continue
                
                # Generate topology
                logger.info("Generating topology...")
                generated_code = generator.generate_topology(description)
                
                # Validate
                if generator.validate_topology(generated_code):
                    logger.info("Generated code validation: PASSED")
                else:
                    logger.warning("Generated code validation: FAILED")
                
                # Show result
                print("\n" + "="*50)
                print("GENERATED TOPOLOGY CODE")
                print("="*50)
                print(generated_code)
                print("="*50)
                
                # Ask if user wants to save
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save in ['y', 'yes']:
                    filename = input("Enter filename (default: generated_topology.py): ").strip()
                    if not filename:
                        filename = "generated_topology.py"
                    
                    generator.generate_and_save(description, filename)
                    print(f"Topology saved to: {filename}")
                
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                print()
        
        return 0
        
    except LFTException as e:
        logger.error(f"LFT Error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

def handle_examples():
    """Handle the examples command."""
    examples = [
        {
            "title": "Simple SDN Topology",
            "description": "Create a simple SDN topology with 2 hosts connected to a switch"
        },
        {
            "title": "4G Wireless Network",
            "description": "Create a 4G wireless network with 2 UEs connected to an eNodeB and EPC"
        },
        {
            "title": "Multi-Switch SDN",
            "description": "Create an SDN topology with 3 switches, 1 controller, and 4 hosts"
        },
        {
            "title": "Fog Computing Network",
            "description": "Create a fog computing network with edge nodes, fog nodes, and cloud connection"
        },
        {
            "title": "Enterprise Network",
            "description": "Create an enterprise network with multiple VLANs, switches, and a gateway"
        },
        {
            "title": "IoT Network",
            "description": "Create an IoT network with sensors, gateways, and cloud connectivity"
        }
    ]
    
    print("Example Topology Descriptions")
    print("="*50)
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
        print(f"   {example['description']}")
        print()
    
    print("Usage:")
    print("  lft-ai generate \"<description>\" -o output.py")
    print("  lft-ai interactive")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 