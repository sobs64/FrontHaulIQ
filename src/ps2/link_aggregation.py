import pandas as pd

def aggregate_link_throughput(slot_throughput_data, link_mapping):
    """
    Aggregates slot-level throughput per inferred fronthaul link.

    Raw values: BYTES per OFDM symbol
    Output: Gbps per slot
    """
    link_data = {}

    for link, cells in link_mapping.items():
        dfs = []

        for cell in cells:
            df = slot_throughput_data[cell].copy()
            df = df.rename(columns={"throughput": cell})
            dfs.append(df.set_index("slot"))

        merged = pd.concat(dfs, axis=1).fillna(0)

        # Sum BYTES across cells per slot
        merged["total_bytes"] = merged.sum(axis=1)

        # Convert BYTES/slot → Gbps
        merged["total_throughput"] = (
            merged["total_bytes"] * 8 / 0.0005 / 1e9
        )

        link_data[link] = merged[["total_throughput"]].reset_index()

    return link_data
