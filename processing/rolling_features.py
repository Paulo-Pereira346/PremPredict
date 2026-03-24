import pandas as pd

df = pd.read_csv("../data/processed/epl_pre_rolling.csv")

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

print(df[df["team"]=="Arsenal"][["date","gf","cum_gf"]])
# print(df.head())



