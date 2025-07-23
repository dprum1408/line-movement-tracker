import requests
import pandas as pd
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine

API_KEY = '2c2efd119d34af0b708047a6466fc0c1'
SPORT = 'soccer_epl'
REGION = 'us'
MARKET = 'h2h'
postgresql://postgres:[Ladlad081404!]@db.cbocblphttmjtaeenbbr.supabase.co:5432/postgres"

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

    engine = create_engine(DB_URI)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['odds'] = pd.to_numeric(df['odds'], errors='coerce')
    df = df.dropna(subset=['odds'])  # Drop rows where odds couldn't be converted

    # Optional: Round odds for consistency
    df['odds'] = df['odds'].round(4)
    df.to_sql("odds", engine, if_exists="append", index=False)

if __name__ == "__main__":
    fetch_odds()
