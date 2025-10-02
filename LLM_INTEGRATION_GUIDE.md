# LFT AI Integration Guide
## Using Large Language Models with Lightweight Fog Testbed

**Version:** 1.0  
**Date:** October 2, 2025  
**Default Model:** DeepSeek-R1-0528

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Understanding LFT AI Architecture](#understanding-lft-ai-architecture)
4. [Installation & Setup](#installation--setup)
5. [Quick Start Guide](#quick-start-guide)
6. [Comprehensive Tutorial](#comprehensive-tutorial)
7. [Advanced Usage](#advanced-usage)
8. [Model Selection Guide](#model-selection-guide)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Introduction

The Lightweight Fog Testbed (LFT) now includes AI-powered topology generation using Large Language Models (LLMs). This feature allows you to create complex network topologies using natural language descriptions, making network experimentation more accessible and faster.

### What Can You Do?

- 🤖 **Generate topologies from text**: Describe what you want, get working Python code
- 🔄 **Iterate quickly**: Modify descriptions and regenerate instantly
- 🎓 **Learn LFT**: Use AI to understand LFT components and patterns
- 🚀 **Prototype faster**: Go from idea to running topology in minutes
- 📚 **Explore examples**: Generate variations of network scenarios

---

## Prerequisites

### Required Knowledge

- **Basic Python**: Understanding of Python syntax and modules
- **Networking Basics**: Concepts like hosts, switches, IP addressing
- **Linux Command Line**: Basic terminal navigation and commands

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.9 or higher
- **Memory**: 
  - Minimum: 8GB RAM (for API mode)
  - Recommended: 16GB+ RAM (for local models)
- **Disk Space**: 10-50GB (depending on models)
- **GPU**: Optional but recommended for local inference
  - CUDA-compatible GPU with 8GB+ VRAM for best performance

### Software Requirements

- Docker (for LFT containers)
- Python pip
- Virtual environment support

---

## Understanding LFT AI Architecture

### Components Overview

```
┌─────────────────────────────────────────────────┐
│           User Input (Natural Language)         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│     ModernAITopologyGenerator                   │
│  ┌─────────────────────────────────────────┐   │
│  │  1. Prompt Engineering                  │   │
│  │  2. Model Selection                     │   │
│  │  3. Token Management                    │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│  Local Model │    │ HuggingFace  │
│  (DeepSeek,  │    │     API      │
│   Phi-3, etc)│    │              │
└──────┬───────┘    └──────┬───────┘
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        Generated Python Code                    │
│  ┌─────────────────────────────────────────┐   │
│  │  1. Code Validation                     │   │
│  │  2. Syntax Checking                     │   │
│  │  3. LFT Pattern Matching                │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│     Executable LFT Topology Script              │
└─────────────────────────────────────────────────┘
```

### Available LLM Models

| Model | Size | Best For | Speed | Quality | Local |
|-------|------|----------|-------|---------|-------|
| **DeepSeek-R1** | Large | Complex reasoning, best quality | Slower | ⭐⭐⭐⭐⭐ | ✓ |
| **Phi-3-mini** | 3.8B | Balanced performance | Fast | ⭐⭐⭐⭐ | ✓ |
| **Stable Code 3B** | 3B | Code generation | Fast | ⭐⭐⭐⭐ | ✓ |
| **Qwen2-7B** | 7B | General purpose | Medium | ⭐⭐⭐⭐ | ✓ |
| **Code Llama 7B** | 7B | Code-specific tasks | Medium | ⭐⭐⭐⭐ | ✓ |
| **Gemma2-9B** | 9B | High quality output | Slower | ⭐⭐⭐⭐⭐ | ✓ |

---

## Installation & Setup

### Step 1: Install LFT with AI Support

```bash
# Clone the repository (if not already done)
cd ~/UnB
git clone https://github.com/dcasseb/lft_ai.git
cd lft_ai

# Create and activate virtual environment
python3 -m venv lft_env
source lft_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements_ai.txt

# Install LFT package
pip install -e .
```

### Step 2: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Check installed packages
pip list | grep -E "torch|transformers|profissa"

# Test import
python -c "from profissa_lft import ModernAITopologyGenerator; print('✓ Installation successful!')"
```

### Step 3: Configure Environment (Optional)

```bash
# For Hugging Face API access (optional)
export HF_TOKEN="your_huggingface_token_here"

# Add to your ~/.bashrc for persistence
echo 'export HF_TOKEN="your_token"' >> ~/.bashrc
```

### Step 4: Verify Model Cache

```bash
# Check which models are already downloaded
ls -lh ~/.cache/huggingface/hub/

# Expected output: models--deepseek-ai--DeepSeek-R1-0528 (and others)
```

---

## Quick Start Guide

### Method 1: Python Script (Recommended for Beginners)

Create a file called `my_first_ai_topology.py`:

```python
#!/usr/bin/env python3
"""
My First AI-Generated Topology
This script uses DeepSeek-R1 to generate a simple network topology
"""

from profissa_lft import ModernAITopologyGenerator

# Initialize the AI generator (uses DeepSeek-R1 by default)
print("🤖 Initializing AI Generator (this may take 30-60 seconds)...")
generator = ModernAITopologyGenerator(
    use_hf_api=False,  # Use local model
    load_in_8bit=True  # Memory efficient
)

print("✓ Generator ready!")

# Define what you want
description = """
Create a simple SDN network with:
- 2 hosts (h1 and h2)
- 1 switch (s1)
- Connect both hosts to the switch
- Configure IPs: h1=10.0.0.1/24, h2=10.0.0.2/24
"""

# Generate the topology code
print("\n🎨 Generating topology...")
print(f"Description: {description.strip()}")

try:
    generated_code = generator.generate_topology(description)
    
    # Save to file
    output_file = "generated_simple_topology.py"
    with open(output_file, 'w') as f:
        f.write(generated_code)
    
    print(f"\n✓ Topology generated and saved to: {output_file}")
    print("\n" + "="*60)
    print("Generated Code Preview:")
    print("="*60)
    print(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code)
    
except Exception as e:
    print(f"✗ Error: {e}")
```

Run it:

```bash
source lft_env/bin/activate
python my_first_ai_topology.py
```

### Method 2: Interactive Python Session

```python
# Start Python
python

# Import the generator
from profissa_lft import ModernAITopologyGenerator

# Initialize (wait ~30-60 seconds)
gen = ModernAITopologyGenerator()

# Generate a topology
code = gen.generate_topology("Create a network with 3 hosts and 1 switch")

# View the code
print(code)

# Save it
with open('my_topology.py', 'w') as f:
    f.write(code)
```

### Method 3: One-Line Generation

```python
from profissa_lft import ModernAITopologyGenerator; \
    gen = ModernAITopologyGenerator(); \
    open('topology.py', 'w').write(gen.generate_topology("Simple network with 2 hosts"))
```

---

## Comprehensive Tutorial

### Tutorial 1: Basic SDN Topology

**Objective**: Create a simple Software-Defined Network with hosts and a switch.

#### Step 1: Create the Generation Script

```python
#!/usr/bin/env python3
"""Tutorial 1: Basic SDN Topology"""

from profissa_lft import ModernAITopologyGenerator
import time

def generate_basic_sdn():
    """Generate a basic SDN topology using AI"""
    
    # Initialize generator
    print("Initializing AI Generator...")
    start = time.time()
    generator = ModernAITopologyGenerator(
        model_name="deepseek-r1",  # Explicitly use DeepSeek
        load_in_8bit=True
    )
    print(f"✓ Ready in {time.time()-start:.1f} seconds\n")
    
    # Define the network
    description = """
    Create a Software-Defined Network with:
    - 3 hosts: h1, h2, h3
    - 1 OpenFlow switch: s1
    - 1 SDN controller (OpenDaylight): c1
    
    Configuration:
    - Connect all hosts to the switch
    - h1 IP: 10.0.0.1/24
    - h2 IP: 10.0.0.2/24  
    - h3 IP: 10.0.0.3/24
    - Controller IP: 192.168.1.100
    
    All nodes should be instantiated.
    """
    
    print("Generating topology...")
    print(f"Description: {description.strip()}\n")
    
    # Generate
    code = generator.generate_topology(description)
    
    # Save
    filename = "tutorial1_basic_sdn.py"
    with open(filename, 'w') as f:
        f.write(code)
    
    print(f"✓ Generated: {filename}")
    print(f"✓ Lines of code: {len(code.splitlines())}")
    
    return filename

if __name__ == "__main__":
    output = generate_basic_sdn()
    print(f"\nNext step: Run the generated topology:")
    print(f"  sudo python {output}")
```

#### Step 2: Run the Generator

```bash
python tutorial1_generate.py
```

#### Step 3: Inspect the Generated Code

```bash
cat tutorial1_basic_sdn.py
```

#### Step 4: Execute the Topology

```bash
# Run with sudo (required for Docker containers)
sudo python tutorial1_basic_sdn.py
```

### Tutorial 2: 4G Wireless Network

**Objective**: Create a 4G/LTE network with User Equipment, eNodeB, and EPC.

```python
#!/usr/bin/env python3
"""Tutorial 2: 4G Wireless Network"""

from profissa_lft import ModernAITopologyGenerator

def generate_4g_network():
    """Generate a 4G wireless network"""
    
    generator = ModernAITopologyGenerator()
    
    description = """
    Create a 4G/LTE wireless network with:
    
    Components:
    - 2 User Equipment (UE): ue1, ue2
    - 1 eNodeB (base station): enb1
    - 1 Evolved Packet Core: epc1
    
    Configuration:
    - Connect UEs to eNodeB
    - Connect eNodeB to EPC
    - Configure EPC with default settings
    - Instantiate all components
    
    The network should support basic 4G connectivity.
    """
    
    print("Generating 4G network topology...")
    code = generator.generate_topology(description)
    
    filename = "tutorial2_4g_network.py"
    with open(filename, 'w') as f:
        f.write(code)
    
    print(f"✓ Generated: {filename}")
    return filename

if __name__ == "__main__":
    generate_4g_network()
```

### Tutorial 3: Complex Multi-Layer Network

**Objective**: Create a more complex topology with multiple layers.

```python
#!/usr/bin/env python3
"""Tutorial 3: Multi-Layer Network"""

from profissa_lft import ModernAITopologyGenerator

def generate_complex_network():
    """Generate a complex multi-layer network"""
    
    generator = ModernAITopologyGenerator(
        model_name="deepseek-r1",  # Use best model for complexity
    )
    
    description = """
    Create a complex network topology with:
    
    Core Layer:
    - 2 core switches: core1, core2
    - 1 SDN controller: controller1
    
    Distribution Layer:
    - 3 distribution switches: dist1, dist2, dist3
    
    Access Layer:
    - 6 hosts: h1, h2, h3, h4, h5, h6
    
    Topology:
    - Connect dist1, dist2, dist3 to both core switches
    - Connect h1, h2 to dist1
    - Connect h3, h4 to dist2
    - Connect h5, h6 to dist3
    - Controller manages all switches
    
    IP Addressing:
    - Subnet 10.1.0.0/16
    - h1: 10.1.0.1/16
    - h2: 10.1.0.2/16
    - h3: 10.1.0.3/16
    - h4: 10.1.0.4/16
    - h5: 10.1.0.5/16
    - h6: 10.1.0.6/16
    
    Instantiate all components.
    """
    
    print("Generating complex multi-layer network...")
    print("(This may take longer due to complexity)")
    
    code = generator.generate_topology(description)
    
    filename = "tutorial3_complex_network.py"
    with open(filename, 'w') as f:
        f.write(code)
    
    print(f"✓ Generated: {filename}")
    print(f"✓ Components: ~17 network nodes")
    
    return filename

if __name__ == "__main__":
    generate_complex_network()
```

### Tutorial 4: Iterative Refinement

**Objective**: Learn to refine and improve generated topologies.

```python
#!/usr/bin/env python3
"""Tutorial 4: Iterative Refinement"""

from profissa_lft import ModernAITopologyGenerator

def iterative_generation():
    """Demonstrate iterative refinement"""
    
    generator = ModernAITopologyGenerator()
    
    # Version 1: Basic request
    desc_v1 = "Create a network with 2 hosts and 1 switch"
    print("Version 1 - Basic:")
    code_v1 = generator.generate_topology(desc_v1)
    with open("topology_v1.py", 'w') as f:
        f.write(code_v1)
    print("✓ Saved: topology_v1.py\n")
    
    # Version 2: Add details
    desc_v2 = """
    Create a network with:
    - 2 hosts (h1, h2) with IPs 10.0.0.1/24 and 10.0.0.2/24
    - 1 switch (s1)
    - Connect hosts to switch
    - Instantiate all nodes
    """
    print("Version 2 - With IP configuration:")
    code_v2 = generator.generate_topology(desc_v2)
    with open("topology_v2.py", 'w') as f:
        f.write(code_v2)
    print("✓ Saved: topology_v2.py\n")
    
    # Version 3: Add controller
    desc_v3 = """
    Create an SDN network with:
    - 2 hosts (h1, h2) with IPs 10.0.0.1/24 and 10.0.0.2/24
    - 1 OpenFlow switch (s1)
    - 1 OpenDaylight controller (c1) at IP 192.168.1.100
    - Connect hosts to switch
    - Connect switch to controller
    - Instantiate all nodes
    """
    print("Version 3 - Full SDN with controller:")
    code_v3 = generator.generate_topology(desc_v3)
    with open("topology_v3.py", 'w') as f:
        f.write(code_v3)
    print("✓ Saved: topology_v3.py\n")
    
    print("="*60)
    print("Comparison:")
    print(f"  V1: {len(code_v1.splitlines())} lines (basic)")
    print(f"  V2: {len(code_v2.splitlines())} lines (with IPs)")
    print(f"  V3: {len(code_v3.splitlines())} lines (full SDN)")
    print("="*60)

if __name__ == "__main__":
    iterative_generation()
```

---

## Advanced Usage

### Custom Model Selection

```python
from profissa_lft import ModernAITopologyGenerator

# Use different models for different scenarios

# Fast prototyping - Phi-3 (fastest)
fast_gen = ModernAITopologyGenerator(
    model_name="phi3-mini",
    load_in_8bit=True
)

# Best quality - DeepSeek-R1 (default)
quality_gen = ModernAITopologyGenerator(
    model_name="deepseek-r1",
    load_in_8bit=True
)

# Code-focused - Stable Code
code_gen = ModernAITopologyGenerator(
    model_name="stable-code-3b",
    load_in_8bit=True
)

# Generate with each
fast_code = fast_gen.generate_topology("Simple 2-host network")
quality_code = quality_gen.generate_topology("Complex enterprise network")
code_focused = code_gen.generate_topology("Optimized SDN topology")
```

### Using Hugging Face API

```python
from profissa_lft import ModernAITopologyGenerator
import os

# Set your token
os.environ['HF_TOKEN'] = 'your_token_here'

# Use API instead of local model (faster initialization)
api_gen = ModernAITopologyGenerator(
    model_name="deepseek-r1",
    use_hf_api=True,
    api_token=os.environ['HF_TOKEN']
)

# Generate
code = api_gen.generate_topology("Create a data center network")
```

### Batch Generation

```python
from profissa_lft import ModernAITopologyGenerator
import json

def batch_generate_topologies():
    """Generate multiple topologies from a configuration file"""
    
    generator = ModernAITopologyGenerator()
    
    # Define scenarios
    scenarios = [
        {
            "name": "small_office",
            "description": "Office network: 5 hosts, 1 switch, 1 controller"
        },
        {
            "name": "datacenter",
            "description": "Data center: 10 servers, 2 core switches, redundant"
        },
        {
            "name": "wireless_4g",
            "description": "4G network: 3 UEs, 1 eNodeB, 1 EPC"
        },
        {
            "name": "campus",
            "description": "Campus network: 3 buildings, 20 hosts, hierarchical"
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\nGenerating: {scenario['name']}")
        try:
            code = generator.generate_topology(scenario['description'])
            filename = f"generated_{scenario['name']}.py"
            
            with open(filename, 'w') as f:
                f.write(code)
            
            results.append({
                "scenario": scenario['name'],
                "status": "success",
                "filename": filename,
                "lines": len(code.splitlines())
            })
            print(f"  ✓ Saved: {filename}")
            
        except Exception as e:
            results.append({
                "scenario": scenario['name'],
                "status": "failed",
                "error": str(e)
            })
            print(f"  ✗ Failed: {e}")
    
    # Save summary
    with open('generation_summary.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print(f"Generated {len([r for r in results if r['status']=='success'])} topologies")
    print("Summary saved to: generation_summary.json")

if __name__ == "__main__":
    batch_generate_topologies()
```

### Code Validation

```python
from profissa_lft import ModernAITopologyGenerator

generator = ModernAITopologyGenerator()

description = "Create a network with 3 hosts and 1 switch"
code = generator.generate_topology(description)

# Validate the generated code
try:
    # Check syntax
    compile(code, '<string>', 'exec')
    print("✓ Syntax valid")
    
    # Check for required imports
    if 'from profissa_lft' in code:
        print("✓ Has LFT imports")
    
    # Check for instantiation
    if '.instantiate()' in code:
        print("✓ Includes instantiation")
    
    # Save if valid
    with open('validated_topology.py', 'w') as f:
        f.write(code)
    print("✓ Saved validated topology")
    
except SyntaxError as e:
    print(f"✗ Syntax error: {e}")
```

### Template-Based Generation

```python
from profissa_lft import ModernAITopologyGenerator

class TopologyTemplates:
    """Pre-defined templates for common scenarios"""
    
    @staticmethod
    def simple_sdn(num_hosts=3):
        return f"""
        Create a simple SDN topology with:
        - {num_hosts} hosts (h1 to h{num_hosts})
        - 1 switch (s1)
        - 1 controller (c1)
        - All hosts connected to switch
        - IPs: 10.0.0.1/24 to 10.0.0.{num_hosts}/24
        - Controller at 192.168.1.100
        """
    
    @staticmethod
    def wireless_4g(num_ues=2):
        return f"""
        Create a 4G wireless network with:
        - {num_ues} UEs (ue1 to ue{num_ues})
        - 1 eNodeB (enb1)
        - 1 EPC (epc1)
        - Connect all UEs to eNodeB
        - Connect eNodeB to EPC
        """
    
    @staticmethod
    def spine_leaf(num_leaf=3, num_hosts_per_leaf=2):
        return f"""
        Create a spine-leaf topology with:
        - 2 spine switches (spine1, spine2)
        - {num_leaf} leaf switches (leaf1 to leaf{num_leaf})
        - {num_hosts_per_leaf} hosts per leaf
        - Full mesh between spine and leaf
        - Hosts connected to their leaf switches
        """

# Usage
generator = ModernAITopologyGenerator()
templates = TopologyTemplates()

# Generate from templates
sdn_code = generator.generate_topology(templates.simple_sdn(5))
wireless_code = generator.generate_topology(templates.wireless_4g(3))
datacenter_code = generator.generate_topology(templates.spine_leaf(4, 3))
```

---

## Model Selection Guide

### When to Use Each Model

#### DeepSeek-R1 (Default) ⭐⭐⭐⭐⭐
**Best for:**
- Complex topologies with many components
- Enterprise-grade networks
- When quality is paramount
- Learning and exploration

**Pros:**
- Best reasoning capabilities
- Most accurate code generation
- Handles complex requirements
- Already cached locally

**Cons:**
- Slower initialization (~30-60s)
- Higher memory usage
- Slower generation

**Use when:** You need the best quality and can wait a bit longer

```python
gen = ModernAITopologyGenerator(model_name="deepseek-r1")
```

#### Phi-3-mini ⭐⭐⭐⭐
**Best for:**
- Quick prototyping
- Simple to medium networks
- Rapid iteration
- Limited resources

**Pros:**
- Fast initialization (~15-30s)
- Good quality output
- Lower memory usage
- Balanced performance

**Cons:**
- Less sophisticated reasoning
- May struggle with very complex requests

**Use when:** You need speed and reasonable quality

```python
gen = ModernAITopologyGenerator(model_name="phi3-mini")
```

#### Stable Code 3B ⭐⭐⭐⭐
**Best for:**
- Code-focused generation
- Syntax-heavy tasks
- When you know LFT patterns

**Pros:**
- Very fast
- Excellent code structure
- Small footprint

**Cons:**
- Less contextual understanding
- May miss complex requirements

**Use when:** You need clean, fast code generation

```python
gen = ModernAITopologyGenerator(model_name="stable-code-3b")
```

### Comparison Table

| Scenario | Recommended Model | Alternative |
|----------|------------------|-------------|
| Learning LFT | DeepSeek-R1 | Phi-3-mini |
| Production topologies | DeepSeek-R1 | - |
| Quick testing | Phi-3-mini | Stable Code 3B |
| Code templates | Stable Code 3B | Phi-3-mini |
| Complex requirements | DeepSeek-R1 | - |
| Resource-constrained | Phi-3-mini | Stable Code 3B |
| Batch generation | Phi-3-mini | DeepSeek-R1 |

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "No module named 'torch'"

**Solution:**
```bash
source lft_env/bin/activate
pip install torch transformers accelerate
```

#### Issue 2: Model initialization timeout

**Symptoms:** Script hangs during model loading

**Solutions:**
```python
# 1. Use 8-bit quantization (less memory)
gen = ModernAITopologyGenerator(load_in_8bit=True)

# 2. Use smaller model
gen = ModernAITopologyGenerator(model_name="phi3-mini")

# 3. Use API instead
gen = ModernAITopologyGenerator(use_hf_api=True, api_token="your_token")
```

#### Issue 3: Out of memory errors

**Solutions:**
```python
# Use 4-bit quantization
gen = ModernAITopologyGenerator(
    load_in_4bit=True,
    load_in_8bit=False
)

# Or use CPU explicitly
gen = ModernAITopologyGenerator(device="cpu")
```

#### Issue 4: Generated code has syntax errors

**Solutions:**
```python
# 1. Validate before saving
code = gen.generate_topology(description)
try:
    compile(code, '<string>', 'exec')
    with open('topology.py', 'w') as f:
        f.write(code)
except SyntaxError as e:
    print(f"Error: {e}")
    # Regenerate with more specific prompt

# 2. Use more detailed descriptions
description = """
Create a network with:
- Exact component names
- Specific IP addresses  
- Clear connection topology
- Explicit instantiation calls
"""
```

#### Issue 5: Model generates incorrect LFT API usage

**Solution:**
```python
# Provide more context in description
description = """
Using LFT framework:
- Use Host() for hosts
- Use Switch() for switches
- Use .instantiate() method
- Use .connect() for connections
- Use .setIp() for IP configuration

Create: [your topology description]
"""
```

### Debug Mode

```python
import logging
from profissa_lft import ModernAITopologyGenerator

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

generator = ModernAITopologyGenerator()
# Now you'll see detailed logs
```

### Performance Tips

1. **First run is slowest**: Model caching happens on first load
2. **Reuse generators**: Don't recreate for each topology
3. **Use appropriate models**: Phi-3 for speed, DeepSeek for quality
4. **Clear cache if needed**: `rm -rf ~/.cache/huggingface/hub/`
5. **Monitor memory**: `watch -n 1 free -h`

---

## Best Practices

### Writing Good Descriptions

#### ✅ Good Description
```python
description = """
Create a Software-Defined Network with:

Components:
- 3 hosts: h1 (10.0.0.1/24), h2 (10.0.0.2/24), h3 (10.0.0.3/24)
- 1 OpenFlow switch: s1
- 1 OpenDaylight controller: c1 (IP: 192.168.1.100)

Topology:
- Connect h1, h2, h3 to s1
- Connect s1 to controller c1

Configuration:
- All nodes should be instantiated
- Use interface eth0 for host connections
"""
```

**Why it's good:**
- Specific component names
- Exact IP addresses
- Clear topology structure
- Explicit requirements

#### ❌ Poor Description
```python
description = "Make a network"
```

**Why it's poor:**
- Too vague
- No specifics
- Missing details

### Description Template

Use this template for best results:

```python
description = """
Create a [NETWORK TYPE] with:

Components:
- [Number] [Type]: [names] ([optional: IPs/configs])
- [repeat for each type]

Topology:
- [Connection 1]: [node A] to [node B]
- [Connection 2]: [node C] to [node D]
- [repeat for all connections]

Configuration:
- [Specific setting 1]
- [Specific setting 2]
- Always: Instantiate all nodes

Optional:
- [Any special requirements]
"""
```

### Code Organization

```python
# Organize your generation scripts

# 1. Imports
from profissa_lft import ModernAITopologyGenerator
import os
import time

# 2. Configuration
MODEL = "deepseek-r1"
OUTPUT_DIR = "generated_topologies"

# 3. Setup
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 4. Generator initialization (once)
generator = ModernAITopologyGenerator(model_name=MODEL)

# 5. Generation functions
def generate_scenario_1():
    # ...
    pass

def generate_scenario_2():
    # ...
    pass

# 6. Main execution
if __name__ == "__main__":
    generate_scenario_1()
    generate_scenario_2()
```

### Version Control

```python
import json
from datetime import datetime

def save_with_metadata(code, description, filename):
    """Save generated code with metadata"""
    
    # Save the code
    with open(filename, 'w') as f:
        f.write(code)
    
    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "description": description,
        "model": "deepseek-r1",
        "filename": filename,
        "lines": len(code.splitlines())
    }
    
    metadata_file = filename.replace('.py', '_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Saved: {filename}")
    print(f"✓ Metadata: {metadata_file}")
```

---

## Complete Example: End-to-End Workflow

```python
#!/usr/bin/env python3
"""
Complete Example: End-to-End AI Topology Generation
This script demonstrates the full workflow from description to execution
"""

from profissa_lft import ModernAITopologyGenerator
import os
import sys
import time
import json
from datetime import datetime

class LFTAIWorkflow:
    """Complete workflow for AI-powered topology generation"""
    
    def __init__(self, output_dir="generated_topologies"):
        self.output_dir = output_dir
        self.generator = None
        self.metadata = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def initialize_generator(self, model_name="deepseek-r1"):
        """Initialize the AI generator"""
        print("="*60)
        print("LFT AI Topology Generator - Complete Workflow")
        print("="*60)
        print(f"\n📦 Initializing {model_name} model...")
        print("   (This may take 30-60 seconds on first run)")
        
        start = time.time()
        self.generator = ModernAITopologyGenerator(
            model_name=model_name,
            load_in_8bit=True
        )
        elapsed = time.time() - start
        
        print(f"✓ Generator ready in {elapsed:.1f} seconds\n")
    
    def generate_topology(self, name, description):
        """Generate a single topology"""
        print(f"\n🎨 Generating: {name}")
        print(f"Description: {description.strip()[:100]}...")
        
        start = time.time()
        
        try:
            # Generate code
            code = self.generator.generate_topology(description)
            elapsed = time.time() - start
            
            # Validate syntax
            compile(code, '<string>', 'exec')
            
            # Save to file
            filename = os.path.join(self.output_dir, f"{name}.py")
            with open(filename, 'w') as f:
                f.write(code)
            
            # Record metadata
            metadata = {
                "name": name,
                "description": description.strip(),
                "filename": filename,
                "lines": len(code.splitlines()),
                "generated_at": datetime.now().isoformat(),
                "generation_time_seconds": elapsed,
                "status": "success"
            }
            self.metadata.append(metadata)
            
            print(f"✓ Generated in {elapsed:.1f}s")
            print(f"✓ Saved: {filename}")
            print(f"✓ Lines: {metadata['lines']}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            
            metadata = {
                "name": name,
                "description": description.strip(),
                "status": "failed",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
            self.metadata.append(metadata)
            
            return False
    
    def save_summary(self):
        """Save generation summary"""
        summary_file = os.path.join(self.output_dir, "generation_summary.json")
        
        summary = {
            "total_generated": len(self.metadata),
            "successful": len([m for m in self.metadata if m['status'] == 'success']),
            "failed": len([m for m in self.metadata if m['status'] == 'failed']),
            "topologies": self.metadata
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary saved: {summary_file}")
        return summary
    
    def print_summary(self):
        """Print generation summary"""
        print("\n" + "="*60)
        print("GENERATION SUMMARY")
        print("="*60)
        
        successful = [m for m in self.metadata if m['status'] == 'success']
        failed = [m for m in self.metadata if m['status'] == 'failed']
        
        print(f"\n✓ Successful: {len(successful)}")
        print(f"✗ Failed: {len(failed)}")
        
        if successful:
            print("\nGenerated topologies:")
            for m in successful:
                print(f"  • {m['name']}: {m['lines']} lines ({m['generation_time_seconds']:.1f}s)")
        
        if failed:
            print("\nFailed topologies:")
            for m in failed:
                print(f"  • {m['name']}: {m['error']}")
        
        print("="*60)


def main():
    """Main execution"""
    
    # Initialize workflow
    workflow = LFTAIWorkflow(output_dir="my_topologies")
    workflow.initialize_generator(model_name="deepseek-r1")
    
    # Define scenarios to generate
    scenarios = [
        {
            "name": "simple_sdn",
            "description": """
            Create a simple SDN network with:
            - 3 hosts (h1, h2, h3) with IPs 10.0.0.1/24, 10.0.0.2/24, 10.0.0.3/24
            - 1 switch (s1)
            - 1 controller (c1) at 192.168.1.100
            - Connect all hosts to switch
            - Instantiate all nodes
            """
        },
        {
            "name": "wireless_4g",
            "description": """
            Create a 4G wireless network with:
            - 2 UEs (ue1, ue2)
            - 1 eNodeB (enb1)
            - 1 EPC (epc1)
            - Connect UEs to eNodeB
            - Connect eNodeB to EPC
            - Instantiate all nodes
            """
        },
        {
            "name": "datacenter_spine_leaf",
            "description": """
            Create a spine-leaf datacenter topology with:
            - 2 spine switches (spine1, spine2)
            - 3 leaf switches (leaf1, leaf2, leaf3)
            - 6 servers (2 per leaf): srv1-srv6
            - Full mesh between spine and leaf layers
            - Servers connected to their respective leaf switches
            - All nodes instantiated
            """
        }
    ]
    
    # Generate all scenarios
    for scenario in scenarios:
        workflow.generate_topology(
            name=scenario['name'],
            description=scenario['description']
        )
    
    # Print and save summary
    workflow.print_summary()
    workflow.save_summary()
    
    print("\n✨ Workflow complete!")
    print(f"   Check the '{workflow.output_dir}' directory for generated topologies")


if __name__ == "__main__":
    main()
```

Save this as `complete_workflow.py` and run:

```bash
python complete_workflow.py
```

---

## Next Steps

### Continue Learning

1. **Experiment with models**: Try different models for different scenarios
2. **Iterate on descriptions**: Refine your prompts for better results
3. **Build templates**: Create reusable topology templates
4. **Integrate into workflows**: Use AI generation in your testing pipelines

### Resources

- **LFT Documentation**: Check `README.md` and `AI_README.md`
- **Examples**: Look in `examples/` directory
- **Test Scripts**: Review `test_ai_generator.py` and `test_new_ai.py`
- **Source Code**: Explore `profissa_lft/ai_generator.py`

### Community

- **GitHub**: [https://github.com/dcasseb/lft_ai](https://github.com/dcasseb/lft_ai)
- **Issues**: Report bugs or request features
- **Contributions**: PRs welcome!

---

## Appendix

### A. LFT Component Reference

| Component | Class | Purpose | Key Methods |
|-----------|-------|---------|-------------|
| Host | `Host` | Network endpoints | `setIp()`, `setDefaultGateway()` |
| Switch | `Switch` | OpenFlow switches | `connect()` |
| Controller | `Controller` | SDN controller | `instantiate()` |
| UE | `UE` | User Equipment (4G) | `connect()` |
| eNodeB | `EnB` | Base station (4G) | `connect()` |
| EPC | `EPC` | Core network (4G) | `addUE()`, `addEnB()` |

### B. Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `HF_TOKEN` | Hugging Face API token | `export HF_TOKEN="hf_xxx"` |
| `CUDA_VISIBLE_DEVICES` | GPU selection | `export CUDA_VISIBLE_DEVICES="0"` |
| `PYTORCH_CUDA_ALLOC_CONF` | CUDA memory config | `export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512` |

### C. Model Download Sizes

| Model | Download Size | Disk Space |
|-------|--------------|------------|
| DeepSeek-R1-0528 | ~15-30 GB | ~30 GB |
| Phi-3-mini | ~2.4 GB | ~5 GB |
| Stable Code 3B | ~3 GB | ~6 GB |
| Qwen2-7B | ~7 GB | ~14 GB |
| Code Llama 7B | ~7 GB | ~14 GB |

### D. Keyboard Shortcuts

When using interactive Python:
- `Ctrl+D`: Exit Python
- `Ctrl+C`: Interrupt execution
- `Ctrl+L`: Clear screen
- `↑/↓`: Command history

---

**Document Version:** 1.0  
**Last Updated:** October 2, 2025  
**Author:** LFT AI Team  
**License:** GPL-3.0

For questions or support, please open an issue on GitHub.

---
