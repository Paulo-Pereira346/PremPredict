import pandas as pd
from pathlib import Path
from sklearn.linear_model import PoissonRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error


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

#Time-Series Split
tscv = TimeSeriesSplit(n_splits = 5)

# Poisson Regression and Gradient Boosting training and comparison
MAE_home_list_Pois = []
MAE_away_list_Pois = []

MAE_home_list_GB = []
MAE_away_list_GB = []

for fold, (train_index,test_index) in enumerate(tscv.split(X)):
    
    X_train,X_test = X.iloc[train_index],X.iloc[test_index]
    Y_home_train,Y_home_test = Y_home.iloc[train_index],Y_home.iloc[test_index]
    Y_away_train,Y_away_test = Y_away.iloc[train_index],Y_away.iloc[test_index]
    
    #Define Models
    model_home_pois = PoissonRegressor(max_iter=200)   #Using parameters for poisson since Poisson baseline prediction was better
    model_away_pois = PoissonRegressor(max_iter=200)
     
    model_home_gb = GradientBoostingRegressor(n_estimators=300,max_depth=4,learning_rate=0.04,subsample=0.8,min_samples_leaf=8,random_state=42)
    model_away_gb = GradientBoostingRegressor(n_estimators=300,max_depth=4,learning_rate=0.04,subsample=0.8,min_samples_leaf=8,random_state=42)
   
   #Fitting Models 
    model_home_pois.fit(X_train,Y_home_train)
    model_away_pois.fit(X_train,Y_away_train)
    
    model_home_gb.fit(X_train,Y_home_train)
    model_away_gb.fit(X_train,Y_away_train)
   
   #Predicting test values 
    Y_home_pred_pois = model_home_pois.predict(X_test)
    Y_away_pred_pois = model_away_pois.predict(X_test)
    
    Y_home_pred_gb = model_home_gb.predict(X_test)
    Y_away_pred_gb = model_away_gb.predict(X_test)
   
   #Error Calculation 
    MAE_home_pois = mean_absolute_error(Y_home_test,Y_home_pred_pois)
    MAE_away_pois = mean_absolute_error(Y_away_test,Y_away_pred_pois)
           
    MAE_home_gb = mean_absolute_error(Y_home_test,Y_home_pred_gb)
    MAE_away_gb = mean_absolute_error(Y_away_test,Y_away_pred_gb)
    
    MAE_home_list_Pois.append(MAE_home_pois)
    MAE_away_list_Pois.append(MAE_away_pois)
    
    MAE_home_list_GB.append(MAE_home_gb)
    MAE_away_list_GB.append(MAE_away_gb)
   
    
MAE_home_avg_Pois = sum(MAE_home_list_Pois) / len(MAE_home_list_Pois) 
MAE_away_avg_Pois = sum(MAE_away_list_Pois) / len(MAE_away_list_Pois) 

MAE_home_avg_GB = sum(MAE_home_list_GB) / len(MAE_home_list_GB) 
MAE_away_avg_GB = sum(MAE_away_list_GB) / len(MAE_away_list_GB) 

print("(Poisson)Average of MAE for Home is:", MAE_home_avg_Pois)
print("(Poisson)Average of MAE for Away is:", MAE_away_avg_Pois)

print("(Gradient Boosting)Average of MAE for Home is:", MAE_home_avg_GB)
print("(Gradient Boosting)Average of MAE for Away is:", MAE_away_avg_GB)    
