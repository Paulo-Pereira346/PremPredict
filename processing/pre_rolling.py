import pandas as pd
import numpy as np

def pre_rolling_dataset():
    df = pd.read_csv("../data/processed/epl_with_elo.csv")

    df_home = df[["date","home","hg","ag","home_shots","home_sot"]]
    df_home["venue"] = "home"
    df_home = df_home.rename(columns={"home":"team","hg":"gf","ag":"ga","home_shots":"shots","home_sot":"sot"})
    # print(df_home.head())

    df_away = df[["date","away","ag","hg","away_shots","away_sot"]]
    df_away["venue"] = "away"
    df_away = df_away.rename(columns={"away":"team","ag":"gf","hg":"ga","away_shots":"shots","away_sot":"sot"})
    # print(df_away.head())

    df_prem = pd.concat([df_home,df_away],ignore_index=True)
    df_prem = df_prem.sort_values(["team","date"])
    df_prem = df_prem.reset_index(drop=True)
    # print(df_prem.head(10))
    # print(len(df_prem))

    df_prem[["win","draw","loss","points","gd","cs"]] = np.nan

    df_prem["win"] = np.where(df_prem["gf"] > df_prem["ga"], 1, 0)
    df_prem["loss"] = np.where(df_prem["gf"] < df_prem["ga"], 1, 0)
    df_prem["draw"] = np.where(df_prem["gf"] == df_prem["ga"], 1, 0)
    df_prem["cs"] = np.where((df_prem["ga"] == 0), 1, 0)

    df_prem["gd"] = df_prem["gf"] - df_prem["ga"]
    df_prem["points"] = (3 * df_prem["win"]) + (1 * df_prem["draw"])
    # print(df_prem)


    #Checks
    if((df_prem["win"] + df_prem["loss"] + df_prem["draw"]) != 1).any():
        print("There is an issue with win+draw+loss")
    else:
        print("There is no issue with win+draw+loss")

    cs_issue = df_prem[
        ((df_prem["ga"] == 0) & (df_prem["cs"] != 1)) | ((df_prem["ga"] != 0) & (df_prem["cs"] == 1))
    ]

    pt_issue = df_prem[~df_prem["points"].isin([0,1,3])]

    if not cs_issue.empty:
        print(f"No of CS issues: {len(cs_issue)}")
        print(cs_issue)
    else:
        print("There is no issue with CS Calculation")
        
    if not pt_issue.empty:
        print(f"No of Point issues: {len(pt_issue)}")
        print(pt_issue)
    else :
        print("There is no issue with Point Calculation")
        

    df_prem.to_csv("../data/processed/epl_pre_rolling.csv" ,index = False)


pre_rolling_dataset()   

