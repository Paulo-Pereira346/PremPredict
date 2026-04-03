import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score,recall_score,precision_score,balanced_accuracy_score,confusion_matrix,classification_report
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns



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
Y = df["FTR"]
print(X.columns)

#Time-Series Split
tscv = TimeSeriesSplit(n_splits = 5)

ACC_list = []
recall_list = []
prec_list = []
bal_acc_list = []
pred_dist_list = []
actual_dist_list = []

for fold, (train_index,test_index) in enumerate(tscv.split(X)):
    
    X_train,X_test = X.iloc[train_index],X.iloc[test_index]
    Y_train,Y_test = Y.iloc[train_index],Y.iloc[test_index]
    
    scaler = StandardScaler()
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    #Define Model
    # model = LogisticRegression(class_weight='balanced',max_iter=1000)
    # model = GradientBoostingClassifier(random_state=42, n_estimators=200, max_depth=4, learning_rate=0.05, min_samples_leaf=10)
    model = GradientBoostingClassifier(
    random_state=42,
    learning_rate=0.03,
    max_depth=4,
    min_samples_leaf=20,
    n_estimators=100
    )
 
   #Fitting Models 
    # model.fit(X_train_scaled,Y_train)
    
    # sample_weights = compute_sample_weight(class_weight={'H':1.0,'D':1.3,'A':1.0},y=Y_train)
    sample_weights = compute_sample_weight(class_weight='balanced',y=Y_train)
    model.fit(X_train_scaled, Y_train, sample_weight=sample_weights)
   
   #Predicting test values 
    Y_pred = model.predict(X_test_scaled)
   
   #Error Calculation 
    ACC = accuracy_score(Y_test,Y_pred)
    recall = recall_score(Y_test,Y_pred,labels=['H','D','A'],average=None)
    precision = precision_score(Y_test,Y_pred,labels=['H','D','A'],average=None)
    bal_acc = balanced_accuracy_score(Y_test,Y_pred)
    pred_dist = pd.Series(Y_pred).value_counts(normalize=True)
    actual_dist = pd.Series(Y_test).value_counts(normalize=True)
    
    ACC_list.append(ACC)
    recall_list.append(recall)
    prec_list.append(precision)
    bal_acc_list.append(bal_acc)
    pred_dist_list.append(pred_dist)
    actual_dist_list.append(actual_dist)
    
    
# param_grid = {
# 'n_estimators': [100, 200, 300],
# 'max_depth': [3, 4, 5],
# 'learning_rate': [0.03, 0.05, 0.1],
# 'min_samples_leaf': [5, 10, 20]
# }

# grid = GridSearchCV(
# GradientBoostingClassifier(random_state=42),
# param_grid,
# cv=TimeSeriesSplit(n_splits=5),
# scoring='balanced_accuracy',
# n_jobs=-1,
# verbose=1
# )

# # sample_weights = compute_sample_weight(class_weight={'H':1.0,'D':1.3,'A':1.0},y=Y_train)
# sample_weights = compute_sample_weight(class_weight='balanced',y=Y_train)
# grid.fit(X_train_scaled, Y_train, sample_weight=sample_weights)

# print("Best params:", grid.best_params_)
# print("Best balanced accuracy:", grid.best_score_)

# Y_pred = grid.best_estimator_.predict(X_test_scaled)   

ACC_avg = sum(ACC_list) / len(ACC_list) 
print("Average of Accuracy Score is:", ACC_avg)

recall_avg = np.mean(recall_list, axis=0)
print("Avg Recall [H, D, A]:", recall_avg)

print("Avg Balanced Accuracy:", np.mean(bal_acc_list))

pred_dist_avg = pd.concat(pred_dist_list, axis=1).mean(axis=1)
actual_dist_avg = pd.concat(actual_dist_list, axis=1).mean(axis=1)

print("Avg Predicted Distribution:\n", pred_dist_avg)
print("Avg Actual Distribution:\n", actual_dist_avg)

print(classification_report(Y_test,Y_pred,labels=['H','D','A']))

Y_test_final = Y_test
Y_pred_final = Y_pred
cm = confusion_matrix(Y_test_final,Y_pred_final, labels=['H', 'D', 'A'])

plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=['H','D','A'], yticklabels=['H','D','A'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()