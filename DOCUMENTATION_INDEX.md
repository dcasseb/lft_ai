# LFT AI Documentation Index
## Your Complete Guide to Using LLMs with Lightweight Fog Testbed

This directory contains comprehensive documentation for using Large Language Models (LLMs) with the Lightweight Fog Testbed (LFT) framework.

---

## 📚 Documentation Overview

### For Beginners: Start Here! ⭐

**[QUICK_START_LLM.md](QUICK_START_LLM.md)** - Get started in 5 minutes
- Installation (30 seconds)
- Your first AI topology (3 minutes)
- Common use cases with copy-paste code
- Quick troubleshooting

**Estimated time:** 5-10 minutes

### For Comprehensive Learning 📖

**[LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)** - Complete guide (600+ lines)
- Full installation and setup
- Architecture explanation
- 4 detailed tutorials
- Advanced usage patterns
- Model selection guide
- Best practices
- Troubleshooting
- Complete examples

**Estimated time:** 1-2 hours to read, lifetime value!

### For Hands-On Practice 💻

**[practical_examples.py](practical_examples.py)** - 10 ready-to-run examples
- Execute with: `python practical_examples.py`
- Generates real, working topologies
- Covers 10 different network scenarios
- Each example is fully documented

**Estimated time:** 30 seconds per example

### For Network Visualization 📊 ✨ NEW!

**[VISUALIZER_GUIDE.md](VISUALIZER_GUIDE.md)** - Real-time network visualization
- Live topology graphs
- CPU and memory monitoring
- Traffic flow visualization
- Quick start: `python visualize_network.py`

**Estimated time:** 2 minutes to start visualizing!

---

## Quick Start Guide

### Step 1: Activate Environment (10 seconds)
```bash
cd ~/UnB/lft_ai
source lft_env/bin/activate
```

### Step 2: Choose Your Path

#### Path A: Quick Start (Beginners)
```bash
# Read the quick start guide
cat QUICK_START_LLM.md

# Try your first topology
python << 'EOF'
from profissa_lft import ModernAITopologyGenerator
gen = ModernAITopologyGenerator()
code = gen.generate_topology("Create a network with 2 hosts and 1 switch")
open('my_first.py', 'w').write(code)
print("✓ Generated: my_first.py")
EOF
```

#### Path B: Practical Examples (Hands-On)
```bash
# Generate all 10 examples
python practical_examples.py

# Or generate just one
python practical_examples.py 1

# Run any generated topology
sudo python ai_generated_examples/01_basic_sdn_network.py
```

#### Path C: Deep Dive (Comprehensive)
```bash
# Read the full guide
less LLM_INTEGRATION_GUIDE.md

# Follow tutorials 1-4
# Build your own topologies
```

---

## What Each Document Covers

### QUICK_START_LLM.md
✓ Installation instructions  
✓ First topology in 3 minutes  
✓ 3 common use cases  
✓ Model selection basics  
✓ Quick troubleshooting  
✓ Ready-to-use templates  

**Best for:** Getting started quickly, quick reference

### LLM_INTEGRATION_GUIDE.md
✓ Complete prerequisites  
✓ Architecture deep-dive  
✓ Detailed installation  
✓ 4 comprehensive tutorials  
✓ Advanced usage patterns  
✓ All 6 supported models  
✓ Troubleshooting guide  
✓ Best practices  
✓ Complete workflow example  

**Best for:** Understanding the system, advanced usage, troubleshooting

### practical_examples.py
✓ 10 executable examples  
✓ Various network types  
✓ Production-ready code  
✓ Automatic generation  
✓ Metadata tracking  

**Best for:** Learning by example, quick prototyping, inspiration

---

## Use Case Guide

### "I'm completely new to LFT AI"
1. Read: `QUICK_START_LLM.md` (5 minutes)
2. Run: `python practical_examples.py 1` (generates basic example)
3. Examine: `ai_generated_examples/01_basic_sdn_network.py`
4. Read: `LLM_INTEGRATION_GUIDE.md` when ready for more

### "I need a specific topology now"
1. Run: `python practical_examples.py` (all examples)
2. Check: `ai_generated_examples/` directory
3. Find closest match and customize

### "I want to learn deeply"
1. Read: `LLM_INTEGRATION_GUIDE.md` (complete guide)
2. Follow: All 4 tutorials in order
3. Try: Advanced usage section
4. Experiment: Create your own topologies

### "I'm having problems"
1. Check: Troubleshooting section in `LLM_INTEGRATION_GUIDE.md`
2. Try: Quick fixes in `QUICK_START_LLM.md`
3. Review: Error messages and adjust prompts

### "I want to understand models"
1. Read: "Model Selection Guide" in `LLM_INTEGRATION_GUIDE.md`
2. Check: Comparison tables
3. Experiment: Try different models with same prompt

---

## Document Structure Comparison

| Feature | Quick Start | Complete Guide | Examples |
|---------|-------------|----------------|----------|
| **Length** | ~300 lines | ~600 lines | ~650 lines |
| **Read Time** | 5 min | 60+ min | Interactive |
| **Depth** | Overview | Comprehensive | Practical |
| **Code Examples** | 5 | 15+ | 10 complete |
| **Tutorials** | 0 | 4 detailed | 10 working |
| **Best For** | Quick start | Learning | Practice |

---

## Key Concepts Covered

### Models Available
- **DeepSeek-R1** (default): Best quality, advanced reasoning
- **Phi-3-mini**: Fast, balanced performance
- **Stable Code 3B**: Code-focused, very fast
- **Qwen2-7B**: General purpose
- **Code Llama 7B**: Code generation
- **Gemma2-9B**: High quality

### Network Types Covered
1. Basic SDN networks
2. 4G/LTE wireless networks
3. Redundant networks
4. Hierarchical networks
5. Datacenter topologies
6. Campus networks
7. IoT edge networks
8. Hybrid networks
9. Testing labs
10. Multi-controller SDN

### Skills You'll Learn
✓ Writing effective prompts for topology generation  
✓ Choosing the right model for your use case  
✓ Validating generated code  
✓ Troubleshooting common issues  
✓ Optimizing performance  
✓ Batch generation workflows  
✓ Template-based generation  
✓ Code organization best practices  

---

## Tips for Success

### Writing Good Prompts
```python
# ✅ GOOD: Specific and detailed
description = """
Create an SDN network with:
- 3 hosts: h1 (10.0.0.1/24), h2 (10.0.0.2/24), h3 (10.0.0.3/24)
- 1 switch: s1
- 1 controller: c1 at 192.168.1.100
- Connect all hosts to switch
- Instantiate all nodes
"""

# BAD: Too vague
description = "Make a network"
```

### Model Selection
- **Need quality?** → Use DeepSeek-R1 (default)
- **Need speed?** → Use Phi-3-mini
- **Need code?** → Use Stable Code 3B

### Common Pitfalls
1. Vague descriptions → ✅ Be specific
2. Missing IPs → ✅ Specify all IPs
3. No instantiation → ✅ Request .instantiate() calls
4. Unclear topology → ✅ Describe all connections

---

## Document Statistics

| Document | Lines | Words | Characters |
|----------|-------|-------|------------|
| QUICK_START_LLM.md | ~300 | ~3,000 | ~18,000 |
| LLM_INTEGRATION_GUIDE.md | ~600 | ~7,000 | ~45,000 |
| practical_examples.py | ~650 | ~4,000 | ~25,000 |
| **Total** | **~1,550** | **~14,000** | **~88,000** |

---

## Learning Paths

### Beginner Path (30 minutes)
1. Read `QUICK_START_LLM.md` → 5 min
2. Run first example → 5 min
3. Run `practical_examples.py 1` → 5 min
4. Examine generated code → 5 min
5. Try modifying and regenerating → 10 min

### Intermediate Path (2 hours)
1. Read `LLM_INTEGRATION_GUIDE.md` introduction → 15 min
2. Complete Tutorial 1 → 30 min
3. Complete Tutorial 2 → 30 min
4. Try 3 practical examples → 30 min
5. Create your own topology → 15 min

### Advanced Path (4+ hours)
1. Read entire `LLM_INTEGRATION_GUIDE.md` → 90 min
2. Complete all 4 tutorials → 90 min
3. Work through all practical examples → 60 min
4. Implement advanced patterns → 60+ min

---

## Prerequisites

### System Requirements
- **OS:** Linux (Ubuntu 20.04+)
- **Python:** 3.9+
- **RAM:** 8GB minimum, 16GB recommended
- **Disk:** 30GB for all models
- **GPU:** Optional (CUDA-compatible recommended)

### Software Requirements
✓ Python 3.9+  
✓ Virtual environment (lft_env)  
✓ torch, transformers, accelerate  
✓ Docker (for running topologies)  

### Knowledge Requirements
- Basic Python programming
- Basic networking concepts
- Linux command line basics

---

## Getting Help

### Built-in Resources
1. **Troubleshooting Section:** `LLM_INTEGRATION_GUIDE.md`
2. **Quick Fixes:** `QUICK_START_LLM.md`
3. **Example Code:** `practical_examples.py`

### Common Issues
- Model loading timeout → Normal! Wait 30-60s
- Out of memory → Use quantization (load_in_8bit=True)
- Bad generation → Improve prompt specificity
- Syntax errors → Validate and regenerate

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Quick Reference Commands

### Generate Topology
```bash
python << 'EOF'
from profissa_lft import ModernAITopologyGenerator
gen = ModernAITopologyGenerator()
code = gen.generate_topology("Your description")
open('output.py', 'w').write(code)
EOF
```

### Run Examples
```bash
python practical_examples.py        # All examples
python practical_examples.py 1      # Example 1 only
```

### Execute Topology
```bash
sudo python generated_topology.py
```

### Change Model
```python
gen = ModernAITopologyGenerator(model_name="phi3-mini")  # Faster
gen = ModernAITopologyGenerator(model_name="deepseek-r1")  # Better
```

---

## What Makes This Special

### Comprehensive Coverage
✓ Complete beginner to advanced path  
✓ Theory + practice combined  
✓ 10 working examples included  
✓ All 6 models documented  

### Production Ready
✓ Real, executable code  
✓ Best practices included  
✓ Error handling shown  
✓ Performance optimized  

### Educational Value
✓ Clear explanations  
✓ Step-by-step tutorials  
✓ Common pitfalls addressed  
✓ Learning paths provided  

---

## Additional Resources

### In This Repository
- `AI_README.md` - Original AI feature documentation
- `README.md` - Main LFT documentation
- `examples/` - Additional example topologies
- `test_ai_generator.py` - Test script
- `test_new_ai.py` - Modern test script

### External Resources
- LFT GitHub: https://github.com/dcasseb/lft_ai
- Hugging Face: https://huggingface.co/models
- Model documentation: See links in guide

---

## You're Ready!

You now have access to:
- ✅ Complete installation guide
- ✅ Quick start reference
- ✅ 4 detailed tutorials
- ✅ 10 practical examples
- ✅ Comprehensive documentation
- ✅ Model selection guide
- ✅ Troubleshooting help
- ✅ Best practices

**Next Step:** Choose your learning path and dive in!

```bash
# Beginners start here:
cat QUICK_START_LLM.md

# Comprehensive learners:
less LLM_INTEGRATION_GUIDE.md

# Hands-on learners:
python practical_examples.py
```

---

**Happy topology generation!**

*Documentation created: October 2, 2025*  
*Default Model: DeepSeek-R1-0528*  
*Total Documentation: ~1,550 lines*
