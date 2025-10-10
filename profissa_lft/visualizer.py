#!/usr/bin/env python3
"""
LFT Network Visualizer
Real-time graph visualization for emulated networks
"""

import os
import sys
import time
import threading
import subprocess
import json
from collections import defaultdict, deque
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('TkAgg')  # Use TkAgg backend for interactive display
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
    import networkx as nx
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

try:
    import docker
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False
    print("Warning: docker-py not available. Install with: pip install docker")


class NetworkVisualizer:
    """Real-time network topology and traffic visualizer"""
    
    def __init__(self, update_interval=1000):
        """
        Initialize the network visualizer
        
        Args:
            update_interval: Update interval in milliseconds (default: 1000ms = 1s)
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for visualization")
        
        self.update_interval = update_interval
        self.graph = nx.Graph()
        self.node_colors = {}
        self.node_sizes = {}
        self.node_labels = {}
        self.edge_colors = {}
        self.edge_widths = {}
        
        # Docker client for container monitoring
        self.docker_client = docker.from_env() if HAS_DOCKER else None
        
        # Statistics storage
        self.stats_history = defaultdict(lambda: deque(maxlen=100))
        self.traffic_history = defaultdict(lambda: deque(maxlen=50))
        
        # Figure setup
        self.fig = None
        self.ax_topology = None
        self.ax_stats = None
        self.animation_obj = None
        
        # Node types and their colors
        self.node_type_colors = {
            'host': '#4CAF50',      # Green
            'switch': '#2196F3',    # Blue
            'controller': '#FF9800', # Orange
            'ue': '#9C27B0',        # Purple
            'enb': '#E91E63',       # Pink
            'epc': '#F44336',       # Red
            'unknown': '#9E9E9E'    # Gray
        }
        
        # Running state
        self.running = False
        self.monitor_thread = None
    
    def detect_network_topology(self):
        """Detect running network topology from Docker containers"""
        if not self.docker_client:
            print("Docker client not available")
            return
        
        try:
            containers = self.docker_client.containers.list()
            
            # Clear existing graph
            self.graph.clear()
            
            for container in containers:
                name = container.name
                labels = container.labels
                
                # Detect node type from container name or labels
                node_type = 'unknown'
                if name.startswith('h') and len(name) <= 3:
                    node_type = 'host'
                elif name.startswith('s') and len(name) <= 3:
                    node_type = 'switch'
                elif name.startswith('c') or 'controller' in name.lower():
                    node_type = 'controller'
                elif name.startswith('ue'):
                    node_type = 'ue'
                elif name.startswith('enb'):
                    node_type = 'enb'
                elif name.startswith('epc'):
                    node_type = 'epc'
                
                # Add node to graph
                self.graph.add_node(
                    name,
                    type=node_type,
                    container_id=container.id,
                    status=container.status
                )
                
                self.node_colors[name] = self.node_type_colors.get(node_type, '#9E9E9E')
                self.node_sizes[name] = 2000 if node_type == 'switch' else 1500
                
                # Get network connections
                networks = container.attrs.get('NetworkSettings', {}).get('Networks', {})
                for network_name, network_info in networks.items():
                    # Store network info for edge detection
                    pass
            
            # Detect edges (connections) based on network bridges
            self._detect_connections()
            
        except Exception as e:
            print(f"Error detecting topology: {e}")
    
    def _detect_connections(self):
        """Detect connections between nodes"""
        # This is a simplified version - in reality, you'd inspect bridge networks
        # For demonstration, we'll create logical connections
        
        nodes = list(self.graph.nodes())
        
        # Connect hosts to switches
        hosts = [n for n in nodes if self.graph.nodes[n]['type'] == 'host']
        switches = [n for n in nodes if self.graph.nodes[n]['type'] == 'switch']
        controllers = [n for n in nodes if self.graph.nodes[n]['type'] == 'controller']
        
        # Simple topology: hosts -> switches -> controllers
        if switches:
            for host in hosts:
                # Connect each host to first switch (simplified)
                if switches:
                    self.graph.add_edge(host, switches[0], weight=1.0)
            
            # Connect switches to controllers
            for switch in switches:
                for controller in controllers:
                    self.graph.add_edge(switch, controller, weight=1.0)
        
        # Wireless connections
        ues = [n for n in nodes if self.graph.nodes[n]['type'] == 'ue']
        enbs = [n for n in nodes if self.graph.nodes[n]['type'] == 'enb']
        epcs = [n for n in nodes if self.graph.nodes[n]['type'] == 'epc']
        
        for ue in ues:
            if enbs:
                self.graph.add_edge(ue, enbs[0], weight=1.0)
        
        for enb in enbs:
            if epcs:
                self.graph.add_edge(enb, epcs[0], weight=1.0)
    
    def get_container_stats(self, container_id):
        """Get real-time statistics from a container"""
        if not self.docker_client:
            return {}
        
        try:
            container = self.docker_client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Parse CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Parse memory usage
            mem_usage = stats['memory_stats'].get('usage', 0)
            mem_limit = stats['memory_stats'].get('limit', 1)
            mem_percent = (mem_usage / mem_limit) * 100.0
            
            # Parse network I/O
            networks = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in networks.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in networks.values())
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': mem_percent,
                'memory_usage_mb': mem_usage / (1024 * 1024),
                'rx_bytes': rx_bytes,
                'tx_bytes': tx_bytes,
                'timestamp': time.time()
            }
        
        except Exception as e:
            print(f"Error getting stats for {container_id}: {e}")
            return {}
    
    def update_statistics(self):
        """Update statistics for all nodes"""
        for node, data in self.graph.nodes(data=True):
            if 'container_id' in data:
                stats = self.get_container_stats(data['container_id'])
                if stats:
                    # Store in history
                    self.stats_history[node].append({
                        'timestamp': stats['timestamp'],
                        'cpu': stats['cpu_percent'],
                        'memory': stats['memory_percent'],
                        'rx': stats['rx_bytes'],
                        'tx': stats['tx_bytes']
                    })
    
    def setup_figure(self):
        """Setup the matplotlib figure with subplots"""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('LFT Network Real-Time Visualization', fontsize=16, fontweight='bold')
        
        # Create grid layout
        gs = self.fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.3, wspace=0.3)
        
        # Topology view (large, top-left and top-right)
        self.ax_topology = self.fig.add_subplot(gs[0, :])
        self.ax_topology.set_title('Network Topology', fontsize=14, fontweight='bold')
        self.ax_topology.axis('off')
        
        # Statistics plots (bottom)
        self.ax_cpu = self.fig.add_subplot(gs[1, 0])
        self.ax_cpu.set_title('CPU Usage (%)', fontsize=12)
        self.ax_cpu.set_xlabel('Time')
        self.ax_cpu.set_ylabel('CPU %')
        self.ax_cpu.set_ylim([0, 100])
        
        self.ax_network = self.fig.add_subplot(gs[1, 1])
        self.ax_network.set_title('Network Traffic (KB/s)', fontsize=12)
        self.ax_network.set_xlabel('Time')
        self.ax_network.set_ylabel('KB/s')
        
        # Add legend for node types
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=node_type.capitalize(),
                      markerfacecolor=color, markersize=10)
            for node_type, color in self.node_type_colors.items()
            if node_type != 'unknown'
        ]
        self.ax_topology.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    def update_plot(self, frame):
        """Update plot for animation"""
        # Detect topology changes
        if frame % 10 == 0:  # Re-detect every 10 frames
            self.detect_network_topology()
        
        # Update statistics
        self.update_statistics()
        
        # Clear axes
        self.ax_topology.clear()
        self.ax_cpu.clear()
        self.ax_network.clear()
        
        # Redraw topology
        self.draw_topology()
        
        # Redraw statistics
        self.draw_statistics()
        
        return self.ax_topology, self.ax_cpu, self.ax_network
    
    def draw_topology(self):
        """Draw the network topology"""
        if len(self.graph.nodes()) == 0:
            self.ax_topology.text(0.5, 0.5, 'No network detected\nRun a topology first!',
                                 ha='center', va='center', fontsize=14, color='red')
            self.ax_topology.set_xlim([0, 1])
            self.ax_topology.set_ylim([0, 1])
            return
        
        # Calculate layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        
        # Draw edges
        edge_colors = ['#CCCCCC' for _ in self.graph.edges()]
        edge_widths = [2.0 for _ in self.graph.edges()]
        
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color=edge_colors,
            width=edge_widths,
            alpha=0.6,
            ax=self.ax_topology
        )
        
        # Draw nodes
        node_colors = [self.node_colors.get(node, '#9E9E9E') for node in self.graph.nodes()]
        node_sizes = [self.node_sizes.get(node, 1500) for node in self.graph.nodes()]
        
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            ax=self.ax_topology
        )
        
        # Draw labels
        labels = {node: node for node in self.graph.nodes()}
        nx.draw_networkx_labels(
            self.graph, pos,
            labels=labels,
            font_size=10,
            font_weight='bold',
            ax=self.ax_topology
        )
        
        # Draw status indicators
        for node, (x, y) in pos.items():
            data = self.graph.nodes[node]
            status = data.get('status', 'unknown')
            
            # Add status indicator (small circle)
            status_color = '#4CAF50' if status == 'running' else '#F44336'
            self.ax_topology.plot(x, y + 0.08, 'o', color=status_color, markersize=8, 
                                 markeredgecolor='white', markeredgewidth=2, zorder=10)
        
        self.ax_topology.set_title('Network Topology', fontsize=14, fontweight='bold')
        self.ax_topology.axis('off')
        
        # Re-add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=node_type.capitalize(),
                      markerfacecolor=color, markersize=10)
            for node_type, color in self.node_type_colors.items()
            if node_type != 'unknown'
        ]
        self.ax_topology.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    def draw_statistics(self):
        """Draw statistics plots"""
        # CPU usage plot
        self.ax_cpu.clear()
        self.ax_cpu.set_title('CPU Usage (%)', fontsize=12)
        self.ax_cpu.set_xlabel('Samples')
        self.ax_cpu.set_ylabel('CPU %')
        self.ax_cpu.set_ylim([0, 100])
        self.ax_cpu.grid(True, alpha=0.3)
        
        for node, history in self.stats_history.items():
            if len(history) > 0:
                cpu_values = [s['cpu'] for s in history]
                color = self.node_colors.get(node, '#9E9E9E')
                self.ax_cpu.plot(cpu_values, label=node, color=color, linewidth=2)
        
        if len(self.stats_history) > 0:
            self.ax_cpu.legend(loc='upper right', fontsize=8)
        
        # Network traffic plot
        self.ax_network.clear()
        self.ax_network.set_title('Network Traffic (KB/s)', fontsize=12)
        self.ax_network.set_xlabel('Samples')
        self.ax_network.set_ylabel('KB/s')
        self.ax_network.grid(True, alpha=0.3)
        
        for node, history in self.stats_history.items():
            if len(history) > 1:
                # Calculate throughput (delta bytes / delta time)
                throughput = []
                for i in range(1, len(history)):
                    delta_bytes = (history[i]['rx'] + history[i]['tx']) - \
                                 (history[i-1]['rx'] + history[i-1]['tx'])
                    delta_time = history[i]['timestamp'] - history[i-1]['timestamp']
                    if delta_time > 0:
                        throughput.append((delta_bytes / delta_time) / 1024)  # KB/s
                    else:
                        throughput.append(0)
                
                if throughput:
                    color = self.node_colors.get(node, '#9E9E9E')
                    self.ax_network.plot(throughput, label=node, color=color, linewidth=2)
        
        if len(self.stats_history) > 0:
            self.ax_network.legend(loc='upper right', fontsize=8)
    
    def start(self):
        """Start the real-time visualization"""
        if not HAS_MATPLOTLIB:
            print("Error: matplotlib is required")
            return
        
        print("Starting LFT Network Visualizer...")
        print("Detecting network topology...")
        
        # Initial topology detection
        self.detect_network_topology()
        
        if len(self.graph.nodes()) == 0:
            print("Warning: No network detected. Make sure containers are running.")
        else:
            print(f"Detected {len(self.graph.nodes())} nodes and {len(self.graph.edges())} connections")
        
        # Setup figure
        self.setup_figure()
        
        # Start animation
        self.running = True
        self.animation_obj = animation.FuncAnimation(
            self.fig,
            self.update_plot,
            interval=self.update_interval,
            blit=False,
            cache_frame_data=False
        )
        
        print("Visualization started!")
        print("Close the window to stop.")
        
        try:
            plt.show()
        except KeyboardInterrupt:
            print("\nStopping visualization...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the visualization"""
        self.running = False
        if self.animation_obj:
            self.animation_obj.event_source.stop()
        plt.close('all')
        print("Visualization stopped.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LFT Network Real-Time Visualizer')
    parser.add_argument(
        '--interval',
        type=int,
        default=1000,
        help='Update interval in milliseconds (default: 1000)'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required")
        print("Install with: pip install matplotlib")
        sys.exit(1)
    
    if not HAS_DOCKER:
        print("Warning: docker-py not found. Container monitoring will be limited.")
        print("Install with: pip install docker")
    
    # Create and start visualizer
    visualizer = NetworkVisualizer(update_interval=args.interval)
    
    try:
        visualizer.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        visualizer.stop()


if __name__ == "__main__":
    main()
