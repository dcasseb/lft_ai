#!/usr/bin/env python3
"""
LFT Network Visualizer
Real-time graph visualization for emulated networks.
Uses the telemetry module for parallel data collection.
"""

import sys

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import networkx as nx
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from .telemetry import TelemetryStore, TelemetryCollector, guess_node_type, get_docker_client


class NetworkVisualizer:
    """Real-time network topology and traffic visualizer"""

    _LAYOUT_PARAMS = dict(k=2, iterations=50, seed=42)

    NODE_TYPE_COLORS = {
        'host': '#4CAF50',      # Green
        'switch': '#2196F3',    # Blue
        'controller': '#FF9800', # Orange
        'ue': '#9C27B0',        # Purple
        'enb': '#E91E63',       # Pink
        'epc': '#F44336',       # Red
        'unknown': '#9E9E9E'    # Gray
    }

    def __init__(self, update_interval=1000, telemetry_store=None):
        """
        Initialize the network visualizer.

        Args:
            update_interval: Update interval in milliseconds (default: 1000ms = 1s)
            telemetry_store: Optional TelemetryStore instance to share with external code.
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for visualization. "
                              "Install with: pip install matplotlib networkx")

        self.update_interval = update_interval
        self.graph = nx.Graph()

        # Single Docker client — shared with telemetry collector
        self._docker_client = get_docker_client()

        # Telemetry — pass our docker client to avoid a second connection
        self.store = telemetry_store or TelemetryStore()
        self.collector = TelemetryCollector(
            self.store, docker_client=self._docker_client
        )

        # Figure handles
        self.fig = None
        self.ax_topology = None
        self.ax_cpu = None
        self.ax_memory = None
        self.ax_network = None
        self.ax_latency = None
        self.animation_obj = None

        # Cached layout
        self._cached_layout = None

    def detect_network_topology(self):
        """Detect running network topology from Docker containers."""
        if not self._docker_client:
            return

        try:
            containers = self._docker_client.containers.list()
            self.graph.clear()

            for container in containers:
                name = container.name
                labels = container.labels
                node_type = labels.get('lft.type', guess_node_type(name))

                self.graph.add_node(
                    name,
                    type=node_type,
                    container_id=container.id,
                    status=container.status
                )
                self.collector.register_container(name, node_type)

            self._detect_connections()

            if len(self.graph.nodes()) > 0:
                self._cached_layout = nx.spring_layout(self.graph, **self._LAYOUT_PARAMS)
            else:
                self._cached_layout = None

        except Exception as e:
            print(f"Error detecting topology: {e}")

    def _detect_connections(self):
        """Detect connections between nodes."""
        nodes = list(self.graph.nodes())

        hosts = [n for n in nodes if self.graph.nodes[n]['type'] == 'host']
        switches = [n for n in nodes if self.graph.nodes[n]['type'] == 'switch']
        controllers = [n for n in nodes if self.graph.nodes[n]['type'] == 'controller']

        if switches:
            for host in hosts:
                self.graph.add_edge(host, switches[0], weight=1.0)
            for switch in switches:
                for controller in controllers:
                    self.graph.add_edge(switch, controller, weight=1.0)

        ues = [n for n in nodes if self.graph.nodes[n]['type'] == 'ue']
        enbs = [n for n in nodes if self.graph.nodes[n]['type'] == 'enb']
        epcs = [n for n in nodes if self.graph.nodes[n]['type'] == 'epc']

        for ue in ues:
            if enbs:
                self.graph.add_edge(ue, enbs[0], weight=1.0)
        for enb in enbs:
            if epcs:
                self.graph.add_edge(enb, epcs[0], weight=1.0)

    def _build_legend(self, ax):
        """Build the node type legend on the given axis."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=node_type.capitalize(),
                      markerfacecolor=color, markersize=10)
            for node_type, color in self.NODE_TYPE_COLORS.items()
            if node_type != 'unknown'
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    def _node_color(self, node):
        ntype = self.graph.nodes.get(node, {}).get('type', 'unknown')
        return self.NODE_TYPE_COLORS.get(ntype, '#9E9E9E')

    def setup_figure(self):
        """Setup the matplotlib figure with subplots."""
        self.fig = plt.figure(figsize=(18, 12))
        self.fig.suptitle('LFT Network Real-Time Monitoring', fontsize=16, fontweight='bold')

        gs = self.fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.35, wspace=0.3)

        self.ax_topology = self.fig.add_subplot(gs[0, :])
        self.ax_cpu = self.fig.add_subplot(gs[1, 0])
        self.ax_memory = self.fig.add_subplot(gs[1, 1])
        self.ax_network = self.fig.add_subplot(gs[2, 0])
        self.ax_latency = self.fig.add_subplot(gs[2, 1])

    def update_plot(self, frame):
        """Update plot for animation.

        Data collection happens in a background thread (started in start()),
        so this method only reads from the store — it never blocks on Docker.
        """
        if frame > 0 and frame % 10 == 0:
            self.detect_network_topology()

        self.ax_topology.clear()
        self.draw_topology()
        self._draw_cpu()
        self._draw_memory()
        self._draw_network()
        self._draw_latency()

        return self.ax_topology, self.ax_cpu, self.ax_memory, self.ax_network, self.ax_latency

    def draw_topology(self):
        """Draw the network topology."""
        if len(self.graph.nodes()) == 0:
            self.ax_topology.text(0.5, 0.5, 'No network detected\nRun a topology first!',
                                 ha='center', va='center', fontsize=14, color='red')
            self.ax_topology.set_xlim([0, 1])
            self.ax_topology.set_ylim([0, 1])
            return

        pos = self._cached_layout
        if pos is None:
            pos = nx.spring_layout(self.graph, **self._LAYOUT_PARAMS)

        nx.draw_networkx_edges(
            self.graph, pos, edge_color='#CCCCCC', width=2.0, alpha=0.6, ax=self.ax_topology
        )

        node_colors = [self._node_color(n) for n in self.graph.nodes()]
        node_sizes = [2000 if self.graph.nodes[n].get('type') == 'switch' else 1500
                      for n in self.graph.nodes()]

        nx.draw_networkx_nodes(
            self.graph, pos, node_color=node_colors, node_size=node_sizes,
            alpha=0.9, ax=self.ax_topology
        )
        nx.draw_networkx_labels(
            self.graph, pos, font_size=10, font_weight='bold', ax=self.ax_topology
        )

        for node, (x, y) in pos.items():
            status = self.graph.nodes[node].get('status', 'unknown')
            status_color = '#4CAF50' if status == 'running' else '#F44336'
            self.ax_topology.plot(x, y + 0.08, 'o', color=status_color, markersize=8,
                                 markeredgecolor='white', markeredgewidth=2, zorder=10)

        self.ax_topology.set_title('Network Topology', fontsize=14, fontweight='bold')
        self.ax_topology.axis('off')
        self._build_legend(self.ax_topology)

    def _draw_timeseries(self, ax, metric, title, ylabel, ylim=None, filter_fn=None):
        """Generic helper to draw a per-node time-series on an axis."""
        ax.clear()
        ax.set_title(title, fontsize=12)
        ax.set_xlabel('Samples')
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(ylim)
        ax.grid(True, alpha=0.3)

        has_data = False
        for node in self.store.nodes():
            series = self.store.get(node, metric)
            if series:
                values = [v for _, v in series]
                if filter_fn:
                    values = [v for v in values if filter_fn(v)]
                if values:
                    ax.plot(values, label=node, color=self._node_color(node), linewidth=2)
                    has_data = True

        if has_data:
            ax.legend(loc='upper right', fontsize=8)

    def _draw_cpu(self):
        self._draw_timeseries(self.ax_cpu, 'cpu_pct', 'CPU Usage (%)', 'CPU %', ylim=[0, 100])

    def _draw_memory(self):
        self._draw_timeseries(self.ax_memory, 'mem_mb', 'Memory Usage (MB)', 'MB')

    def _draw_network(self):
        """Draw network throughput (KB/s) derived from cumulative byte counters."""
        ax = self.ax_network
        ax.clear()
        ax.set_title('Network Throughput (KB/s)', fontsize=12)
        ax.set_xlabel('Samples')
        ax.set_ylabel('KB/s')
        ax.grid(True, alpha=0.3)

        has_data = False
        for node in self.store.nodes():
            rx = self.store.get(node, 'rx_bytes')
            tx = self.store.get(node, 'tx_bytes')
            if len(rx) > 1 and len(tx) > 1:
                throughput = []
                for i in range(1, min(len(rx), len(tx))):
                    dt = rx[i][0] - rx[i-1][0]
                    if dt > 0:
                        db = (rx[i][1] + tx[i][1]) - (rx[i-1][1] + tx[i-1][1])
                        throughput.append(db / dt / 1024)
                    else:
                        throughput.append(0)
                if throughput:
                    ax.plot(throughput, label=node, color=self._node_color(node), linewidth=2)
                    has_data = True

        if has_data:
            ax.legend(loc='upper right', fontsize=8)

    def _draw_latency(self):
        self._draw_timeseries(
            self.ax_latency, 'rtt_avg', 'Latency (ms)', 'RTT ms',
            filter_fn=lambda v: v >= 0
        )

    def start(self):
        """Start the real-time visualization.

        Telemetry collection runs in a background daemon thread so the GUI
        never blocks on Docker API calls.
        """
        try:
            matplotlib.use('TkAgg')
        except Exception:
            pass

        print("Starting LFT Network Visualizer...")
        print("Detecting network topology...")

        self.detect_network_topology()

        if len(self.graph.nodes()) == 0:
            print("Warning: No network detected. Make sure containers are running.")
        else:
            print(f"Detected {len(self.graph.nodes())} nodes and {len(self.graph.edges())} connections")

        self.collector.start_background(interval=self.update_interval / 1000.0)

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
        """Stop the visualization and background collection."""
        self.collector.stop_background()
        if self.animation_obj:
            self.animation_obj.event_source.stop()
        plt.close('all')
        print("Visualization stopped.")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='LFT Network Real-Time Visualizer')
    parser.add_argument(
        '--interval', type=int, default=1000,
        help='Update interval in milliseconds (default: 1000)'
    )
    parser.add_argument(
        '--export-csv', type=str, default=None,
        help='Export telemetry data to CSV on exit'
    )
    parser.add_argument(
        '--export-json', type=str, default=None,
        help='Export telemetry data to JSON on exit'
    )

    args = parser.parse_args()

    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required. Install with: pip install matplotlib networkx")
        sys.exit(1)

    if not HAS_DOCKER:
        print("Warning: docker-py not found. Container monitoring will be limited.")

    store = TelemetryStore()
    visualizer = NetworkVisualizer(update_interval=args.interval, telemetry_store=store)

    try:
        visualizer.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        visualizer.stop()
    finally:
        if args.export_csv:
            store.export_csv(args.export_csv)
            print(f"Telemetry exported to {args.export_csv}")
        if args.export_json:
            store.export_json(args.export_json)
            print(f"Telemetry exported to {args.export_json}")


if __name__ == "__main__":
    main()
