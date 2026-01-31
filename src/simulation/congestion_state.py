
"""
Congestion State Model
======================

Converts raw packet loss data into a time-series congestion state model.
Congestion Levels:
    0: No Congestion (Loss < 1)
    1: Mild Congestion (1 <= Loss < 5)
    2: Severe Congestion (Loss >= 5)
"""

import pandas as pd
import numpy as np

def build_congestion_state(packet_data):
    """
    Converts packet data into a time-indexed congestion state dictionary.
    
    Args:
        packet_data (dict): Dictionary mapping cell_id -> DataFrame(slot, packet_loss)
        
    Returns:
        pd.DataFrame: A DataFrame where index is time slot, columns are cell IDs,
                      and values are congestion levels (0, 1, 2).
    """
    # 1. Collect all data into a single DataFrame
    combined_data = []
    
    for cell_id, df in packet_data.items():
        temp = df.copy()
        temp['cell_id'] = cell_id
        combined_data.append(temp)
        
    if not combined_data:
        return pd.DataFrame()
        
    full_df = pd.concat(combined_data)
    
    # 2. Pivot to generic matrix form (Index=Slot, Columns=Cell)
    # We use max() in case of duplicates, filling missing with 0 loss
    loss_matrix = full_df.pivot_table(
        index='slot', 
        columns='cell_id', 
        values='packet_loss', 
        aggfunc='max'
    ).fillna(0)
    
    # 3. Apply Congestion Logic
    # Level 0: < 1
    # Level 1: >= 1 AND < 5
    # Level 2: >= 5
    
    congestion_state = pd.DataFrame(0, index=loss_matrix.index, columns=loss_matrix.columns)
    
    congestion_state[loss_matrix >= 1] = 1
    congestion_state[loss_matrix >= 5] = 2
    
    return congestion_state
