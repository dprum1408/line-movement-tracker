import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📉 Line Movement Tracker")

# Refresh button
if st.button("🔄 Refresh CSV"):
    st.cache_data.clear()

try:
    df = pd.read_csv("odds_history.csv")
except FileNotFoundError:
    st.warning("No data yet. Run fetch_odds.py first.")
    st.stop()

# Match filter
match = st.selectbox("Select Match", df['match'].dropna().unique())
filtered = df[df['match'] == match]

# Stats summary
st.subheader("Summary Stats")
summary = filtered.groupby('team')['odds'].agg(['min', 'max', 'mean']).round(3)
st.dataframe(summary)

# Plot
teams = filtered['team'].unique()
for team in teams:
    sub = filtered[filtered['team'] == team]
    fig, ax = plt.subplots()
    for book in sub['bookmaker'].unique():
        odds = sub[sub['bookmaker'] == book]
        ax.plot(pd.to_datetime(odds['timestamp']), odds['odds'], label=book)
    ax.set_title(f"{team} Odds")
    ax.set_ylabel("Decimal Odds")
    ax.set_xlabel("Time")
    ax.legend()
    st.pyplot(fig)
