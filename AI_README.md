# LFT AI Topology Generator

The Lightweight Fog Testbed (LFT) now includes AI-powered topology generation capabilities using the **deepseek-ai/DeepSeek-R1-0528** model. This feature allows you to generate complex network topologies from natural language descriptions, similar to OpenSUMO's approach.

## Features

- 🤖 **AI-Powered Generation**: Uses DeepSeek-R1-0528 for intelligent topology creation
- 🌐 **Multiple Deployment Options**: Support for both Hugging Face API and local model inference
- 🎯 **Specialized Training**: Model trained specifically on LFT components and patterns
- 🔧 **Code Validation**: Built-in validation of generated topology code
- 💻 **CLI Interface**: Easy-to-use command-line tools
- 📝 **Interactive Mode**: Real-time topology generation with immediate feedback
- 🐍 **Programmatic API**: Full Python API for integration into existing workflows

## Installation

### Prerequisites

1. **Python 3.9+** (required for LFT)
2. **Hugging Face Account** (for API access)
3. **Optional**: GPU with CUDA support (for local model inference)

### Setup

1. **Install LFT with AI dependencies**:
   ```bash
   pip3 install profissa_lft
   ```

2. **Get Hugging Face API Token**:
   - Visit [Hugging Face](https://huggingface.co/settings/tokens)
   - Create a new token with read permissions
   - Set environment variable:
     ```bash
     export HF_TOKEN="your_token_here"
     ```

3. **For Local Model Usage** (Optional):
   ```bash
   # Install additional dependencies for local inference
   pip3 install torch transformers accelerate
   ```

## Quick Start

### Command Line Interface

1. **Generate a simple topology**:
   ```bash
   lft-ai generate "Create a simple SDN topology with 2 hosts connected to a switch" -o my_topology.py
   ```

2. **Interactive mode**:
   ```bash
   lft-ai interactive
   ```

3. **View examples**:
   ```bash
   lft-ai examples
   ```

### Programmatic Usage

```python
from profissa_lft.ai_generator import AITopologyGenerator

# Initialize generator
generator = AITopologyGenerator(
    model_name="deepseek-ai/DeepSeek-R1-0528",
    use_hf_api=True,  # Use Hugging Face API
    api_token="your_token_here"
)

# Generate topology
description = "Create a 4G wireless network with 3 UEs connected to an eNodeB and EPC"
generated_code = generator.generate_topology(description)

# Save to file
generator.generate_and_save(description, "wireless_network.py")

# Validate code
if generator.validate_topology(generated_code):
    print("Generated code is valid!")
```

## Usage Examples

### Example 1: Simple SDN Topology

**Description**: "Create a simple SDN topology with 2 hosts connected to a switch"

**Generated Code**:
```python
from profissa_lft.host import Host
from profissa_lft.switch import Switch

h1 = Host('h1')
h2 = Host('h2')
s1 = Switch('s1')

h1.instantiate()
h2.instantiate()
s1.instantiate()

h1.connect(s1, "h1s1", "s1h1")
h2.connect(s1, "h2s1", "s1h2")

h1.setIp('10.0.0.1', 24, "h1s1")
h2.setIp('10.0.0.2', 24, "h2s1")

s1.connectToInternet('10.0.0.4', 24, "s1host", "hosts1")

h1.setDefaultGateway('10.0.0.4', "h1s1")
h2.setDefaultGateway('10.0.0.4', "h2s1")
```

### Example 2: 4G Wireless Network

**Description**: "Create a 4G wireless network with 2 UEs connected to an eNodeB and EPC"

**Generated Code**:
```python
from profissa_lft.ue import UE
from profissa_lft.enb import EnB
from profissa_lft.epc import EPC

ue1 = UE('ue1')
ue2 = UE('ue2')
enb = EnB('enb1')
epc = EPC('epc1')

ue1.instantiate()
ue2.instantiate()
enb.instantiate()
epc.instantiate()

ue1.connect(enb, "ue1enb", "enblue1")
ue2.connect(enb, "ue2enb", "enblue2")
enb.connect(epc, "enbs1", "s1enb")

ue1.setIp('192.168.1.10', 24, "ue1enb")
ue2.setIp('192.168.1.11', 24, "ue2enb")
enb.setIp('192.168.1.1', 24, "enblue1")
enb.setIp('192.168.1.2', 24, "enblue2")
enb.setIp('10.0.0.1', 24, "enbs1")
epc.setIp('10.0.0.2', 24, "s1enb")

epc.connectToInternet('10.0.0.4', 24, "epchost", "hostepc")

ue1.setDefaultGateway('192.168.1.1', "ue1enb")
ue2.setDefaultGateway('192.168.1.1', "ue2enb")
enb.setDefaultGateway('10.0.0.2', "enbs1")
epc.setDefaultGateway('10.0.0.4', "epchost")
```

## CLI Reference

### Commands

#### `generate`
Generate topology from description:
```bash
lft-ai generate "description" [options]
```

**Options**:
- `-o, --output FILE`: Output file path
- `--local`: Use local model instead of API
- `--model MODEL`: Model name (default: deepseek-ai/DeepSeek-R1-0528)
- `--token TOKEN`: Hugging Face API token
- `--validate`: Validate generated code
- `-v, --verbose`: Verbose output

#### `interactive`
Start interactive mode:
```bash
lft-ai interactive [options]
```

**Options**:
- `--local`: Use local model instead of API
- `--model MODEL`: Model name
- `--token TOKEN`: Hugging Face API token
- `-v, --verbose`: Verbose output

#### `examples`
Show example topology descriptions:
```bash
lft-ai examples
```

### Interactive Mode Commands

- `quit`: Exit interactive mode
- `help`: Show examples
- `clear`: Clear screen

## API Reference

### AITopologyGenerator

#### Constructor
```python
AITopologyGenerator(
    model_name="deepseek-ai/DeepSeek-R1-0528",
    use_hf_api=True,
    api_token=None
)
```

#### Methods

##### `generate_topology(description: str) -> str`
Generate LFT topology code from natural language description.

**Parameters**:
- `description`: Natural language description of the desired topology

**Returns**: Generated Python code for the LFT topology

##### `generate_and_save(description: str, output_file: str) -> str`
Generate topology code and save it to a file.

**Parameters**:
- `description`: Natural language description of the desired topology
- `output_file`: Path to save the generated code

**Returns**: Path to the saved file

##### `validate_topology(code: str) -> bool`
Validate the generated topology code.

**Parameters**:
- `code`: Python code to validate

**Returns**: True if valid, False otherwise

## Configuration

### Environment Variables

- `HF_TOKEN`: Hugging Face API token (required for API usage)

### Model Configuration

The AI generator supports both Hugging Face API and local model inference:

#### Hugging Face API (Recommended)
- **Pros**: No local resources required, always up-to-date model
- **Cons**: Requires internet connection, API rate limits
- **Setup**: Set `HF_TOKEN` environment variable

#### Local Model
- **Pros**: No internet required, no rate limits, faster inference
- **Cons**: Requires significant disk space (~35GB), GPU recommended
- **Setup**: Install `torch`, `transformers`, `accelerate`

## Supported Topology Types

The AI generator can create various network topologies:

1. **SDN Topologies**
   - Simple host-switch configurations
   - Multi-switch networks
   - Controller-based SDN setups

2. **Wireless Networks**
   - 4G LTE networks (UE → eNodeB → EPC)
   - Multi-UE configurations
   - Wireless backhaul networks

3. **Fog Computing Networks**
   - Edge node configurations
   - Fog-to-cloud connectivity
   - IoT gateway setups

4. **Enterprise Networks**
   - VLAN configurations
   - Multi-tier architectures
   - Gateway and firewall setups

## Best Practices

### Writing Effective Descriptions

1. **Be Specific**: Include number of devices and connection types
   ```
   Good: "Create a network with 3 hosts, 2 switches, and 1 controller"
   Bad: "Create a network"
   ```

2. **Specify Technologies**: Mention specific technologies when needed
   ```
   Good: "Create a 4G wireless network with UEs, eNodeB, and EPC"
   Bad: "Create a wireless network"
   ```

3. **Include Requirements**: Mention specific requirements
   ```
   Good: "Create an SDN topology with OpenFlow switches and ONOS controller"
   Bad: "Create an SDN topology"
   ```

### Error Handling

```python
from profissa_lft.ai_generator import AITopologyGenerator
from profissa_lft.exceptions import LFTException

try:
    generator = AITopologyGenerator()
    code = generator.generate_topology("Create a simple network")
    print("Success!")
except LFTException as e:
    print(f"LFT Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Troubleshooting

### Common Issues

1. **API Token Not Set**
   ```
   Error: Hugging Face API token required
   Solution: Set HF_TOKEN environment variable
   ```

2. **Model Loading Failed**
   ```
   Error: Failed to setup model
   Solution: Check internet connection or use local model
   ```

3. **Generated Code Invalid**
   ```
   Error: Generated code validation failed
   Solution: Try a more specific description or check LFT syntax
   ```

4. **Local Model Out of Memory**
   ```
   Error: CUDA out of memory
   Solution: Use smaller model or enable CPU inference
   ```

### Performance Optimization

1. **For API Usage**:
   - Use concise descriptions
   - Implement retry logic for rate limits
   - Cache generated topologies

2. **For Local Usage**:
   - Use GPU if available
   - Enable model quantization
   - Use smaller model variants

## Examples Directory

Check the `examples/` directory for complete working examples:

- `ai_generated_topology.py`: Programmatic usage example
- `simpleSDNTopology.py`: Manual topology creation
- `simple4GTopology.py`: 4G network example

## Contributing

To contribute to the AI features:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review existing examples
3. Open an issue on GitHub
4. Contact the maintainers

---

**Note**: The AI generator is designed to assist with topology creation but should be reviewed before deployment in production environments. 