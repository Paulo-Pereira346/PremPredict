import pandas as pd
from pathlib import Path

def update_epl_data(year = None):
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]
    
    existing_path = root / "data" / "raw" / "epl_matches.csv"
    
    # Load existing data to find last date
    df_existing = pd.read_csv(existing_path)
    df_existing['date'] = pd.to_datetime(df_existing['date'])
    last_date = df_existing['date'].max()
    print(f"Last match date in database: {last_date}")
    
    # Download current season only
    if(year == None):
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if current_month < 8:
            season_start = current_year - 1
        else:
            season_start = current_year
            
    else:
        season_start = year
    

    
    prefix = str(season_start)[2:4]
    suffix = str(season_start + 1)[2:4]
    year_code = prefix + suffix
    
    try:
        df_web = pd.read_csv(f"https://www.football-data.co.uk/mmz4281/{year_code}/E0.csv")
        
        df_imp = df_web[["Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR","HS","AS","HST","AST"]]
        
        col_names = {
            "Date": "date", "HomeTeam": "home", "AwayTeam": "away",
            "FTHG": "hg", "FTAG": "ag", "HS": "home_shots",
            "AS": "away_shots", "HST": "home_sot", "AST": "away_sot"
        }
        
        df_imp = df_imp.rename(columns=col_names)
        df_imp.insert(1, "season", f"{season_start}/{season_start+1}")
        df_imp = df_imp.dropna(subset=['hg', 'ag'])
        df_imp['date'] = pd.to_datetime(df_imp['date'], dayfirst=True, errors='coerce')
        
        # Only keep matches newer than what we already have
        df_new = df_imp[df_imp['date'] > last_date]
        
        if df_new.empty:
            print("No new matches found.")
            return False
        
        print(f"Found {len(df_new)} new matches")
        
        # Cast types
        for col in ['hg', 'ag', 'home_shots', 'away_shots', 'home_sot', 'away_sot']:
            df_new[col] = df_new[col].astype(int)
        
        # Append to existing data
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.sort_values('date').reset_index(drop=True)
        df_combined.to_csv(existing_path, index=False)
        
        print(f"Database updated. Total matches: {len(df_combined)}")
        return True
        
    except Exception as e:
        print(f"Error updating data: {e}")
        return False

update_epl_data()