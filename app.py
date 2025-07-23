import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Line Movement Tracker", layout="wide")
st.title("📉 Line Movement Tracker")

# Load from SQLite
conn = sqlite3.connect("odds_data.db")
df = pd.read_sql("SELECT * FROM odds", conn)

# Refresh button (optional)
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Match filter
match_options = df['match'].dropna().unique()
selected_match = st.sidebar.selectbox("Select Match", match_options)

filtered = df[df['match'] == selected_match]

# Embedded Stats
st.subheader(f"📊 Summary Stats for {selected_match}")
grouped = filtered.groupby(['team'])['odds'].agg(['min', 'max', 'mean']).reset_index()
st.dataframe(grouped)

# Line Movement Charts
for team in filtered['team'].unique():
    team_df = filtered[filtered['team'] == team]
    fig, ax = plt.subplots()
    for book in team_df['bookmaker'].unique():
        sub = team_df[team_df['bookmaker'] == book]
        ax.plot(pd.to_datetime(sub['timestamp']), sub['odds'], label=book)
    ax.set_title(f"{team} Odds Over Time")
    ax.set_ylabel("Decimal Odds")
    ax.set_xlabel("Time")
    ax.legend()
    st.pyplot(fig)
