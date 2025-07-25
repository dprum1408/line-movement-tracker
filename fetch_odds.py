import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = "your_api_key_here"
SPORT = "soccer_epl"
REGION = "us"
MARKET = "h2h"
CSV_FILE = "odds_history.csv"

def clean_csv():
    """Load and clean the CSV (timestamps, odds)."""
    if not os.path.exists(CSV_FILE):
        return
    df = pd.read_csv(CSV_FILE)

    # Clean timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Clean odds
    df["odds"] = pd.to_numeric(df["odds"], errors="coerce")
    df = df.dropna(subset=["odds"])

    # Save cleaned CSV
    df.to_csv(CSV_FILE, index=False)

def fetch_odds(sport=SPORT):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal",
    }
    response = requests.get(url, params=params)
    data = response.json()

    rows = []
    for game in data:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    rows.append(
                        {
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "match": f"{game['home_team']} vs {game['away_team']}",
                            "bookmaker": bookmaker["title"],
                            "market": market["key"],
                            "team": outcome["name"],
                            "odds": outcome["price"],
                        }
                    )

    if rows:
        df = pd.DataFrame(rows)
        file_exists = os.path.isfile(CSV_FILE)
        df.to_csv(CSV_FILE, mode="a", index=False, header=not file_exists)
        clean_csv()
        print(f"Fetched {len(df)} rows for {sport} at {datetime.utcnow()}")

if __name__ == "__main__":
    fetch_odds()
