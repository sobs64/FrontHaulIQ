import numpy as np

def required_capacity_no_buffer(link_df, percentile=99):
    """
    Required capacity without buffering.
    Uses high-percentile traffic to ensure <1% loss.
    """
    return np.percentile(link_df["total_throughput"], percentile)


def required_capacity_with_buffer(link_df, buffer_slots=2, percentile=99):
    """
    Required capacity with buffer smoothing.
    Buffer absorbs short-term bursts.

    buffer_slots=2 corresponds to ~4-symbol buffer.
    """
    smoothed = (
        link_df["total_throughput"]
        .rolling(window=buffer_slots, min_periods=1)
        .mean()
    )

    return np.percentile(smoothed, percentile)
