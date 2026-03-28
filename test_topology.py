#!/usr/bin/env python3
"""Simple test topology: 2 hosts + 1 switch, for visualizer testing."""
import sys
sys.path.insert(0, '.')
from profissa_lft import Host, Switch

# Create nodes
h1 = Host("h1")
h2 = Host("h2")
s1 = Switch("s1")

# Instantiate containers
h1.instantiate()
h2.instantiate()
s1.instantiate()

# Connect hosts to switch
h1.connect(s1, "eth0", "eth1")
h2.connect(s1, "eth0", "eth2")

# Set IPs
h1.setIp("10.0.0.1", 24, "eth0")
h2.setIp("10.0.0.2", 24, "eth0")

print("Topology running. Containers:")
print("  h1, h2 (hosts), s1 (switch)")
print("Press Ctrl+C to stop.")

try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nCleaning up...")
    h1.delete()
    h2.delete()
    s1.delete()
    print("Done.")
