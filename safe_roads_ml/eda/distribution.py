import matplotlib.pyplot as plt
import pandas as pd
import sys


def quarter_to_hour_counts(q_series: pd.Series) -> dict[int, int]:
    s = pd.to_numeric(q_series, errors="coerce").dropna().astype(int)
    s = s[(s >= 1) & (s <= 96)]
    hours = (s - 1) // 4
    counts = hours.value_counts().sort_index()
    counts = counts.reindex(range(24), fill_value=0)
    return counts.to_dict()


def compute_distribution(counts_dict: dict[int, int], name: str) -> None:
    total = sum(counts_dict.values())
    if total == 0:
        print("Can't compute distribution of 0 values")
        return
        
    dist_percent = {k: v / total * 100 for k, v in counts_dict.items()}
    print(f'========== Distribution : {name} ==========')
    print(f"{'Value':>8}  ||  {'Amount':>8}  ||  {'Percentage':>10}")
    
    for k in sorted(counts_dict):
        amount = counts_dict[k]
        percent = dist_percent[k]
        print(f"{k:>8}      {amount:>8}      {percent:>9.2f}%")
        
    plot_distribution(dist_percent, title=f"Distribution of {name}", filename=f"{name}_distribution.png")

 
def plot_distribution(dist: dict, title: str, filename: str) -> None:
    keys = sorted(dist)
    values = [dist[k] for k in keys]

    plt.figure()
    plt.bar(keys, values)
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Percentage")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def run_analysis() -> None:
    df = pd.read_excel("accidents_copy_for_data_disturbution.xlsx", engine="openpyxl")
    col_names = df.columns.tolist()
    
    for col_name in col_names:
        if col_name == "SHAA":
            value_counts = quarter_to_hour_counts(df[col_name])
        else:
            col = df[col_name]
            s = pd.to_numeric(col, errors="coerce").dropna().astype(int)
            value_counts = s.value_counts().sort_index().to_dict()
        
        compute_distribution(value_counts, col_name)

def main() -> None:
    output_file = "distribution_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        sys.stdout = f
        
        run_analysis()
        
    sys.stdout = sys.__stdout__
    
if __name__ == "__main__":
    main()