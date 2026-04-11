import pandas as pd
from pathlib import Path

def compute_elo():
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]
    
    df = pd.read_csv(root / "data" / "raw" / "epl_matches.csv")
    
    df['date'] = pd.to_datetime(df['date'],errors='coerce')
    df = df.dropna(subset=['date'])
    
    df['hg'] = df['hg'].astype(int)
    df['ag'] = df['ag'].astype(int)
    
    df = df.sort_values('date').reset_index(drop=True)
    
    K = 32
    initial_elo = 1500
    elo_ratings = {}
    
    home_elos = []
    away_elos = []
    
    for _, row in df.iterrows():
        home = row['home']
        away = row['away']
        
        # Get current Elo or assign initial
        home_elo = elo_ratings.get(home, initial_elo)
        away_elo = elo_ratings.get(away, initial_elo)
        
        home_elos.append(home_elo)
        away_elos.append(away_elo)
        
        # Expected scores
        expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
        expected_away = 1 - expected_home
        
        # Actual scores
        if row['hg'] > row['ag']:
            actual_home, actual_away = 1, 0
        elif row['hg'] < row['ag']:
            actual_home, actual_away = 0, 1
        else:
            actual_home, actual_away = 0.5, 0.5
        
        # Update Elo
        elo_ratings[home] = home_elo + K * (actual_home - expected_home)
        elo_ratings[away] = away_elo + K * (actual_away - expected_away)
    
    df['home_elo'] = home_elos
    df['away_elo'] = away_elos
    df['elo_diff'] = df['home_elo'] - df['away_elo']
    
    df.to_csv(root / "data" / "processed" / "epl_with_elo.csv", index=False)
    print(f"Elo computed for {len(df)} matches")
    
    # Also save current Elo ratings for API use
    elo_df = pd.DataFrame([
        {"team": team, "current_elo": elo} 
        for team, elo in elo_ratings.items()
    ])
    
    (root / "data" / "api_data").mkdir(exist_ok=True)
    elo_df.to_csv(root / "data" / "api_data" / "current_elo.csv", index=False)
    print("Current Elo ratings saved")

if __name__ == "__main__":
    compute_elo()