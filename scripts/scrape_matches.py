import requests 
from bs4 import BeautifulSoup
import re
import json

#URL to be scraped
url = "https://en.wikipedia.org/wiki/2022%E2%80%9323_Premier_League#League_table"

#Additional header information to bypass security 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url,headers=headers)            #Sending GET request to URL and storing response HTTP in response variable
print(response.status_code)

soup = BeautifulSoup(response.text,"html.parser")       #Initializing BeautifulSoup Object

print(soup.title)

# tables = soup.find_all("table")
# print("No. of tables is:", len(tables))

wiki_tables = soup.find_all("table",class_="wikitable")      #Finding all tables with class wiki_tables
# print("No. of tables is:", len(wiki_tables))


# for i, table in enumerate(wiki_tables):           #Finding which table with class "wiki_tables" 
#     header = table.find("tr")                     # has the league table using for loop
#     print(f"\nTable index: {i}")
#     print(header.text.strip())

# Table no 3 is the league table

league_table = wiki_tables[3]
# print(league_table)

rows = league_table.find_all("tr")
# print(len(rows))
# print(rows[0].text.strip())

# print(rows[1])
# print(rows[1].text.strip())

# cells = rows[1].find_all(["th","td"])

# print(len(cells))

# for i, cell in enumerate(cells):
#     print(f"{i} : {cell.text.strip()}")

# dict_row = {
#     "Position":  int(cells[0].text.strip()),  
# 	"Team":  cells[1].text.strip(),
#     "Pld":   int(cells[2].text.strip()),
#     "Wins":  int(cells[3].text.strip()),
#     "Draws": int(cells[4].text.strip()),
#     "Losses": int(cells[5].text.strip()),
#     "GF": int(cells[6].text.strip()),
#     "GA": int(cells[7].text.strip()),
#     "GD": cells[8].text.strip(),
#     "Pts": int(cells[9].text.strip()),
#     "Qualification": cells[10].text.strip()
# }

#Storing all cells of all rows in the form of a list of dictionaries where each row is
# one dictionary

dict_table = []
qual = None
for row in rows[1:]:   
    cell = row.find_all(["th","td"])
    if not cell:
        continue
    
    dict_row = {
    "Position":  int(cell[0].text.strip()),  
    "Team":  re.sub(r" \(.*?\)","",cell[1].text.strip()),
    "Pld":   int(cell[2].text.strip()),
    "Wins":  int(cell[3].text.strip()),
    "Draws": int(cell[4].text.strip()),
    "Losses": int(cell[5].text.strip()),
    "GF": int(cell[6].text.strip()),
    "GA": int(cell[7].text.strip()),
    "GD": int(cell[8].text.strip().replace("−", "-")),
    "Pts": int(cell[9].text.strip()),
    }
    if(len(cell)==11):
        dict_row["Qualification"] = re.sub(r"\[.*?\]", "", cell[10].text.strip())        
        qual = dict_row["Qualification"]
    else:
        dict_row["Qualification"] =  qual
    dict_table.append(dict_row)

# print(dict_table)
# print(len(dict_table))

#Storing structurally normalized dict_table in raw folder

# with open("../data/raw/2022_23_league_table_raw.json","w", encoding="utf-8") as f:
#     json.dump(dict_table,f,indent=4)

with open("../data/raw/2022_23_league_table_raw.json","r", encoding="utf-8") as f:
    json_data = json.load(f)

print(json_data[0])


