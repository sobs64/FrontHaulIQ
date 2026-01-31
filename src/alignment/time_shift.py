import numpy as np
import pandas as pd
from scipy.signal import correlate

def detect_time_shift(throughput_slots, packet_loss_slots, max_lag=50):
    """
    Detect time shift between DU throughput and RU packet loss.

    Returns:
        lag (int): positive means packet_loss lags throughput
    """
    # Normalize
    t = (throughput_slots - throughput_slots.mean()) / (throughput_slots.std() + 1e-6)
    p = (packet_loss_slots - packet_loss_slots.mean()) / (packet_loss_slots.std() + 1e-6)

    corr = correlate(p, t, mode="full")
    lags = np.arange(-len(t) + 1, len(t))

    # Limit lag search
    valid = (lags >= -max_lag) & (lags <= max_lag)
    best_lag = lags[valid][np.argmax(corr[valid])]

    return int(best_lag)


def align_packet_loss(throughput_df, packet_df):
    """
    Align packet loss timeline to throughput timeline.
    """
    min_len = min(len(throughput_df), len(packet_df))

    t_series = throughput_df["throughput"].iloc[:min_len]
    p_series = packet_df["packet_loss"].iloc[:min_len]

    lag = detect_time_shift(t_series.values, p_series.values)

    aligned_packet = packet_df.copy()

    if lag > 0:
        aligned_packet["packet_loss"] = aligned_packet["packet_loss"].shift(-lag)
    elif lag < 0:
        aligned_packet["packet_loss"] = aligned_packet["packet_loss"].shift(abs(lag))

    aligned_packet["packet_loss"] = aligned_packet["packet_loss"].fillna(0)

    return aligned_packet, lag
