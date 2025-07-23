import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os

API_KEY = 'your_api_key_here'
SPORT = 'soccer_epl'
REGION = 'us'
MARKET = 'h2h'

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': REGION,
        'markets': MARKET,
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    data = response.json()

    rows = []
    for game in data:
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    rows.append({
                        'timestamp': datetime.utcnow(),
                        'match': f"{game['home_team']} vs {game['away_team']}",
                        'bookmaker': bookmaker['title'],
                        'market': market['key'],
                        'team': outcome['name'],
                        'odds': outcome['price']
                    })

    df = pd.DataFrame(rows)

    conn = sqlite3.connect("odds_data.db")
    df.to_sql("odds", conn, if_exists="append", index=False)
    conn.close()

if __name__ == "__main__":
    fetch_odds()
