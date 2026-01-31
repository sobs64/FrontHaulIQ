import pandas as pd
import numpy as np

def build_congestion_matrix(event_data: dict):
    """
    Builds slot-aligned congestion event matrix.

    Args:
        event_data: dict[cell_id] -> DataFrame(slot, congestion_event)

    Returns:
        DataFrame[slot x cell_id]
    """
    series = []

    for cell_id, df in event_data.items():
        s = df.set_index("slot")["congestion_event"]
        s.name = cell_id
        series.append(s)

    matrix = pd.concat(series, axis=1).fillna(0)
    return matrix


def compute_correlation_matrix(loss_matrix: pd.DataFrame):
    """
    Computes cell-to-cell correlation matrix.

    Returns:
        DataFrame[cell_id x cell_id]
    """
    corr = loss_matrix.corr(method="pearson")

    return corr
