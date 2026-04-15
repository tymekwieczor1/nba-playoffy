import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
# Czas startu (zostawiam 2026, bo nie podano retro-roku)
START_TIME = datetime(2026, 4, 18, 19, 0)
ADMIN_PIN = "1398"

PLAYERS = ["Tymek", "Soból", "Maciek", "Kowal", "Paweł", "Mateusz", "Tomasz"]

# Zaktualizowany słownik LOGOS o retro drużyny ze screena
LOGOS = {
    # Drużyny Zachodu
    "Thunder": "https://loodibee.com/wp-content/uploads/nba-oklahoma-city-thunder-logo.png",
    "Lakers": "https://loodibee.com/wp-content/uploads/nba-los-angeles-lakers-logo.png",
    "Rockets": "https://loodibee.com/wp-content/uploads/nba-houston-rockets-logo.png",
    "Nuggets": "https://loodibee.com/wp-content/uploads/denver-nuggets-logo-symbol.png",
    "Timberwolves": "https://loodibee.com/wp-content/uploads/nba-minnesota-timberwolves-logo.png",
    "Spurs": "https://loodibee.com/wp-content/uploads/nba-san-antonio-spurs-logo.png",
    "Trail Blazers": "https://loodibee.com/wp-content/uploads/nba-portland-trail-blazers-logo.png",
    
    # Drużyny Wschodu
    "Pistons": "https://loodibee.com/wp-content/uploads/nba-detroit-pistons-logo.png",
    "Cavaliers": "https://loodibee.com/wp-content/uploads/nba-cleveland-cavaliers-logo.png",
    "Raptors": "https://loodibee.com/wp-content/uploads/nba-toronto-raptors-logo.png",
    "Knicks": "https://loodibee.com/wp-content/uploads/nba-new-york-knicks-logo.png",
    "Hawks": "https://loodibee.com/wp-content/uploads/nba-atlanta-hawks-logo.png",
    "Celtics": "https://loodibee.com/wp-content/uploads/nba-boston-celtics-logo.png",
    
    # Generyczne logo dla nieustalonych seedów
    "8 Seed": "https://via.placeholder.com/150/000000/FFFFFF?text=SEED+8",
    "7 Seed": "https://via.placeholder.com/150/000000/FFFFFF?text=SEED+7"
}

# Zaktualizowane pary meczowe ze screena (od góry do dołu)
SERIES = [
    # Zachód
    "Thunder vs 8 Seed", "Lakers vs Rockets", "Nuggets vs Timberwolves", "Spurs vs Trail Blazers",
    # Wschód
    "Pistons vs 8 Seed", "Cavaliers vs Raptors", "Knicks vs Hawks", "Celtics vs 7 Seed"
]

st.set_page_config(page_title="NBA Retro Predictor", page_icon="🏀", layout="wide")

st.markdown("""
    <style>
    .login-box { background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #555; margin-bottom: 25px; }
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(255, 255, 255, 0.05); }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    if os.path.exists("wyniki.csv"):
        try: return pd.read_csv("wyniki.csv", index_col=0, dtype={'PIN': str}).to_dict('index')
        except: return {}
    return {}

def save_data(data):
    pd.DataFrame.from_dict(data, orient='index').to_csv("wyniki.csv")

if 'db' not in st.session_state:
    st.session_state.db = load_data()

if 'logged_user' not in st.session_state:
    st.session_state.logged_user = None

st.title("🏀 NBA Retro Playoff Challenge")
now = datetime.now()
is_locked = now > START_TIME

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

with tab1:
    if st.session_state.logged_user is None:
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("🔐 Zaloguj się, aby typować retro playoffy")
            col_u, col_p = st.columns(2)
            with col_u:
                user = st.selectbox("Wybierz gracza:", [""] + PLAYERS, key="login_select")
            if user:
                user_data = st.session_state.db.get(user, {})
                saved_pwd = str(user_data.get("PIN", ""))
                if saved_pwd.endswith(".0"): saved_pwd = saved_pwd[:-2]
                with col_p:
                    if saved_pwd == "" or saved_pwd == "nan":
                        new_pwd = st.text_input("Ustal hasło:", type="password", key=f"setup_{user}")
                        if st.button("Ustaw hasło i wejdź"):
                            if len(new_pwd) >= 3:
                                user_data["PIN"] = str(new_pwd)
                                st.session_state.db[user] = user_data
                                save_data(st.session_state.db)
                                st.session_state.logged_user = user
                                st.rerun()
                    else:
                        pwd_input = st.text_input("Wpisz hasło:", type="password", key=f"login_{user}")
                        if st.button("Zaloguj"):
                            if pwd_input == saved_pwd:
                                st.session_state.logged_user = user
                                st.rerun()
                            else:
                                st.error("Błędne hasło!")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success(f"Zalogowano jako **{st.session_state.logged_user}**")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()
        st.markdown("---")
        user_data = st.session_state.db.get(st.session_state.logged_user, {})
        new_picks = {}
        options = ["4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"]
        cols = st.columns(2)
        for i, match in enumerate(SERIES):
            col = cols[i % 2]
            default_val = user_data.get(match, "4-0")
            idx = options.index(default_val) if default_val in options else 0
            pick = col.selectbox(f"{match}", options, key=f"in_{st.session_state.logged_user}_{match}", index=idx, disabled=is_locked)
            new_picks[match] = pick
        if st.button("Zapisz wszystkie typy", disabled=is_locked, use_container_width=True):
            new_picks["PIN"] = user_data.get("PIN")
            st.session_state.db[st.session_state.logged_user] = new_picks
            save_data(st.session_state.db)
            st.balloons()
            st.success("✅ Retro typy zostały zapisane na serwerze!")

with tab2:
    st.subheader("Tabela Wyników (Retro Mode)")
    if not st.session_state.db:
        st.write("Czekamy na retro-typy...")
    else:
        display_rows = []
        for p in PLAYERS:
            row = {"Gracz": p}
            p_data = st.session_state.db.get(p, {})
            for match in SERIES:
                val = p_data.get(match, "-")
                row[match] = "🔒" if (not is_locked and p != st.session_state.logged_user) else val
            display_rows.append(row)
        st.dataframe(pd.DataFrame(display_rows), use_container_width=True)

with tab3:
    st.subheader("📊 Drabinka Retro Playoff")
    curr_user = st.session_state.logged_user
    u_picks = st.session_state.db.get(curr_user, {}) if curr_user else {}
    
    def bracket_card(t1, seed1, t2, seed2):
        match_key = f"{t1} vs {t2}"
        my_pick = u_picks.get(match_key, "-")
        st.markdown(f"""
        <div class="match-box">
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS[t1]}" width="35"></div><span style="margin-left: 10px; font-weight: bold;">({seed1}) {t1}</span></div>
            <div style="text-align: center; margin: 5px 0;"><span style="color: #666; font-size: 0.8em; background: #222; padding: 2px 10px; border-radius: 10px;">Twoje: {my_pick}</span></div>
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS[t2]}" width="35"></div><span style="margin-left: 10px; font-weight: bold;">({seed2}) {t2}</span></div>
        </div>
        """, unsafe_allow_html=True)

    c_e, _, c_w = st.columns([1, 0.1, 1])
    with c_e:
        st.markdown("#### 🔵 WSCHÓD")
        # Pary ze screena (Wschód - prawa kolumna, od góry)
        bracket_card("Pistons", 1, "8 Seed", 8)
        bracket_card("Cavaliers", 4, "Raptors", 5)
        st.markdown("<br>", unsafe_allow_html=True) # Przerwa między górą a dołem
        bracket_card("Knicks", 3, "Hawks", 6)
        bracket_card("Celtics", 2, "7 Seed", 7)
    with c_w:
        st.markdown("#### 🔴 ZACHÓD")
        # Pary ze screena (Zachód - lewa kolumna, od góry)
        bracket_card("Thunder", 1, "8 Seed", 8)
        bracket_card("Lakers", 4, "Rockets", 5)
        st.markdown("<br>", unsafe_allow_html=True) # Przerwa między górą a dołem
        bracket_card("Nuggets", 3, "Timberwolves", 6)
        bracket_card("Spurs", 2, "Trail Blazers", 7)

with tab4:
    st.subheader("⚙️ Admin")
    admin_auth = st.text_input("Hasło admina:", type="password", key="admin_pwd")
    if admin_auth == ADMIN_PIN:
        st.success("Dostęp przyznany")
        if st.session_state.db:
            df_admin = pd.DataFrame.from_dict(st.session_state.db, orient='index')
            st.dataframe(df_admin)
            csv_data = df_admin.to_csv().encode('utf-8')
            st.download_button(label="Pobierz backup CSV", data=csv_data, file_name="wyniki_nba.csv", mime="text/csv")
