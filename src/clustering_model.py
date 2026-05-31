import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest

file_path = Path(__file__).resolve()
root = file_path.parents[1]

df = pd.read_csv(root / "data" / "processed" / "Final_dataset.csv")

EXCLUDE_COLS = ['date', 'season', 'home', 'away', 'hg', 'ag', 'FTR']
COLS = [c for c in df.columns if c not in EXCLUDE_COLS]

X = df[COLS].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- 1. Elbow Method ---
inertia = []
K_range = range(1, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertia.append(km.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(K_range, inertia, marker='o', color='steelblue')
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia")
plt.title("Elbow Method — Optimal Number of Clusters")
plt.grid(True)
plt.tight_layout()
plt.savefig(root / "assets" / "elbow_method.png")
plt.show()

# --- 2. K-Means Clustering (K=4) ---
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
pca_df = pd.DataFrame({
    "PC1": X_pca[:, 0],
    "PC2": X_pca[:, 1],
    "Cluster": df['Cluster'].astype(str),
    "Result": df['FTR']
})

plt.figure(figsize=(10, 7))
sns.scatterplot(data=pca_df, x="PC1", y="PC2", hue="Cluster",
                palette="Set1", s=40, alpha=0.6)
centers_pca = pca.transform(kmeans.cluster_centers_)
plt.scatter(centers_pca[:, 0], centers_pca[:, 1],
            c='black', s=300, marker='X', label='Centroids', zorder=5)
plt.title("K-Means Clustering of EPL Matches (PCA Projection)")
plt.legend()
plt.tight_layout()
plt.savefig(root / "assets" / "kmeans_clusters.png")
plt.show()

# Cluster composition
print("Cluster vs Match Result Distribution:")
print(pd.crosstab(df['Cluster'], df['FTR'], normalize='index').round(3))

print("\nCluster Feature Means:")
print(df.groupby('Cluster')[['elo_diff', 'form_diff_5', 'att_edge_5',
                               'H_gf_last_5_home', 'A_gf_last_5_away']].mean().round(3))

# --- 3. Outlier Detection using Isolation Forest ---
iso = IsolationForest(contamination=0.05, random_state=42)
df['Outlier'] = iso.fit_predict(X_scaled)
# -1 = outlier, 1 = normal
n_outliers = (df['Outlier'] == -1).sum()
print(f"\nIsolation Forest detected {n_outliers} outliers ({n_outliers/len(df)*100:.1f}% of matches)")

plt.figure(figsize=(10, 7))
colors = df['Outlier'].map({1: 'steelblue', -1: 'red'})
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=colors, s=20, alpha=0.5)
plt.scatter([], [], c='steelblue', label='Normal', s=40)
plt.scatter([], [], c='red', label='Outlier', s=40)
plt.title("Outlier Detection — Isolation Forest (PCA Projection)")
plt.legend()
plt.tight_layout()
plt.savefig(root / "assets" / "outlier_detection.png")
plt.show()

print("\nOutlier Match Result Distribution:")
print(df[df['Outlier'] == -1]['FTR'].value_counts())