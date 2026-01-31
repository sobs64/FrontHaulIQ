
"""
Graph Frames Visualizer
=======================

Handles the Matplotlib drawing logic for a single frame of the simulation.
"""

import matplotlib.pyplot as plt
import networkx as nx

# Visual Constants
COLOR_MAP = {
    0: "#2ca02c", # Green (Normal)
    1: "#ff7f0e", # Orange (Mild)
    2: "#d62728"  # Red (Severe)
}

SIZE_MAP = {
    0: 300,
    1: 450,
    2: 600
}

def draw_network_frame(G, pos, active_congestion, current_slot, ax=None):
    """
    Draws the network graph on a Matplotlib axis for a given time step.
    
    Args:
        G (nx.Graph): The network topology graph.
        pos (dict): Node positions.
        active_congestion (pd.Series): Congestion levels for cells at this slot (index=cell, val=level).
        current_slot (int): The current time slot being rendered.
        ax (matplotlib.axes.Axes): Optional axis to draw on.
    
    Returns:
        matplotlib.figure.Figure: The figure object (if ax was not provided)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    else:
        fig = ax.figure

    ax.clear()
    
    # 1. Determine Node Colors and Sizes
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        node_type = G.nodes[node].get("type", "cell")
        
        if node_type == "link":
            # Link Hubs are always neutral/grayish or distinct
            node_colors.append("#7f7f7f")
            node_sizes.append(400)
            continue
            
        # For Cells, look up congestion
        level = 0
        if node in active_congestion:
            level = active_congestion[node]
            
        node_colors.append(COLOR_MAP.get(level, "#2ca02c"))
        node_sizes.append(SIZE_MAP.get(level, 300))

    # 2. Determine Edge Colors
    # Edge is congested if connected to a congested node? 
    # Requirement: "If >=2 nodes on same link are congested -> edge turns orange/red"
    # Actually, standard logic: usually edge takes color of worst connected node, 
    # or if we have Hub-Spoke, if Cell is congested, the Spoke edge is congested.
    
    edge_colors = []
    edge_widths = []
    
    for u, v in G.edges():
        # Check congestion of endpoints
        state_u = active_congestion.get(u, 0) if u in active_congestion else 0
        state_v = active_congestion.get(v, 0) if v in active_congestion else 0
        
        # Heuristic: Edge is colored if the non-hub node is congested (Spoke link)
        # Assuming one is Link Hub and one is Cell
        loss_val = max(state_u, state_v)
        
        if loss_val == 2:
            edge_colors.append("#d62728")
            edge_widths.append(3.0)
        elif loss_val == 1:
            edge_colors.append("#ff7f0e")
            edge_widths.append(2.0)
        else:
            edge_colors.append("#cccccc") # Light gray
            edge_widths.append(1.0)

    # 3. Draw
    nx.draw_networkx_nodes(
        G, pos, 
        node_size=node_sizes, 
        node_color=node_colors, 
        edgecolors="white", 
        linewidths=1.5,
        ax=ax
    )
    
    nx.draw_networkx_edges(
        G, pos, 
        edge_color=edge_colors, 
        width=edge_widths,
        ax=ax
    )
    
    # Labels (Only Links identifiers or Cells?)
    # Requirement: "Node labels must remain readable"
    # To avoid clutter, maybe just label Links clearly and cells small
    labels = {}
    for node in G.nodes():
        if G.nodes[node].get("type") == "link":
            labels[node] = node
        else:
            # cell-12 -> 12
            labels[node] = node.replace("cell-", "")
    
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color="#333", ax=ax)
    
    # 4. Styling
    ax.set_title(f"Simulation Time: Slot {current_slot}", fontsize=14, loc='left')
    ax.axis('off')
    
    return fig
