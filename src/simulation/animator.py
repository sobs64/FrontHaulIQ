
import pandas as pd
import networkx as nx

def prepare_animation_frames(link_mapping, packet_data, throughput_data=None, steps=200):
    """
    Prepares a DataFrame for Plotly animation.
    
    Args:
        link_mapping (dict): Map of Link -> [Cells]
        packet_data (dict): Map of Cell -> DataFrame[slot, packet_loss]
        throughput_data (dict): Map of Cell -> DataFrame[slot, throughput] (Optional)
        steps (int): Number of time steps to check for animation (to limit range)
        
    Returns:
        pd.DataFrame: DataFrame with columns [Time, Node, Type, Value, Label, X, Y]
    """
    
    # 1. Build a static graph layout for consistent positions
    G = nx.Graph()
    for link, cells in link_mapping.items():
        G.add_node(link, type="link")
        for cell in cells:
            G.add_node(cell, type="cell")
            G.add_edge(link, cell)
            
    # Use spring layout but fix link nodes to be central if possible
    pos = nx.spring_layout(G, seed=42, k=0.5)
    
    # 2. Collect timestamps (slots)
    # intersection of slots across all cells is ideal, but union is safer
    # For demo, we take the first cell's slots and limit to 'steps'
    first_cell = list(packet_data.keys())[0]
    available_slots = packet_data[first_cell]['slot'].sort_values().unique()
    
    # If too many slots, subsample or slice
    if len(available_slots) > steps:
        target_slots = available_slots[:steps]
    else:
        target_slots = available_slots
        
    animation_rows = []
    
    # Pre-process data for fast lookup
    # Pivot packet data: index=slot, columns=cell
    combined_packets = []
    for cell, df in packet_data.items():
        temp = df.copy()
        temp['cell'] = cell
        combined_packets.append(temp)
    
    big_df = pd.concat(combined_packets)
    # Pivot to get a matrix of packet loss: index=slot, cols=cells
    loss_matrix = big_df.pivot_table(index='slot', columns='cell', values='packet_loss', fill_value=0)
    
    # Same for throughput if available
    tp_matrix = None
    if throughput_data:
        combined_tp = []
        for cell, df in throughput_data.items():
            temp = df.copy()
            temp['cell'] = cell
            combined_tp.append(temp)
        if combined_tp:
            big_tp = pd.concat(combined_tp)
            # Ensure slot column is correct
            # Throughput might be symbol level, need agg if not already done. 
            # Assuming input is already slot-aligned or we just take raw match
            tp_matrix = big_tp.pivot_table(index='slot', columns='cell', values='throughput', fill_value=0)

    # 3. Generate frames
    for t in target_slots:
        # For each node in the graph
        for node in G.nodes():
            node_type = G.nodes[node]['type']
            x, y = pos[node]
            
            val = 0
            label = f"{node}"
            
            if node_type == 'cell':
                # Get packet loss for this cell at time t
                if t in loss_matrix.index and node in loss_matrix.columns:
                    val = loss_matrix.loc[t, node]
                
                # Append throughput info to label if available
                if tp_matrix is not None and t in tp_matrix.index and node in tp_matrix.columns:
                    tp_val = tp_matrix.loc[t, node]
                    label += f"<br>Loss: {val:.1f}<br>T-put: {tp_val:.2f}"
                else:
                    label += f"<br>Loss: {val:.1f}"

            elif node_type == 'link':
                # Link value could be aggregate of connected cells
                # For now, keep it static or average
                val = 0 
                label = f"{node}<br>(Hub)"

            animation_rows.append({
                "Time": t,
                "Node": node,
                "Type": node_type,
                "Value": val,  # Used for color (congestion)
                "Label": label,
                "X": x,
                "Y": y,
                "Size": 25 if node_type == 'link' else 15
            })
            
    return pd.DataFrame(animation_rows)
