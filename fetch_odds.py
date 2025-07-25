import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = "2c2efd119d34af0b708047a6466fc0c1"
REGION = "us"
MARKET = "h2h"
CSV_FILE = "odds_history.csv"

def initialize_csv():
    """Create a fresh CSV with headers if it doesn't exist or is empty."""
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        columns = ["timestamp", "sport", "match", "bookmaker", "market", "team", "odds"]
        pd.DataFrame(columns=columns).to_csv(CSV_FILE, index=False)
        print("Created a fresh odds_history.csv")

def fetch_odds(sport="soccer_epl"):
    """Fetch odds and append to CSV."""
    initialize_csv()  # Ensure CSV exists with correct headers

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not isinstance(data, list):
        print(f"Error fetching odds: {data}")
        return

    rows = []
    for game in data:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    rows.append({
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "sport": sport,
                        "match": f"{game['home_team']} vs {game['away_team']}",
                        "bookmaker": bookmaker["title"],
                        "market": market["key"],
                        "team": outcome["name"],
                        "odds": outcome["price"],
                    })

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(CSV_FILE, mode="a", index=False, header=False)
        print(f"Fetched {len(df)} rows for {sport}")

if __name__ == "__main__":
    fetch_odds()
