import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from scipy.stats import poisson
from sklearn.linear_model import PoissonRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error,accuracy_score, recall_score, precision_score, balanced_accuracy_score
from scipy.stats import poisson

def predict_outcome(lambda_home, lambda_away, max_goals=10):
    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0
    best_prob = -1
    scoreline = {"home": 0, "away": 0}

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

            # if p > best_prob:
            #     best_prob = p
            #     scoreline["home"] = i
            #     scoreline["away"] = j

            if i > j:
                home_win_prob += p
            elif i == j:
                draw_prob += p
            else:
                away_win_prob += p

    probs = {"H": home_win_prob, "D": draw_prob, "A": away_win_prob}
    return max(probs, key=probs.get)

def retrain_and_save():
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]
    
    df = pd.read_csv(root / "data" / "processed" / "Final_dataset.csv")
    df = df.sort_values("date").reset_index(drop=True)
    
    EXCLUDE_COLS = ['date', 'season', 'home', 'away', 'hg', 'ag', 'FTR']
    COLS = [c for c in df.columns if c not in EXCLUDE_COLS]
    
    X = df[COLS]
    Y_home = df["hg"]
    Y_away = df["ag"]
    
    model_home = PoissonRegressor(max_iter=1000)
    model_away = PoissonRegressor(max_iter=1000)
    model_home.fit(X, Y_home)
    model_away.fit(X, Y_away)
    
    (root / "models").mkdir(exist_ok=True)
    joblib.dump(model_home, root / "models" / "poisson_home.pkl")
    joblib.dump(model_away, root / "models" / "poisson_away.pkl")
    joblib.dump(COLS, root / "models" / "feature_columns.pkl")
    print("Models retrained and saved")
    
    
if __name__ == "__main__":
    file_path = Path(__file__).resolve()
    root = file_path.parents[1]

    df = pd.read_csv(root / "data"/ "processed" / "Final_dataset.csv")
    df = df.sort_values("date").reset_index(drop=True)

    EXCLUDE_COLS = ['date', 'season', 'home', 'away', 'hg', 'ag', 'FTR']
    COLS = df.columns.tolist()

    for col in EXCLUDE_COLS:
        COLS.remove(col)

    #Defining X and Y variables
    X = df[COLS]
    Y_home = df["hg"]
    Y_away = df["ag"]
    Y_res = df["FTR"]

    print(X.columns)
    #Time-Series Split
    tscv = TimeSeriesSplit(n_splits = 5)

    # Poisson Regression and Gradient Boosting training and comparison
    MAE_home_list_Pois = []
    MAE_away_list_Pois = []
    ACC_list = []
    recall_list = []
    bal_acc_list = []
    pred_dist_list = []


    for fold, (train_index, test_index) in enumerate(tscv.split(X)):
        
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        Y_home_train, Y_home_test = Y_home.iloc[train_index], Y_home.iloc[test_index]
        Y_away_train, Y_away_test = Y_away.iloc[train_index], Y_away.iloc[test_index]
        Y_res_train, Y_res_test = Y_res.iloc[train_index], Y_res.iloc[test_index]

        model_home_pois = PoissonRegressor(max_iter=1000)
        model_away_pois = PoissonRegressor(max_iter=1000)

        model_home_pois.fit(X_train, Y_home_train)
        model_away_pois.fit(X_train, Y_away_train)

        Y_home_pred = model_home_pois.predict(X_test)
        Y_away_pred = model_away_pois.predict(X_test)

        # MAE
        MAE_home_list_Pois.append(mean_absolute_error(Y_home_test, Y_home_pred))
        MAE_away_list_Pois.append(mean_absolute_error(Y_away_test, Y_away_pred))

        # Outcome prediction
        # Y_res_list = []
        # scoreline_list = []
        # for i in range(len(Y_home_pred)):
        #     outcome, home_goals, away_goals = predict_outcome(Y_home_pred[i], Y_away_pred[i])
        #     Y_res_list.append(outcome)
        #     scoreline_list.append((home_goals, away_goals))
        
        Y_res_list = []
        scoreline_list = []

        for i in range(len(Y_home_pred)):
            outcome = predict_outcome(Y_home_pred[i], Y_away_pred[i])
            
            Y_res_list.append(outcome)
            scoreline_list.append((round(Y_home_pred[i]), round(Y_away_pred[i])))

        Y_res_pred = pd.Series(Y_res_list, index=Y_res_test.index)

        ACC_list.append(accuracy_score(Y_res_test, Y_res_pred))
        recall_list.append(recall_score(Y_res_test, Y_res_pred, labels=['H','D','A'], average=None))
        bal_acc_list.append(balanced_accuracy_score(Y_res_test, Y_res_pred))
        pred_dist_list.append(pd.Series(Y_res_list).value_counts(normalize=True))
    
        
    MAE_home_avg_Pois = sum(MAE_home_list_Pois) / len(MAE_home_list_Pois) 
    MAE_away_avg_Pois = sum(MAE_away_list_Pois) / len(MAE_away_list_Pois) 

    print("(Poisson)Average of MAE for Home is:", MAE_home_avg_Pois)
    print("(Poisson)Average of MAE for Away is:", MAE_away_avg_Pois)
    print("(Poisson) Avg Accuracy:", sum(ACC_list)/len(ACC_list))
    print("(Poisson) Avg Recall [H,D,A]:", np.mean(recall_list, axis=0))
    print("(Poisson) Avg Balanced Accuracy:", np.mean(bal_acc_list))
    print("(Poisson) Avg Predicted Distribution:\n", pd.concat(pred_dist_list, axis=1).mean(axis=1))
    print("Baseline (always H):", (Y_res == 'H').mean())

    results_df = pd.DataFrame({
        "actual_result": Y_res_test,
        "predicted_result": Y_res_pred,
        "actual_score": list(zip(df.loc[Y_res_test.index, "hg"], df.loc[Y_res_test.index, "ag"])),
        "predicted_score": scoreline_list
    })
    print(results_df.head(20))

    # H/A only evaluation (last fold)
    mask = Y_res_test != 'D'
    Y_res_test_no_draw = Y_res_test[mask]
    Y_res_pred_no_draw = Y_res_pred[mask]

    print("\nH/A only accuracy:", accuracy_score(Y_res_test_no_draw, Y_res_pred_no_draw))
    print("H/A only recall [H, A]:", recall_score(Y_res_test_no_draw, Y_res_pred_no_draw, labels=['H','A'], average=None))

    model_home_final = PoissonRegressor(max_iter=1000)
    model_away_final = PoissonRegressor(max_iter=1000)
    model_home_final.fit(X, Y_home)
    model_away_final.fit(X, Y_away)

    (root / "models").mkdir(exist_ok=True)
    joblib.dump(model_home_final, root / "models" / "poisson_home.pkl")
    joblib.dump(model_away_final, root / "models" / "poisson_away.pkl")
    joblib.dump(COLS, root / "models" / "feature_columns.pkl")
    print("Models saved")
