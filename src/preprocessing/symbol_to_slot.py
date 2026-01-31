import pandas as pd
import numpy as np

SLOT_DURATION_SEC = 0.0005  # 500 microseconds


def convert_to_slot_level(throughput_df):
    df = throughput_df.copy()

    df = df.rename(columns={
        df.columns[0]: "time",
        df.columns[1]: "throughput"
    })

    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["throughput"] = pd.to_numeric(df["throughput"], errors="coerce").fillna(0)

    df["slot"] = (df["time"] / 0.0005).astype(int)

    slot_df = df.groupby("slot", as_index=False)["throughput"].sum()

    return slot_df


