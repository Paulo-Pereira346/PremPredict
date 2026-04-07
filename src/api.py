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

    probs = {"H": home_win_prob, "D": draw_prob, "A": away_win_prob}
    return max(probs, key=probs.get)



def predict_match(input_data: dict):
    try:
        # Convert to DataFrame
        df = pd.DataFrame([input_data])

        # Enforce column order (CRITICAL)
        df = df[feature_cols]

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing or incorrect feature: {str(e)}"
        )

    lambda_home = model_home.predict(df)[0]
    lambda_away = model_away.predict(df)[0]

    outcome = predict_outcome(lambda_home, lambda_away)

    return {
        "lambda_home": float(lambda_home),
        "lambda_away": float(lambda_away),
        "prediction": outcome,
        "score": f"{round(lambda_home)}-{round(lambda_away)}"
    }


#Endpoint
@app.post("/predict")
def predict(data: dict):
    return predict_match(data)