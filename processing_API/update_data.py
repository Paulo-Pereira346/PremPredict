import pandas as pd
from pathlib import Path
from datetime import datetime

def get_season_code(year):
    prefix = str(year)[2:4]
    suffix = str(year + 1)[2:4]
    return prefix + suffix

def update_epl_data():
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]
    
    existing_path = root / "data" / "raw" / "epl_matches.csv"
    
    # Load existing data
    df_existing = pd.read_csv(existing_path)
    df_existing['date'] = pd.to_datetime(df_existing['date'])
    
    last_date = df_existing['date'].max()
    print(f"Last match date in database: {last_date}")
    
    # Get last season in dataset
    last_season_str = df_existing['season'].iloc[-1]
    last_season_start = int(last_season_str.split("/")[0])
    
    # Determine current season
    now = datetime.now()
    if now.month < 8:
        current_season_start = now.year - 1
    else:
        current_season_start = now.year
    
    print(f"Last season in dataset: {last_season_start}")
    print(f"Current season: {current_season_start}")
    
    # Generate all missing seasons
    seasons_to_fetch = list(range(last_season_start + 1, current_season_start + 1))
    
    if not seasons_to_fetch:
        print("No missing seasons. Checking current season for updates...")
    
    print(f"Fetching seasons: {seasons_to_fetch}")
    
    all_new_data = []

    for season_start in seasons_to_fetch:
        year_code = get_season_code(season_start)
        
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{year_code}/E0.csv"
            df_web = pd.read_csv(url)
            
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
            
            all_new_data.append(df_imp)
            
            print(f"Fetched season {season_start}/{season_start+1}")
        
        except Exception as e:
            print(f"Failed to fetch {season_start}: {e}")
    
    # Always fetch current season for updates
    if current_season_start not in seasons_to_fetch:
        print("Checking current season for new matches...")
        
        try:
            year_code = get_season_code(current_season_start)
            url = f"https://www.football-data.co.uk/mmz4281/{year_code}/E0.csv"
            
            df_web = pd.read_csv(url)
            
            df_imp = df_web[["Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR","HS","AS","HST","AST"]]
            
            col_names = {
                "Date": "date", "HomeTeam": "home", "AwayTeam": "away",
                "FTHG": "hg", "FTAG": "ag", "HS": "home_shots",
                "AS": "away_shots", "HST": "home_sot", "AST": "away_sot"
            }
            
            df_imp = df_imp.rename(columns=col_names)
            df_imp.insert(1, "season", f"{current_season_start}/{current_season_start+1}")
            df_imp = df_imp.dropna(subset=['hg', 'ag'])
            df_imp['date'] = pd.to_datetime(df_imp['date'], dayfirst=True, errors='coerce')
            
            all_new_data.append(df_imp)
            
            print("Checked current season for updates")
        
        except Exception as e:
            print(f"Failed to check current season: {e}")
    
    if not all_new_data:
        print("No data fetched.")
        return False
    
    df_new_all = pd.concat(all_new_data, ignore_index=True)
    
    # Filter ONLY truly new matches
    df_new = df_new_all[df_new_all['date'] >= last_date]

    if df_new.empty:
        print("No new matches found after filtering.")
        return False

    print(f"Found {len(df_new)} potential matches (including overlaps)")

    df_new = df_new.copy()

    for col in ['hg', 'ag', 'home_shots', 'away_shots', 'home_sot', 'away_sot']:
        df_new[col] = df_new[col].astype(int)

    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    df_combined = df_combined.drop_duplicates(
        subset=["date", "home", "away"],
        keep="last"
    )

    df_combined = df_combined.sort_values('date').reset_index(drop=True)
    
    df_combined.to_csv(existing_path, index=False)
    
    print(f"Database updated. Total matches: {len(df_combined)}")
    
    return True

if __name__ == "__main__":
    update_epl_data()