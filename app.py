import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import os

st.set_page_config(layout="wide")
st.title("📉 Line Movement Tracker")

API_KEY = "2c2efd119d34af0b708047a6466fc0c1"  # Add your Odds API key here
REGION = "us"
MARKET = "h2h"
CSV_FILE = "odds_history.csv"

# --- Function to fetch odds ---
def fetch_odds(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data or isinstance(data, dict) and data.get("message"):
        st.error(f"Error fetching odds: {data.get('message', 'Unknown error')}")
        return

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
        st.success(f"Fetched {len(df)} rows for {sport} at {datetime.utcnow()}")

# --- Sidebar: Sport Selection ---
st.sidebar.header("⚙️ Settings")
sport = st.sidebar.selectbox(
    "Choose a sport/league:",
    [
        "soccer_epl",
        "soccer_uefa_champs_league",
        "basketball_nba",
        "americanfootball_nfl",
        "baseball_mlb",
    ],
)

if st.sidebar.button("Fetch Odds Now"):
    fetch_odds(sport)

# --- Load and Display Data ---
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df["odds"] = pd.to_numeric(df["odds"], errors="coerce")
    df = df.dropna(subset=["odds"])

    matches = df["match"].unique()
    selected_match = st.sidebar.selectbox("Select Match", matches)
    filtered = df[df["match"] == selected_match]

    st.subheader(f"📊 Summary Stats for {selected_match}")
    summary = filtered.groupby("team")["odds"].agg(["min", "max", "mean"]).round(3)
    st.dataframe(summary)

    # Plot odds
    teams = filtered["team"].unique()
    for team in teams:
        team_df = filtered[filtered["team"] == team]
        fig, ax = plt.subplots()
        for book in team_df["bookmaker"].unique():
            sub = team_df[team_df["bookmaker"] == book]
            # Safely parse timestamps
            sub["timestamp"] = pd.to_datetime(sub["timestamp"], errors="coerce")
            sub = sub.dropna(subset=["timestamp"])

            ax.plot(sub["timestamp"], sub["odds"], label=book)

        ax.set_title(f"{team} Odds Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Decimal Odds")
        ax.legend()
        st.pyplot(fig)
else:
    st.info("No data yet. Use the sidebar to fetch odds.")
