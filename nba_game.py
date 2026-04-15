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
    "7 Seed": "https://via.placeholder.com/150/ffffff/000000?text=7+SEED",
    "TBD": "https://via.placeholder.com/150/333333/FFFFFF?text=?"
}

# Definicja drabinki (Klucz meczu : [Drużyna 1, Drużyna 2, Seed 1, Seed 2])
R1_MAP = {
    "W1": ["Thunder", "8 Seed", "1", "8"], "W2": ["Lakers", "Rockets", "4", "5"],
    "W3": ["Nuggets", "Timberwolves", "3", "6"], "W4": ["Spurs", "Trail Blazers", "2", "7"],
    "E1": ["Pistons", "8 Seed", "1", "8"], "E2": ["Cavaliers", "Raptors", "4", "5"],
    "E3": ["Knicks", "Hawks", "3", "6"], "E4": ["Celtics", "7 Seed", "2", "7"]
}

ALL_SERIES_KEYS = list(R1_MAP.keys()) + ["W_SF1", "W_SF2", "E_SF1", "E_SF2", "W_CF", "E_CF", "FINALS"]

st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    .login-box { background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #555; margin-bottom: 25px; }
    .round-header { background-color: #1e1e1e; padding: 10px; border-radius: 10px; text-align: center; margin: 20px 0 10px 0; border-left: 5px solid #f82910; font-weight: bold; }
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(0, 0, 0, 0.2); }
    .res-exact { background-color: rgba(0, 200, 0, 0.15) !important; border-color: rgba(0, 255, 0, 0.4) !important; }
    .res-winner { background-color: rgba(0, 0, 200, 0.15) !important; border-color: rgba(0, 0, 255, 0.4) !important; }
    .res-wrong { background-color: rgba(200, 0, 0, 0.15) !important; border-color: rgba(255, 0, 0, 0.4) !important; }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-normal { background-color: #444; color: #bbb; }
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

def get_winner(match_key, results):
    res = results.get("OFFICIAL", {}).get(match_key, "W toku")
    if res == "W toku": return "TBD"
    try:
        s = res.split("-")
        if int(s[0]) == 4: return R1_MAP[match_key][0] if match_key in R1_MAP else "Winner A"
        if int(s[1]) == 4: return R1_MAP[match_key][1] if match_key in R1_MAP else "Winner B"
    except: pass
    return "TBD"

def get_points_logic(user_pick, actual_result):
    if actual_result == "W toku" or user_pick == "-": return 0, "", "pts-normal"
    if user_pick == actual_result: return 5, "res-exact", "pts-exact"
    try:
        u_win = int(user_pick.split("-")[0]) == 4
        a_win = int(actual_result.split("-")[0]) == 4
        if u_win == a_win: return 3, "res-winner", "pts-winner"
    except: pass
    return 0, "res-wrong", "pts-wrong"

# Inicjalizacja
if 'db' not in st.session_state: st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state: st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state: st.session_state.logged_user = None

actual_res_db = st.session_state.results.get("OFFICIAL", {})

# Logika awansów (pobieranie zwycięzców dla wyższych rund)
winners = {k: get_winner(k, st.session_state.results) for k in ALL_SERIES_KEYS}

# Dynamiczne pary dla R2, R3 i Finału
BRACKET_DYNAMIC = {
    **R1_MAP,
    "W_SF1": [winners["W1"], winners["W2"], "1/8", "4/5"],
    "W_SF2": [winners["W3"], winners["W4"], "3/6", "2/7"],
    "E_SF1": [winners["E1"], winners["E2"], "1/8", "4/5"],
    "E_SF2": [winners["E3"], winners["E4"], "3/6", "2/7"],
    "W_CF": [get_winner("W_SF1", st.session_state.results), get_winner("W_SF2", st.session_state.results), "SF1", "SF2"],
    "E_CF": [get_winner("E_SF1", st.session_state.results), get_winner("E_SF2", st.session_state.results), "SF1", "SF2"],
    "FINALS": [get_winner("W_CF", st.session_state.results), get_winner("E_CF", st.session_state.results), "WEST", "EAST"]
}

st.title("🏀 NBA Playoff 2026")
tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

# --- TYPY ---
with tab1:
    if st.session_state.logged_user is None:
        user = st.selectbox("Wybierz gracza:", [""] + PLAYERS)
        if user:
            user_data = st.session_state.db.get(user, {})
            pwd = st.text_input("Hasło:", type="password", key=f"login_{user}")
            if st.button("Wejdź"):
                if pwd == user_data.get("PIN", "123"): # Domyślny PIN jeśli pusty
                    st.session_state.logged_user = user
                    st.rerun()
    else:
        st.write(f"Zalogowano: **{st.session_state.logged_user}**")
        user_picks = st.session_state.db.get(st.session_state.logged_user, {})
        new_picks = {"PIN": user_picks.get("PIN", "123")}
        for k in ALL_SERIES_KEYS:
            team1, team2 = BRACKET_DYNAMIC[k][0], BRACKET_DYNAMIC[k][1]
            new_picks[k] = st.selectbox(f"{team1} vs {team2}", ["4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"], 
                                         index=0, key=f"p_{k}", disabled=now > START_TIME)
        if st.button("Zapisz"):
            st.session_state.db[st.session_state.logged_user] = new_picks
            save_data(st.session_state.db, "wyniki.csv")
            st.success("Zapisano!")

# --- RANKING ---
with tab2:
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        pts = sum(get_points_logic(p_data.get(k, "-"), actual_res_db.get(k, "W toku"))[0] for k in ALL_SERIES_KEYS)
        leaderboard.append({"Gracz": p, "Suma": pts})
    st.table(pd.DataFrame(leaderboard).sort_values("Suma", ascending=False))

# --- DRABINKA ---
with tab3:
    def draw_match(k):
        t1, t2, s1, s2 = BRACKET_DYNAMIC[k]
        u_pick = st.session_state.db.get(st.session_state.logged_user, {}).get(k, "-") if st.session_state.logged_user else "-"
        a_res = actual_res_db.get(k, "W toku")
        pts, css_b, css_p = get_points_logic(u_pick, a_res)
        
        st.markdown(f"""
        <div class="match-box {css_b}">
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS.get(t1, LOGOS['TBD'])}" width="30"></div> <b>({s1}) {t1}</b></div>
            <div style="text-align: center; margin: 5px 0; font-size: 0.8em; color: #888;">{a_res} | Typ: {u_pick} <span class="pts-badge {css_p}">+{pts}</span></div>
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS.get(t2, LOGOS['TBD'])}" width="30"></div> <b>({s2}) {t2}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="round-header">ZACHÓD</div>', unsafe_allow_html=True)
    for k in ["W1", "W2", "W3", "W4"]: draw_match(k)
    st.markdown('<div class="round-header">WSCHÓD</div>', unsafe_allow_html=True)
    for k in ["E1", "E2", "E3", "E4"]: draw_match(k)
    st.markdown('<div class="round-header">PÓŁFINAŁY KONFERENCJI</div>', unsafe_allow_html=True)
    for k in ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]: draw_match(k)
    st.markdown('<div class="round-header">FINAŁY KONFERENCJI</div>', unsafe_allow_html=True)
    for k in ["W_CF", "E_CF"]: draw_match(k)
    st.markdown('<div class="round-header">FINAŁ NBA</div>', unsafe_allow_html=True)
    draw_match("FINALS")

# --- ADMIN ---
with tab4:
    admin_auth = st.text_input("Kod:", type="password")
    if admin_auth == ADMIN_PIN:
        new_results = {}
        for k in ALL_SERIES_KEYS:
            t1, t2 = BRACKET_DYNAMIC[k][0], BRACKET_DYNAMIC[k][1]
            new_results[k] = st.selectbox(f"Wynik {t1}-{t2}", ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"], key=f"adm_{k}")
        if st.button("Zatwierdź"):
            st.session_state.results["OFFICIAL"] = new_results
            save_data(st.session_state.results, "oficjalne_wyniki.csv")
            st.rerun()
