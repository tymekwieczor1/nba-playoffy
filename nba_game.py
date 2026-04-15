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

# Linki do logo drużyn (zaktualizowane Denver i poprawiona czytelność)
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
    "Nuggets": "https://loodibee.com/wp-content/uploads/denver-nuggets-logo-symbol.png",
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

# Stylizacja dla białego tła pod logami i obramowania meczów
st.markdown("""
    <style>
    .match-box {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: rgba(255, 255, 255, 0.05);
    }
    .logo-bg {
        background-color: white;
        border-radius: 50%;
        padding: 5px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

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
    st.subheader("Drabinka Pierwszej Rundy")
    
    def bracket_card(t1, seed1, t2, seed2):
        with st.container():
            st.markdown(f"""
            <div class="match-box">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center;">
                        <div class="logo-bg"><img src="{LOGOS[t1]}" width="35"></div>
                        <span style="margin-left: 10px; font-weight: bold;">({seed1}) {t1}</span>
                    </div>
                </div>
                <div style="text-align: center; color: #888; font-size: 0.8em; margin: 5px 0;">VS</div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center;">
                        <div class="logo-bg"><img src="{LOGOS[t2]}" width="35"></div>
                        <span style="margin-left: 10px; font-weight: bold;">({seed2}) {t2}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    col_east, col_space, col_west = st.columns([1, 0.1, 1])
    
    with col_east:
        st.markdown("#### 🔵 KONFERENCJA WSCHODNIA")
        bracket_card("Celtics", 1, "Heat", 8)
        bracket_card("Cavs", 4, "Magic", 5)
        st.markdown("<br>", unsafe_allow_html=True)
        bracket_card("Bucks", 3, "Pacers", 6)
        bracket_card("Knicks", 2, "Sixers", 7)

    with col_west:
        st.markdown("#### 🔴 KONFERENCJA ZACHODNIA")
        bracket_card("Thunder", 1, "Pelicans", 8)
        bracket_card("Clippers", 4, "Mavericks", 5)
        st.markdown("<br>", unsafe_allow_html=True)
        bracket_card("Timberwolves", 3, "Suns", 6)
        bracket_card("Nuggets", 2, "Lakers", 7)
