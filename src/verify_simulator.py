
import sys
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

try:
    from simulation.congestion_state import build_congestion_state
    from simulation.graph_frames import draw_network_frame
    print("Imports successful.")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

# Mock Data
print("Building mock data...")
packet_data = {
    "cell-1": pd.DataFrame({"slot": [1, 2, 3], "packet_loss": [0.5, 2.0, 6.0]}),
    "cell-2": pd.DataFrame({"slot": [1, 2, 3], "packet_loss": [0.0, 0.0, 0.0]})
}

# Test Congestion State Model
print("Testing congestion state model...")
try:
    state = build_congestion_state(packet_data)
    print("Congestion State Shape:", state.shape)
    print(state)
    
    # Validation
    assert state.loc[1, "cell-1"] == 0 # Loss 0.5 -> Level 0
    assert state.loc[2, "cell-1"] == 1 # Loss 2.0 -> Level 1
    assert state.loc[3, "cell-1"] == 2 # Loss 6.0 -> Level 2
    print("Congestion state logic valid.")
except Exception as e:
    print(f"Verification Failed: {e}")
    sys.exit(1)

# Test Graph Drawing
print("Testing graph drawing...")
try:
    G = nx.Graph()
    G.add_edge("Link1", "cell-1")
    G.add_edge("Link1", "cell-2")
    pos = nx.spring_layout(G)
    
    # Test Frame 3 (Severe Congestion)
    curr_state = state.loc[3].to_dict()
    fig = draw_network_frame(G, pos, curr_state, current_slot=3)
    
    # Save a test image to prove it works
    fig.savefig("test_frame.png")
    print("Frame drawing successful. Saved test_frame.png")
except Exception as e:
    print(f"Drawing Failed: {e}")
    sys.exit(1)

print("Verification Passed.")
