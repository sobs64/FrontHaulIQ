
"""
Simulation Animator
===================

Controls the Streamlit animation loop for the congestion simulation.
"""

import time
import streamlit as st
import matplotlib.pyplot as plt
from simulation.graph_frames import draw_network_frame

def render_simulation_ui(G, pos, congestion_state):
    """
    Renders the simulation UI and handles the animation loop.
    
    Args:
        G (nx.Graph): Network topology.
        pos (dict): Node positions.
        congestion_state (pd.DataFrame): Time-series congestion data (Index=Slot, Columns=Cells).
    """
    st.markdown("### 🚦 Fronthaul Congestion Propagation Simulator")
    
    # --- Controls ---
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        run_sim = st.button("▶️ Play Simulation")
        stop_sim = st.button("⏹️ Stop")
        
    with col2:
        speed = st.slider("Animation Speed (sec/frame)", 0.05, 1.0, 0.1, 0.05)
        
    with col3:
        # Time Window Selection
        min_slot = int(congestion_state.index.min())
        max_slot = int(congestion_state.index.max())
        start_slot, end_slot = st.slider(
            "Time Window", 
            min_slot, max_slot, 
            (min_slot, min(min_slot + 100, max_slot))
        )

    # --- Animation Area ---
    plot_placeholder = st.empty()
    
    # Initialize Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Initial Frame (Static)
    draw_network_frame(G, pos, {}, start_slot, ax=ax)
    plot_placeholder.pyplot(fig)
    
    # --- Animation Loop ---
    if run_sim:
        for slot in range(start_slot, end_slot + 1):
            if stop_sim:
                break
            
            # Get current state
            if slot in congestion_state.index:
                current_state = congestion_state.loc[slot].to_dict()
            else:
                current_state = {}
                
            # Draw Frame
            draw_network_frame(G, pos, current_state, slot, ax=ax)
            
            # Update Streamlit
            plot_placeholder.pyplot(fig)
            
            # Wait
            time.sleep(speed)
            
        st.success("Simulation Complete")
