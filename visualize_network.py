#!/usr/bin/env python3
"""
LFT Visualizer - Quick Start Script
Visualize your running LFT network topology in real-time
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import matplotlib
    except ImportError:
        missing.append('matplotlib')
    
    try:
        import docker
    except ImportError:
        missing.append('docker')
    
    try:
        import networkx
    except ImportError:
        missing.append('networkx')
    
    if missing:
        print("⚠️  Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        print("\nOr install all at once:")
        print("   pip install matplotlib docker networkx")
        return False
    
    return True

def main():
    """Main entry point"""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     LFT Network Real-Time Visualizer                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✓ All dependencies found")
    print()
    print("Starting visualizer...")
    print("  • Detecting network topology")
    print("  • Monitoring container statistics")
    print("  • Real-time graph updates")
    print()
    print("Controls:")
    print("  • Close window to stop")
    print("  • Ctrl+C in terminal to exit")
    print()
    print("─" * 60)
    print()
    
    # Import and run visualizer
    try:
        from profissa_lft.visualizer import NetworkVisualizer
        
        visualizer = NetworkVisualizer(update_interval=1000)
        visualizer.start()
        
    except KeyboardInterrupt:
        print("\n\n✓ Visualizer stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
