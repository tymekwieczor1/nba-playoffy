import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
# Ustaw datę startu pierwszego meczu (format: ROK, MIESIĄC, DZIEŃ, GODZINA, MINUTA)
# Playoffy 2026 zaczynają się ok. 18 kwietnia.
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

# --- FUNKCJE BAZY DANYCH ---
def load_data():
    if os.path.exists("wyniki.csv"):
        return pd.read_csv("wyniki.csv", index_col=0).to_dict('index')
    return {}

def save_data(data):
    df_to_save = pd.DataFrame.from_dict(data, orient='index')
    df_to_save.to_csv("wyniki.csv")

# Inicjalizacja danych w sesji
if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- INTERFEJS ---
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
        st.write(f"Cześć **{user}**! Wybierz wyniki serii (np. 4-2 oznacza zwycięstwo pierwszej drużyny):")
        
        # Pobierz stare typy użytkownika, jeśli istnieją
        current_user_data = st.session_state.db.get(user, {})
        new_picks = {}

        for match in SERIES:
            default_val = current_user_data.get(match, "4-0")
            pick = st.selectbox(
                f"{match}", 
                ["4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"],
                key=f"input_{user}_{match}",
                index=["4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"].index(default_val) if default_val in ["4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"] else 0,
                disabled=is_locked
            )
            new_picks[match] = pick
        
        if st.button("Zapisz moje typy", disabled=is_locked):
            st.session_state.db[user] = new_picks
            save_data(st.session_state.db)
            st.success("✅ Twoje typy zostały zapisane pomyślnie!")

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
                
                # PRYWATNOŚĆ: Ukrywamy jeśli przed czasem i to nie Ty
                if not is_locked and p != user:
                    row[match] = "🔒"
                else:
                    row[match] = val
            display_rows.append(row)
        
        df_display = pd.DataFrame(display_rows)
        st.dataframe(df_display, use_container_width=True)

    if not is_locked:
        st.caption("ℹ️ Typy innych graczy pojawią się tutaj automatycznie po starcie pierwszego meczu.")
    else:
        st.caption("✅ Wszystkie typy są już jawne. Powodzenia!")
