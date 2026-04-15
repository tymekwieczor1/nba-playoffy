import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
START_TIME = datetime(2026, 4, 18, 19, 0)
ADMIN_PIN = "1398"
now = datetime.now()

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
    "7 Seed": "https://via.placeholder.com/150/ffffff/000000?text=7+SEED",
    "TBD": "https://via.placeholder.com/150/333333/FFFFFF?text=?"
}

R1_MAP = {
    "W1": ["Thunder", "8 Seed", "1", "8"], "W2": ["Lakers", "Rockets", "4", "5"],
    "W3": ["Nuggets", "Timberwolves", "3", "6"], "W4": ["Spurs", "Trail Blazers", "2", "7"],
    "E1": ["Pistons", "8 Seed", "1", "8"], "E2": ["Cavaliers", "Raptors", "4", "5"],
    "E3": ["Knicks", "Hawks", "3", "6"], "E4": ["Celtics", "7 Seed", "2", "7"]
}

ALL_SERIES_KEYS = list(R1_MAP.keys()) + ["W_SF1", "W_SF2", "E_SF1", "E_SF2", "W_CF", "E_CF", "FINALS"]

st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="centered")

# CSS dla przycisków wyboru
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; }
    .match-card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 1px solid #444; margin-bottom: 20px; }
    .round-header { background-color: #1e1e1e; padding: 10px; border-radius: 10px; text-align: center; margin: 20px 0 10px 0; border-left: 5px solid #f82910; font-weight: bold; }
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-exact { background-color: #008000; color: white; }
    .pts-winner { background-color: #000080; color: white; }
    .pts-wrong { background-color: #800000; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_data(filename):
    if os.path.exists(filename):
        try: return pd.read_csv(filename, index_col=0, dtype=str).to_dict('index')
        except: return {}
    return {}

def save_data(data, filename):
    pd.DataFrame.from_dict(data, orient='index').to_csv(filename)

def get_winner(match_key, results, current_bracket):
    res = results.get("OFFICIAL", {}).get(match_key, "W toku")
    if res == "W toku": return "TBD"
    try:
        s = res.split("-")
        if int(s[0]) == 4: return current_bracket[match_key][0]
        if int(s[1]) == 4: return current_bracket[match_key][1]
    except: pass
    return "TBD"

def get_points_logic(user_pick, actual_result):
    if actual_result == "W toku" or user_pick == "-": return 0, "pts-normal"
    if user_pick == actual_result: return 5, "pts-exact"
    try:
        u_left_win = int(user_pick.split("-")[0]) == 4
        a_left_win = int(actual_result.split("-")[0]) == 4
        if u_left_win == a_left_win: return 3, "pts-winner"
    except: pass
    return 0, "pts-wrong"

# Bazy
if 'db' not in st.session_state: st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state: st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state: st.session_state.logged_user = None

actual_res_db = st.session_state.results.get("OFFICIAL", {})

# Drabinka
BRACKET = {**R1_MAP}
BRACKET["W_SF1"] = [get_winner("W1", st.session_state.results, BRACKET), get_winner("W2", st.session_state.results, BRACKET), "SF", "SF"]
BRACKET["W_SF2"] = [get_winner("W3", st.session_state.results, BRACKET), get_winner("W4", st.session_state.results, BRACKET), "SF", "SF"]
BRACKET["E_SF1"] = [get_winner("E1", st.session_state.results, BRACKET), get_winner("E2", st.session_state.results, BRACKET), "SF", "SF"]
BRACKET["E_SF2"] = [get_winner("E3", st.session_state.results, BRACKET), get_winner("E4", st.session_state.results, BRACKET), "SF", "SF"]
BRACKET["W_CF"] = [get_winner("W_SF1", st.session_state.results, BRACKET), get_winner("W_SF2", st.session_state.results, BRACKET), "CF", "CF"]
BRACKET["E_CF"] = [get_winner("E_SF1", st.session_state.results, BRACKET), get_winner("E_SF2", st.session_state.results, BRACKET), "CF", "CF"]
BRACKET["FINALS"] = [get_winner("W_CF", st.session_state.results, BRACKET), get_winner("E_CF", st.session_state.results, BRACKET), "Final", "Final"]

st.title("🏀 NBA Playoff 2026")
tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

with tab1:
    if st.session_state.logged_user is None:
        user = st.selectbox("Wybierz gracza:", [""] + PLAYERS)
        if user:
            user_data = st.session_state.db.get(user, {})
            pwd = st.text_input("Hasło:", type="password", key=f"login_{user}")
            if st.button("Wejdź"):
                if pwd == user_data.get("PIN", "123"):
                    st.session_state.logged_user = user
                    st.rerun()
    else:
        st.success(f"Zalogowano: **{st.session_state.logged_user}**")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()
        
        user_picks = st.session_state.db.get(st.session_state.logged_user, {})
        new_picks = {"PIN": user_picks.get("PIN", "123")}
        
        is_locked = now > START_TIME
        
        for k in ALL_SERIES_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            st.markdown(f"#### {t1} vs {t2}")
            
            # Pobieramy aktualny typ, by przyciski były zaznaczone
            current_pick = user_picks.get(k, "4-0")
            cur_left_win = int(current_pick.split("-")[0]) == 4
            cur_games = sum(map(int, current_pick.split("-")))
            
            col_t1, col_t2 = st.columns(2)
            # Wybór zwycięzcy
            with col_t1:
                t1_btn = st.radio(f"Zwycięzca:", [t1, t2], index=0 if cur_left_win else 1, key=f"win_{k}", disabled=is_locked)
            # Wybór liczby meczów
            with col_t2:
                games_btn = st.radio(f"W ilu meczach?", [4, 5, 6, 7], index=[4, 5, 6, 7].index(cur_games), key=f"games_{k}", disabled=is_locked)
            
            # Przeliczanie na format 4-X
            if t1_btn == t1:
                final_val = f"4-{games_btn - 4}"
            else:
                final_val = f"{games_btn - 4}-4"
            
            new_picks[k] = final_val
            st.markdown("---")
            
        if st.button("Zapisz wszystkie typy", disabled=is_locked):
            st.session_state.db[st.session_state.logged_user] = new_picks
            save_data(st.session_state.db, "wyniki.csv")
            st.success("Typy zapisane!")

with tab2:
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        pts = sum(get_points_logic(p_data.get(k, "-"), actual_res_db.get(k, "W toku"))[0] for k in ALL_SERIES_KEYS)
        leaderboard.append({"Gracz": p, "Punkty": pts})
    st.table(pd.DataFrame(leaderboard).sort_values("Punkty", ascending=False))

with tab3:
    for k in ALL_SERIES_KEYS:
        t1, t2, s1, s2 = BRACKET[k]
        u_pick = st.session_state.db.get(st.session_state.logged_user, {}).get(k, "-") if st.session_state.logged_user else "-"
        a_res = actual_res_db.get(k, "W toku")
        pts, css_p = get_points_logic(u_pick, a_res)
        
        st.markdown(f"""
        <div class="match-card">
            <b>{t1} ({s1}) vs {t2} ({s2})</b><br>
            Oficjalnie: {a_res} | Twój typ: {u_pick} <span class="pts-badge {css_p}">+{pts} pkt</span>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    admin_auth = st.text_input("Kod Admina:", type="password")
    if admin_auth == ADMIN_PIN:
        new_results = {}
        for k in ALL_SERIES_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            curr = actual_res_db.get(k, "W toku")
            opts = ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"]
            idx = opts.index(curr) if curr in opts else 0
            new_results[k] = st.selectbox(f"{t1}-{t2}", opts, index=idx, key=f"adm_{k}")
        if st.button("Zapisz wyniki"):
            st.session_state.results["OFFICIAL"] = new_results
            save_data(st.session_state.results, "oficjalne_wyniki.csv")
            st.rerun()
