import pandas as pd 
def download_epl_seasons(start_year,end_year):
    frames = []
    for year in range(start_year,end_year):
        prefix = str(year)[2:4]
        suffix = str(year + 1)[2:4]
        year_code = prefix+suffix
        # print(year_code)
        
        try:
            df_web = pd.read_csv(f"https://www.football-data.co.uk/mmz4281/{year_code}/E0.csv")
            
            # filename = f"../data/raw/football-data_website/league{year}_{suffix}.csv"
            
            df_imp = df_web[["Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR","HS","AS","HST","AST"]]
            
            col_names = {
                "Date" : "date",
                "HomeTeam" : "home",
                "AwayTeam" : "away",
                "FTHG" : "hg",
                "FTAG" : "ag",
                "HS" : "home_shots",
                "AS" : "away_shots",
                "HST" : "home_sot",
                "AST" : "away_sot"
            }
            
            df_imp = df_imp.rename(columns=col_names)
            
            df_imp.insert(1,"season",f"{year}/{year+1}")
            
            # if(year == 2010):
            #     print(df_imp.head())
            
            frames.append(df_imp)       
            
        #     with open(filename,"w",encoding="utf-8") as f:
        #         f.write(response.content.decode('utf-8'))
        except IOError as e:
            print(f"An error occurred while saving the file: {e}")
    
    df_prem = pd.concat(frames,ignore_index=True) 
    
    df_prem = df_prem.dropna(subset = ['hg','ag'])
    
    df_prem['date'] = pd.to_datetime(df_prem['date'],dayfirst=True, errors="coerce")
    
    # df_prem['hg'] = pd.to_numeric(df_prem['hg'],errors = "coerce")
    # df_prem['ag'] = pd.to_numeric(df_prem['ag'],errors = "coerce")
    # df_prem['home_shots'] = pd.to_numeric(df_prem['home_shots'],errors = "coerce")
    # df_prem['away_shots'] = pd.to_numeric(df_prem['away_shots'],errors = "coerce")
    # df_prem['home_sot'] = pd.to_numeric(df_prem['home_sot'],errors = "coerce")
    # df_prem['away_sot'] = pd.to_numeric(df_prem['away_sot'],errors = "coerce")
       
    
    # print(df_prem['hg'].isnull().sum())
    # print(df_prem['ag'].isnull().sum())
    # print(df_prem['home_shots'].isnull().sum())
    # print(df_prem['away_shots'].isnull().sum())
    # print(df_prem['home_sot'].isnull().sum())
    # print(df_prem['away_sot'].isnull().sum())
    
    # print(df_prem[df_prem.isnull().any(axis=1)].count())
    
    df_prem['hg'] = df_prem['hg'].astype(int)
    df_prem['ag'] = df_prem['ag'].astype(int)
    df_prem['home_shots'] = df_prem['home_shots'].astype(int)
    df_prem['away_shots'] = df_prem['away_shots'].astype(int)
    df_prem['home_sot'] = df_prem['home_sot'].astype(int)
    df_prem['away_sot'] = df_prem['away_sot'].astype(int)
    
    df_prem.sort_values(by='date',ascending=True,inplace=True)
    df_prem.reset_index(drop=True, inplace=True)

    print(df_prem.head())  
    print(df_prem.tail())
    
    # print(df_prem.info())
    
    df_prem.to_csv("../data/raw/epl_matches.csv",index=False)
    
        
 
                   
download_epl_seasons(2010,2024)