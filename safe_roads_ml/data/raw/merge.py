# Merge the yearly CSV files in chronological order.

import pandas as pd

files = [
    "data-2018.csv",
    "data-2019.csv",
    "data-2020.csv",
    "data-2021.csv",
    "data-2022.csv",
    "data-2023.csv"
]

dfs = []

for f in files:
    print("Loading", f, "...")
    df = pd.read_csv(f, low_memory=False)
    dfs.append(df)

master = pd.concat(dfs, ignore_index=True)
master.to_csv("accidents_raw_master.csv", index=False)

print("Done!")
