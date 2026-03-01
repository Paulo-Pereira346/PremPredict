import pandas as pd 

def validate_json(season,file_path):
    df_prem = pd.read_json(file_path)
    # print(df_prem.head())

    for mw in df_prem["matchweek"].unique():
        flag = 0
        df_mw = df_prem[df_prem['matchweek'] == mw]

        if(df_mw["overall_ga"].sum() != df_mw["overall_gf"].sum()):
            print("Overall ga != Overall gf")
            flag = 1

        if(df_mw["overall_wins"].sum() != df_mw["overall_loss"].sum()):
            print("Overall wins and losses arent equal")
            flag = 1

        if((df_mw["overall_draws"].sum() % 2) != 0):
            print("No. of Draws are wrong")
            flag = 1
        
        if(df_mw["overall_points"].sum() != ((3*df_mw["overall_wins"].sum())+df_mw["overall_draws"].sum())):
            print("Points are wrong")
            flag = 1
        

        if(df_mw['overall_gd'] != (df_mw['overall_gf'] - df_mw['overall_ga'])).any():
            print("GD Calculation is wrong")
            flag = 1

        if(df_mw['overall_played'] != (df_mw['home_played'] + df_mw['away_played'])).any():
            print("HP + AP != OP")
            flag = 1

        if(df_mw['overall_wins'] != (df_mw['home_wins'] + df_mw['away_wins'])).any():
            print("HW + AW != OW")
            flag = 1

        if(df_mw['overall_draws'] != (df_mw['home_draws'] + df_mw['away_draws'])).any():
            print("HD + AD != OD")
            flag = 1

        if(df_mw['overall_loss'] != (df_mw['home_loss'] + df_mw['away_loss'])).any():
            print("HL + AL != OL")
            flag = 1

        if(df_mw['overall_points'] != (df_mw['home_points'] + df_mw['away_points'])).any():
            print("H.points + A.points != O.points")
            flag = 1           
            
        
        if(flag == 0):
            print(f"Everything is A-ok with matchweek {mw} of season {season}")

       

for season in range(2015,2024):
    validate_json(season, f"../data/raw/{season}_{season-2000+1}_standings.json") 