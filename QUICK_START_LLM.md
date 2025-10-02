# LFT AI Quick Start Guide
## Get Started in 5 Minutes

**Default Model:** DeepSeek-R1-0528 (Already cached locally!)

---

## Installation (30 seconds)

```bash
cd ~/UnB/lft_ai
source lft_env/bin/activate  # Activate virtual environment
```

That's it! All dependencies are already installed.

---

## Your First AI Topology (3 minutes)

### Step 1: Create a Script

```python
# Save as: my_first_ai_topology.py
from profissa_lft import ModernAITopologyGenerator

# Initialize (takes ~30-60 seconds)
print("Loading AI model...")
gen = ModernAITopologyGenerator()

# Generate
print("Generating topology...")
code = gen.generate_topology("""
Create a simple network with:
- 2 hosts: h1 (10.0.0.1/24), h2 (10.0.0.2/24)
- 1 switch: s1
- Connect both hosts to switch
- Instantiate all nodes
""")

# Save
with open('my_topology.py', 'w') as f:
    f.write(code)

print("✓ Done! Saved to my_topology.py")
```

### Step 2: Run It

```bash
python my_first_ai_topology.py
```

### Step 3: Execute Your Topology

```bash
sudo python my_topology.py
```

---

## Common Use Cases

### Use Case 1: Simple SDN Network

```python
from profissa_lft import ModernAITopologyGenerator

gen = ModernAITopologyGenerator()
code = gen.generate_topology("""
Create an SDN network with:
- 3 hosts with IPs 10.0.0.1/24, 10.0.0.2/24, 10.0.0.3/24
- 1 switch
- 1 OpenDaylight controller at 192.168.1.100
""")

open('sdn_network.py', 'w').write(code)
```

### Use Case 2: 4G Wireless Network

```python
from profissa_lft import ModernAITopologyGenerator

gen = ModernAITopologyGenerator()
code = gen.generate_topology("""
Create a 4G network with:
- 2 User Equipment (ue1, ue2)
- 1 eNodeB (enb1)
- 1 EPC (epc1)
""")

open('4g_network.py', 'w').write(code)
```

### Use Case 3: Data Center Topology

```python
from profissa_lft import ModernAITopologyGenerator

gen = ModernAITopologyGenerator()
code = gen.generate_topology("""
Create a spine-leaf datacenter with:
- 2 spine switches
- 3 leaf switches
- 6 servers (2 per leaf)
- Full mesh between spine and leaf
""")

open('datacenter.py', 'w').write(code)
```

---

## Model Selection

### Fast Mode (Phi-3)

```python
gen = ModernAITopologyGenerator(model_name="phi3-mini")
```
- ⚡ Fast (~15s initialization)
- ✓ Good for quick prototyping
- ✓ Lower memory usage

### Best Quality (DeepSeek - Default)

```python
gen = ModernAITopologyGenerator(model_name="deepseek-r1")
```
- 🎯 Best reasoning
- ✓ Complex topologies
- ⏱️ Slower (~60s initialization)

### Code-Focused (Stable Code)

```python
gen = ModernAITopologyGenerator(model_name="stable-code-3b")
```
- ⚡ Very fast
- ✓ Clean code
- ✓ Good syntax

---

## Tips for Better Results

### ✅ Good Prompt
```python
description = """
Create a network with:
- 3 hosts: h1 (10.0.0.1/24), h2 (10.0.0.2/24), h3 (10.0.0.3/24)
- 1 switch: s1
- 1 controller: c1 at 192.168.1.100
- Connect all hosts to switch
- Instantiate all components
"""
```

**Why:** Specific, clear, detailed

### ❌ Poor Prompt
```python
description = "Make a network"
```

**Why:** Too vague

---

## Troubleshooting

### Problem: Script hangs during initialization

**Solution:** This is normal! Models take 30-60s to load.

```python
# If you want faster initialization:
gen = ModernAITopologyGenerator(model_name="phi3-mini")
```

### Problem: Out of memory

**Solution:** Use quantization

```python
gen = ModernAITopologyGenerator(load_in_4bit=True)
```

### Problem: Generated code has errors

**Solution:** Be more specific in your description

```python
# Add more details:
description = """
Using LFT framework components:
- Use Host() class for hosts
- Use Switch() class for switches  
- Call .instantiate() on all nodes
- Use .connect() to link nodes
- Use .setIp() for IP configuration

Create: [your specific topology]
"""
```

---

## Complete Example Template

Save this as `generate_template.py`:

```python
#!/usr/bin/env python3
"""Template for generating LFT topologies with AI"""

from profissa_lft import ModernAITopologyGenerator
import sys

def main():
    # Configuration
    MODEL = "deepseek-r1"  # or "phi3-mini" for speed
    OUTPUT_FILE = "generated_topology.py"
    
    # Your topology description
    DESCRIPTION = """
    Create a network with:
    - [Number] hosts: [names] with IPs [IPs]
    - [Number] switches: [names]
    - [Optional: controllers, wireless components, etc.]
    - Connection topology: [describe connections]
    - Instantiate all nodes
    """
    
    # Initialize generator
    print(f"Initializing {MODEL} model...")
    gen = ModernAITopologyGenerator(model_name=MODEL)
    print("✓ Ready!\n")
    
    # Generate
    print(f"Generating topology...")
    print(f"Description: {DESCRIPTION.strip()[:100]}...\n")
    
    try:
        code = gen.generate_topology(DESCRIPTION)
        
        # Save
        with open(OUTPUT_FILE, 'w') as f:
            f.write(code)
        
        print(f"✓ Success!")
        print(f"✓ Saved to: {OUTPUT_FILE}")
        print(f"✓ Lines: {len(code.splitlines())}")
        print(f"\nNext step: sudo python {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Customize the `DESCRIPTION` and run:

```bash
python generate_template.py
```

---

## Quick Reference

### Import
```python
from profissa_lft import ModernAITopologyGenerator
```

### Initialize
```python
gen = ModernAITopologyGenerator()  # Uses DeepSeek-R1
```

### Generate
```python
code = gen.generate_topology("Your description here")
```

### Save
```python
with open('output.py', 'w') as f:
    f.write(code)
```

### Execute
```bash
sudo python output.py
```

---

## Available Models

| Model | Speed | Quality | Use When |
|-------|-------|---------|----------|
| `deepseek-r1` | ⭐⭐ | ⭐⭐⭐⭐⭐ | Need best quality |
| `phi3-mini` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Need speed |
| `stable-code-3b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Need clean code |

---

## Next Steps

1. **Read full guide**: `LLM_INTEGRATION_GUIDE.md`
2. **Try examples**: `examples/` directory
3. **Run tests**: `test_new_ai.py`
4. **Experiment**: Try different models and prompts!

---

## Common Questions

**Q: How long does initialization take?**  
A: 30-60 seconds for DeepSeek, 15-30s for Phi-3

**Q: Can I use multiple models?**  
A: Yes! Create separate generator instances

**Q: Is Internet required?**  
A: No! All models are cached locally

**Q: How much memory needed?**  
A: 8GB minimum, 16GB+ recommended

**Q: Can I interrupt generation?**  
A: Yes, use Ctrl+C

---

**Quick Start Guide v1.0**  
**October 2, 2025**

For detailed information, see: `LLM_INTEGRATION_GUIDE.md`
