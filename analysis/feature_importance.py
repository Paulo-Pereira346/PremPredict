import joblib
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

file_path = Path(__file__).resolve()
root = file_path.parents[1]

home_model = joblib.load( root / "models" / "poisson_home.pkl")
away_model = joblib.load( root / "models" / "poisson_away.pkl")
COLS = joblib.load( root / "models" / "feature_columns.pkl")


# Get coefficients
coef_home = pd.Series(home_model.coef_, index=COLS).sort_values(key=abs, ascending=False)
coef_away = pd.Series(away_model.coef_, index=COLS).sort_values(key=abs, ascending=False)

# Plot top 15 features for home model
plt.figure(figsize=(10, 6))
coef_home.head(15).plot(kind='barh')
plt.title('Top 15 Features — Home Goals Model')
plt.xlabel('Coefficient')
plt.tight_layout()
plt.show()

# Plot top 15 features for away model
plt.figure(figsize=(10, 6))
coef_away.head(15).plot(kind='barh')
plt.title('Top 15 Features — Away Goals Model')
plt.xlabel('Coefficient')
plt.tight_layout()
plt.show()

print("Top 10 Home Model Features:")
print(coef_home.head(10))
print("\nTop 10 Away Model Features:")
print(coef_away.head(10))