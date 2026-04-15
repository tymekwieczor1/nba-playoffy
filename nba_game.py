import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
START_TIME = datetime(2026, 4, 18, 19, 0)
ADMIN_PIN = "1398"

PLAYERS = ["Tymek", "Soból", "Maciek", "Kowal", "Paweł", "Mateusz", "Tomasz"]

LOGOS = {
    "Thunder": "https://loodibee.com/wp-content/uploads/nba-oklahoma-city-thunder-logo.png",
    "Lakers": "https://loodibee.com/wp-content/uploads/nba-los-angeles-lakers-logo.png",
    "Rockets": "https://loodibee.com/wp-content/uploads/nba-houston-rockets-logo.png",
    "Nuggets": "https://loodibee.com/wp-content/uploads/denver-nuggets-logo-symbol.png",
    "Timberwolves": "https://loodibee.com/wp-content/uploads/nba-minnesota-timberwolves-logo.png",
    "Spurs": "https://loodibee.com/wp-content/uploads/nba-san-antonio-spurs-logo.png",
    "Trail Blazers": "https://loodibee.com/wp-content/uploads/nba-portland-trail-blazers-logo.png",
    "Pistons": "https://loodibee.com/wp-content/uploads/nba-detroit-pistons-logo.png",
    "Cavaliers": "https://loodibee.com/wp-content/uploads/nba-cleveland-cavaliers-logo.png",
    "Raptors": "https://loodibee.com/wp-content/uploads/nba-toronto-raptors-logo.png",
    "Knicks": "https://loodibee.com/wp-content/uploads/nba-new-york-knicks-logo.png",
    "Hawks": "https://loodibee.com/wp-content/uploads/nba-atlanta-hawks-logo.png",
    "Celtics": "https://loodibee.com/wp-content/uploads/nba-boston-celtics-logo.png",
    "8 Seed": "https://via.placeholder.com/150/ffffff/000000?text=8+SEED",
    "7 Seed": "https://via.placeholder.com/150/ffffff/000000?text=7+SEED"
}

SERIES = [
    "Thunder vs 8 Seed", "Lakers vs Rockets", "Nuggets vs Timberwolves", "Spurs vs Trail Blazers",
    "Pistons vs 8 Seed", "Cavaliers vs Raptors", "Knicks vs Hawks", "Celtics vs 7 Seed"
]

st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="wide")

# ROZBUDOWANY CSS (Czcionka Action Condensed Bold i kolory)
st.markdown("""
    <style>
    @import url('https://fonts.cdnfonts.com/css/action-condensed');

    /* Globalna zmiana czcionki na Action Condensed Bold */
    html, body, [class*="st-"], .stMarkdown, p, h1, h2, h3, h4, span, div {
        font-family: 'Action Condensed', sans-serif !important;
        text-transform: uppercase; /* Font ten najlepiej wygląda wielkimi literami */
    }

    .login-box { background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #555; margin-bottom: 25px; }
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(255, 255, 255, 0.05); }
    .res-exact { background-color: rgba(0, 200, 0, 0.2) !important; border-color: rgba(0, 255, 0, 0.5) !important; }
    .res-winner { background-color: rgba(0, 0, 200, 0.2) !important; border-color: rgba(0, 0, 255, 0.5) !important; }
    .res-wrong { background-color: rgba(200, 0, 0, 0.2) !important; border-color: rgba(255, 0, 0, 0.5) !important; }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-normal { background-color: #444; color: #bbb; }
    .pts-exact { background-color: #008000; color: white; }
    .pts-winner { background-color: #000080; color: white; }
    .pts-wrong { background-color: #800000; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_data(filename="wyniki.csv"):
    if os.path.exists(filename):
        try: return pd.
