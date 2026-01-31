import pandas as pd
import numpy as np

def extract_windowed_congestion_events(packet_df, loss_threshold=1, window=5):
    """
    Converts packet loss into windowed congestion events.

    window = number of slots before/after to mark congestion
    """
    df = packet_df.copy()
    df["event"] = (df["packet_loss"] >= loss_threshold).astype(int)

    # Rolling max to expand events in time
    df["event_windowed"] = (
        df["event"]
        .rolling(window=2 * window + 1, center=True, min_periods=1)
        .max()
    )

    return df[["slot", "event_windowed"]].rename(
        columns={"event_windowed": "congestion_event"}
    )
