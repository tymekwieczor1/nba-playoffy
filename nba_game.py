import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
START_TIME = datetime(2026, 4, 18, 19, 0)

USER_PINS = {
    "Tymek": "832941", "Soból": "157482", "Maciek": "920375", 
    "Kowal": "461829", "Paweł": "735106", "Mateusz": "284963", "Tomasz": "619247"
}

# Linki do logo drużyn
LOGOS = {
    "Celtics": "https://loodibee.com/wp-content/uploads/nba-boston-celtics-logo.png",
    "Heat": "https://loodibee.com/wp-content/uploads/nba-miami-heat-logo.png",
    "Knicks": "https://loodibee.com/wp-content/uploads/nba-new-york-knicks-logo.png",
    "Sixers": "https://loodibee.com/wp-content/uploads/nba-philadelphia-76ers-logo.png",
    "Bucks": "https://loodibee.com/wp-content/uploads/nba-milwaukee-bucks-logo.png",
    "Pacers": "https://loodibee.com/wp-content/uploads/nba-indiana-pacers-logo.png",
    "Cavs": "https://loodibee.com/wp-content/uploads/nba-cleveland-cavaliers-logo.png",
    "Magic": "https://loodibee.com/wp-content/uploads/nba-orlando-magic-logo.png",
    "Thunder": "https://loodibee.com/wp-content/uploads/nba-oklahoma-city-thunder-logo.png",
    "Pelicans": "https://loodibee.com/wp-content/uploads/nba-new-orleans-pelicans-logo.png",
    "Nuggets": "https://loodibee.com/wp-content/uploads/nba-denver-nuggets-logo.png",
    "Lakers": "https://loodibee.com/wp-content/uploads/nba-los-angeles-lakers-logo.png",
    "Timberwolves": "https://loodibee.com/wp-content/uploads/nba-minnesota-timberwolves-logo.png",
    "Suns": "https://loodibee.com/wp-content/uploads/nba-phoenix-suns-logo.png",
    "Clippers": "https://loodibee.com/wp-content/uploads/nba-la-clippers-logo.png",
    "Mavericks": "https://loodibee.com/wp-content/uploads/nba-dallas-mavericks-logo.png"
}

PLAYERS = list(USER_PINS.keys())
SERIES = [
    "Celtics vs Heat", "Knicks vs Sixers", "Bucks vs Pacers", "Cavs vs Magic",
    "Thunder vs Pelicans", "Nuggets vs Lakers", "Timberwolves vs Suns", "Clippers vs Mavericks"
]

st.set_page_config(page_title="NBA Playoff Predictor", page_icon="🏀", layout="wide")

def load_data():
    if os.path.exists("wyniki.csv"):
        try: return pd.read_csv("wyniki.csv", index_col=0).to_dict('index')
        except: return {}
    return {}

def save_data(data):
    pd.DataFrame.from_dict(data, orient='index').to_csv("wyniki.csv")

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🏀 NBA Playoff Challenge 2026")
now = datetime.now()
is_locked = now > START_TIME

tab1, tab2, tab3 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff"])

with tab1:
    user = st.selectbox("Wybierz swoje imię:", [""] + PLAYERS)
    if user:
        pin_input = st.text_input(f"Podaj swój 6-cyfrowy PIN, {user}:", type="password")
        if pin_input == USER_PINS[user]:
            st.success(f"Zalogowano jako {user}")
            current_user_data = st.session_state.db.get(user, {})
            new_picks = {}
            options = ["4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"]
            
            cols = st.columns(2)
            for i, match in enumerate(SERIES):
                col = cols[i % 2]
                default_val = current_user_data.get(match, "4-0")
                idx = options.index(default_val) if default_val in options else 0
                pick = col.selectbox(f"{match}", options, key=f"in_{user}_{match}", index=idx, disabled=is_locked)
                new_picks[match] = pick
            
            if st.button("Zapisz moje typy", disabled=is_locked, use_container_width=True):
                st.session_state.db[user] = new_picks
                save_data(st.session_state.db)
                st.success("✅ Zapisano!")
        elif pin_input != "":
            st.error("Błędny PIN!")

with tab2:
    st.subheader("Tabela Wyników")
    if not st.session_state.db:
        st.write("Czekamy na typy...")
    else:
        display_rows = []
        for p in PLAYERS:
            row = {"Gracz": p}
            p_data = st.session_state.db.get(p, {})
            for match in SERIES:
                val = p_data.get(match, "-")
                row[match] = "🔒" if not is_locked else val
            display_rows.append(row)
        st.dataframe(pd.DataFrame(display_rows), use_container_width=True)

with tab3:
    st.subheader("Aktualna Drabinka Playoffów")
    
    def match_row(t1, t2):
        c1, c2, c3, c4 = st.columns([0.2, 1, 0.2, 1])
        c1.image(LOGOS[t1], width=40)
        c2.write(f"**{t1}**")
        c3.image(LOGOS[t2], width=40)
        c4.write(f"**{t2}**")

    col_west, col_empty, col_east = st.columns([1, 0.1, 1])
    
    with col_east:
        st.markdown("### 🔵 KONFERENCJA WSCHODNIA")
        match_row("Celtics", "Heat")
        match_row("Cavs", "Magic")
        match_row("Bucks", "Pacers")
        match_row("Knicks", "Sixers")

    with col_west:
        st.markdown("### 🔴 KONFERENCJA ZACHODNIA")
        match_row("Thunder", "Pelicans")
        match_row("Clippers", "Mavericks")
        match_row("Timberwolves", "Suns")
        match_row("Nuggets", "Lakers")
