import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
START_TIME = datetime(2026, 4, 18, 19, 0)
ADMIN_PIN = "1398"

PLAYERS = ["Tymek", "Soból", "Maciek", "Kowal", "Paweł", "Mateusz", "Tomasz"]

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

SERIES = [
    "Celtics vs Heat", "Knicks vs Sixers", "Bucks vs Pacers", "Cavs vs Magic",
    "Thunder vs Pelicans", "Nuggets vs Lakers", "Timberwolves vs Suns", "Clippers vs Mavericks"
]

st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="wide")

# Stylizacja ramki logowania i meczów
st.markdown("""
    <style>
    .login-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #555;
        margin-bottom: 25px;
    }
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

st.title("🏀 NBA Playoff Challenge 2026")
now = datetime.now()
is_locked = now > START_TIME

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

with tab1:
    # --- KAFELEK LOGOWANIA ---
    if st.session_state.logged_user is None:
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("🔐 Zaloguj się, aby typować")
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
        # --- WIDOK PO ZALOGOWANIU ---
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
            # Zachowujemy hasło przy zapisie!
            new_picks["PIN"] = user_data.get("PIN")
            st.session_state.db[st.session_state.logged_user] = new_picks
            save_data(st.session_state.db)
            st.balloons()
            st.success("✅ Typy zostały zapisane na serwerze!")

with tab2:
    st.subheader("Tabela Wyników")
    if not st.session_state.db:
        st.write("Brak danych.")
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
    st.subheader("Drabinka Playoff")
    # Pobieramy typy zalogowanego użytkownika dla drabinki
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
        bracket_card("Celtics", 1, "Heat", 8); bracket_card("Cavs", 4, "Magic", 5)
        st.markdown("<br>", unsafe_allow_html=True)
        bracket_card("Bucks", 3, "Pacers", 6); bracket_card("Knicks", 2, "Sixers", 7)
    with c_w:
        st.markdown("#### 🔴 ZACHÓD")
        bracket_card("Thunder", 1, "Pelicans", 8); bracket_card("Clippers", 4, "Mavericks", 5)
        st.markdown("<br>", unsafe_allow_html=True)
        bracket_card("Timberwolves", 3, "Suns", 6); bracket_card("Nuggets", 2, "Lakers", 7)

with tab4:
    st.subheader("Panel Administratora")
    admin_auth = st.text_input("Hasło admina:", type="password", key="admin_pwd")
    if admin_auth == ADMIN_PIN:
        st.success("Dostęp przyznany")
        if st.session_state.db:
            df_admin = pd.DataFrame.from_dict(st.session_state.db, orient='index')
            st.dataframe(df_admin)
            csv_data = df_admin.to_csv().encode('utf-8')
            st.download_button(label="Pobierz backup CSV", data=csv_data, file_name="wyniki_nba.csv", mime="text/csv")
