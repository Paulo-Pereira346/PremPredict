import pandas as pd 

def create_labels(season,file_path):
    df_label = pd.read_json(file_path)
    df_mw38 = df_label[df_label["matchweek"] == 38]
    max_points = df_mw38["overall_points"].max()
    df_champions = df_mw38[df_mw38["overall_points"] == max_points]
    df_champions = df_champions.sort_values(by = ["overall_points","overall_gd","overall_gf"], ascending = [False,False,False])
    champion = df_champions["team"].iloc[0]

    df_label["champion_label"] = (df_label["team"] == champion).astype(int) 
    

    # print(df_label.columns.tolist())
    new_order = ['season', 'matchweek', 'team', 'overall_pos', 'overall_wins', 'overall_loss', 
    'overall_draws', 'overall_points', 'overall_played', 'overall_gf', 'overall_ga', 'overall_gd', 
    'home_pos', 'home_wins', 'home_loss', 'home_draws', 'home_points', 'home_played', 'home_gf', 'home_ga', 
    'home_gd', 'away_pos', 'away_wins', 'away_loss', 'away_draws', 'away_points', 'away_played', 'away_gf', 
    'away_ga', 'away_gd', 'champion_label']

    df_label = df_label[new_order]

    # print(df_label.shape)

    # print(df_label[df_label["champion_label"]==1])
    df_label.to_csv(f"../data/processed/{season}_{season-2000+1}_labeled.csv",index = False)


for season in range(2015,2024):
    create_labels(season, f"../data/raw/{season}_{season-2000+1}_standings.json")