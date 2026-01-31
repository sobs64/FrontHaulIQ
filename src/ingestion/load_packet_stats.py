import os
import re
import pandas as pd

def load_packet_stats(directory: str):
    packet_data = {}

    for file in os.listdir(directory):
        if not file.endswith(".dat"):
            continue

        match = re.search(r"cell[-_]?(\d+)", file, re.IGNORECASE)
        if not match:
            print(f"[WARN] Could not extract cell id from {file}")
            continue

        cell_id = f"cell-{match.group(1)}"
        file_path = os.path.join(directory, file)

        df = pd.read_csv(file_path, sep=r"\s+", header=None)

        df = df[[0, 1]]
        df.columns = ["slot", "packet_loss"]

        df = df[df["slot"] != "<slot>"]

        df["slot"] = pd.to_numeric(df["slot"], errors="coerce")
        df["packet_loss"] = pd.to_numeric(df["packet_loss"], errors="coerce").fillna(0)

        packet_data[cell_id] = df.reset_index(drop=True)

    return packet_data
