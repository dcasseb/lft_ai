#!/usr/bin/env python3
"""
LFT Network Visualizer
Real-time graph visualization for emulated networks
"""

import os
import sys
import time
from collections import defaultdict, deque

try:
    import matplotlib
    matplotlib.use('TkAgg')  # Use TkAgg backend for interactive display
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import networkx as nx
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import docker
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False


class NetworkVisualizer:
    """Real-time network topology and traffic visualizer"""

    NODE_TYPE_COLORS = {
        'host': '#4CAF50',      # Green
        'switch': '#2196F3',    # Blue
        'controller': '#FF9800', # Orange
        'ue': '#9C27B0',        # Purple
        'enb': '#E91E63',       # Pink
        'epc': '#F44336',       # Red
        'unknown': '#9E9E9E'    # Gray
    }

    def __init__(self, update_interval=1000):
        """
        Initialize the network visualizer

        Args:
            update_interval: Update interval in milliseconds (default: 1000ms = 1s)
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for visualization. "
                              "Install with: pip install matplotlib networkx")

        self.update_interval = update_interval
        self.graph = nx.Graph()

        # Docker client for container monitoring
        self.docker_client = docker.from_env() if HAS_DOCKER else None

        # Statistics storage
        self.stats_history = defaultdict(lambda: deque(maxlen=100))

        # Figure setup
        self.fig = None
        self.ax_topology = None
        self.animation_obj = None

        # Cached layout — recomputed only when topology changes
        self._cached_layout = None

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

                # Detect node type from container labels first, then fall back to name
                node_type = labels.get('lft.type', self._guess_node_type(name))

                # Add node to graph
                self.graph.add_node(
                    name,
                    type=node_type,
                    container_id=container.id,
                    status=container.status
                )

            # Detect edges (connections) based on network bridges
            self._detect_connections()

            # Recompute layout for the new topology
            if len(self.graph.nodes()) > 0:
                self._cached_layout = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
            else:
                self._cached_layout = None

        except Exception as e:
            print(f"Error detecting topology: {e}")

    @staticmethod
    def _guess_node_type(name):
        """Guess node type from container name (fallback heuristic)."""
        if name.startswith('h') and len(name) <= 3:
            return 'host'
        elif name.startswith('s') and len(name) <= 3:
            return 'switch'
        elif name.startswith('c') or 'controller' in name.lower():
            return 'controller'
        elif name.startswith('ue'):
            return 'ue'
        elif name.startswith('enb'):
            return 'enb'
        elif name.startswith('epc'):
            return 'epc'
        return 'unknown'

    def _detect_connections(self):
        """Detect connections between nodes"""
        nodes = list(self.graph.nodes())

        hosts = [n for n in nodes if self.graph.nodes[n]['type'] == 'host']
        switches = [n for n in nodes if self.graph.nodes[n]['type'] == 'switch']
        controllers = [n for n in nodes if self.graph.nodes[n]['type'] == 'controller']

        # Simple topology: hosts -> switches -> controllers
        if switches:
            for host in hosts:
                self.graph.add_edge(host, switches[0], weight=1.0)

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
            return {}

    def update_statistics(self):
        """Update statistics for all nodes"""
        for node, data in self.graph.nodes(data=True):
            if 'container_id' in data:
                stats = self.get_container_stats(data['container_id'])
                if stats:
                    self.stats_history[node].append({
                        'timestamp': stats['timestamp'],
                        'cpu': stats['cpu_percent'],
                        'memory': stats['memory_percent'],
                        'rx': stats['rx_bytes'],
                        'tx': stats['tx_bytes']
                    })

    def _build_legend(self, ax):
        """Build the node type legend on the given axis."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=node_type.capitalize(),
                      markerfacecolor=color, markersize=10)
            for node_type, color in self.NODE_TYPE_COLORS.items()
            if node_type != 'unknown'
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    def setup_figure(self):
        """Setup the matplotlib figure with subplots"""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('LFT Network Real-Time Visualization', fontsize=16, fontweight='bold')

        # Create grid layout
        gs = self.fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.3, wspace=0.3)

        # Topology view (large, spans both columns)
        self.ax_topology = self.fig.add_subplot(gs[0, :])

        # Statistics plots (bottom)
        self.ax_cpu = self.fig.add_subplot(gs[1, 0])
        self.ax_network = self.fig.add_subplot(gs[1, 1])

    def update_plot(self, frame):
        """Update plot for animation"""
        # Re-detect topology periodically
        if frame % 10 == 0:
            self.detect_network_topology()

        # Update statistics
        self.update_statistics()

        # Clear and redraw
        self.ax_topology.clear()
        self.draw_topology()
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

        pos = self._cached_layout
        if pos is None:
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

        # Draw edges
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color='#CCCCCC',
            width=2.0,
            alpha=0.6,
            ax=self.ax_topology
        )

        # Draw nodes
        node_colors = [self.NODE_TYPE_COLORS.get(self.graph.nodes[n].get('type', 'unknown'), '#9E9E9E')
                       for n in self.graph.nodes()]
        node_sizes = [2000 if self.graph.nodes[n].get('type') == 'switch' else 1500
                      for n in self.graph.nodes()]

        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            ax=self.ax_topology
        )

        # Draw labels
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=10,
            font_weight='bold',
            ax=self.ax_topology
        )

        # Draw status indicators
        for node, (x, y) in pos.items():
            status = self.graph.nodes[node].get('status', 'unknown')
            status_color = '#4CAF50' if status == 'running' else '#F44336'
            self.ax_topology.plot(x, y + 0.08, 'o', color=status_color, markersize=8,
                                 markeredgecolor='white', markeredgewidth=2, zorder=10)

        self.ax_topology.set_title('Network Topology', fontsize=14, fontweight='bold')
        self.ax_topology.axis('off')
        self._build_legend(self.ax_topology)

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
                color = self.NODE_TYPE_COLORS.get(
                    self.graph.nodes.get(node, {}).get('type', 'unknown'), '#9E9E9E')
                self.ax_cpu.plot(cpu_values, label=node, color=color, linewidth=2)

        if self.stats_history:
            self.ax_cpu.legend(loc='upper right', fontsize=8)

        # Network traffic plot
        self.ax_network.clear()
        self.ax_network.set_title('Network Traffic (KB/s)', fontsize=12)
        self.ax_network.set_xlabel('Samples')
        self.ax_network.set_ylabel('KB/s')
        self.ax_network.grid(True, alpha=0.3)

        for node, history in self.stats_history.items():
            if len(history) > 1:
                throughput = []
                for i in range(1, len(history)):
                    delta_bytes = (history[i]['rx'] + history[i]['tx']) - \
                                 (history[i-1]['rx'] + history[i-1]['tx'])
                    delta_time = history[i]['timestamp'] - history[i-1]['timestamp']
                    if delta_time > 0:
                        throughput.append((delta_bytes / delta_time) / 1024)
                    else:
                        throughput.append(0)

                if throughput:
                    color = self.NODE_TYPE_COLORS.get(
                        self.graph.nodes.get(node, {}).get('type', 'unknown'), '#9E9E9E')
                    self.ax_network.plot(throughput, label=node, color=color, linewidth=2)

        if self.stats_history:
            self.ax_network.legend(loc='upper right', fontsize=8)

    def start(self):
        """Start the real-time visualization"""
        print("Starting LFT Network Visualizer...")
        print("Detecting network topology...")

        self.detect_network_topology()

        if len(self.graph.nodes()) == 0:
            print("Warning: No network detected. Make sure containers are running.")
        else:
            print(f"Detected {len(self.graph.nodes())} nodes and {len(self.graph.edges())} connections")

        self.setup_figure()

        self.animation_obj = animation.FuncAnimation(
            self.fig,
            self.update_plot,
            interval=self.update_interval,
            blit=False,
            cache_frame_data=False
        )

        print("Visualization started! Close the window to stop.")

        try:
            plt.show()
        except KeyboardInterrupt:
            print("\nStopping visualization...")
        finally:
            self.stop()

    def stop(self):
        """Stop the visualization"""
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

    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required. Install with: pip install matplotlib networkx")
        sys.exit(1)

    if not HAS_DOCKER:
        print("Warning: docker-py not found. Container monitoring will be limited.")
        print("Install with: pip install docker")

    visualizer = NetworkVisualizer(update_interval=args.interval)

    try:
        visualizer.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        visualizer.stop()


if __name__ == "__main__":
    main()
