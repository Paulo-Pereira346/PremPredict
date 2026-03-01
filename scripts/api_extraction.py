import requests
import json

for season in range(2015,2023):
    print(f"This is Season {season} data")
    season_data = []
    for i in range(1,39):
        api_url = f"https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v5/competitions/8/seasons/{season}/matchweeks/{i}/standings?live=false"
        response = requests.get(api_url)

        if(response.status_code != 200):
            continue

        print(i)
        data = response.json()
        # print(data.keys())

        # print(data["tables"])
        # print(data["tables"][0].keys())
        

        entries = data["tables"][0]["entries"]
    # print(len(entries))
    # # print(entries[0])


        for entry in entries:
            dict_team = {
                "season": season,
                "matchweek": data["matchweek"],
                "team": entry['team']['name'],

                "overall_pos": entry['overall']['position'],
                "overall_wins" : entry['overall']['won'],
                "overall_loss" : entry['overall']['lost'],
                "overall_draws" : entry['overall']['drawn'],
                "overall_points": entry['overall']['points'],
                "overall_played": entry['overall']['played'],
                "overall_gf": entry['overall']['goalsFor'],
                "overall_ga": entry['overall']['goalsAgainst'],

                "home_pos": entry['home']['position'],
                "home_wins" : entry['home']['won'],
                "home_loss" : entry['home']['lost'],
                "home_draws" : entry['home']['drawn'],
                "home_points": entry['home']['points'],
                "home_played": entry['home']['played'],
                "home_gf": entry['home']['goalsFor'],
                "home_ga": entry['home']['goalsAgainst'],

                "away_pos": entry['away']['position'],
                "away_wins" : entry['away']['won'],
                "away_loss" : entry['away']['lost'],
                "away_draws" : entry['away']['drawn'],
                "away_points": entry['away']['points'],
                "away_played": entry['away']['played'],
                "away_gf": entry['away']['goalsFor'],
                "away_ga": entry['away']['goalsAgainst'],

            }

            dict_team["away_gd"] = dict_team["away_gf"] - dict_team["away_ga"]
            dict_team["home_gd"] = dict_team["home_gf"] - dict_team["home_ga"]
            dict_team["overall_gd"] = dict_team["overall_gf"] - dict_team["overall_ga"]

            season_data.append(dict_team)

            # print(dict_team)
    with open(f"../data/raw/{season}_{season-2000+1}_standings.json","w",encoding="utf-8") as f:
        json.dump(season_data,f,indent=4)