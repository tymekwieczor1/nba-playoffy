import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. KONFIGURACJA ---
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

# --- 2. FUNKCJE POMOCNICZE ---
def load_data(filename):
    if os.path.exists(filename):
        try: return pd.read_csv(filename, index_col=0, dtype=str).to_dict('index')
        except: return {}
    return {}

def save_data(data, filename):
    pd.DataFrame.from_dict(data, orient='index').to_csv(filename)

def get_points_logic(user_pick, actual_result):
    if actual_result == "W toku" or user_pick == "-" or pd.isna(actual_result): 
        return 0, "", "pts-normal"
    if user_pick == actual_result: 
        return 5, "res-exact", "pts-exact"
    try:
        u_left_wins = int(user_pick.split("-")[0]) == 4
        a_left_wins = int(actual_result.split("-")[0]) == 4
        if u_left_wins == a_left_wins: 
            return 3, "res-winner", "pts-winner"
    except: pass
    return 0, "res-wrong", "pts-wrong"

# --- 3. INICJALIZACJA BAZ ---
if 'db' not in st.session_state: st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state: st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state: st.session_state.logged_user = None
if 'temp_picks' not in st.session_state: st.session_state.temp_picks = {}

actual_res_db = st.session_state.results.get("OFFICIAL", {})

# --- 4. LOGIKA AWANSÓW ---
def get_winner(match_key, results, teams):
    res = results.get("OFFICIAL", {}).get(match_key, "W toku")
    if res == "W toku": return "TBD"
    try:
        s = res.split("-")
        if int(s[0]) == 4: return teams[0]
        if int(s[1]) == 4: return teams[1]
    except: pass
    return "TBD"

R1_MAP = {
    "W1": ["Thunder", "8 Seed", "1", "8"], "W2": ["Lakers", "Rockets", "4", "5"],
    "W3": ["Nuggets", "Timberwolves", "3", "6"], "W4": ["Spurs", "Trail Blazers", "2", "7"],
    "E1": ["Pistons", "8 Seed", "1", "8"], "E2": ["Cavaliers", "Raptors", "4", "5"],
    "E3": ["Knicks", "Hawks", "3", "6"], "E4": ["Celtics", "7 Seed", "2", "7"]
}

BRACKET = {**R1_MAP}
BRACKET["W_SF1"] = [get_winner("W1", st.session_state.results, BRACKET["W1"]), get_winner("W2", st.session_state.results, BRACKET["W2"]), "SF", "SF"]
BRACKET["W_SF2"] = [get_winner("W3", st.session_state.results, BRACKET["W3"]), get_winner("W4", st.session_state.results, BRACKET["W4"]), "SF", "SF"]
BRACKET["E_SF1"] = [get_winner("E1", st.session_state.results, BRACKET["E1"]), get_winner("E2", st.session_state.results, BRACKET["E2"]), "SF", "SF"]
BRACKET["E_SF2"] = [get_winner("E3", st.session_state.results, BRACKET["E3"]), get_winner("E4", st.session_state.results, BRACKET["E4"]), "SF", "SF"]
BRACKET["W_CF"] = [get_winner("W_SF1", st.session_state.results, BRACKET["W_SF1"]), get_winner("W_SF2", st.session_state.results, BRACKET["W_SF2"]), "CF", "CF"]
BRACKET["E_CF"] = [get_winner("E_SF1", st.session_state.results, BRACKET["E_SF1"]), get_winner("E_SF2", st.session_state.results, BRACKET["E_SF2"]), "CF", "CF"]
BRACKET["FINALS"] = [get_winner("W_CF", st.session_state.results, BRACKET["W_CF"]), get_winner("E_CF", st.session_state.results, BRACKET["E_CF"]), "Final", "Final"]

ALL_KEYS = list(BRACKET.keys())

# --- 5. INTERFEJS ---
st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    .match-card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 20px; border: 1px solid #444; margin-bottom: 30px; text-align: center; }
    .selected-team { border: 4px solid #00ff00 !important; border-radius: 15px; padding: 10px; background: rgba(0,255,0,0.1); }
    .unselected-team { opacity: 0.5; padding: 10px; border: 4px solid transparent; }
    .round-header { background-color: #1e1e1e; padding: 10px; border-radius: 10px; text-align: center; margin: 20px 0; border-left: 5px solid #f82910; font-weight: bold; }
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-exact { background-color: #008000; color: white; }
    .pts-winner { background-color: #000080; color: white; }
    .pts-wrong { background-color: #800000; color: white; }
    .pts-normal { background-color: #444; color: #bbb; }
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(0, 0, 0, 0.2); }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

# --- TYPY ---
with tab1:
    if st.session_state.logged_user is None:
        user = st.selectbox("Wybierz gracza:", [""] + PLAYERS)
        if user:
            user_data = st.session_state.db.get(user, {})
            pwd = st.text_input("Hasło:", type="password", key=f"login_{user}")
            if st.button("Wejdź"):
                if pwd == user_data.get("PIN", "123"):
                    st.session_state.logged_user = user
                    st.session_state.temp_picks = user_data.copy()
                    st.rerun()
    else:
        st.success(f"Zalogowano: **{st.session_state.logged_user}**")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()
        
        is_locked = now > START_TIME
        st.info("Kliknij w logo zwycięskiej drużyny i wybierz liczbę meczów.")

        for k in ALL_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            current_val = st.session_state.temp_picks.get(k, "4-0")
            left_wins = int(current_val.split("-")[0]) == 4
            num_games = sum(map(int, current_val.split("-")))

            st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown(f'<div class="{"selected-team" if left_wins else "unselected-team"}">', unsafe_allow_html=True)
                st.image(LOGOS.get(t1, LOGOS["TBD"]), width=70)
                if st.button(f"Win {t1}", key=f"bt1_{k}", disabled=is_locked):
                    st.session_state.temp_picks[k] = f"4-{num_games-4}"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown(f'<div class="{"selected-team" if not left_wins else "unselected-team"}">', unsafe_allow_html=True)
                st.image(LOGOS.get(t2, LOGOS["TBD"]), width=70)
                if st.button(f"Win {t2}", key=f"bt2_{k}", disabled=is_locked):
                    st.session_state.temp_picks[k] = f"{num_games-4}-4"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            selected_games = st.selectbox(f"Długość serii {t1}-{t2}:", [4, 5, 6, 7], 
                                         index=[4, 5, 6, 7].index(num_games), key=f"sl_{k}", disabled=is_locked)
            
            if left_wins: st.session_state.temp_picks[k] = f"4-{selected_games-4}"
            else: st.session_state.temp_picks[k] = f"{selected_games-4}-4"
            st.markdown(f'<b>Aktualny wybór: {st.session_state.temp_picks[k]}</b>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("ZAPISZ WSZYSTKIE TYPY", use_container_width=True, disabled=is_locked):
            st.session_state.db[st.session_state.logged_user] = st.session_state.temp_picks
            save_data(st.session_state.db, "wyniki.csv")
            st.success("Zapisano!")

# --- RANKING ---
with tab2:
    st.subheader("Ranking")
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        pts = sum(get_points_logic(p_data.get(k, "-"), actual_res_db.get(k, "W toku"))[0] for k in ALL_KEYS)
        leaderboard.append({"Gracz": p, "Suma": pts})
    st.table(pd.DataFrame(leaderboard).sort_values("Suma", ascending=False))

# --- DRABINKA ---
with tab3:
    def draw_bracket_card(k, title=""):
        t1, t2, s1, s2 = BRACKET[k]
        u_pick = st.session_state.db.get(st.session_state.logged_user, {}).get(k, "-") if st.session_state.logged_user else "-"
        a_res = actual_res_db.get(k, "W toku")
        pts, css_box, css_pts = get_points_logic(u_pick, a_res)
        
        st.markdown(f"""
        <div class="match-box {css_box}">
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS.get(t1, LOGOS['TBD'])}" width="30"></div> <b>({s1}) {t1}</b></div>
            <div style="text-align: center; margin: 5px 0; font-size: 0.8em; color: #888;">{a_res if a_res != "W toku" else "W toku"} | Twój typ: {u_pick} <span class="pts-badge {css_pts}">+{pts}</span></div>
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS.get(t2, LOGOS['TBD'])}" width="30"></div> <b>({s2}) {t2}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="round-header">ZACHÓD</div>', unsafe_allow_html=True)
    for k in ["W1", "W2", "W3", "W4"]: draw_bracket_card(k)
    st.markdown('<div class="round-header">WSCHÓD</div>', unsafe_allow_html=True)
    for k in ["E1", "E2", "E3", "E4"]: draw_bracket_card(k)
    st.markdown('<div class="round-header">PÓŁFINAŁY KONFERENCJI</div>', unsafe_allow_html=True)
    for k in ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]: draw_bracket_card(k)
    st.markdown('<div class="round-header">FINAŁY KONFERENCJI</div>', unsafe_allow_html=True)
    for k in ["W_CF", "E_CF"]: draw_bracket_card(k)
    st.markdown('<div class="round-header">FINAŁ NBA</div>', unsafe_allow_html=True)
    draw_bracket_card("FINALS")

# --- ADMIN ---
with tab4:
    admin_auth = st.text_input("Kod Administratora:", type="password")
    if admin_auth == ADMIN_PIN:
        new_results = {}
        for k in ALL_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            curr = actual_res_db.get(k, "W toku")
            opts = ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"]
            idx = opts.index(curr) if curr in opts else 0
            new_results[k] = st.selectbox(f"Wynik {t1}-{t2}", opts, index=idx, key=f"adm_{k}")
        if st.button("Zatwierdź Wyniki"):
            st.session_state.results["OFFICIAL"] = new_results
            save_data(st.session_state.results, "oficjalne_wyniki.csv")
            st.rerun()
