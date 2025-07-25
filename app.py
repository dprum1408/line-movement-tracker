import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📉 Line Movement Tracker")

@st.cache_data
def load_data(path="odds_history.csv"):
    df = pd.read_csv(path)
    # Make sure required cols exist
    required = {"timestamp", "match", "bookmaker", "market", "team", "odds"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Fix types
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["odds"] = pd.to_numeric(df["odds"], errors="coerce")

    # Drop rows where key fields are invalid
    df = df.dropna(subset=["timestamp", "match", "team", "bookmaker", "odds"])
    return df

# Refresh button
if st.button("🔄 Refresh CSV"):
    load_data.clear()

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

if df.empty:
    st.warning("No valid rows found in odds_history.csv yet. Let the scheduler run a bit.")
    st.stop()

# --- Sidebar filters ---
matches = df["match"].unique()
selected_match = st.sidebar.selectbox("Select Match", matches)

filtered = df[df["match"] == selected_match].copy()
if filtered.empty:
    st.warning("No rows for that match.")
    st.stop()

# --- Summary stats ---
st.subheader(f"📊 Summary Stats for {selected_match}")
summary = (
    filtered.groupby("team", as_index=False)["odds"]
    .agg(min_odds="min", max_odds="max", mean_odds="mean")
    .round(3)
)
st.dataframe(summary, use_container_width=True)

# --- Plots ---
teams = filtered["team"].unique()
for team in teams:
    team_df = filtered[filtered["team"] == team]
    if team_df.empty:
        continue

    fig, ax = plt.subplots()
    for book in team_df["bookmaker"].unique():
        sub = team_df[team_df["bookmaker"] == book].sort_values("timestamp")
        ax.plot(sub["timestamp"], sub["odds"], label=book)

    ax.set_title(f"{team} Odds Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Decimal Odds")
    ax.legend()
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)
