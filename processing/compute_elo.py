import pandas as pd 
from pathlib import Path

def compute_elo():
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]
    
    df = pd.read_csv(root / "data" / "raw" / "epl_matches.csv")
    
    ratings = {}
    home_elo_list = []
    away_elo_list = []
    base = 1500
    K = 32
    
    for _,row in df.iterrows():
        
        home_team = row["home"]
        away_team = row["away"]
        old_home_elo = ratings.get(home_team,base)
        old_away_elo = ratings.get(away_team,base)
        
        home_elo_list.append(old_home_elo)
        away_elo_list.append(old_away_elo)
        
        exp_home = 1 / (1 + 10**((old_away_elo - old_home_elo) / 400))
        exp_away = 1 - exp_home
        
        if(row["FTR"] == 'H'):
            act_home, act_away = 1 , 0
        elif(row["FTR"] == 'A'):
            act_home, act_away = 0 , 1
        else:
            act_home, act_away = 0.5 , 0.5
            
        new_home_elo = old_home_elo + K*(act_home - exp_home)
        new_away_elo = old_away_elo + K*(act_away - exp_away)
        
        ratings[home_team] = new_home_elo
        ratings[away_team] = new_away_elo
        
    
    df["home_elo"] = home_elo_list
    df["away_elo"] = away_elo_list   
    df["elo_diff"] = df["home_elo"] - df["away_elo"]
    
    
    df.to_csv(root / "data" / "processed" / "epl_with_elo.csv", index=False)
    
        

compute_elo()