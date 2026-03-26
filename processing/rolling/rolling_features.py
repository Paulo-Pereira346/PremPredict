import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve()
root = file_path.parents[2]
df = pd.read_csv(root / "data" / "processed" / "epl_pre_rolling.csv")

# print(df.head())
# print(df["team"].is_monotonic_increasing)
# df_temp = df[df["team"] == "Arsenal"]
# print(df_temp["date"].is_monotonic_increasing)


#Rolling Features over 5,10 windows
windows = [5,10]
rolling_attributes = ["gf","ga","gd","points","win","sot","cs"]
for att in rolling_attributes:
    for i in windows:
        col = f"{att}_last_{i}"
        df[col] = df.groupby("team")[att].transform(lambda x: x.shift(1).rolling(window=i,min_periods=1).mean()) 
        #Shift is required to prevent data leakage
        
cumulative_attributes = ["gf","ga","points"]
for att in cumulative_attributes:
    col = f"cum_{att}"
    df[col] = df.groupby("team")[att].transform(lambda x: x.shift(1).expanding().mean())


#Preliminary Checks before Saving data
# print(df[df["team"]=="Arsenal"][["date","gf","gf_last_5","gf_last_10","cum_gf"]].head(11))
print(df.head())
print(df.shape)
print(df.columns)
df = df.sort_values(["team", "date"]).reset_index(drop=True)
print(df.groupby("team")["date"].is_monotonic_increasing.all())

df.to_csv(root / "data" / "processed" / "epl_rolling.csv" ,index = False)



