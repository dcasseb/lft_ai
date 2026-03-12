# LFT Network Visualizer Guide
## Real-Time Graph Visualization for Emulated Networks

**Version:** 1.1
**Date:** March 12, 2026
**Features:** Real-time topology visualization, live statistics, traffic monitoring, static file visualization, Podman support

---

## Overview

The LFT Network Visualizer provides real-time graphical visualization of your running network topologies. It displays:

- **Network Topology**: Visual graph showing all nodes and connections
- **Live Statistics**: CPU and memory usage for each container
- **Traffic Monitoring**: Real-time network throughput graphs
- **Latency Monitoring**: RTT/latency between node pairs
- **Status Indicators**: Visual health status for each node
- **Static Visualization**: Render topology graphs from generated `.py` files
- **Podman Support**: Works with both Docker and Podman container runtimes

---

## Installation

### Prerequisites

```bash
# Activate your LFT environment
cd lft_ai
source lft_ai/bin/activate  # or your virtual environment name
```

### Install Dependencies

```bash
# Install visualization dependencies
pip install matplotlib networkx docker

# Or install from requirements
pip install -r requirements_visualizer.txt
```

---

## Quick Start

### Step 1: Run a Network Topology

First, you need a running LFT topology. Here's a simple example:

```python
# Save as: simple_topology.py
from profissa_lft import Host, Switch, Controller

# Create nodes
h1 = Host('h1')
h2 = Host('h2')
s1 = Switch('s1')
c1 = Controller('c1')

# Instantiate
h1.instantiate()
h2.instantiate()
s1.instantiate()
c1.instantiate()

# Configure IPs
h1.setIp('10.0.0.1', 24, 'eth0')
h2.setIp('10.0.0.2', 24, 'eth0')

# Connect nodes
h1.connect(s1, 'eth0', 's1-eth1')
h2.connect(s1, 'eth0', 's1-eth2')

print("Network running! Press Ctrl+C to stop.")
input()  # Keep running
```

Run it:
```bash
sudo python simple_topology.py
```

### Step 2: Start the Visualizer

In a **new terminal**:

```bash
source lft_ai/bin/activate  # or your virtual environment name
python lft_ai_standalone.py visualize
```

That's it! The visualization window will open showing your network in real-time.

---

## Features

### 1. Network Topology View

The main panel shows:
- **Nodes**: Colored circles representing network components
  - 🟢 Green: Hosts
  - 🔵 Blue: Switches
  - 🟠 Orange: Controllers
  - 🟣 Purple: User Equipment (UE)
  - 🔴 Red: EPC
  - 🩷 Pink: eNodeB

- **Connections**: Lines showing network links
- **Status Indicators**: Small dots showing running (green) or stopped (red) status
- **Labels**: Node names clearly displayed

### 2. CPU Usage Graph

Bottom-left panel shows:
- Real-time CPU usage percentage for each container
- Color-coded per node type
- Historical data (last 100 samples)
- Auto-scaling Y-axis

### 3. Network Traffic Graph

Bottom-left (second row, right) panel shows:
- Real-time network throughput in KB/s
- Combined RX/TX traffic
- Color-coded per node

### 4. Memory Usage Graph

Tracks memory consumption (in MB) per container in real-time.

### 5. Latency Graph

Bottom-right panel shows:
- RTT/latency between node pairs (in ms)
- Measured via ping between containers

---

## Usage Examples

### Example 1: Visualize Simple SDN Network

```bash
# Terminal 1: Run topology
sudo python examples/simpleSDNTopology.py

# Terminal 2: Visualize
python lft_ai_standalone.py visualize
```

### Example 2: Visualize 4G Network

```bash
# Terminal 1: Run topology
sudo python examples/simple4GTopology.py

# Terminal 2: Visualize  
python lft_ai_standalone.py visualize
```

### Example 3: Static Visualization from File

You can visualize a generated topology `.py` file without running containers:

```bash
# Visualize a generated topology file
python lft_ai_standalone.py visualize --file topology.py
```

This parses the Python file, extracts nodes and connections, and renders a static graph.

### Example 4: Visualize AI-Generated Topology

```bash
# Terminal 1: Generate and run
python << 'EOF'
from profissa_lft import ModernAITopologyGenerator
gen = ModernAITopologyGenerator()
code = gen.generate_topology("""
Create a network with:
- 4 hosts: h1-h4 with IPs 10.0.0.1-4/24
- 2 switches: s1, s2
- 1 controller: c1
- Hosts h1,h2 on s1, h3,h4 on s2
- Both switches connected to controller
""")
open('generated.py', 'w').write(code)
print("Generated! Run with: sudo python generated.py")
EOF

sudo python generated.py

# Terminal 2: Visualize
python lft_ai_standalone.py visualize
```

---

## Advanced Usage

### Custom Update Interval

```bash
# Update every 500ms (faster, more CPU)
python lft_ai_standalone.py visualize --interval 500

# Update every 2 seconds (slower, less CPU)
python lft_ai_standalone.py visualize --interval 2000
```

### Programmatic Usage

```python
from profissa_lft.visualizer import NetworkVisualizer

# Create visualizer with custom interval
visualizer = NetworkVisualizer(update_interval=1000)

# Start visualization
visualizer.start()

# The visualizer will run until window is closed
```

### Integration with Existing Code

```python
#!/usr/bin/env python3
"""Example: Topology with integrated visualizer"""

import threading
from profissa_lft import Host, Switch
from profissa_lft.visualizer import NetworkVisualizer

# Create topology
h1 = Host('h1')
h2 = Host('h2')
s1 = Switch('s1')

h1.instantiate()
h2.instantiate()
s1.instantiate()

h1.setIp('10.0.0.1', 24, 'eth0')
h2.setIp('10.0.0.2', 24, 'eth0')

h1.connect(s1, 'eth0', 's1-eth1')
h2.connect(s1, 'eth0', 's1-eth2')

print("Network running!")

# Start visualizer in background
visualizer = NetworkVisualizer()
viz_thread = threading.Thread(target=visualizer.start)
viz_thread.daemon = True
viz_thread.start()

# Keep running
try:
    input("Press Enter to stop...\n")
except KeyboardInterrupt:
    pass

print("Stopping...")
```

---

## Understanding the Visualization

### Node Colors and Types

| Color | Type | Description |
|-------|------|-------------|
| 🟢 Green | Host | Network endpoints/clients |
| 🔵 Blue | Switch | OpenFlow switches |
| 🟠 Orange | Controller | SDN controllers |
| 🟣 Purple | UE | User Equipment (4G) |
| 🔴 Red | EPC | Evolved Packet Core |
| 🩷 Pink | eNodeB | Base station (4G) |
| ⚫ Gray | Unknown | Unclassified nodes |

### Status Indicators

- **Green dot**: Container running normally
- **Red dot**: Container stopped or error

### Graph Layout

The visualizer uses a spring layout algorithm that:
- Automatically arranges nodes for optimal viewing
- Minimizes edge crossings
- Groups related nodes together
- Updates dynamically as topology changes

---

## Troubleshooting

### Issue: "No network detected"

**Solution:**
1. Make sure your topology is running: `sudo docker ps`
2. Verify containers are created by LFT
3. Restart the visualizer after starting the topology

### Issue: "matplotlib not available"

**Solution:**
```bash
pip install matplotlib
```

### Issue: "docker not available"

**Solution:**
```bash
pip install docker
```

### Issue: Visualization window not responding

**Solution:**
1. Close the window
2. Check terminal for errors
3. Restart with Ctrl+C and rerun

### Issue: High CPU usage

**Solution:**
```bash
# Increase update interval to reduce CPU
python lft_ai_standalone.py visualize --interval 2000
```

### Issue: Statistics not updating

**Solution:**
1. Verify Docker daemon is running: `sudo systemctl status docker`
2. Check container stats manually: `docker stats`
3. Ensure your user has Docker permissions

### Issue: Using Podman instead of Docker

**Solution:**
The visualizer supports Podman via the Docker-compatible API. Set the `DOCKER_HOST` environment variable:

```bash
# Start Podman socket
systemctl --user start podman.socket

# Run visualizer with Podman
DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock python lft_ai_standalone.py visualize
```

You may also need to configure short image names:
```bash
# Create registries config for Podman
mkdir -p ~/.config/containers
echo 'unqualified-search-registries = ["docker.io"]' > ~/.config/containers/registries.conf
```

---

## Performance Tips

1. **Adjust Update Interval**: Higher intervals (e.g., 2000ms) reduce CPU usage
2. **Close When Not Needed**: Visualizer uses resources even when idle
3. **Limit History**: Modify `maxlen` in visualizer code for less memory usage
4. **Use with Moderate Topologies**: Best with <20 nodes for smooth performance

---

## Features in Detail

### Auto-Discovery

The visualizer automatically:
- Detects running Docker containers
- Identifies node types by naming convention
- Discovers connections between nodes
- Updates when topology changes

### Real-Time Metrics

Collected metrics:
- **CPU Usage**: Percentage of CPU used by each container
- **Memory Usage**: Percentage and absolute memory used
- **Network I/O**: Bytes received and transmitted
- **Throughput**: Calculated as delta bytes / delta time

### Graph Updates

The visualization updates:
- Topology: Every 10 frames (~10 seconds with 1s interval)
- Statistics: Every frame (1 second by default)
- Traffic: Calculated from consecutive samples

---

## Integration with LFT AI

You can generate and visualize topologies in one workflow:

```python
#!/usr/bin/env python3
"""Generate, run, and visualize a topology"""

import subprocess
import time
from profissa_lft import ModernAITopologyGenerator
from profissa_lft.visualizer import NetworkVisualizer

# Generate topology
print("🤖 Generating topology with AI...")
gen = ModernAITopologyGenerator()
code = gen.generate_topology("""
Create a datacenter topology with:
- 2 spine switches
- 3 leaf switches  
- 6 servers (2 per leaf)
- Full mesh between spine and leaf
""")

# Save
with open('datacenter.py', 'w') as f:
    f.write(code)

print("✓ Topology generated: datacenter.py")

# Run in background
print("🚀 Starting topology...")
proc = subprocess.Popen(['sudo', 'python', 'datacenter.py'])
time.sleep(5)  # Wait for containers to start

# Visualize
print("📊 Starting visualizer...")
visualizer = NetworkVisualizer()
visualizer.start()

# Cleanup
print("🧹 Cleaning up...")
proc.terminate()
```

---

## Command Reference

### Basic Commands

```bash
# Start live visualizer (monitors running containers)
python lft_ai_standalone.py visualize

# Visualize a topology file (static graph, no containers needed)
python lft_ai_standalone.py visualize --file topology.py

# Custom update interval
python lft_ai_standalone.py visualize --interval 2000

# Export telemetry data
python lft_ai_standalone.py visualize --export-csv metrics.csv
python lft_ai_standalone.py visualize --export-json metrics.json

# Get help
python lft_ai_standalone.py visualize --help
```

### Docker Commands (for debugging)

```bash
# List running containers
sudo docker ps

# Check container stats
sudo docker stats

# Inspect network
sudo docker network ls
sudo docker network inspect <network_name>
```

---

## Keyboard Shortcuts

When visualization window is active:

- **Close Window**: Stop visualizer
- **Ctrl+C** (terminal): Force stop
- **Mouse**: Pan/zoom (if enabled in matplotlib config)

---

## Future Enhancements

Planned features:
- [ ] Interactive node selection
- [ ] Detailed node information on click
- [ ] Traffic flow animation
- [ ] Export topology to image
- [ ] Save statistics to CSV
- [ ] Alert on threshold violations
- [ ] Packet capture integration
- [ ] Multi-topology comparison

---

## Examples Gallery

### Basic SDN Network
```
┌────────┐     ┌────────┐
│   h1   │────▶│   s1   │◀────┐
└────────┘     └────┬───┘     │
                    │         │
┌────────┐          │    ┌────────┐
│   h2   │──────────┘    │   c1   │
└────────┘               └────────┘
```

### 4G Wireless Network
```
┌────────┐     ┌────────┐     ┌────────┐
│  ue1   │────▶│  enb1  │────▶│  epc1  │
└────────┘     └────┬───┘     └────────┘
                    │
┌────────┐          │
│  ue2   │──────────┘
└────────┘
```

### Datacenter Topology
```
          ┌───────┐   ┌───────┐
          │spine1 │   │spine2 │
          └───┬───┘   └───┬───┘
              │ \   / │   │
              │  \ /  │   │
              │  / \  │   │
              │ /   \ │   │
          ┌───┴───┬───┴───┬───────┐
          │leaf1  │leaf2  │leaf3  │
          └───┬───┴───┬───┴───┬───┘
              │       │       │
        ┌─────┴──┐ ┌──┴────┐ └─────┬──┐
        │srv1-2  │ │srv3-4 │       │srv5-6│
        └────────┘ └───────┘       └──────┘
```

---

## FAQ

**Q: Can I visualize topologies running on remote machines?**  
A: Currently, the visualizer connects to the local Docker daemon. For remote visualization, you can configure Docker to accept remote connections or use SSH tunneling.

**Q: Does it work with Mininet topologies?**  
A: The visualizer is designed for LFT (containerized) topologies. Mininet uses network namespaces differently and would need a separate visualizer.

**Q: Can I customize the colors?**  
A: Yes! Edit `node_type_colors` dictionary in `profissa_lft/visualizer.py`.

**Q: How much overhead does visualization add?**  
A: Minimal. The visualizer runs in a separate process and queries Docker stats API, which has negligible performance impact.

**Q: Can I visualize multiple topologies simultaneously?**  
A: The current version shows all running LFT containers in one view. For separate visualizations, you'd need multiple visualizer instances with filtering logic.

---

## Technical Details

### Architecture

```
┌─────────────────────────────────────────┐
│        NetworkVisualizer                │
│  ┌───────────────────────────────────┐  │
│  │  Topology Detection               │  │
│  │  - Docker API                     │  │
│  │  - Container discovery            │  │
│  │  - Connection inference           │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Statistics Collection            │  │
│  │  - CPU/Memory monitoring          │  │
│  │  - Network I/O tracking           │  │
│  │  - Historical data storage        │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Visualization                    │  │
│  │  - NetworkX graph layout          │  │
│  │  - Matplotlib rendering           │  │
│  │  - Real-time animation            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Dependencies

- **matplotlib**: Plotting and visualization
- **networkx**: Graph data structures and algorithms
- **docker**: Docker API client
- **Python 3.9+**: Core language features

### Data Flow

1. **Discovery**: Query Docker for running containers
2. **Classification**: Identify node types from names
3. **Connection Mapping**: Infer connections from network bridges
4. **Statistics Gathering**: Collect real-time metrics via Docker stats API
5. **Rendering**: Update matplotlib figure with new data
6. **Loop**: Repeat at configured interval

---

## Conclusion

The LFT Network Visualizer provides an intuitive, real-time view of your emulated networks. Use it to:

- **Debug**: Quickly identify topology issues
- **Monitor**: Track resource usage and traffic
- **Demonstrate**: Show network behavior visually
- **Learn**: Understand network topology and dynamics

For questions or issues, please open an issue on GitHub!

---

**Version:** 1.1
**Last Updated:** March 12, 2026
**Maintainer:** Profissa - UnB
