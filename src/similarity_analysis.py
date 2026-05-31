import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import euclidean, cosine

file_path = Path(__file__).resolve()
root = file_path.parents[1]

df = pd.read_csv(root / "data" / "processed" / "Final_dataset.csv")

EXCLUDE_COLS = ['date', 'season', 'home', 'away', 'hg', 'ag', 'FTR']
COLS = [c for c in df.columns if c not in EXCLUDE_COLS]

X = df[COLS]

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ==========================================================
# 1. Euclidean Distance between sample matches
# ==========================================================

sample = X_scaled[500:510]

n = len(sample)
dist_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        dist_matrix[i][j] = euclidean(sample[i], sample[j])

plt.figure(figsize=(8, 6))
sns.heatmap(
    dist_matrix,
    annot=True,
    fmt=".2f",
    cmap="YlOrRd",
    xticklabels=[f"M{i+1}" for i in range(n)],
    yticklabels=[f"M{i+1}" for i in range(n)]
)

plt.title("Euclidean Distance Matrix (Sample Matches)")
plt.tight_layout()
plt.savefig(root / "assets" / "euclidean_distance.png")
plt.show()

print("Euclidean Distance Matrix:")
print(
    pd.DataFrame(
        dist_matrix,
        index=[f"M{i+1}" for i in range(n)],
        columns=[f"M{i+1}" for i in range(n)]
    ).round(3)
)

# ==========================================================
# 2. Cosine Similarity between sample matches
# ==========================================================

cos_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        cos_matrix[i][j] = 1 - cosine(sample[i], sample[j])

plt.figure(figsize=(8, 6))
sns.heatmap(
    cos_matrix,
    annot=True,
    fmt=".3f",
    cmap="Blues",
    xticklabels=[f"M{i+1}" for i in range(n)],
    yticklabels=[f"M{i+1}" for i in range(n)]
)

plt.title("Cosine Similarity Matrix (Sample Matches)")
plt.tight_layout()
plt.savefig(root / "assets" / "cosine_similarity.png")
plt.show()

print("\nCosine Similarity Matrix:")
print(
    pd.DataFrame(
        cos_matrix,
        index=[f"M{i+1}" for i in range(n)],
        columns=[f"M{i+1}" for i in range(n)]
    ).round(3)
)

# ==========================================================
# 3. Feature Statistics
# ==========================================================

print("\nFeature Statistics:")
print(df[COLS].describe().round(3))

# ==========================================================
# 4. Feature Correlation Analysis
# ==========================================================

corr_matrix = df[COLS].corr()

plt.figure(figsize=(14, 12))
sns.heatmap(
    corr_matrix,
    cmap="coolwarm",
    center=0,
    square=True
)

plt.title("Feature Correlation Matrix")
plt.tight_layout()
plt.savefig(root / "assets" / "feature_correlation.png")
plt.show()

# Find strongest correlations
corr_pairs = (
    corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )
    .stack()
    .sort_values(key=abs, ascending=False)
)

print("\nTop 20 Strongest Feature Correlations:")
print(corr_pairs.head(20).round(3))