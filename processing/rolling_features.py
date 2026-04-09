import pandas as pd
from pathlib import Path

def rolling_features():
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]
    df = pd.read_csv(root / "data" / "processed" / "epl_pre_rolling.csv")

    # print(df.head())
    # print(df["team"].is_monotonic_increasing)
    # df_temp = df[df["team"] == "Arsenal"]
    # print(df_temp["date"].is_monotonic_increasing)


    #Rolling Features over 5,10 windows
    windows = [5,10]
    rolling_attributes = ["gd","sot","cs"]
    for att in rolling_attributes:
        for i in windows:
            col = f"{att}_last_{i}"
            df[col] = df.groupby("team")[att].transform(lambda x: x.shift(1).rolling(window=i,min_periods=1).mean()) 
            #Shift is required to prevent data leakage

    windows = [5]
    venue_split_attributes = ["gf","ga","win","points"]
    for att in venue_split_attributes:
        for venue in ["home", "away"]:
            col = f"{att}_last_5_{venue}"
            mask = df["venue"] == venue
            df.loc[mask, col] = (
                df[mask].groupby("team")[att]
                .transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            )
    # print(df.head(11))
    arsenal_home = df[(df["team"] == "Arsenal") & (df["venue"] == "home")]
    print(arsenal_home[["date", "gf", "gf_last_5_home", "gf_last_5_away"]].head(10))

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

if __name__ == "__main__":
    rolling_features()

