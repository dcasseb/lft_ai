#!/usr/bin/env python3
"""Test that all imports work correctly."""
print("Testing imports (this may take 30-60 seconds due to torch)...")
print("Loading profissa_lft modules...")

from profissa_lft import (
    Node, Host, Controller, Switch, 
    UE, EPC, EnB,
    AITopologyGenerator,
    ModernAITopologyGenerator
)

print("✓ All imports successful!")
print("✓ AITopologyGenerator available")
print("✓ ModernAITopologyGenerator available")
print("\nAvailable classes:", [
    'Node', 'Host', 'Controller', 'Switch', 
    'UE', 'EPC', 'EnB', 
    'AITopologyGenerator', 'ModernAITopologyGenerator'
])
