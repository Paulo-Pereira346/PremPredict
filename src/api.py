from fastapi import FastAPI, HTTPException
import pandas as pd
import joblib
from pathlib import Path
from scipy.stats import poisson

app = FastAPI()

#Load Models
file_path = Path(__file__).resolve()
root = file_path.parents[1]

model_home = joblib.load(root / "models" / "poisson_home.pkl")
model_away = joblib.load(root / "models" / "poisson_away.pkl")
feature_cols = joblib.load(root / "models" / "feature_columns.pkl")



def predict_outcome(lambda_home, lambda_away, max_goals=10):
    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

            if i > j:
                home_win_prob += p
            elif i == j:
                draw_prob += p
            else:
                away_win_prob += p
    
    #Normalization
    total = home_win_prob + draw_prob + away_win_prob
    if total > 0:
        home_win_prob /= total
        draw_prob /= total
        away_win_prob /= total

    probs = {"H": home_win_prob, "D": draw_prob, "A": away_win_prob}
    return max(probs, key=probs.get),home_win_prob, draw_prob, away_win_prob



def predict_match(input_data: dict):
    try:
        df = pd.DataFrame([input_data])

        # Enforce column order 
        df = df[feature_cols]

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing or incorrect feature: {str(e)}"
        )

    lambda_home = model_home.predict(df)[0]
    lambda_away = model_away.predict(df)[0]

    outcome,home_prob, draw_prob, away_prob = predict_outcome(lambda_home, lambda_away)

    return {
        "lambda_home": round(float(lambda_home),3),
        "lambda_away": round(float(lambda_away),3),
        "prediction": outcome,
        
        "predicted_score": f"{round(lambda_home)}-{round(lambda_away)}",
        
        "probabilities": {
            "home_win":round(home_prob,3),
            "draw":round(draw_prob,3),
            "away_win":round(away_prob,3)
        }
    }

def rolling(df, team):
    df = df[df["team"] == team].sort_values("date")
    
    result = {}
    
    # For non-venue-split stats — last 5 and 10 games overall
    for att in ["gd", "sot", "cs"]:
        result[f"{att}_last_5"] = df[att].tail(5).mean()
        result[f"{att}_last_10"] = df[att].tail(10).mean()
    
    # For venue-split stats — last 5 home and away separately
    for att in ["gf", "ga", "win", "points"]:
        result[f"{att}_last_5_home"] = df[df["venue"] == "home"][att].tail(5).mean()
        result[f"{att}_last_5_away"] = df[df["venue"] == "away"][att].tail(5).mean()
    
    # Cumulative stats
    result["cum_gf"] = df["gf"].mean()
    result["cum_ga"] = df["ga"].mean()
    result["cum_points"] = df["points"].mean()
    
    return result


def feature_eng(home,away,date):
    
    data = {}
    #Date is entered by user in YYYY-MM-DD format
    data["date"] = pd.to_datetime(date, dayfirst=True, errors="coerce")
    season = int(date[:4])
    season = f"{season-1}/{season}"
    data["season"] = season
    data["home"] = home
    data["away"] = away
    
    df_roll = pd.read_csv(root / "data" / "processed" / "epl_pre_rolling.csv")
    df_cur_elo = pd.read_csv(root / "data" / "api_data" / "current_elo.csv")
    
    home_elo = int(df_cur_elo.loc[df_cur_elo["team"] == home, "current_elo"].iloc[0])
    away_elo = int(df_cur_elo.loc[df_cur_elo["team"] == away, "current_elo"].iloc[0])
    
    data["elo_diff"] = home_elo - away_elo
    
    rolling_home = rolling(df_roll,home)
    rolling_away = rolling(df_roll,away)
    
    for venue in ["H","A"]:
        for col in list(rolling_home):
            if venue == "H":
                data[f"{venue}_{col}"] = rolling_home[col]
                
            if venue == "A":
                data[f"{venue}_{col}"] = rolling_away[col]
        
    #Calculating complex derived features
    data["form_diff_5"] = data["H_points_last_5_home"] - data["A_points_last_5_away"]
    data["att_edge_5"] = data["H_gf_last_5_home"] - data["A_ga_last_5_away"]
    data["cum_att_edge"] = data["H_cum_gf"] - data["A_cum_ga"]
    data["sot_edge_5"] = data["H_sot_last_5"] - data["A_sot_last_5"]
    data["sot_edge_10"] = data["H_sot_last_10"] - data["A_sot_last_10"]
    data["def_matchup_5"] = data["H_ga_last_5_home"] + data["A_ga_last_5_away"]
    data["att_matchup_5"] = data["H_gf_last_5_home"] + data["A_gf_last_5_away"]
    data["elo_diff_abs"] = abs(data["elo_diff"])
    data["form_diff_5_abs"] = abs(data["form_diff_5"])
    data["match_balance"] = data["elo_diff_abs"] + data["form_diff_5_abs"] + abs(data["att_edge_5"])
    data["H_draw_last_5"] = data["H_points_last_5_home"] - 3 * data["H_win_last_5_home"]
    data["A_draw_last_5"] = data["A_points_last_5_away"] - 3 * data["A_win_last_5_away"]
    
    EXCLUDE = ['date', 'season', 'home', 'away']
    input_data = {k: v for k, v in data.items() if k not in EXCLUDE}
    return input_data
    
@app.get("/predict")
def predict(home: str, away: str, date: str):
    input = feature_eng(home, away, date)  
    return predict_match(input)
    
