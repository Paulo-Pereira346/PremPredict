import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import PoissonRegressor

file_path = Path(__file__).resolve()
root = file_path.parents[1]

df = pd.read_csv(root / "data" / "processed" / "Final_dataset.csv")
df = df.sort_values("date").reset_index(drop=True)

EXCLUDE_COLS = ['date', 'season', 'home', 'away', 'hg', 'ag', 'FTR']
COLS = [c for c in df.columns if c not in EXCLUDE_COLS]

# --- 1. FTR Distribution ---
plt.figure(figsize=(6, 4))
colors = ['#2ecc71', '#f39c12', '#e74c3c']
df['FTR'].value_counts().plot(kind='bar', color=colors, edgecolor='black')
plt.title("Match Result Distribution (FTR)")
plt.xlabel("Result")
plt.ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(root / "assets" / "ftr_distribution.png")
plt.show()

# --- 2. Home vs Away Goals Distribution ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(df['hg'], bins=range(0, 12), color='steelblue', edgecolor='black', alpha=0.8)
axes[0].set_title("Home Goals Distribution")
axes[0].set_xlabel("Goals")
axes[0].set_ylabel("Frequency")
axes[1].hist(df['ag'], bins=range(0, 12), color='salmon', edgecolor='black', alpha=0.8)
axes[1].set_title("Away Goals Distribution")
axes[1].set_xlabel("Goals")
plt.tight_layout()
plt.savefig(root / "assets" / "goals_distribution.png")
plt.show()

# --- 3. Elo Diff vs Result ---
plt.figure(figsize=(8, 5))
for result, color in zip(['H', 'D', 'A'], ['#2ecc71', '#f39c12', '#e74c3c']):
    subset = df[df['FTR'] == result]['elo_diff']
    plt.hist(subset, bins=30, alpha=0.5, label=result, color=color)
plt.title("Elo Difference Distribution by Match Result")
plt.xlabel("Elo Difference (Home - Away)")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(root / "assets" / "elo_diff_by_result.png")
plt.show()

# --- 4. Feature Correlation Heatmap ---
key_features = ['elo_diff', 'form_diff_5', 'att_edge_5', 'sot_edge_5',
                 'H_gf_last_5_home', 'H_ga_last_5_home',
                 'A_gf_last_5_away', 'A_ga_last_5_away',
                 'H_draw_last_5', 'A_draw_last_5', 'match_balance', 'hg', 'ag']

plt.figure(figsize=(12, 9))
corr = df[key_features].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, square=True, linewidths=0.5)
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(root / "assets" / "correlation_heatmap.png")
plt.show()

# --- 5. Model Accuracy per Fold ---
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score

X_data = df[COLS]
Y = df['FTR']
tscv = TimeSeriesSplit(n_splits=5)
acc_list = []
bal_acc_list = []

for fold, (train_idx, test_idx) in enumerate(tscv.split(X_data)):
    X_train, X_test = X_data.iloc[train_idx], X_data.iloc[test_idx]
    Y_train, Y_test = Y.iloc[train_idx], Y.iloc[test_idx]
    model = GradientBoostingClassifier(random_state=42, learning_rate=0.03,
                                        max_depth=4, min_samples_leaf=20, n_estimators=100)
    sw = compute_sample_weight('balanced', y=Y_train)
    model.fit(X_train, Y_train, sample_weight=sw)
    Y_pred = model.predict(X_test)
    acc_list.append(accuracy_score(Y_test, Y_pred))
    bal_acc_list.append(balanced_accuracy_score(Y_test, Y_pred))

plt.figure(figsize=(8, 5))
folds = [f"Fold {i+1}" for i in range(5)]
x = np.arange(5)
width = 0.35
plt.bar(x - width/2, acc_list, width, label='Accuracy', color='steelblue', alpha=0.8)
plt.bar(x + width/2, bal_acc_list, width, label='Balanced Accuracy', color='salmon', alpha=0.8)
plt.axhline(y=0.452, color='gray', linestyle='--', label='Baseline (always H)')
plt.xlabel("Fold")
plt.ylabel("Score")
plt.title("Model Performance Across TimeSeriesSplit Folds")
plt.xticks(x, folds)
plt.legend()
plt.tight_layout()
plt.savefig(root / "assets" / "fold_accuracy.png")
plt.show()

print("Fold Accuracies:", [round(a, 3) for a in acc_list])
print("Avg Accuracy:", round(sum(acc_list)/len(acc_list), 3))
print("Avg Balanced Accuracy:", round(sum(bal_acc_list)/len(bal_acc_list), 3))