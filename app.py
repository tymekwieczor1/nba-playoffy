import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
START_TIME = datetime(2026, 4, 18, 19, 0)

PLAYERS = ["Adam", "Bartek", "Czarek", "Dawid", "Eryk", "Filip", "Grzegorz"]
SERIES = [
    "Celtics vs Heat", 
    "Knicks vs Sixers", 
    "Bucks vs Pacers", 
    "Cavs vs Magic",
    "Thunder vs Pelicans",
    "Nuggets vs Lakers",
    "Timberwolves vs Suns",
    "Clippers vs Mavericks"
]

st.set_page_config(page_title="NBA Playoff Predictor", page_icon="🏀")

def load_data():
    if os.path.exists("wyniki.csv"):
        try:
            return pd.read_csv("wyniki.csv", index_col=0).to_dict('index')
        except:
            return {}
    return {}

def save_data(data):
    df_to_save = pd.DataFrame.from_dict(data, orient='index')
    df_to_save.to_csv("wyniki.csv")

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🏀 NBA Playoff Challenge")
now = datetime.now()
is_locked = now > START_TIME

if not is_locked:
    st.info(f"⏳ Czas na typowanie do: {START_TIME.strftime('%d.%m.%Y %H:%M')}")
else:
    st.warning("🔒 Mecze się rozpoczęły. Typy są zablokowane!")

tab1, tab2 = st.tabs(["🖋️ Wpisz Swoje Typy", "🏆 Ranking i Podgląd"])

with tab1:
    user = st.selectbox("Kim jesteś?", [""] + PLAYERS)
    if user:
        st.write(f"Cześć **{user}**! Wybierz wyniki serii:")
        current_user_data = st.session_state.db.get(user, {})
        new_picks = {}
        options = ["4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"]

        for match in SERIES:
            default_val = current_user_data.get(match, "4-0")
            idx = options.index(default_val) if default_val in options else 0
            pick = st.selectbox(f"{match}", options, key=f"in_{user}_{match}", index=idx, disabled=is_locked)
            new_picks[match] = pick
        
        if st.button("Zapisz moje typy", disabled=is_locked):
            st.session_state.db[user] = new_picks
            save_data(st.session_state.db)
            st.success("✅ Zapisano!")

with tab2:
    st.subheader("Aktualna Tabela")
    if not st.session_state.db:
        st.write("Brak wpisanych typów.")
    else:
        display_rows = []
        for p in PLAYERS:
            row = {"Gracz": p}
            p_data = st.session_state.db.get(p, {})
            for match in SERIES:
                val = p_data.get(match, "-")
                row[match] = "🔒" if (not is_locked and p != user) else val
            display_rows.append(row)
        st.dataframe(pd.DataFrame(display_rows), use_container_width=True)
