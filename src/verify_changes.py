
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

try:
    from simulation.animator import prepare_animation_frames
    from dashboard.ps1_views import show_network_animation, show_topology_graph
    # We can't easily test streamlit functions without a mock, but we can test the animator logic
    print("Imports successful.")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

# Mock data for animator
import pandas as pd
link_mapping = {"Link1": ["cell-1", "cell-2"]}
packet_data = {"cell-1": pd.DataFrame({"slot": [1, 2], "packet_loss": [0, 1]})}
throughput_data = {"cell-1": pd.DataFrame({"slot": [1, 2], "throughput": [100, 200]})}

try:
    df = prepare_animation_frames(link_mapping, packet_data, throughput_data=throughput_data, steps=2)
    print("prepare_animation_frames ran successfully.")
    print(df.head())
except Exception as e:
    print(f"Error in prepare_animation_frames: {e}")
    sys.exit(1)
