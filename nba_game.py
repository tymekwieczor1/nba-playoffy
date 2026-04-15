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

# --- 2. FUNKCJE ---
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

def get_winner(match_key, results, teams):
    res = results.get("OFFICIAL", {}).get(match_key, "W toku")
    if res == "W toku": return "TBD"
    try:
        s = res.split("-")
        if int(s[0]) == 4: return teams[0]
        if int(s[1]) == 4: return teams[1]
    except: pass
    return "TBD"

# --- 3. INICJALIZACJA ---
if 'db' not in st.session_state: st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state: st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state: st.session_state.logged_user = None
if 'temp_picks' not in st.session_state: st.session_state.temp_picks = {}

actual_res_db = st.session_state.results.get("OFFICIAL", {})

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

# --- 4. CSS (LOGA W RAMKACH I STYLIZACJA) ---
st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    /* --- ZAKŁADKI ZAWSZE NA GÓRZE I WIĘKSZE --- */
    div[data-testid="stTabs"] > div:first-child {
        position: sticky;
        top: 40px; 
        z-index: 999;
        background-color: #0e1117; 
        padding: 10px 0 15px 0;
        border-bottom: 2px solid #333;
    }
    
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div {
        font-size: 26px !important; 
        font-weight: bold !important;
    }

    button[data-baseweb="tab"] {
        padding-top: 15px !important;
        padding-bottom: 15px !important;
    }

    .match-card { 
        margin-bottom: 20px; 
    }
    
    /* --- KONTENER DRUŻYNY --- */
    .team-box {
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid #444;
        background: rgba(255,255,255,0.02);
        transition: 0.3s;
        height: 140px; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .team-box img {
        margin-bottom: 10px;
        max-height: 60px; 
        object-fit: contain;
    }
    
    /* --- TRIK Z NIEWIDZIALNYM PRZYCISKIEM --- */
    div.element-container:has(.team-box) + div.element-container {
        margin-top: -140px; 
        position: relative;
        z-index: 10;
    }
    div.element-container:has(.team-box) + div.element-container button {
        height: 140px; 
        opacity: 0 !important; 
        cursor: pointer;
    }

    /* Podświetlenie na niebiesko */
    .selected-blue { 
        border: 3px solid #0099ff !important; 
        background: rgba(0, 153, 255, 0.1) !important;
        box-shadow: 0 0 10px rgba(0, 153, 255, 0.3);
    }
    .unselected { opacity: 0.5; }
    
    .stButton > button {
        width: 100%;
        background-color: transparent !important;
        border: 1px solid #555 !important;
        color: white !important;
    }
    .stButton > button:hover {
        border-color: #0099ff !important;
        color: #0099ff !important;
    }

    /* --- CZCIONKA W MENU ROZWIJANYM (STONOWANA) --- */
    div[data-baseweb="select"] {
        font-size: 20px !important; 
    }
    div[data-baseweb="select"] > div {
        font-size: 20px !important;
        min-height: 50px !important; 
    }
    div[data-baseweb="popover"] ul li {
        font-size: 20px !important; 
        padding: 10px !important; 
    }

    /* Wygląd nagłówków etapów */
    .round-header { 
        background-color: #1e1e1e; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        margin: 40px 0 30px 0; 
        border-left: 5px solid #f82910; 
        border-right: 5px solid #f82910;
        font-weight: bold; 
        font-size: 1.4em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-exact { background-color: #008000; color: white; }
    .pts-winner { background-color: #000080; color: white; }
    .pts-wrong { background-color: #800000; color: white; }
    .pts-normal { background-color: #444; color: #bbb; }
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(0, 0, 0, 0.2); }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka", "⚙️ Admin"])

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
        st.subheader(f"Zalogowano: {st.session_state.logged_user}")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()
        
        is_locked = now > START_TIME

        STAGE_GROUPS = [
            ("PIERWSZA RUNDA - ZACHÓD", ["W1", "W2", "W3", "W4"]),
            ("PIERWSZA RUNDA - WSCHÓD", ["E1", "E2", "E3", "E4"]),
            ("PÓŁFINAŁY KONFERENCJI", ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]),
            ("FINAŁY KONFERENCJI", ["W_CF", "E_CF"]),
            ("FINAŁ NBA", ["FINALS"])
        ]

        for stage_name, keys in STAGE_GROUPS:
            # Filtrowanie tylko tych kluczy, w których ZNANE są obie drużyny
            valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
            
            # Jeśli w tym etapie nie ma jeszcze żadnego znanego meczu, w ogóle go nie wyświetlamy
            if not valid_keys:
                continue

            st.markdown(f'<div class="round-header">{stage_name}</div>', unsafe_allow_html=True)
            
            for i, k in enumerate(valid_keys):
                t1, t2 = BRACKET[k][0], BRACKET[k][1]
                current_val = st.session_state.temp_picks.get(k, "4-0")
                left_wins = int(current_val.split("-")[0]) == 4
                num_games = sum(map(int, current_val.split("-")))

                st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center; margin-bottom: 15px; color: #ddd;'>{t1} vs {t2}</h4>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                
                logo_t1 = LOGOS.get(t1, LOGOS["TBD"])
                logo_t2 = LOGOS.get(t2, LOGOS["TBD"])
                
                with c1:
                    st.markdown(f'''
                    <div class="team-box {"selected-blue" if left_wins else "unselected"}">
                        <img src="{logo_t1}" alt="{t1}">
                        <span style="font-weight: bold; font-size: 1.1em;">{t1}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"Wybierz {t1}", key=f"bt1_{k}", disabled=is_locked, use_container_width=True):
                        st.session_state.temp_picks[k] = f"4-{num_games-4}"
                        st.rerun()

                with c2:
                    st.markdown(f'''
                    <div class="team-box {"selected-blue" if not left_wins else "unselected"}">
                        <img src="{logo_t2}" alt="{t2}">
                        <span style="font-weight: bold; font-size: 1.1em;">{t2}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"Wybierz {t2}", key=f"bt2_{k}", disabled=is_locked, use_container_width=True):
                        st.session_state.temp_picks[k] = f"{num_games-4}-4"
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown(f'<div style="font-size: 1.1em; font-weight: bold; margin-bottom: 5px; color: #ccc;">Liczba meczów serii:</div>', unsafe_allow_html=True)
                
                selected_games = st.selectbox(
                    f"Ukryty Label {k}", 
                    [4, 5, 6, 7], 
                    index=[4, 5, 6, 7].index(num_games), 
                    key=f"sl_{k}", 
                    disabled=is_locked,
                    label_visibility="collapsed"
                )
                
                if left_wins: st.session_state.temp_picks[k] = f"4-{selected_games-4}"
                else: st.session_state.temp_picks[k] = f"{selected_games-4}-4"
                
                st.markdown(f'<p style="margin-top:15px; font-size: 1.3em;">Twój typ: <b style="color: #0099ff;">{st.session_state.temp_picks[k]}</b></p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if i < len(valid_keys) - 1:
                    st.markdown("<hr style='margin: 30px 0; border: 0; border-top: 1px solid #333;'>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("ZAPISZ WSZYSTKIE TYPY", use_container_width=True, disabled=is_locked):
            st.session_state.db[st.session_state.logged_user] = st.session_state.temp_picks
            save_data(st.session_state.db, "wyniki.csv")
            st.balloons()
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
    def draw_bracket_card(k):
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

    STAGE_GROUPS_BRACKET = [
        ("ZACHÓD", ["W1", "W2", "W3", "W4"]),
        ("WSCHÓD", ["E1", "E2", "E3", "E4"]),
        ("PÓŁFINAŁY KONFERENCJI", ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]),
        ("FINAŁY KONFERENCJI", ["W_CF", "E_CF"]),
        ("FINAŁ NBA", ["FINALS"])
    ]

    for stage_name, keys in STAGE_GROUPS_BRACKET:
        # Pokaż nagłówek tylko, jeśli jest chociaż jeden gotowy mecz w danym etapie
        valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
        if valid_keys:
            st.markdown(f'<div class="round-header">{stage_name}</div>', unsafe_allow_html=True)
            for k in valid_keys:
                draw_bracket_card(k)

# --- ADMIN ---
with tab4:
    admin_auth = st.text_input("Kod Administratora:", type="password")
    if admin_auth == ADMIN_PIN:
        new_results = {}
        for k in ALL_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            curr = actual_res_db.get(k, "W toku")
            
            # Ukrywamy pole wyboru dla meczów, w których brakuje drużyn, 
            # ale jednocześnie musimy przepisać starą (lub domyślną) wartość
            if t1 == "TBD" or t2 == "TBD":
                new_results[k] = curr
                continue
                
            opts = ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"]
            idx = opts.index(curr) if curr in opts else 0
            new_results[k] = st.selectbox(f"Wynik {t1}-{t2}", opts, index=idx, key=f"adm_{k}")
            
        if st.button("Zatwierdź Wyniki"):
            st.session_state.results["OFFICIAL"] = new_results
            save_data(st.session_state.results, "oficjalne_wyniki.csv")
            st.rerun()
