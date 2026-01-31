import os
import re
import pandas as pd

def load_throughput_data(directory: str):
    throughput_data = {}

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

        df = df[[0, df.columns[-1]]]
        df.columns = ["time", "throughput"]

        df["time"] = pd.to_numeric(df["time"], errors="coerce")
        df["throughput"] = pd.to_numeric(df["throughput"], errors="coerce").fillna(0)

        throughput_data[cell_id] = df.reset_index(drop=True)

    return throughput_data
