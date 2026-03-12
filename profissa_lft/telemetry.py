#!/usr/bin/env python3
"""
LFT Network Telemetry Module
Collects real-time metrics from Docker containers, OVS switches, and network links.
Feeds data to the visualizer or exports to CSV/JSON.
"""

import time
import subprocess
import json
import re
import csv
import logging
import threading
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Any, Set, Tuple

try:
    import docker
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False


def get_docker_client():
    """Create a Docker client from the environment, or return None."""
    if not HAS_DOCKER:
        return None
    try:
        return docker.from_env()
    except Exception:
        return None


def guess_node_type(name: str) -> str:
    """Guess LFT node type from container name (fallback heuristic)."""
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


class TelemetryStore:
    """Thread-safe rolling time-series store for telemetry data."""

    def __init__(self, maxlen: int = 300):
        self.maxlen = maxlen
        self._lock = threading.Lock()
        self._data: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=maxlen))
        )

    def append(self, node: str, metric: str, value: float, timestamp: float = None):
        if timestamp is None:
            timestamp = time.time()
        with self._lock:
            self._data[node][metric].append((timestamp, value))

    def get(self, node: str, metric: str) -> List[Tuple[float, float]]:
        with self._lock:
            if node in self._data and metric in self._data[node]:
                return list(self._data[node][metric])
            return []

    def get_latest(self, node: str, metric: str) -> Optional[Tuple[float, float]]:
        with self._lock:
            if node in self._data and metric in self._data[node]:
                d = self._data[node][metric]
                return d[-1] if d else None
            return None

    def nodes(self) -> List[str]:
        with self._lock:
            return list(self._data.keys())

    def metrics(self, node: str) -> List[str]:
        with self._lock:
            if node in self._data:
                return list(self._data[node].keys())
            return []

    def clear(self):
        with self._lock:
            self._data.clear()

    def export_csv(self, filepath: str):
        with self._lock:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'node', 'metric', 'value'])
                for node in sorted(self._data):
                    for metric in sorted(self._data[node]):
                        for ts, val in self._data[node][metric]:
                            writer.writerow([ts, node, metric, val])

    def export_json(self, filepath: str):
        with self._lock:
            out = {}
            for node in self._data:
                out[node] = {}
                for metric in self._data[node]:
                    out[node][metric] = [
                        {'timestamp': ts, 'value': val}
                        for ts, val in self._data[node][metric]
                    ]
            serialized = json.dumps(out, indent=2)
        with open(filepath, 'w') as f:
            f.write(serialized)


class ContainerCollector:
    """Collects per-container metrics via the Docker API."""

    def __init__(self, docker_client):
        self.client = docker_client
        self.logger = logging.getLogger(__name__)

    def collect(self, container_name: str) -> Dict[str, float]:
        """Collect CPU, memory, and aggregate network stats for a container."""
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)

            # CPU — Podman may omit system_cpu_usage from precpu_stats
            cpu_delta = (stats['cpu_stats']['cpu_usage']['total_usage']
                         - stats['precpu_stats']['cpu_usage']['total_usage'])
            sys_cur = stats['cpu_stats'].get('system_cpu_usage', 0)
            sys_pre = stats['precpu_stats'].get('system_cpu_usage', 0)
            system_delta = sys_cur - sys_pre
            online_cpus = stats['cpu_stats'].get('online_cpus', 1)
            cpu_pct = (cpu_delta / system_delta * online_cpus * 100.0) if system_delta > 0 else 0.0

            # Memory
            mem_usage = stats['memory_stats'].get('usage', 0)
            mem_limit = stats['memory_stats'].get('limit', 1)
            mem_pct = (mem_usage / mem_limit) * 100.0
            mem_mb = mem_usage / (1024 * 1024)

            # Network (aggregate across all interfaces)
            networks = stats.get('networks', {})
            rx_bytes = sum(n.get('rx_bytes', 0) for n in networks.values())
            tx_bytes = sum(n.get('tx_bytes', 0) for n in networks.values())
            rx_packets = sum(n.get('rx_packets', 0) for n in networks.values())
            tx_packets = sum(n.get('tx_packets', 0) for n in networks.values())
            rx_errors = sum(n.get('rx_errors', 0) for n in networks.values())
            tx_errors = sum(n.get('tx_errors', 0) for n in networks.values())
            rx_dropped = sum(n.get('rx_dropped', 0) for n in networks.values())
            tx_dropped = sum(n.get('tx_dropped', 0) for n in networks.values())

            return {
                'cpu_pct': cpu_pct,
                'mem_pct': mem_pct,
                'mem_mb': mem_mb,
                'rx_bytes': rx_bytes,
                'tx_bytes': tx_bytes,
                'rx_packets': rx_packets,
                'tx_packets': tx_packets,
                'rx_errors': rx_errors,
                'tx_errors': tx_errors,
                'rx_dropped': rx_dropped,
                'tx_dropped': tx_dropped,
            }
        except Exception as e:
            self.logger.debug(f"Container stats failed for {container_name}: {e}")
            return {}


class OVSCollector:
    """Collects OpenFlow / OVS statistics from switch containers."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def collect_port_stats(self, switch_name: str) -> Dict[str, Dict[str, int]]:
        """Run ovs-ofctl dump-ports and parse per-port stats."""
        try:
            result = subprocess.run(
                ['docker', 'exec', switch_name, 'ovs-ofctl', 'dump-ports', switch_name],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return {}
            return self._parse_port_stats(result.stdout)
        except Exception as e:
            self.logger.debug(f"OVS port stats failed for {switch_name}: {e}")
            return {}

    def collect_flow_count(self, switch_name: str) -> int:
        """Return number of flow entries in the switch."""
        try:
            result = subprocess.run(
                ['docker', 'exec', switch_name, 'ovs-ofctl', 'dump-flows', switch_name],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return 0
            lines = [l for l in result.stdout.strip().split('\n')
                     if l and 'NXST_FLOW' not in l and 'OFPST_FLOW' not in l]
            return len(lines)
        except Exception as e:
            self.logger.debug(f"OVS flow count failed for {switch_name}: {e}")
            return 0

    def _parse_port_stats(self, output: str) -> Dict[str, Dict[str, int]]:
        """Parse ovs-ofctl dump-ports output."""
        ports = {}
        current_port = None
        for line in output.split('\n'):
            port_match = re.match(
                r'\s+port\s+(\S+):\s+rx\s+pkts=(\d+),\s+bytes=(\d+),\s+drop=(\d+),\s+errs=(\d+)', line)
            if port_match:
                current_port = port_match.group(1)
                ports[current_port] = {
                    'rx_packets': int(port_match.group(2)),
                    'rx_bytes': int(port_match.group(3)),
                    'rx_drops': int(port_match.group(4)),
                    'rx_errors': int(port_match.group(5)),
                }
                continue
            tx_match = re.match(
                r'\s+tx\s+pkts=(\d+),\s+bytes=(\d+),\s+drop=(\d+),\s+errs=(\d+)', line)
            if tx_match and current_port:
                ports[current_port].update({
                    'tx_packets': int(tx_match.group(1)),
                    'tx_bytes': int(tx_match.group(2)),
                    'tx_drops': int(tx_match.group(3)),
                    'tx_errors': int(tx_match.group(4)),
                })
        return ports


class LatencyCollector:
    """Measures RTT/latency between node pairs using ping."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def measure(self, src_container: str, dst_ip: str, count: int = 3) -> Dict[str, float]:
        """Ping dst_ip from inside src_container."""
        try:
            result = subprocess.run(
                ['docker', 'exec', src_container, 'ping', '-c', str(count), '-W', '2', dst_ip],
                capture_output=True, text=True, timeout=count * 3 + 5
            )
            return self._parse_ping(result.stdout)
        except subprocess.TimeoutExpired:
            return {'rtt_avg': -1, 'packet_loss': 100.0}
        except Exception as e:
            self.logger.debug(f"Ping failed {src_container} -> {dst_ip}: {e}")
            return {}

    def _parse_ping(self, output: str) -> Dict[str, float]:
        stats = {}
        loss_match = re.search(r'(\d+(?:\.\d+)?)%\s+packet\s+loss', output)
        if loss_match:
            stats['packet_loss'] = float(loss_match.group(1))

        rtt_match = re.search(
            r'rtt\s+min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
        if rtt_match:
            stats['rtt_min'] = float(rtt_match.group(1))
            stats['rtt_avg'] = float(rtt_match.group(2))
            stats['rtt_max'] = float(rtt_match.group(3))
            stats['rtt_mdev'] = float(rtt_match.group(4))

        return stats


class TelemetryCollector:
    """Main telemetry collector that orchestrates all sub-collectors.

    Usage:
        store = TelemetryStore()
        collector = TelemetryCollector(store)
        collector.register_container('h1', node_type='host')
        collector.register_container('s1', node_type='switch')
        collector.register_link('h1', 's1', src_ip='10.0.0.1')
        collector.collect_all()  # populates store with latest metrics
    """

    def __init__(self, store: TelemetryStore, docker_client=None, max_workers: int = 4):
        self.store = store
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

        # Docker client — accept externally provided client or create one
        self._docker_client = docker_client or get_docker_client()

        # Sub-collectors
        self._container_collector = ContainerCollector(self._docker_client) if self._docker_client else None
        self._ovs_collector = OVSCollector()
        self._latency_collector = LatencyCollector()

        # Persistent thread pool
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

        # Registered nodes and links
        self._containers: Dict[str, str] = {}  # name -> node_type
        self._link_keys: Set[str] = set()  # for dedup
        self._links: List[Dict[str, str]] = []  # [{src, dst, src_ip}]

        # Background collection
        self._bg_thread: Optional[threading.Thread] = None
        self._bg_stop = threading.Event()
        self._bg_interval = 1.0

    def register_container(self, name: str, node_type: str = 'host'):
        self._containers[name] = node_type

    def register_link(self, src: str, dst: str, src_ip: str):
        key = f"{src}->{dst}"
        if key not in self._link_keys:
            self._link_keys.add(key)
            self._links.append({'src': src, 'dst': dst, 'src_ip': src_ip})

    def auto_discover(self):
        """Auto-discover containers from Docker."""
        if not self._docker_client:
            return
        try:
            for container in self._docker_client.containers.list():
                name = container.name
                labels = container.labels
                node_type = labels.get('lft.type', guess_node_type(name))
                self._containers[name] = node_type
        except Exception as e:
            self.logger.warning(f"Auto-discover failed: {e}")

    def collect_all(self):
        """Collect all metrics in parallel. Populates self.store."""
        ts = time.time()
        futures = {}

        # Container stats
        if self._container_collector:
            for name in self._containers:
                futures[self._pool.submit(self._container_collector.collect, name)] = ('container', name)

        # OVS stats for switches
        for name, ntype in self._containers.items():
            if ntype == 'switch':
                futures[self._pool.submit(self._ovs_collector.collect_port_stats, name)] = ('ovs_ports', name)
                futures[self._pool.submit(self._ovs_collector.collect_flow_count, name)] = ('ovs_flows', name)

        # Latency for registered links
        for link in self._links:
            futures[self._pool.submit(
                self._latency_collector.measure, link['src'], link['src_ip']
            )] = ('latency', f"{link['src']}->{link['dst']}")

        # Gather results
        for future in as_completed(futures):
            kind, key = futures[future]
            try:
                result = future.result()
            except Exception as e:
                self.logger.debug(f"Collection failed for {kind}/{key}: {e}")
                continue

            if kind == 'container' and result:
                for metric, value in result.items():
                    self.store.append(key, metric, value, ts)
            elif kind == 'ovs_ports' and result:
                for port, stats in result.items():
                    for metric, value in stats.items():
                        self.store.append(key, f"port_{port}_{metric}", value, ts)
            elif kind == 'ovs_flows':
                self.store.append(key, 'flow_count', result, ts)
            elif kind == 'latency' and result:
                for metric, value in result.items():
                    self.store.append(key, metric, value, ts)

    def start_background(self, interval: float = 1.0):
        """Start collecting telemetry in a background daemon thread."""
        if self._bg_thread and self._bg_thread.is_alive():
            return

        self._bg_interval = interval
        self._bg_stop.clear()
        self._bg_thread = threading.Thread(target=self._bg_loop, daemon=True)
        self._bg_thread.start()
        self.logger.info(f"Background telemetry started (interval={interval}s)")

    def stop_background(self):
        """Stop the background collection thread."""
        self._bg_stop.set()
        if self._bg_thread:
            self._bg_thread.join(timeout=5)
            self._bg_thread = None
        self._pool.shutdown(wait=False)
        self.logger.info("Background telemetry stopped")

    @property
    def is_running(self) -> bool:
        return self._bg_thread is not None and self._bg_thread.is_alive()

    def _bg_loop(self):
        """Background loop with fixed-rate scheduling."""
        while not self._bg_stop.is_set():
            t0 = time.monotonic()
            try:
                self.collect_all()
            except Exception as e:
                self.logger.debug(f"Background collection error: {e}")
            elapsed = time.monotonic() - t0
            remaining = max(0, self._bg_interval - elapsed)
            if remaining > 0:
                self._bg_stop.wait(timeout=remaining)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """Return latest values for all nodes and metrics."""
        out = {}
        for node in self.store.nodes():
            out[node] = {}
            for metric in self.store.metrics(node):
                latest = self.store.get_latest(node, metric)
                if latest:
                    out[node][metric] = latest[1]
        return out

    def print_summary(self):
        """Print a formatted summary to stdout."""
        s = self.summary()
        if not s:
            print("No telemetry data collected.")
            return
        for node in sorted(s):
            print(f"\n--- {node} ({self._containers.get(node, '?')}) ---")
            for metric in sorted(s[node]):
                val = s[node][metric]
                if isinstance(val, float):
                    print(f"  {metric}: {val:.2f}")
                else:
                    print(f"  {metric}: {val}")
