import pandas as pd
import json

with open("../data/raw/2022_23_league_table_raw.json","r", encoding="utf-8") as f:
    json_data = json.load(f)

# print(json_data[0])

df_prem = pd.DataFrame(json_data)
df_prem.set_index("Position",inplace=True)
# print(df_prem.head())

df_prem.info()
df_prem.describe()