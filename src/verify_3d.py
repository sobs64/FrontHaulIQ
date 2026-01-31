
import sys
import os
import networkx as nx

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

try:
    from visualization.threed_graph import generate_3d_topology
    print("Imports successful.")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

# Mock Data
print("Building mock topology...")
link_mapping = {
    "Link1": ["cell-1", "cell-2", "cell-3"],
    "Link2": ["cell-4"]
}

try:
    fig = generate_3d_topology(link_mapping)
    print("3D Topology Figure Generated Successfully.")
    
    # Check if traces are correct
    assert len(fig.data) == 2 # Edge trace + Node trace
    assert fig.data[1].mode == 'markers'
    print("Traces verified.")
    
except Exception as e:
    print(f"3D Generation Failed: {e}")
    sys.exit(1)

print("Verification Passed.")
