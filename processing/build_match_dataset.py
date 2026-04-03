import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve()
root = file_path.parents[1]
df_epl = pd.read_csv(root / "data" / "processed" / "epl_with_elo.csv")

df_roll = pd.read_csv(root / "data" / "processed" / "epl_rolling.csv")
df_roll = df_roll.sort_values("date").reset_index(drop=True)

df_home = df_roll[df_roll["venue"] == "home"]
df_home = df_home.drop("venue",axis=1)
df_away = df_roll[df_roll["venue"] == "away"]
df_away = df_away.drop("venue",axis=1)

columns = df_home.columns.tolist()
home_dict = {}
away_dict = {}
for col in columns:
    old = col
    new_h = f"H_{col}"    
    new_a = f"A_{col}" 
    if col == "date":
        home_dict[old] = old
        away_dict[old] = old 
        continue
    if col == "team":
        home_dict[old] = "home"
        away_dict[old] = "away" 
        continue
    home_dict[old] = new_h
    away_dict[old] = new_a

df_home = df_home.rename(columns = home_dict)
df_away = df_away.rename(columns = away_dict)

df_full = pd.merge(df_epl,df_home,on=["date","home"], how="inner")
df_full = pd.merge(df_full,df_away,on=["date","away"], how="inner")


df_full["form_diff_5"] = df_full["H_points_last_5_home"] - df_full["A_points_last_5_away"]
# df_full["form_diff_10"] = df_full["H_points_last_10"] - df_full["A_points_last_10"]

df_full["att_edge_5"] = df_full["H_gf_last_5_home"] - df_full["A_ga_last_5_away"]
# df_full["att_edge_10"] = df_full["H_gf_last_10"] - df_full["A_ga_last_10"]
df_full["cum_att_edge"] = df_full["H_cum_gf"] - df_full["A_cum_ga"]

df_full["sot_edge_5"] = df_full["H_sot_last_5"] - df_full["A_sot_last_5"]
df_full["sot_edge_10"] = df_full["H_sot_last_10"] - df_full["A_sot_last_10"]

df_full["def_matchup_5"] = df_full["H_ga_last_5_home"] + df_full["A_ga_last_5_away"]
df_full["att_matchup_5"] = df_full["H_gf_last_5_home"] + df_full["A_gf_last_5_away"]

df_full["elo_diff_abs"] = abs(df_full["elo_diff"])
df_full["form_diff_5_abs"] = abs(df_full["form_diff_5"])
df_full["match_balance"] = df_full["elo_diff_abs"] + df_full["form_diff_5_abs"] + abs(df_full["att_edge_5"])
# df_full["form_diff_10_abs"] = abs(df_full["form_diff_10"])

df_full["H_draw_last_5"] = df_full["H_points_last_5_home"] - 3*df_full["H_win_last_5_home"]
df_full["A_draw_last_5"] = df_full["A_points_last_5_away"] - 3*df_full["A_win_last_5_away"]
# df_full["draw_tendency_sum"] = df_full["H_draw_last_5"] + df_full["A_draw_last_5"]
# df_full["H_draw_last_10"] = df_full["H_points_last_10"] - 3*df_full["H_win_last_10"]
# df_full["A_draw_last_10"] = df_full["A_points_last_10"] - 3*df_full["A_win_last_10"]

#Removing Unnecessary columns or columns that cause data leakage

remove_cols = ['home_shots','away_shots', 'home_sot', 'away_sot', 'home_elo', 'away_elo',
        'H_gf', 'H_ga', 'H_shots', 'H_sot', 'H_win', 'H_draw', 'H_loss', 'H_points', 'H_gd', 'H_cs', 
        'A_gf', 'A_ga', 'A_shots','A_sot', 'A_win', 'A_draw', 'A_loss', 'A_points', 'A_gd', 'A_cs',
        'H_gf_last_5_away', 'H_ga_last_5_away', 'H_win_last_5_away', 'H_points_last_5_away',
        'A_gf_last_5_home', 'A_ga_last_5_home', 'A_win_last_5_home', 'A_points_last_5_home']

df_full = df_full.drop(remove_cols,axis=1)

#Cleaning the final dataset by removing NaNs
cols = df_full.columns.tolist()
l = ["date","season","home","away","hg","ag","FTR"]
for col in l:
    cols.remove(col)
# print(cols)

df_full[cols] = df_full[cols].fillna(df_full[cols].mean())
# print(df_full.head(11))
# print(df_full.isna().sum().sum())
print(df_full.isna().sum()[df_full.isna().sum() > 0])
print(df_full.head())
print(df_full["H_draw_last_5"].describe())
print(df_full["A_draw_last_5"].describe())

df_full.to_csv(root / "data" / "processed" / "Final_dataset.csv",index=False)

