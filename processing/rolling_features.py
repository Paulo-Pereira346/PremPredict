import pandas as pd

df = pd.read_csv("../data/processed/epl_pre_rolling.csv")

# print(df.head())
# print(df["team"].is_monotonic_increasing)
# df_temp = df[df["team"] == "Arsenal"]
# print(df_temp["date"].is_monotonic_increasing)

windows = [5,10]
attributes = ["gf","ga","gd","points","win","sot","cs"]
for att in attributes:
    for i in windows:
        col = f"{att}_last_{i}"
        df[col] = df.groupby("team")[att].transform(lambda x: x.shift(1).rolling(window=i,min_periods=1).mean())

print(df[df["team"]=="Man United"][["date","gf","gf_last_5","gf_last_10"]].head(11))
# print(df.head())



