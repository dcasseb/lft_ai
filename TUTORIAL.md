# LFT AI - Complete Tutorial
## GUI, CLI, Visualization & Data Access

**Version:** 1.0 | **Date:** March 2026 | **Maintainer:** Profissa - UnB

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [GUI Mode (`lft-gui`)](#2-gui-mode)
   - [AI Generator Tab](#21-ai-generator-tab)
   - [Topology Builder Tab](#22-topology-builder-tab)
   - [Experiments Tab](#23-experiments-tab)
   - [Results Tab](#24-results-tab)
   - [Monitoring Tab](#25-monitoring-tab)
3. [CLI / Standalone Mode (`lft-ai`)](#3-cli--standalone-mode)
   - [Generate Topologies](#31-generate-topologies)
   - [Interactive Mode](#32-interactive-mode)
   - [View Examples](#33-view-examples)
   - [Standalone Script](#34-standalone-script)
4. [Visualization](#4-visualization)
   - [Live Monitoring (Running Containers)](#41-live-monitoring)
   - [Static Visualization (From File)](#42-static-visualization)
   - [Programmatic Visualization](#43-programmatic-visualization)
5. [Accessing Simulation Data](#5-accessing-simulation-data)
   - [Experiment Results (JSON)](#51-experiment-results-json)
   - [Telemetry Data (CSV/JSON)](#52-telemetry-data)
   - [Analyzing Results](#53-analyzing-results)
6. [Programmatic Python API](#6-programmatic-python-api)
7. [Model Selection Guide](#7-model-selection-guide)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

```bash
# 1. Python 3.9+ required
python3 --version

# 2. Install LFT
pip3 install profissa_lft

# 3. Docker (or Podman) must be running
sudo systemctl start docker

# 4. For AI features, install model dependencies
pip3 install torch transformers accelerate

# 5. For visualization features
pip3 install matplotlib networkx docker

# 6. (Optional) Hugging Face API token for remote inference
export HF_TOKEN="your_token_here"
```

---

## 2. GUI Mode

Launch the graphical interface:

```bash
lft-gui
# or directly:
python3 lft_gui.py
```

The GUI opens a window with five tabs and a shared console output panel at the bottom.

### 2.1 AI Generator Tab

This tab lets you describe a network in natural language and have an AI model generate the LFT Python code.

**Step-by-step:**

1. **Write a description** in the text area on the left. Be specific:
   ```
   Create a simple SDN topology with 2 hosts connected to a switch
   ```

2. **Choose a model** from the "Model" dropdown. Default is DeepSeek-R1 (best quality). For faster results, select Phi-3 Mini or Stable Code 3B.

3. **Configure API settings** (optional):
   - Check "Use Hugging Face API" to use remote inference (requires HF token)
   - Leave unchecked to use a locally downloaded model

4. **Click "Generate Topology"**. The status label shows progress. Generation takes 30-60 seconds depending on the model.

5. **Review and edit** the generated code in the right-side editor. The editor is fully editable -- you can fix or customize anything before running.

6. **Run, save, or copy** the code:
   - **"Run Generated Code"**: Executes the code immediately (creates Docker containers). Output appears in the Console at the bottom.
   - **"Save to File"**: Saves the code as a `.py` file.
   - **"Copy All"** / **"Undo"** / **"Clear"**: Editor toolbar actions.

**Using example topologies:**

Instead of generating from scratch, click any of the six pre-verified example buttons at the bottom of the left panel:

- **Simple SDN Topology** -- 2 hosts + 1 switch
- **4G Wireless Network** -- 2 UEs + eNodeB + EPC
- **Multi-Switch SDN** -- 3 switches + 1 controller + 4 hosts
- **Fog Computing Network** -- 3 edge nodes + 2 fog nodes + cloud
- **Enterprise Network** -- gateway + 2 department switches + 4 hosts
- **IoT Network** -- 3 sensors + gateway + cloud server

Clicking an example loads both the prompt and the verified code, ready to run.

### 2.2 Topology Builder Tab

Build topologies manually without AI, using point-and-click controls.

**Create a node:**
1. Select a **Type** (Host, Switch, Controller, UE, EnB, EPC, Perfsonar)
2. Enter a **Name** (e.g., `h1`)
3. The **Docker Image** auto-fills based on type (editable)
4. Optionally set **Memory** (e.g., `512m`) and **CPUs** (e.g., `1.0`)
5. Click **"Create Node"**

**Connect two nodes:**
1. Select **Node 1** and **Node 2** from the dropdowns (auto-populated from running containers)
2. Enter interface names (e.g., `h1s1` and `s1h1`)
3. Click **"Connect"**

**Configure IP:**
1. Select a **Node** and **Interface**
2. Enter **IP** address and **Mask** (e.g., `10.0.0.1` / `24`)
3. Click **"Set IP"**

**Run a script:** Browse for any `.py` topology file and click "Run".

The right panel shows all **Active Docker Containers** with name, type, image, and status. Use "Refresh", "Delete Selected", or "Delete All Containers" to manage them.

### 2.3 Experiments Tab

Run network performance experiments on your running topology.

**Custom test:**
1. Select **Test Type**: Throughput, RTT, or Latency
2. Enter a **Test Name** (used for the output filename)
3. Enter **Source IP** and **Target IP** of nodes in your topology
4. Click **"Run Experiment"**

Results are saved as JSON files in `results/data/` and output appears in the right panel.

**Predefined scripts:** Click any of the preset experiment buttons:
- Emu-Emu Wired / Emu-Phy Wired
- Emu-Emu Wireless / Emu-Phy Wireless
- Deploy LFT Benchmark
- Simple SDN Topology

### 2.4 Results Tab

Browse and inspect experiment result files.

1. Use the **Filter** dropdown to show only Throughput, RTT, Latency, CSV, or All files
2. Click a file in the left list to view its contents (JSON or CSV) in the right panel
3. Click **"Plot Results"** to run `analyzeResults.py`, which generates comparison plots
4. Click **"Export Selected"** to save a copy of any result file

### 2.5 Monitoring Tab

Real-time telemetry and visualization for running containers.

**Start Real-Time Visualizer:**
1. Set the update interval in milliseconds (default: 1000)
2. Click **"Start Real-Time Visualizer"** -- opens a matplotlib window showing:
   - Network topology graph (nodes color-coded by type)
   - CPU usage chart
   - Memory usage chart
   - Network traffic chart
   - Latency chart

**Collect Telemetry Snapshot:** Click to get a one-time reading of CPU, memory, and network stats for all running containers.

**Export Telemetry Data:** Save collected telemetry as CSV or JSON for external analysis.

---

## 3. CLI / Standalone Mode

### 3.1 Generate Topologies

```bash
# Basic generation (uses default DeepSeek-R1 model, local inference)
lft-ai generate "Create an SDN topology with 2 hosts connected to a switch" -o my_topology.py

# Use a specific model
lft-ai generate "Create a 4G network with 2 UEs" --model phi3-mini -o wireless.py

# Use Hugging Face API instead of local model
lft-ai generate "Create a datacenter topology" --token YOUR_HF_TOKEN -o datacenter.py

# Generate with validation
lft-ai generate "Create a fog computing network" -o fog.py --validate

# Verbose output (shows model loading progress, generation details)
lft-ai generate "Create a simple network" -o simple.py -v
```

**Available model aliases:** `deepseek-r1`, `deepseek-r1-8b`, `phi3-mini`, `stable-code-3b`, `qwen2-7b`, `gemma2-9b`, `code-llama-7b`, `deepseek-coder-7b`

After generating, run your topology:
```bash
sudo python3 my_topology.py
```

### 3.2 Interactive Mode

```bash
lft-ai interactive
# or with a specific model:
lft-ai interactive --model phi3-mini
```

Interactive mode opens a REPL where you type descriptions and get code back immediately:

```
LFT AI Interactive Mode
Type a topology description and press Enter.
Commands: quit, help, clear

>>> Create a simple network with 2 hosts and 1 switch
[Generating...]

# Generated code appears here
from profissa_lft.host import Host
from profissa_lft.switch import Switch
...

>>> quit
```

### 3.3 View Examples

```bash
lft-ai examples
```

Prints example topology descriptions and their expected output to help you learn the prompt format.

### 3.4 Standalone Script

The standalone script bundles all LFT AI functionality in a single file (no package installation needed):

```bash
# Generate topology
python3 lft_ai_standalone.py generate "Create an SDN topology with 2 hosts" -o topology.py

# Interactive mode
python3 lft_ai_standalone.py interactive

# Live visualization (monitors running containers)
python3 lft_ai_standalone.py visualize

# Static visualization from a topology file
python3 lft_ai_standalone.py visualize --file topology.py

# Custom update interval
python3 lft_ai_standalone.py visualize --interval 2000

# Export telemetry
python3 lft_ai_standalone.py visualize --export-csv metrics.csv
python3 lft_ai_standalone.py visualize --export-json metrics.json

# Show examples
python3 lft_ai_standalone.py examples
```

---

## 4. Visualization

### 4.1 Live Monitoring

Monitor running Docker containers in real-time with an interactive matplotlib dashboard.

**From the GUI:**
Go to the Monitoring tab and click "Start Real-Time Visualizer".

**From the CLI:**
```bash
python3 lft_ai_standalone.py visualize
```

**What it shows:**
- **Topology Graph**: Nodes as colored circles (green=Host, blue=Switch, orange=Controller, purple=UE, red=EPC, pink=eNodeB), with lines for connections
- **CPU Usage**: Real-time % per container (last 100 samples)
- **Memory Usage**: MB consumed per container
- **Network Traffic**: Throughput in KB/s (RX+TX combined)
- **Latency**: RTT between node pairs

**Workflow example:**
```bash
# Terminal 1: Start your topology
sudo python3 my_topology.py

# Terminal 2: Start the visualizer
python3 lft_ai_standalone.py visualize
```

The visualizer auto-discovers all running containers. Close the matplotlib window to stop.

### 4.2 Static Visualization

Render a topology graph from a `.py` file without running any containers:

```bash
python3 lft_ai_standalone.py visualize --file generated_topology.py
```

This parses the Python file, extracts node instantiations and `.connect()` calls, and renders a static network graph. Useful for previewing a topology before deployment.

### 4.3 Programmatic Visualization

```python
from profissa_lft.visualizer import NetworkVisualizer

# Basic usage
visualizer = NetworkVisualizer(update_interval=1000)
visualizer.start()  # Blocks until window is closed

# In a background thread (for integration with other code)
import threading
visualizer = NetworkVisualizer()
viz_thread = threading.Thread(target=visualizer.start)
viz_thread.daemon = True
viz_thread.start()

# ... your topology keeps running ...
input("Press Enter to stop...\n")
```

---

## 5. Accessing Simulation Data

### 5.1 Experiment Results (JSON)

Experiments produce JSON files in `results/data/`. There are three types:

**Throughput (iperf3):**
```bash
# Run a throughput test
lft-ai generate "..." -o topo.py && sudo python3 topo.py
# Then in another terminal, or via the GUI Experiments tab:
python3 -c "
from experiment.experiment import runThroughput
runThroughput('my_test', '10.0.0.1', '10.0.0.2')
"
```

Output file: `results/data/my_test_throughput_1.json`

Key fields in the JSON:
```json
{
  "intervals": [
    {
      "sum": {
        "bits_per_second": 943215600.0,
        "bytes": 117901950
      }
    }
  ],
  "end": {
    "sum_sent": { "bits_per_second": 943718400.0 },
    "sum_received": { "bits_per_second": 943214300.0 }
  }
}
```

**RTT (ping):**
```python
from experiment.experiment import runRTT
runRTT('my_test', '10.0.0.1', '10.0.0.2')
```

Output file: `results/data/my_test_rtt_1.json`

Key fields:
```json
{
  "result": {
    "roundtrips": [
      {
        "seq": 1,
        "length": 64,
        "ip": "10.0.0.2",
        "rtt": "PT0.000234S"
      }
    ]
  }
}
```
RTT values use ISO 8601 duration format (e.g., `PT0.000234S` = 0.234 ms).

**Latency (OWAMP one-way):**
```python
from experiment.experiment import runLatency
runLatency('my_test', '10.0.0.1', '10.0.0.2')
```

Output file: `results/data/my_test_latency_1.json`

Key fields:
```json
{
  "result": {
    "succeeded": true,
    "packets-sent": 100,
    "packets-received": 100,
    "packets-lost": 0
  }
}
```

### 5.2 Telemetry Data

The telemetry system collects live Docker container metrics.

**From the GUI:** Use the Monitoring tab to collect snapshots or export data.

**Programmatically:**
```python
from profissa_lft.telemetry import TelemetryStore, TelemetryCollector

# Create store and collector
store = TelemetryStore()
collector = TelemetryCollector(store)

# Auto-discover running containers
collector.auto_discover()

# Collect metrics
collector.collect_all()

# Get a summary dict
summary = collector.summary()
for node, metrics in summary.items():
    print(f"\n{node}:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")

# Export to file
store.export_csv("telemetry_data.csv")
store.export_json("telemetry_data.json")
```

**From the CLI:**
```bash
# Export during visualization
python3 lft_ai_standalone.py visualize --export-csv metrics.csv
python3 lft_ai_standalone.py visualize --export-json metrics.json
```

### 5.3 Analyzing Results

The `results/analyzeResults.py` script processes experiment JSON files and generates plots:

```bash
cd /path/to/lft_ai
python3 results/analyzeResults.py
```

This produces:
- Throughput comparison bar charts (LFT vs Mininet-WiFi)
- RTT box plots
- Latency distributions
- Deployment time comparisons (from CSV benchmarks)
- 99% confidence intervals with outlier removal

**From the GUI:** Go to the Results tab and click "Plot Results (analyzeResults.py)".

**Result file location:**
```
lft_ai/
  results/
    data/
      wired_emu_emu_throughput_1.json    # Throughput results
      wired_emu_emu_rtt_1.json           # RTT results
      wired_emu_emu_latency_1.json       # Latency results
      deployLftTime.csv                  # Deployment benchmarks
      deployLftMem.csv                   # Memory benchmarks
    analyzeResults.py                    # Analysis/plotting script
```

---

## 6. Programmatic Python API

Use LFT AI from your own Python scripts:

```python
from profissa_lft import ModernAITopologyGenerator

# Initialize (loads model, takes 30-60s)
gen = ModernAITopologyGenerator(model_name="deepseek-r1")

# Generate code from description
code = gen.generate_topology("""
Create a network with:
- 3 hosts: h1 (10.0.0.1/24), h2 (10.0.0.2/24), h3 (10.0.0.3/24)
- 1 switch: s1
- Connect all hosts to switch
- Instantiate all nodes
""")

# Validate the generated code
if gen.validate_generated_code(code):
    print("Code is valid!")

# Save to file
with open('my_topology.py', 'w') as f:
    f.write(code)

# Or generate directly to file
gen.generate_topology("Create a simple SDN topology", output_file="topology.py")
```

**Tip:** For best results, include specifics in your description: node counts, IP addresses, connection patterns, and which LFT components to use.

---

## 7. Model Selection Guide

| Model | Alias | Speed | Quality | Best For |
|-------|-------|-------|---------|----------|
| DeepSeek-R1-0528 | `deepseek-r1` | Slow (~60s init) | Best | Complex topologies |
| DeepSeek-R1-8B | `deepseek-r1-8b` | Medium | Very Good | Balanced use |
| Phi-3 Mini | `phi3-mini` | Fast (~15s init) | Good | Quick prototyping |
| Stable Code 3B | `stable-code-3b` | Very Fast | Good | Clean, simple code |
| Qwen2-7B | `qwen2-7b` | Medium | Good | Code-focused tasks |
| Gemma2-9B | `gemma2-9b` | Medium | Good | General purpose |
| Code Llama 7B | `code-llama-7b` | Medium | Good | Code generation |
| DeepSeek Coder 7B | `deepseek-coder-7b` | Medium | Good | Code generation |

**Memory requirements:**
- 3B models: ~4 GB RAM/VRAM
- 7-8B models: ~8 GB RAM/VRAM
- Full DeepSeek-R1: ~16+ GB RAM/VRAM (use `load_in_4bit=True` to reduce)

---

## 8. Troubleshooting

### GUI won't start
```bash
# Make sure tkinter is installed
sudo apt install python3-tk   # Debian/Ubuntu
```

### "No network detected" in visualizer
Make sure containers are running: `sudo docker ps`. The visualizer only sees running Docker containers.

### Model loading is slow or fails
```bash
# Use a smaller model for faster startup
lft-ai generate "..." --model phi3-mini -o topology.py

# Or use quantization in Python
gen = ModernAITopologyGenerator(load_in_4bit=True)
```

### Out of memory during AI generation
Use a smaller model (`phi3-mini` or `stable-code-3b`) or enable 4-bit quantization.

### Docker permission denied
```bash
sudo usermod -aG docker $USER
# Then log out and back in, or:
newgrp docker
```

### Using Podman instead of Docker
```bash
# Start Podman socket
systemctl --user start podman.socket

# Set Docker-compatible socket
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock

# Configure image registry
mkdir -p ~/.config/containers
echo 'unqualified-search-registries = ["docker.io"]' > ~/.config/containers/registries.conf
```

### Generated code doesn't work
- Be more specific in your description (include node names, IPs, connections)
- Use the GUI examples as templates -- they contain verified, working code
- Edit the generated code in the GUI editor before running

---

## Quick Reference Card

| Task | GUI | CLI |
|------|-----|-----|
| Generate topology | AI Generator tab | `lft-ai generate "..." -o file.py` |
| Interactive generation | -- | `lft-ai interactive` |
| Run topology | "Run Generated Code" button | `sudo python3 topology.py` |
| Live visualization | Monitoring tab > "Start Visualizer" | `python3 lft_ai_standalone.py visualize` |
| Static visualization | -- | `python3 lft_ai_standalone.py visualize --file topology.py` |
| Run experiment | Experiments tab | `python3 -c "from experiment.experiment import runThroughput; ..."` |
| View results | Results tab | Open `results/data/*.json` |
| Plot results | Results tab > "Plot Results" | `python3 results/analyzeResults.py` |
| Export telemetry | Monitoring tab > "Export CSV/JSON" | `python3 lft_ai_standalone.py visualize --export-csv file.csv` |
| Collect telemetry | Monitoring tab > "Collect Snapshot" | Programmatic via `TelemetryCollector` |
| View examples | AI Generator tab > example buttons | `lft-ai examples` |

---

**License:** GNU General Public License v3.0
**Maintainer:** Profissa - UnB
