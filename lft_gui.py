#!/usr/bin/env python3
"""
LFT GUI - Graphical User Interface for the Lightweight Fog Testbed.
Provides access to all LFT features: AI topology generation, manual topology
building, experiment execution, result viewing, and real-time monitoring.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import subprocess
import json
import os
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


class LFTGui:

    MODELS = {
        "DeepSeek-R1 (Best Quality)": "deepseek-r1",
        "DeepSeek-R1-8B (Fast)": "deepseek-r1-8b",
        "Phi-3 Mini (Very Fast)": "phi3-mini",
        "Qwen2-7B (Code-focused)": "qwen2-7b",
        "Gemma2-9B (All-around)": "gemma2-9b",
        "Stable Code 3B (Very Fast)": "stable-code-3b",
        "Code Llama 7B (Code)": "code-llama-7b",
        "DeepSeek Coder 7B (Code)": "deepseek-coder-7b",
    }

    NODE_TYPES = ["Host", "Switch", "Controller", "UE", "EnB", "EPC", "Perfsonar"]

    DEFAULT_IMAGES = {
        "Host": "alexandremitsurukaihara/lst2.0:host",
        "Switch": "alexandremitsurukaihara/lst2.0:host",
        "Controller": "alexandremitsurukaihara/lst2.0:host",
        "UE": "alexandremitsurukaihara/lft:srsran-perfsonar-uhd4",
        "EnB": "alexandremitsurukaihara/lft:srsran-perfsonar-uhd4",
        "EPC": "alexandremitsurukaihara/lft:srsran-perfsonar-uhd4",
        "Perfsonar": "alexandremitsurukaihara/lft:perfsonar-testpoint-ubuntu",
    }

    EXAMPLES = {
        "Simple SDN Topology": {
            "prompt": "Create a simple SDN topology with 2 hosts connected to a switch",
            "code": (
                "from profissa_lft.host import Host\n"
                "from profissa_lft.switch import Switch\n"
                "\n"
                "# Create nodes\n"
                "h1 = Host('h1')\n"
                "h2 = Host('h2')\n"
                "s1 = Switch('s1')\n"
                "\n"
                "# Instantiate containers\n"
                "h1.instantiate()\n"
                "h2.instantiate()\n"
                "s1.instantiate()\n"
                "\n"
                "# Connect hosts to switch\n"
                "h1.connect(s1, 'h1s1', 's1h1')\n"
                "h2.connect(s1, 'h2s1', 's1h2')\n"
                "\n"
                "# Configure IP addresses\n"
                "h1.setIp('10.0.0.1', 24, 'h1s1')\n"
                "h2.setIp('10.0.0.2', 24, 'h2s1')\n"
                "\n"
                "# Connect switch to host network for internet access\n"
                "s1.connectToInternet('10.0.0.4', 24, 's1host', 'hosts1')\n"
                "\n"
                "# Set default gateways\n"
                "h1.setDefaultGateway('10.0.0.4', 'h1s1')\n"
                "h2.setDefaultGateway('10.0.0.4', 'h2s1')\n"
                "\n"
                "print('Simple SDN topology created successfully!')\n"
                "print('h1: 10.0.0.1  h2: 10.0.0.2  switch: s1')\n"
            ),
        },
        "4G Wireless Network": {
            "prompt": "Create a 4G wireless network with 2 UEs connected to an eNodeB and EPC",
            "code": (
                "from profissa_lft.ue import UE\n"
                "from profissa_lft.epc import EPC\n"
                "from profissa_lft.enb import EnB\n"
                "import time\n"
                "\n"
                "# Create 4G network components\n"
                "epc = EPC('epc')\n"
                "enb = EnB('enb')\n"
                "ue1 = UE('ue1')\n"
                "ue2 = UE('ue2')\n"
                "\n"
                "# Instantiate containers\n"
                "epc.instantiate()\n"
                "enb.instantiate()\n"
                "ue1.instantiate()\n"
                "ue2.instantiate()\n"
                "\n"
                "# Connect: eNodeB <-> EPC, UEs <-> eNodeB\n"
                "enb.connect(epc, 'enbepc', 'epcenb')\n"
                "ue1.connect(enb, 'ue1enb', 'enbue1')\n"
                "ue2.connect(enb, 'ue2enb', 'enbue2')\n"
                "\n"
                "# Configure IP addresses\n"
                "epc.setIp('10.0.0.1', 24, 'epcenb')\n"
                "enb.setIp('10.0.0.2', 24, 'enbepc')\n"
                "enb.setIp('11.0.0.1', 30, 'enbue1')\n"
                "enb.setIp('11.0.0.5', 30, 'enbue2')\n"
                "ue1.setIp('11.0.0.2', 29, 'ue1enb')\n"
                "ue2.setIp('11.0.0.6', 29, 'ue2enb')\n"
                "\n"
                "# Internet access via EPC\n"
                "epc.connectToInternet('10.0.0.6', 24, 'epchost', 'hostepc')\n"
                "\n"
                "# Default gateways\n"
                "epc.setDefaultGateway('10.0.0.6', 'epchost')\n"
                "enb.setDefaultGateway('10.0.0.1', 'enbepc')\n"
                "ue1.setDefaultGateway('11.0.0.1', 'ue1enb')\n"
                "ue2.setDefaultGateway('11.0.0.5', 'ue2enb')\n"
                "\n"
                "# Configure EPC\n"
                "epc.setEPCAddress('10.0.0.1')\n"
                "epc.addNewUE(ue1.getNodeName(), '001010123456780', '172.16.0.2')\n"
                "epc.addNewUE(ue2.getNodeName(), '001010123456789', '172.16.0.3')\n"
                "\n"
                "# Configure eNodeB\n"
                "enb.setEPCAddress('10.0.0.1')\n"
                "enb.setEnBAddress('10.0.0.2')\n"
                "\n"
                "# Configure UE identities\n"
                "ue1.setUEID('001010123456780')\n"
                "ue2.setUEID('001010123456789')\n"
                "\n"
                "print('4G wireless network created successfully!')\n"
                "print('EPC: 10.0.0.1  eNB: 10.0.0.2')\n"
                "print('UE1: 11.0.0.2  UE2: 11.0.0.6')\n"
            ),
        },
        "Multi-Switch SDN": {
            "prompt": "Create an SDN topology with 3 switches, 1 controller, and 4 hosts",
            "code": (
                "from profissa_lft.host import Host\n"
                "from profissa_lft.switch import Switch\n"
                "from profissa_lft.controller import Controller\n"
                "\n"
                "# Create controller\n"
                "c1 = Controller('c1')\n"
                "c1.instantiate()\n"
                "\n"
                "# Create switches\n"
                "s1 = Switch('s1')\n"
                "s2 = Switch('s2')\n"
                "s3 = Switch('s3')\n"
                "s1.instantiate()\n"
                "s2.instantiate()\n"
                "s3.instantiate()\n"
                "\n"
                "# Create hosts\n"
                "h1 = Host('h1')\n"
                "h2 = Host('h2')\n"
                "h3 = Host('h3')\n"
                "h4 = Host('h4')\n"
                "h1.instantiate()\n"
                "h2.instantiate()\n"
                "h3.instantiate()\n"
                "h4.instantiate()\n"
                "\n"
                "# Connect controller to switch s1 for management\n"
                "c1.connect(s1, 'c1s1', 's1c1')\n"
                "c1.setIp('192.168.0.1', 24, 'c1s1')\n"
                "s1.setIp('192.168.0.2', 24, 's1c1')\n"
                "\n"
                "# Connect switches in a chain: s1 -- s2 -- s3\n"
                "s1.connect(s2, 's1s2', 's2s1')\n"
                "s2.connect(s3, 's2s3', 's3s2')\n"
                "\n"
                "# Connect hosts: h1,h2 -> s1 | h3 -> s2 | h4 -> s3\n"
                "h1.connect(s1, 'h1s1', 's1h1')\n"
                "h2.connect(s1, 'h2s1', 's1h2')\n"
                "h3.connect(s2, 'h3s2', 's2h3')\n"
                "h4.connect(s3, 'h4s3', 's3h4')\n"
                "\n"
                "# Configure host IPs\n"
                "h1.setIp('10.0.0.1', 24, 'h1s1')\n"
                "h2.setIp('10.0.0.2', 24, 'h2s1')\n"
                "h3.setIp('10.0.0.3', 24, 'h3s2')\n"
                "h4.setIp('10.0.0.4', 24, 'h4s3')\n"
                "\n"
                "# Set controller on all switches (via management IP)\n"
                "s1.setController('192.168.0.1', 6633)\n"
                "s2.setController('192.168.0.1', 6633)\n"
                "s3.setController('192.168.0.1', 6633)\n"
                "\n"
                "# Start the Ryu controller\n"
                "c1.initController('192.168.0.1', 6633)\n"
                "\n"
                "# Internet access via s1\n"
                "s1.connectToInternet('10.0.0.254', 24, 's1host', 'hosts1')\n"
                "h1.setDefaultGateway('10.0.0.254', 'h1s1')\n"
                "h2.setDefaultGateway('10.0.0.254', 'h2s1')\n"
                "h3.setDefaultGateway('10.0.0.254', 'h3s2')\n"
                "h4.setDefaultGateway('10.0.0.254', 'h4s3')\n"
                "\n"
                "print('Multi-switch SDN topology created successfully!')\n"
                "print('Controller c1: 192.168.0.1:6633')\n"
                "print('Switches: s1, s2, s3')\n"
                "print('h1: 10.0.0.1  h2: 10.0.0.2  h3: 10.0.0.3  h4: 10.0.0.4')\n"
            ),
        },
        "Fog Computing Network": {
            "prompt": "Create a fog computing network with edge nodes, fog nodes, and cloud connection",
            "code": (
                "from profissa_lft.host import Host\n"
                "from profissa_lft.switch import Switch\n"
                "\n"
                "# Edge layer: IoT devices\n"
                "edge1 = Host('edge1')\n"
                "edge2 = Host('edge2')\n"
                "edge3 = Host('edge3')\n"
                "\n"
                "# Fog layer: local processing\n"
                "fog1 = Host('fog1')\n"
                "fog2 = Host('fog2')\n"
                "\n"
                "# Cloud layer\n"
                "cloud = Host('cloud')\n"
                "\n"
                "# Network switches\n"
                "sw_edge = Switch('se')\n"
                "sw_fog = Switch('sf')\n"
                "\n"
                "# Instantiate all nodes\n"
                "for node in [edge1, edge2, edge3, fog1, fog2, cloud, sw_edge, sw_fog]:\n"
                "    node.instantiate()\n"
                "\n"
                "# Connect edge devices to edge switch\n"
                "edge1.connect(sw_edge, 'e1se', 'see1')\n"
                "edge2.connect(sw_edge, 'e2se', 'see2')\n"
                "edge3.connect(sw_edge, 'e3se', 'see3')\n"
                "\n"
                "# Connect edge switch to fog switch\n"
                "sw_edge.connect(sw_fog, 'sesf', 'sfse')\n"
                "\n"
                "# Connect fog nodes to fog switch\n"
                "fog1.connect(sw_fog, 'f1sf', 'sff1')\n"
                "fog2.connect(sw_fog, 'f2sf', 'sff2')\n"
                "\n"
                "# Connect cloud to fog switch\n"
                "cloud.connect(sw_fog, 'clsf', 'sfcl')\n"
                "\n"
                "# Configure IPs - Edge: 10.0.1.0/24\n"
                "edge1.setIp('10.0.1.1', 24, 'e1se')\n"
                "edge2.setIp('10.0.1.2', 24, 'e2se')\n"
                "edge3.setIp('10.0.1.3', 24, 'e3se')\n"
                "\n"
                "# Fog: 10.0.2.0/24\n"
                "fog1.setIp('10.0.2.1', 24, 'f1sf')\n"
                "fog2.setIp('10.0.2.2', 24, 'f2sf')\n"
                "\n"
                "# Cloud: 10.0.3.0/24\n"
                "cloud.setIp('10.0.3.1', 24, 'clsf')\n"
                "\n"
                "# Internet access via fog switch\n"
                "sw_fog.connectToInternet('10.0.0.254', 24, 'sfhost', 'hostsf')\n"
                "\n"
                "# Default gateways\n"
                "edge1.setDefaultGateway('10.0.0.254', 'e1se')\n"
                "edge2.setDefaultGateway('10.0.0.254', 'e2se')\n"
                "edge3.setDefaultGateway('10.0.0.254', 'e3se')\n"
                "fog1.setDefaultGateway('10.0.0.254', 'f1sf')\n"
                "fog2.setDefaultGateway('10.0.0.254', 'f2sf')\n"
                "cloud.setDefaultGateway('10.0.0.254', 'clsf')\n"
                "\n"
                "print('Fog computing network created successfully!')\n"
                "print('Edge layer: edge1(10.0.1.1), edge2(10.0.1.2), edge3(10.0.1.3)')\n"
                "print('Fog layer:  fog1(10.0.2.1), fog2(10.0.2.2)')\n"
                "print('Cloud:      cloud(10.0.3.1)')\n"
            ),
        },
        "Enterprise Network": {
            "prompt": "Create an enterprise network with multiple switches, a gateway, and department hosts",
            "code": (
                "from profissa_lft.host import Host\n"
                "from profissa_lft.switch import Switch\n"
                "\n"
                "# Gateway router (host acting as router)\n"
                "gw = Host('gw')\n"
                "\n"
                "# Department switches\n"
                "sw_eng = Switch('seng')\n"
                "sw_hr = Switch('shr')\n"
                "\n"
                "# Engineering hosts\n"
                "eng1 = Host('eng1')\n"
                "eng2 = Host('eng2')\n"
                "\n"
                "# HR hosts\n"
                "hr1 = Host('hr1')\n"
                "hr2 = Host('hr2')\n"
                "\n"
                "# Instantiate all\n"
                "for node in [gw, sw_eng, sw_hr, eng1, eng2, hr1, hr2]:\n"
                "    node.instantiate()\n"
                "\n"
                "# Connect gateway to both department switches\n"
                "gw.connect(sw_eng, 'gwse', 'segw')\n"
                "gw.connect(sw_hr, 'gwsh', 'shgw')\n"
                "\n"
                "# Connect engineering hosts\n"
                "eng1.connect(sw_eng, 'e1se', 'see1')\n"
                "eng2.connect(sw_eng, 'e2se', 'see2')\n"
                "\n"
                "# Connect HR hosts\n"
                "hr1.connect(sw_hr, 'r1sh', 'shr1')\n"
                "hr2.connect(sw_hr, 'r2sh', 'shr2')\n"
                "\n"
                "# Engineering subnet: 10.10.0.0/24\n"
                "gw.setIp('10.10.0.254', 24, 'gwse')\n"
                "eng1.setIp('10.10.0.1', 24, 'e1se')\n"
                "eng2.setIp('10.10.0.2', 24, 'e2se')\n"
                "\n"
                "# HR subnet: 10.20.0.0/24\n"
                "gw.setIp('10.20.0.254', 24, 'gwsh')\n"
                "hr1.setIp('10.20.0.1', 24, 'r1sh')\n"
                "hr2.setIp('10.20.0.2', 24, 'r2sh')\n"
                "\n"
                "# Enable forwarding on gateway between departments\n"
                "gw.enableForwarding('gwse', 'gwsh')\n"
                "\n"
                "# Internet access\n"
                "gw.connectToInternet('192.168.1.1', 24, 'gwhost', 'hostgw')\n"
                "gw.setDefaultGateway('192.168.1.1', 'gwhost')\n"
                "\n"
                "# Default gateways for hosts\n"
                "eng1.setDefaultGateway('10.10.0.254', 'e1se')\n"
                "eng2.setDefaultGateway('10.10.0.254', 'e2se')\n"
                "hr1.setDefaultGateway('10.20.0.254', 'r1sh')\n"
                "hr2.setDefaultGateway('10.20.0.254', 'r2sh')\n"
                "\n"
                "print('Enterprise network created successfully!')\n"
                "print('Gateway: gw (10.10.0.254 / 10.20.0.254)')\n"
                "print('Engineering: eng1(10.10.0.1), eng2(10.10.0.2)')\n"
                "print('HR: hr1(10.20.0.1), hr2(10.20.0.2)')\n"
            ),
        },
        "IoT Network": {
            "prompt": "Create an IoT network with sensor nodes, a gateway, and a cloud server",
            "code": (
                "from profissa_lft.host import Host\n"
                "from profissa_lft.switch import Switch\n"
                "\n"
                "# IoT sensor nodes\n"
                "sen1 = Host('sen1')\n"
                "sen2 = Host('sen2')\n"
                "sen3 = Host('sen3')\n"
                "\n"
                "# IoT gateway\n"
                "iotgw = Host('iotgw')\n"
                "\n"
                "# Cloud server\n"
                "cloud = Host('cloud')\n"
                "\n"
                "# Switches\n"
                "sw_iot = Switch('siot')\n"
                "sw_wan = Switch('swan')\n"
                "\n"
                "# Instantiate all\n"
                "for node in [sen1, sen2, sen3, iotgw, cloud, sw_iot, sw_wan]:\n"
                "    node.instantiate()\n"
                "\n"
                "# Connect sensors to IoT switch\n"
                "sen1.connect(sw_iot, 's1si', 'sis1')\n"
                "sen2.connect(sw_iot, 's2si', 'sis2')\n"
                "sen3.connect(sw_iot, 's3si', 'sis3')\n"
                "\n"
                "# Connect gateway to both switches\n"
                "iotgw.connect(sw_iot, 'gwsi', 'sigw')\n"
                "iotgw.connect(sw_wan, 'gwsw', 'swgw')\n"
                "\n"
                "# Connect cloud to WAN switch\n"
                "cloud.connect(sw_wan, 'clsw', 'swcl')\n"
                "\n"
                "# Sensor network: 10.0.1.0/24\n"
                "sen1.setIp('10.0.1.1', 24, 's1si')\n"
                "sen2.setIp('10.0.1.2', 24, 's2si')\n"
                "sen3.setIp('10.0.1.3', 24, 's3si')\n"
                "iotgw.setIp('10.0.1.254', 24, 'gwsi')\n"
                "\n"
                "# WAN network: 10.0.2.0/24\n"
                "iotgw.setIp('10.0.2.1', 24, 'gwsw')\n"
                "cloud.setIp('10.0.2.100', 24, 'clsw')\n"
                "\n"
                "# Enable forwarding on gateway\n"
                "iotgw.enableForwarding('gwsi', 'gwsw')\n"
                "\n"
                "# Internet access\n"
                "sw_wan.connectToInternet('10.0.2.254', 24, 'swhost', 'hostsw')\n"
                "\n"
                "# Default gateways\n"
                "sen1.setDefaultGateway('10.0.1.254', 's1si')\n"
                "sen2.setDefaultGateway('10.0.1.254', 's2si')\n"
                "sen3.setDefaultGateway('10.0.1.254', 's3si')\n"
                "cloud.setDefaultGateway('10.0.2.1', 'clsw')\n"
                "\n"
                "print('IoT network created successfully!')\n"
                "print('Sensors: sen1(10.0.1.1), sen2(10.0.1.2), sen3(10.0.1.3)')\n"
                "print('Gateway: iotgw(10.0.1.254 / 10.0.2.1)')\n"
                "print('Cloud:   cloud(10.0.2.100)')\n"
            ),
        },
    }

    # Colors
    BG_DARK = "#1e1e2e"
    FG_LIGHT = "#cdd6f4"
    ACCENT = "#89b4fa"
    GREEN = "#a6e3a1"
    RED = "#f38ba8"
    YELLOW = "#f9e2af"
    SURFACE = "#313244"

    def __init__(self, root):
        self.root = root
        self.root.title("LFT - Lightweight Fog Testbed")
        self.root.geometry("1280x860")
        self.root.minsize(960, 640)

        self.generated_code = ""

        self._setup_style()
        self._build_ui()

        # Load results list on startup
        self.root.after(200, self._refresh_results)
        self.root.after(200, self._refresh_nodes)

    # ── Style ──────────────────────────────────────────────────────────

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Subtitle.TLabel", font=("Helvetica", 11, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 10, "bold"))
        style.configure("Action.TButton", padding=(10, 5))
        style.configure("Generate.TButton", padding=(20, 10),
                        font=("Helvetica", 11, "bold"))
        style.configure("Example.TButton", padding=(6, 3))

    # ── Main layout ───────────────────────────────────────────────────

    def _build_ui(self):
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        # Header bar
        header = ttk.Frame(main, padding=(10, 6))
        header.pack(fill=tk.X)
        ttk.Label(header, text="LFT - Lightweight Fog Testbed",
                  style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header,
                  text="AI-Powered Network Topology Generator & Manager"
                  ).pack(side=tk.LEFT, padx=20)

        # Vertical pane: notebook on top, console on bottom
        paned = ttk.PanedWindow(main, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.notebook = ttk.Notebook(paned)
        paned.add(self.notebook, weight=4)

        self._build_ai_tab()
        self._build_topology_tab()
        self._build_experiments_tab()
        self._build_results_tab()
        self._build_monitoring_tab()

        # Console
        console_frame = ttk.LabelFrame(paned, text="Console Output", padding=4)
        paned.add(console_frame, weight=1)

        self.console = scrolledtext.ScrolledText(
            console_frame, height=7, font=("Consolas", 10),
            bg=self.BG_DARK, fg=self.FG_LIGHT, insertbackground="white",
            state="disabled")
        self.console.pack(fill=tk.BOTH, expand=True)

        # Console tag colours
        self.console.tag_configure("info", foreground=self.FG_LIGHT)
        self.console.tag_configure("success", foreground=self.GREEN)
        self.console.tag_configure("error", foreground=self.RED)
        self.console.tag_configure("warn", foreground=self.YELLOW)

        btn_row = ttk.Frame(console_frame)
        btn_row.pack(fill=tk.X, pady=(2, 0))
        ttk.Button(btn_row, text="Clear Console",
                   command=self._clear_console).pack(side=tk.RIGHT)

    # ── AI Generator tab ──────────────────────────────────────────────

    def _build_ai_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  AI Generator  ")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ── Left: input ──
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="Describe Your Topology",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(left,
                  text="Write in natural language how you want the network:"
                  ).pack(anchor=tk.W, pady=(0, 4))

        self.ai_prompt = scrolledtext.ScrolledText(
            left, height=8, font=("Consolas", 11), wrap=tk.WORD)
        self.ai_prompt.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.ai_prompt.insert(
            "1.0",
            "Create a simple SDN topology with 2 hosts connected to a "
            "switch and an OpenDaylight controller")

        # Settings
        settings = ttk.LabelFrame(left, text="AI Settings", padding=8)
        settings.pack(fill=tk.X, pady=(0, 8))

        row = ttk.Frame(settings)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=list(self.MODELS.keys())[0])
        ttk.Combobox(row, textvariable=self.model_var,
                     values=list(self.MODELS.keys()), state="readonly",
                     width=30).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(settings)
        row.pack(fill=tk.X, pady=2)
        self.use_api_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Use Hugging Face API (requires token)",
                        variable=self.use_api_var,
                        command=self._toggle_token).pack(side=tk.LEFT)

        row = ttk.Frame(settings)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="HF Token:").pack(side=tk.LEFT)
        self.token_var = tk.StringVar(value=os.getenv("HF_TOKEN", ""))
        self.token_entry = ttk.Entry(row, textvariable=self.token_var,
                                     show="*", width=38)
        self.token_entry.pack(side=tk.LEFT, padx=5)
        self.token_entry.configure(state="disabled")

        self.validate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings, text="Validate generated code",
                        variable=self.validate_var).pack(anchor=tk.W, pady=2)

        # Buttons
        btn = ttk.Frame(left)
        btn.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(btn, text="Generate Topology", style="Generate.TButton",
                   command=self._generate_topology).pack(side=tk.LEFT)
        ttk.Button(btn, text="Save to File",
                   command=self._save_generated).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn, text="Run Generated Code",
                   command=self._run_generated).pack(side=tk.LEFT)

        # Examples
        ex = ttk.LabelFrame(left,
                            text="Example Topologies (click to load prompt + code)",
                            padding=4)
        ex.pack(fill=tk.X)
        for title in self.EXAMPLES:
            ttk.Button(ex, text=f"  {title}", style="Example.TButton",
                       command=lambda t=title: self._load_example(t)
                       ).pack(fill=tk.X, pady=1)

        # ── Right: output ──
        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        ttk.Label(right, text="Generated Code (editable)",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 4))

        self.ai_status = ttk.Label(right, text="Ready", foreground="gray")
        self.ai_status.pack(anchor=tk.W, pady=(0, 4))

        # Code editor toolbar
        code_toolbar = ttk.Frame(right)
        code_toolbar.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(code_toolbar,
                  text="You can edit the code below before running",
                  foreground="gray").pack(side=tk.LEFT)
        ttk.Button(code_toolbar, text="Clear",
                   command=self._clear_code).pack(side=tk.RIGHT, padx=2)
        ttk.Button(code_toolbar, text="Copy All",
                   command=self._copy_code).pack(side=tk.RIGHT, padx=2)
        ttk.Button(code_toolbar, text="Undo",
                   command=lambda: self.code_output.edit_undo()
                   ).pack(side=tk.RIGHT, padx=2)

        self.code_output = scrolledtext.ScrolledText(
            right, font=("Consolas", 11), bg=self.BG_DARK, fg=self.FG_LIGHT,
            insertbackground="white", wrap=tk.NONE, undo=True)
        self.code_output.pack(fill=tk.BOTH, expand=True)

    # ── Topology Builder tab ──────────────────────────────────────────

    def _build_topology_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Topology Builder  ")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ── Left: controls ──
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        # Create node
        cf = ttk.LabelFrame(left, text="Create Node", padding=8)
        cf.pack(fill=tk.X, pady=(0, 8))

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Type:").pack(side=tk.LEFT)
        self.node_type_var = tk.StringVar(value="Host")
        type_combo = ttk.Combobox(row, textvariable=self.node_type_var,
                                  values=self.NODE_TYPES, state="readonly",
                                  width=14)
        type_combo.pack(side=tk.LEFT, padx=5)
        type_combo.bind("<<ComboboxSelected>>", self._on_node_type_change)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Name:").pack(side=tk.LEFT)
        self.node_name_var = tk.StringVar(value="h1")
        ttk.Entry(row, textvariable=self.node_name_var,
                  width=18).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Image:").pack(side=tk.LEFT)
        self.node_image_var = tk.StringVar(
            value=self.DEFAULT_IMAGES["Host"])
        ttk.Entry(row, textvariable=self.node_image_var,
                  width=45).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Memory:").pack(side=tk.LEFT)
        self.node_memory_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.node_memory_var,
                  width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(e.g. 512m)").pack(side=tk.LEFT)
        ttk.Label(row, text="  CPUs:").pack(side=tk.LEFT)
        self.node_cpus_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.node_cpus_var,
                  width=6).pack(side=tk.LEFT, padx=5)

        ttk.Button(cf, text="Create Node", style="Action.TButton",
                   command=self._create_node).pack(pady=(5, 0))

        # Connect nodes
        cn = ttk.LabelFrame(left, text="Connect Nodes", padding=8)
        cn.pack(fill=tk.X, pady=(0, 8))

        row = ttk.Frame(cn); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Node 1:").pack(side=tk.LEFT)
        self.connect_node1_var = tk.StringVar()
        self.connect_node1_combo = ttk.Combobox(
            row, textvariable=self.connect_node1_var, width=12)
        self.connect_node1_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="Iface:").pack(side=tk.LEFT, padx=(8, 0))
        self.connect_if1_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.connect_if1_var,
                  width=10).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cn); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Node 2:").pack(side=tk.LEFT)
        self.connect_node2_var = tk.StringVar()
        self.connect_node2_combo = ttk.Combobox(
            row, textvariable=self.connect_node2_var, width=12)
        self.connect_node2_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="Iface:").pack(side=tk.LEFT, padx=(8, 0))
        self.connect_if2_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.connect_if2_var,
                  width=10).pack(side=tk.LEFT, padx=5)

        ttk.Button(cn, text="Connect", style="Action.TButton",
                   command=self._connect_nodes).pack(pady=(5, 0))

        # Configure IP
        ip = ttk.LabelFrame(left, text="Configure IP", padding=8)
        ip.pack(fill=tk.X, pady=(0, 8))

        row = ttk.Frame(ip); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Node:").pack(side=tk.LEFT)
        self.ip_node_var = tk.StringVar()
        self.ip_node_combo = ttk.Combobox(
            row, textvariable=self.ip_node_var, width=12)
        self.ip_node_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="Iface:").pack(side=tk.LEFT, padx=(8, 0))
        self.ip_if_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.ip_if_var,
                  width=10).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(ip); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="IP:").pack(side=tk.LEFT)
        self.ip_addr_var = tk.StringVar(value="10.0.0.1")
        ttk.Entry(row, textvariable=self.ip_addr_var,
                  width=14).pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="/ Mask:").pack(side=tk.LEFT)
        self.ip_mask_var = tk.StringVar(value="24")
        ttk.Entry(row, textvariable=self.ip_mask_var,
                  width=4).pack(side=tk.LEFT, padx=5)

        ttk.Button(ip, text="Set IP", style="Action.TButton",
                   command=self._set_ip).pack(pady=(5, 0))

        # Run script
        sf = ttk.LabelFrame(left, text="Run Topology Script", padding=8)
        sf.pack(fill=tk.X)
        row = ttk.Frame(sf); row.pack(fill=tk.X, pady=2)
        self.script_path_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.script_path_var,
                  width=38).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(row, text="Browse",
                   command=self._browse_script).pack(side=tk.LEFT)
        ttk.Button(row, text="Run", style="Action.TButton",
                   command=self._run_script).pack(side=tk.LEFT, padx=4)

        # ── Right: active nodes ──
        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        ttk.Label(right, text="Active Docker Containers",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 4))

        cols = ("name", "type", "image", "status")
        self.nodes_tree = ttk.Treeview(right, columns=cols,
                                       show="headings", height=18)
        self.nodes_tree.heading("name", text="Name")
        self.nodes_tree.heading("type", text="Type")
        self.nodes_tree.heading("image", text="Image")
        self.nodes_tree.heading("status", text="Status")
        self.nodes_tree.column("name", width=80)
        self.nodes_tree.column("type", width=70)
        self.nodes_tree.column("image", width=160)
        self.nodes_tree.column("status", width=90)
        self.nodes_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        btn_row = ttk.Frame(right)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Refresh",
                   command=self._refresh_nodes).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="Delete Selected",
                   command=self._delete_node).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="Delete All Containers",
                   command=self._delete_all_nodes).pack(side=tk.LEFT, padx=2)

    # ── Experiments tab ───────────────────────────────────────────────

    def _build_experiments_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Experiments  ")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: config
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="Run Network Experiments",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        cf = ttk.LabelFrame(left, text="Custom Test", padding=10)
        cf.pack(fill=tk.X, pady=(0, 10))

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Test Type:").pack(side=tk.LEFT)
        self.test_type_var = tk.StringVar(value="Throughput")
        ttk.Combobox(row, textvariable=self.test_type_var,
                     values=["Throughput", "RTT", "Latency"],
                     state="readonly", width=14).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Test Name:").pack(side=tk.LEFT)
        self.test_name_var = tk.StringVar(value="my_test")
        ttk.Entry(row, textvariable=self.test_name_var,
                  width=18).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Source IP:").pack(side=tk.LEFT)
        self.source_ip_var = tk.StringVar(value="10.0.0.1")
        ttk.Entry(row, textvariable=self.source_ip_var,
                  width=14).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Target IP:").pack(side=tk.LEFT)
        self.target_ip_var = tk.StringVar(value="10.0.0.2")
        ttk.Entry(row, textvariable=self.target_ip_var,
                  width=14).pack(side=tk.LEFT, padx=5)

        ttk.Button(cf, text="Run Experiment", style="Generate.TButton",
                   command=self._run_experiment).pack(pady=(8, 0))

        # Predefined scripts
        pf = ttk.LabelFrame(left, text="Predefined Experiment Scripts",
                            padding=8)
        pf.pack(fill=tk.X)

        scripts = [
            ("Emu-Emu Wired", "experiment/emu_emu_wired.py"),
            ("Emu-Phy Wired", "experiment/emu_phy_wired.py"),
            ("Emu-Emu Wireless", "experiment/emu_emu_wireless.py"),
            ("Emu-Phy Wireless", "experiment/emu_phy_wireless.py"),
            ("Deploy LFT Benchmark", "experiment/deploy_lft.py"),
            ("Simple SDN Topology", "experiment/simpleSDNTopology.py"),
        ]
        for name, script in scripts:
            ttk.Button(pf, text=f"  {name}",
                       command=lambda s=script: self._run_experiment_script(s)
                       ).pack(fill=tk.X, pady=1)

        # Right: output
        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        ttk.Label(right, text="Experiment Output",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 4))

        self.experiment_output = scrolledtext.ScrolledText(
            right, font=("Consolas", 10), bg=self.BG_DARK, fg=self.FG_LIGHT,
            state="disabled")
        self.experiment_output.pack(fill=tk.BOTH, expand=True)

    # ── Results tab ───────────────────────────────────────────────────

    def _build_results_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Results  ")

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: file list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Result Files",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 4))

        ff = ttk.Frame(left_frame)
        ff.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(ff, text="Filter:").pack(side=tk.LEFT)
        self.result_filter_var = tk.StringVar(value="All")
        combo = ttk.Combobox(
            ff, textvariable=self.result_filter_var,
            values=["All", "Throughput", "RTT", "Latency", "CSV"],
            state="readonly", width=12)
        combo.pack(side=tk.LEFT, padx=5)
        combo.bind("<<ComboboxSelected>>",
                   lambda _: self._refresh_results())
        ttk.Button(ff, text="Refresh",
                   command=self._refresh_results).pack(side=tk.LEFT, padx=5)

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.results_listbox = tk.Listbox(list_frame, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                  command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.bind("<<ListboxSelect>>",
                                  self._on_result_select)

        # Right: viewer
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="File Contents",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 4))

        bf = ttk.Frame(right_frame)
        bf.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(bf, text="Plot Results (analyzeResults.py)",
                   command=self._run_analyze).pack(side=tk.LEFT)
        ttk.Button(bf, text="Export Selected",
                   command=self._export_result).pack(side=tk.LEFT, padx=8)

        self.result_viewer = scrolledtext.ScrolledText(
            right_frame, font=("Consolas", 10), bg=self.BG_DARK,
            fg=self.FG_LIGHT, wrap=tk.NONE, state="disabled")
        self.result_viewer.pack(fill=tk.BOTH, expand=True)

    # ── Monitoring tab ────────────────────────────────────────────────

    def _build_monitoring_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Monitoring  ")

        ttk.Label(tab, text="Real-Time Network Monitoring",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        cf = ttk.LabelFrame(tab, text="Telemetry Controls", padding=10)
        cf.pack(fill=tk.X, pady=(0, 8))

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Update Interval (ms):").pack(side=tk.LEFT)
        self.monitor_interval_var = tk.StringVar(value="1000")
        ttk.Entry(row, textvariable=self.monitor_interval_var,
                  width=8).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(cf); row.pack(fill=tk.X, pady=5)
        ttk.Button(row, text="Start Real-Time Visualizer",
                   style="Generate.TButton",
                   command=self._start_visualizer).pack(side=tk.LEFT)
        ttk.Button(row, text="Collect Telemetry Snapshot",
                   command=self._collect_telemetry
                   ).pack(side=tk.LEFT, padx=8)

        ef = ttk.LabelFrame(tab, text="Export Telemetry Data", padding=10)
        ef.pack(fill=tk.X, pady=(0, 8))
        row = ttk.Frame(ef); row.pack(fill=tk.X)
        ttk.Button(row, text="Export to CSV",
                   command=lambda: self._export_telemetry("csv")
                   ).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Export to JSON",
                   command=lambda: self._export_telemetry("json")
                   ).pack(side=tk.LEFT, padx=4)

        sf = ttk.LabelFrame(tab, text="Telemetry Status", padding=8)
        sf.pack(fill=tk.BOTH, expand=True)
        self.telemetry_display = scrolledtext.ScrolledText(
            sf, font=("Consolas", 10), bg=self.BG_DARK, fg=self.FG_LIGHT,
            state="disabled")
        self.telemetry_display.pack(fill=tk.BOTH, expand=True)

    # ══════════════════════════════════════════════════════════════════
    #  Actions
    # ══════════════════════════════════════════════════════════════════

    # ── Logging ───────────────────────────────────────────────────────

    def _log(self, message, tag="info"):
        prefix = {"info": "[INFO]", "success": "[OK]",
                  "error": "[ERROR]", "warn": "[WARN]"}
        self.console.configure(state="normal")
        self.console.insert(tk.END,
                            f"{prefix.get(tag, '[INFO]')} {message}\n", tag)
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", tk.END)
        self.console.configure(state="disabled")

    def _append_widget(self, widget, text):
        widget.configure(state="normal")
        widget.insert(tk.END, text)
        widget.see(tk.END)
        widget.configure(state="disabled")

    # ── Async command runner ──────────────────────────────────────────

    def _run_command_async(self, command, output_widget=None):
        def _run():
            try:
                proc = subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True)
                for line in proc.stdout:
                    stripped = line.rstrip()
                    if output_widget:
                        self.root.after(
                            0, self._append_widget, output_widget, line)
                    self.root.after(0, self._log, stripped)
                proc.wait()
                if proc.returncode == 0:
                    self.root.after(0, self._log,
                                   "Command completed successfully.",
                                   "success")
                else:
                    self.root.after(0, self._log,
                                   f"Command exited with code "
                                   f"{proc.returncode}", "error")
            except Exception as e:
                self.root.after(0, self._log, f"Command error: {e}", "error")

        threading.Thread(target=_run, daemon=True).start()

    # ── AI Generator actions ──────────────────────────────────────────

    def _set_prompt(self, prompt):
        self.ai_prompt.delete("1.0", tk.END)
        self.ai_prompt.insert("1.0", prompt)

    def _load_example(self, title):
        example = self.EXAMPLES[title]
        self.ai_prompt.delete("1.0", tk.END)
        self.ai_prompt.insert("1.0", example["prompt"])
        self.code_output.delete("1.0", tk.END)
        self.code_output.insert("1.0", example["code"])
        self.code_output.edit_reset()
        self.ai_status.configure(
            text=f"Loaded example: {title} (verified code)",
            foreground="green")
        self._log(f"Loaded example '{title}' with verified LFT code.",
                  "success")

    def _clear_code(self):
        self.code_output.delete("1.0", tk.END)
        self.code_output.edit_reset()

    def _copy_code(self):
        code = self.code_output.get("1.0", tk.END).strip()
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self._log("Code copied to clipboard.", "success")

    def _toggle_token(self):
        state = "normal" if self.use_api_var.get() else "disabled"
        self.token_entry.configure(state=state)

    def _generate_topology(self):
        prompt = self.ai_prompt.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning",
                                   "Please enter a topology description.")
            return

        model_key = self.MODELS[self.model_var.get()]
        use_api = self.use_api_var.get()
        token = self.token_var.get() if use_api else None

        self.ai_status.configure(
            text="Generating... (this may take a while)", foreground="blue")
        self._log(f"Generating topology with model '{model_key}', "
                  f"API={use_api}")
        self._log(f"Prompt: {prompt[:120]}...")

        def _generate():
            try:
                from profissa_lft import AITopologyGenerator
                gen = AITopologyGenerator(
                    model_name=model_key,
                    use_hf_api=use_api,
                    api_token=token)
                code = gen.generate_topology(prompt)
                valid = gen.validate_generated_code(code)
                self.root.after(0, self._on_gen_complete, code, valid)
            except Exception as e:
                self.root.after(0, self._on_gen_error, str(e))

        threading.Thread(target=_generate, daemon=True).start()

    def _on_gen_complete(self, code, valid):
        self.generated_code = code
        self.code_output.delete("1.0", tk.END)
        self.code_output.insert("1.0", code)

        if valid:
            self.ai_status.configure(
                text="Generation complete - Validation: PASSED",
                foreground="green")
            self._log("Topology generated successfully. Validation PASSED.",
                      "success")
        else:
            self.ai_status.configure(
                text="Generation complete - Validation: FAILED",
                foreground="orange")
            self._log("Topology generated but validation failed.", "warn")

    def _on_gen_error(self, error):
        self.ai_status.configure(text=f"Error: {error}", foreground="red")
        self._log(f"Generation failed: {error}", "error")
        messagebox.showerror("Generation Error",
                             f"Failed to generate topology:\n{error}")

    def _save_generated(self):
        code = self.code_output.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No generated code to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialfile="generated_topology.py")
        if filepath:
            with open(filepath, "w") as f:
                f.write(code)
            self._log(f"Code saved to {filepath}", "success")

    def _run_generated(self):
        code = self.code_output.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No generated code to run.")
            return
        if not messagebox.askyesno(
                "Confirm",
                "Run the generated topology code?\n"
                "This will create Docker containers."):
            return

        tmp = "/tmp/lft_generated_topology.py"
        with open(tmp, "w") as f:
            f.write(code)
        self._log("=" * 60)
        self._log("RUNNING TOPOLOGY CODE")
        self._log("=" * 60)
        self.ai_status.configure(text="Running...", foreground="blue")

        def _run_and_report():
            try:
                proc = subprocess.Popen(
                    f"cd {PROJECT_ROOT} && python3 -u {tmp}",
                    shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1)
                for line in proc.stdout:
                    self.root.after(0, self._log, line.rstrip())
                proc.wait()
                if proc.returncode == 0:
                    self.root.after(0, self._log,
                                   "Topology code finished successfully.",
                                   "success")
                    self.root.after(0, self.ai_status.configure,
                                   {"text": "Run complete", "foreground": "green"})
                else:
                    self.root.after(0, self._log,
                                   f"Topology code exited with code "
                                   f"{proc.returncode}", "error")
                    self.root.after(0, self.ai_status.configure,
                                   {"text": f"Run failed (exit {proc.returncode})",
                                    "foreground": "red"})
                self.root.after(0, self._log, "=" * 60)
                self.root.after(500, self._refresh_nodes)
            except Exception as e:
                self.root.after(0, self._log,
                                f"Execution error: {e}", "error")
                self.root.after(0, self.ai_status.configure,
                                {"text": f"Error: {e}", "foreground": "red"})

        threading.Thread(target=_run_and_report, daemon=True).start()

    # ── Topology Builder actions ──────────────────────────────────────

    def _on_node_type_change(self, _event=None):
        ntype = self.node_type_var.get()
        self.node_image_var.set(self.DEFAULT_IMAGES.get(ntype, ""))

    def _create_node(self):
        name = self.node_name_var.get().strip()
        image = self.node_image_var.get().strip()
        memory = self.node_memory_var.get().strip()
        cpus = self.node_cpus_var.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Please enter a node name.")
            return
        if not image:
            messagebox.showwarning("Warning", "Please enter a Docker image.")
            return

        self._log(f"Creating {self.node_type_var.get()} node '{name}'...")

        cmd = (f"docker run -d --network=none --name={name} --privileged"
               f" --dns=8.8.8.8")
        if memory:
            cmd += f" --memory={memory}"
        if cpus:
            cmd += f" --cpus={cpus}"
        cmd += f" {image}"

        def _create():
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True,
                                        text=True)
                if result.returncode == 0:
                    self.root.after(0, self._log,
                                   f"Node '{name}' created.", "success")
                    self.root.after(0, self._refresh_nodes)
                else:
                    err = result.stderr.strip()
                    self.root.after(0, self._log,
                                   f"Failed to create '{name}': {err}",
                                   "error")
            except Exception as e:
                self.root.after(0, self._log,
                                f"Error creating node: {e}", "error")

        threading.Thread(target=_create, daemon=True).start()

    def _connect_nodes(self):
        n1 = self.connect_node1_var.get().strip()
        n2 = self.connect_node2_var.get().strip()
        if1 = self.connect_if1_var.get().strip()
        if2 = self.connect_if2_var.get().strip()

        if not all([n1, n2, if1, if2]):
            messagebox.showwarning("Warning",
                                   "Please fill in all connection fields.")
            return

        self._log(f"Connecting {n1}:{if1} <-> {n2}:{if2}")

        cmd = (
            f"ip link add {if1} type veth peer name {if2} && "
            f"pid1=$(docker inspect -f '{{{{.State.Pid}}}}' {n1}) && "
            f"pid2=$(docker inspect -f '{{{{.State.Pid}}}}' {n2}) && "
            f"ip link set {if1} netns $pid1 && "
            f"ip link set {if2} netns $pid2 && "
            f"nsenter -t $pid1 -n ip link set {if1} up && "
            f"nsenter -t $pid2 -n ip link set {if2} up")
        self._run_command_async(cmd)

    def _set_ip(self):
        node = self.ip_node_var.get().strip()
        ip_addr = self.ip_addr_var.get().strip()
        mask = self.ip_mask_var.get().strip()
        iface = self.ip_if_var.get().strip()

        if not all([node, ip_addr, mask, iface]):
            messagebox.showwarning("Warning",
                                   "Please fill in all IP fields.")
            return

        self._log(f"Setting IP {ip_addr}/{mask} on {node}:{iface}")
        self._run_command_async(
            f"docker exec {node} ip addr add {ip_addr}/{mask} dev {iface}")

    def _refresh_nodes(self):
        for item in self.nodes_tree.get_children():
            self.nodes_tree.delete(item)

        def _refresh():
            try:
                result = subprocess.run(
                    "docker ps --format '{{.Names}}\\t{{.Image}}\\t{{.Status}}'",
                    shell=True, capture_output=True, text=True)
                names = []
                for line in result.stdout.strip().split("\n"):
                    if not line.strip():
                        continue
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        name, image, status = parts[0], parts[1], parts[2]
                        ntype = self._guess_type(name)
                        names.append(name)
                        self.root.after(
                            0,
                            lambda n=name, t=ntype, i=image, s=status:
                                self.nodes_tree.insert(
                                    "", tk.END, values=(n, t, i, s)))
                self.root.after(0, self._update_combos, names)
            except Exception as e:
                self.root.after(0, self._log,
                                f"Refresh failed: {e}", "error")

        threading.Thread(target=_refresh, daemon=True).start()

    @staticmethod
    def _guess_type(name):
        n = name.lower()
        if n.startswith("ue"):
            return "UE"
        if n.startswith("enb"):
            return "EnB"
        if n.startswith("epc"):
            return "EPC"
        if n.startswith("s") and len(n) <= 3:
            return "Switch"
        if n.startswith("c") or "controller" in n:
            return "Controller"
        if n.startswith("h") and len(n) <= 3:
            return "Host"
        return "Unknown"

    def _update_combos(self, names):
        self.connect_node1_combo["values"] = names
        self.connect_node2_combo["values"] = names
        self.ip_node_combo["values"] = names

    def _delete_node(self):
        sel = self.nodes_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a node to delete.")
            return
        name = self.nodes_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Delete container '{name}'?"):
            self._log(f"Deleting container '{name}'...")
            self._run_command_async(f"docker kill {name} && docker rm {name}")
            self.root.after(1500, self._refresh_nodes)

    def _delete_all_nodes(self):
        if not messagebox.askyesno(
                "Confirm",
                "Delete ALL running Docker containers?\n"
                "This affects every container, not just LFT nodes."):
            return
        self._log("Deleting all containers...", "warn")
        self._run_command_async(
            "docker kill $(docker ps -q) 2>/dev/null; "
            "docker rm $(docker ps -aq) 2>/dev/null")
        self.root.after(2500, self._refresh_nodes)

    def _browse_script(self):
        fp = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=str(PROJECT_ROOT))
        if fp:
            self.script_path_var.set(fp)

    def _run_script(self):
        script = self.script_path_var.get().strip()
        if not script:
            messagebox.showwarning("Warning", "Select a script to run.")
            return
        self._log(f"Running script: {script}")
        self._run_command_async(f"cd {PROJECT_ROOT} && python3 {script}")

    # ── Experiment actions ────────────────────────────────────────────

    def _run_experiment(self):
        ttype = self.test_type_var.get()
        tname = self.test_name_var.get().strip()
        src = self.source_ip_var.get().strip()
        dst = self.target_ip_var.get().strip()

        if not all([tname, src, dst]):
            messagebox.showwarning("Warning",
                                   "Please fill in all experiment fields.")
            return

        self._log(f"Running {ttype} experiment '{tname}': {src} -> {dst}")

        func_map = {
            "Throughput": "runThroughput",
            "RTT": "runRTT",
            "Latency": "runLatency",
        }
        func = func_map[ttype]
        code = (
            f"import sys; sys.path.insert(0, '{PROJECT_ROOT}'); "
            f"from experiment.experiment import {func}; "
            f"{func}('{tname}', '{src}', '{dst}')")

        self._run_command_async(f'python3 -c "{code}"',
                                output_widget=self.experiment_output)

    def _run_experiment_script(self, script):
        self._log(f"Running experiment: {script}")
        self._run_command_async(f"cd {PROJECT_ROOT} && python3 {script}",
                                output_widget=self.experiment_output)

    # ── Results actions ───────────────────────────────────────────────

    def _refresh_results(self):
        self.results_listbox.delete(0, tk.END)

        results_dir = PROJECT_ROOT / "results" / "data"
        if not results_dir.exists():
            return

        filt = self.result_filter_var.get().lower()

        for f in sorted(results_dir.iterdir(), key=lambda p: p.name):
            if not f.is_file():
                continue
            name = f.name
            if filt == "all":
                self.results_listbox.insert(tk.END, name)
            elif filt == "csv" and name.endswith(".csv"):
                self.results_listbox.insert(tk.END, name)
            elif filt in name.lower():
                self.results_listbox.insert(tk.END, name)

    def _on_result_select(self, _event):
        sel = self.results_listbox.curselection()
        if not sel:
            return
        filename = self.results_listbox.get(sel[0])
        filepath = PROJECT_ROOT / "results" / "data" / filename

        self.result_viewer.configure(state="normal")
        self.result_viewer.delete("1.0", tk.END)

        try:
            if filename.endswith(".json"):
                with open(filepath) as f:
                    data = json.load(f)
                text = json.dumps(data, indent=2)
                if len(text) > 60000:
                    text = text[:60000] + "\n\n... (truncated)"
                self.result_viewer.insert("1.0", text)
            else:
                with open(filepath) as f:
                    text = f.read(60000)
                self.result_viewer.insert("1.0", text)
        except Exception as e:
            self.result_viewer.insert("1.0", f"Error loading file: {e}")

        self.result_viewer.configure(state="disabled")

    def _run_analyze(self):
        self._log("Running analyzeResults.py...")
        self._run_command_async(
            f"cd {PROJECT_ROOT} && python3 results/analyzeResults.py")

    def _export_result(self):
        sel = self.results_listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a file to export.")
            return
        filename = self.results_listbox.get(sel[0])
        source = PROJECT_ROOT / "results" / "data" / filename
        dest = filedialog.asksaveasfilename(
            initialfile=filename,
            filetypes=[("All files", "*.*")])
        if dest:
            shutil.copy2(source, dest)
            self._log(f"Exported {filename} to {dest}", "success")

    # ── Monitoring actions ────────────────────────────────────────────

    def _start_visualizer(self):
        interval = self.monitor_interval_var.get()
        self._log(f"Starting real-time visualizer (interval={interval}ms)...")

        def _run_viz():
            try:
                from profissa_lft.visualizer import NetworkVisualizer
                viz = NetworkVisualizer(update_interval=int(interval))
                viz.start()
            except ImportError as e:
                self.root.after(0, self._log,
                                f"Missing dependency: {e}", "error")
            except Exception as e:
                self.root.after(0, self._log,
                                f"Visualizer error: {e}", "error")

        threading.Thread(target=_run_viz, daemon=True).start()

    def _collect_telemetry(self):
        self._log("Collecting telemetry snapshot...")

        def _collect():
            try:
                from profissa_lft.telemetry import (TelemetryStore,
                                                    TelemetryCollector)
                store = TelemetryStore()
                collector = TelemetryCollector(store)
                collector.auto_discover()
                collector.collect_all()
                summary = collector.summary()

                if not summary:
                    text = ("No telemetry data collected.\n"
                            "Make sure Docker containers are running.")
                else:
                    lines = []
                    for node in sorted(summary):
                        lines.append(f"\n--- {node} ---")
                        for metric in sorted(summary[node]):
                            val = summary[node][metric]
                            if isinstance(val, float):
                                lines.append(f"  {metric}: {val:.2f}")
                            else:
                                lines.append(f"  {metric}: {val}")
                    text = "\n".join(lines)

                self.root.after(0, self._set_telemetry_display, text)
                self.root.after(0, self._log,
                                "Telemetry snapshot collected.", "success")
            except Exception as e:
                self.root.after(0, self._log,
                                f"Telemetry error: {e}", "error")

        threading.Thread(target=_collect, daemon=True).start()

    def _set_telemetry_display(self, text):
        self.telemetry_display.configure(state="normal")
        self.telemetry_display.delete("1.0", tk.END)
        self.telemetry_display.insert("1.0", text)
        self.telemetry_display.configure(state="disabled")

    def _export_telemetry(self, fmt):
        ext = ".csv" if fmt == "csv" else ".json"
        ft = [("CSV files", "*.csv")] if fmt == "csv" else \
             [("JSON files", "*.json")]
        filepath = filedialog.asksaveasfilename(
            defaultextension=ext, filetypes=ft + [("All files", "*.*")],
            initialfile=f"telemetry_export{ext}")
        if not filepath:
            return

        def _export():
            try:
                from profissa_lft.telemetry import (TelemetryStore,
                                                    TelemetryCollector)
                store = TelemetryStore()
                collector = TelemetryCollector(store)
                collector.auto_discover()
                collector.collect_all()
                if fmt == "csv":
                    store.export_csv(filepath)
                else:
                    store.export_json(filepath)
                self.root.after(0, self._log,
                                f"Telemetry exported to {filepath}",
                                "success")
            except Exception as e:
                self.root.after(0, self._log,
                                f"Export error: {e}", "error")

        threading.Thread(target=_export, daemon=True).start()


def main():
    root = tk.Tk()
    LFTGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
