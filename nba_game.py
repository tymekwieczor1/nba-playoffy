import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. KONFIGURACJA ---
ADMIN_PIN = "1398"
now = pd.Timestamp.now('Europe/Warsaw')
now_str = now.strftime("%Y-%m-%d %H:%M")

PLAYERS = ["Tymek", "Soból", "Maciek", "Kowal", "Paweł", "Mateusz", "Tomasz"]

MULTIPLIERS = {
    "W1": 1.0, "W2": 1.0, "W3": 1.0, "W4": 1.0,
    "E1": 1.0, "E2": 1.0, "E3": 1.0, "E4": 1.0,
    "W_SF1": 1.3, "W_SF2": 1.3, "E_SF1": 1.3, "E_SF2": 1.3,
    "W_CF": 1.6, "E_CF": 1.6,
    "FINALS": 2.0
}

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

ODDS = {
    "Thunder": 1.25, "8 Seed": 3.50, "Lakers": 1.85, "Rockets": 1.95,
    "Nuggets": 1.40, "Timberwolves": 2.70, "Spurs": 1.60, "Trail Blazers": 2.20,
    "Pistons": 1.30, "Cavaliers": 1.75, "Raptors": 2.05, "Knicks": 1.50,
    "Hawks": 2.40, "Celtics": 1.15, "7 Seed": 4.80, "TBD": "-"
}

# --- 2. FUNKCJE ---
def load_data(filename):
    if os.path.exists(filename):
        try: return pd.read_csv(filename, index_col=0, dtype=str).to_dict('index')
        except: return {}
    return {}

def save_data(data, filename):
    pd.DataFrame.from_dict(data, orient='index').to_csv(filename)

def clean_pick(val):
    if pd.isna(val): return "-"
    val_str = str(val).strip()
    if val_str in ["nan", "NaN", "None", ""]: return "-"
    if "-" not in val_str: return "-"
    return val_str

def is_underdog(odd_str):
    try:
        return float(str(odd_str).replace(",", ".")) >= 2.1
    except:
        return False

def check_pick_underdog(user_pick, odd_t1, odd_t2):
    if user_pick == "-": return False
    try:
        parts = str(user_pick).split("-")
        if int(parts[0]) == 4: return is_underdog(odd_t1)
        if int(parts[1]) == 4: return is_underdog(odd_t2)
    except: pass
    return False

def get_points_logic(user_pick, actual_result, multiplier=1.0, is_hot_take=False, is_underdog_pick=False):
    if pd.isna(actual_result) or actual_result == "W toku" or user_pick == "-": 
        return 0, "", "pts-normal"
    pts = 0
    try:
        u_left_wins = int(str(user_pick).split("-")[0]) == 4
        a_left_wins = int(str(actual_result).split("-")[0]) == 4
        if str(user_pick) == str(actual_result): 
            pts = 5 * multiplier
            if is_hot_take: pts += 5  
            if is_underdog_pick: pts += 3  
            return pts, "res-exact", "pts-exact"
        elif u_left_wins == a_left_wins: 
            pts = 3 * multiplier
            if is_hot_take: pts += 2  
            if is_underdog_pick: pts += 1  
            return pts, "res-winner", "pts-winner"
    except: pass
    return 0, "res-wrong", "pts-wrong"

def get_winner(match_key, results, teams):
    res = results.get("OFFICIAL", {}).get(match_key, "W toku")
    if pd.isna(res) or res == "W toku": return "TBD"
    try:
        s = str(res).split("-")
        if int(s[0]) == 4: return teams[0]
        if int(s[1]) == 4: return teams[1]
    except: pass
    return "TBD"

def format_score(pts):
    return f"+{int(pts)}" if pts % 1 == 0 else f"+{round(pts, 1)}"

def clean_odd(odd_val):
    val = str(odd_val).strip()
    if val == "nan" or val == "" or val == "None": return "-"
    return val

# --- 3. INICJALIZACJA ---
if 'db' not in st.session_state: st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state: st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state: st.session_state.logged_user = None
if 'temp_picks' not in st.session_state: st.session_state.temp_picks = {}

actual_res_db = st.session_state.results.get("OFFICIAL", {})
odds_db = st.session_state.results.get("ODDS", {})
times_db = st.session_state.results.get("START_TIMES", {})

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

# --- 4. CSS ---
st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    div[data-testid="stTabs"] > div:first-child {
        position: sticky; top: 40px; z-index: 999;
        background-color: #0e1117; padding: 10px 0 15px 0; border-bottom: 2px solid #333;
    }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div { font-size: 20px !important; font-weight: bold !important; }
    button[data-baseweb="tab"] { padding-top: 15px !important; padding-bottom: 15px !important; }
    .match-card { margin-bottom: 20px; }
    
    .team-box {
        border-radius: 12px; padding: 10px 4px; text-align: center; border: 2px solid #444;
        background: rgba(255,255,255,0.02); transition: 0.3s; height: 180px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden;
    }
    .team-box img { margin-bottom: 8px; max-height: 70px; max-width: 100%; object-fit: contain; }
    div.element-container:has(.team-box) + div.element-container { margin-top: -180px; position: relative; z-index: 10; }
    div.element-container:has(.team-box) + div.element-container button { height: 180px; opacity: 0 !important; cursor: pointer; }

    .game-btn {
        border-radius: 50%; width: 50px; height: 50px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3em; font-weight: bold; margin: 0 auto;
        border: 2px solid #444; transition: 0.3s;
    }
    .game-btn-selected { border-color: #0099ff; background-color: rgba(0, 153, 255, 0.2); color: #0099ff; box-shadow: 0 0 12px rgba(0, 153, 255, 0.4); }
    .game-btn-unselected { background-color: rgba(255,255,255,0.02); color: #aaa; }
    .game-btn-disabled { opacity: 0.3; border-color: #333; }
    
    div.element-container:has(.game-btn) + div.element-container { margin-top: -50px; position: relative; z-index: 10; display: flex; justify-content: center; }
    div.element-container:has(.game-btn) + div.element-container button { height: 50px; opacity: 0 !important; cursor: pointer; padding: 0 !important; margin: 0 auto !important; display: block !important; }

    .hot-box {
        border-radius: 10px; padding: 10px; text-align: center; border: 2px solid #ff4b4b;
        background: rgba(255, 75, 75, 0.05); transition: 0.3s; height: 60px; margin: 15px 0;
        display: flex; align-items: center; justify-content: center;
    }
    .hot-selected { background: rgba(255, 75, 75, 0.2) !important; box-shadow: 0 0 15px rgba(255, 75, 75, 0.5); border: 3px solid #ff4b4b !important; }
    div.element-container:has(.hot-box) + div.element-container { margin-top: -75px; position: relative; z-index: 10; }
    div.element-container:has(.hot-box) + div.element-container button { height: 60px; opacity: 0 !important; cursor: pointer; }

    div[data-testid="column"] { min-width: 0 !important; }

    .selected-blue { border: 3px solid #0099ff !important; background: rgba(0, 153, 255, 0.1) !important; box-shadow: 0 0 10px rgba(0, 153, 255, 0.3); }
    .unselected { opacity: 0.5; filter: grayscale(50%); }
    
    .stButton > button { width: 100%; background-color: transparent !important; border: 1px solid #555 !important; color: white !important; }
    .stButton > button:hover { border-color: #0099ff !important; color: #0099ff !important; }

    .clear-btn-col .stButton > button { border-color: #ff4b4b !important; color: #ff4b4b !important; background-color: rgba(255, 75, 75, 0.1) !important; font-size: 1.1em !important; padding: 10px !important; min-height: 55px !important; margin-top: 5px; }
    .clear-btn-col .stButton > button:hover { background-color: rgba(255, 75, 75, 0.2) !important; }
    
    .save-btn-col .stButton > button { border-color: #28a745 !important; color: #28a745 !important; background-color: rgba(40, 167, 69, 0.1) !important; font-size: 1.1em !important; padding: 10px !important; min-height: 55px !important; margin-top: 5px; }
    .save-btn-col .stButton > button:hover { background-color: rgba(40, 167, 69, 0.2) !important; }

    .round-header { background-color: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; margin: 40px 0 30px 0; border-left: 5px solid #f82910; border-right: 5px solid #f82910; font-weight: bold; font-size: 1.4em; text-transform: uppercase; letter-spacing: 1px; }
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-exact { background-color: #008000; color: white; }
    .pts-winner { background-color: #000080; color: white; }
    .pts-wrong { background-color: #800000; color: white; }
    .pts-normal { background-color: #444; color: #bbb; }
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(0, 0, 0, 0.2); }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖋️ Twoje Typy", "👀 Typy Innych", "🏆 Ranking", "📊 Drabinka", "⚙️ Admin"])

STAGE_GROUPS = [
    ("PIERWSZA RUNDA - ZACHÓD", ["W1", "W2", "W3", "W4"]),
    ("PIERWSZA RUNDA - WSCHÓD", ["E1", "E2", "E3", "E4"]),
    ("PÓŁFINAŁY KONFERENCJI", ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]),
    ("FINAŁY KONFERENCJI", ["W_CF", "E_CF"]),
    ("FINAŁ NBA", ["FINALS"])
]

# --- TYPY ---
with tab1:
    if st.session_state.logged_user is None:
        user = st.selectbox("Wybierz gracza:", [""] + PLAYERS)
        if user:
            if st.button("Wejdź (Test)", use_container_width=True):
                st.session_state.logged_user = user
                user_data = st.session_state.db.get(user, {})
                st.session_state.temp_picks = user_data.copy()
                st.rerun()
    else:
        st.subheader(f"Zalogowano: {st.session_state.logged_user}")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()

        user_saved_data = st.session_state.db.get(st.session_state.logged_user, {})
        placed_picks = sum(1 for k in ALL_KEYS if clean_pick(user_saved_data.get(k, "-")) != "-")
        hot_takes_used = sum(1 for k in ALL_KEYS if str(st.session_state.temp_picks.get(f"hot_{k}", "False")).lower() == "true")
        
        st.markdown(f"""
        <div style="background-color: rgba(0, 153, 255, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #0099ff; text-align: center; margin-top: 20px; margin-bottom: 10px;">
            <span style="font-size: 1.1em; font-weight: bold; color: #0099ff;">✅ Zapisane typy: {placed_picks} / {len(ALL_KEYS)}</span>
        </div>
        <div style="background-color: rgba(255, 75, 75, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; text-align: center; margin-bottom: 20px;">
            <span style="font-size: 1.1em; font-weight: bold; color: #ff4b4b;">🔥 Wykorzystane Hot Take'i: {hot_takes_used} / 2</span>
        </div>
        """, unsafe_allow_html=True)

        for stage_name, keys in STAGE_GROUPS:
            valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
            if not valid_keys: continue

            st.markdown(f'<div class="round-header">{stage_name} (x{MULTIPLIERS[keys[0]]})</div>', unsafe_allow_html=True)
            
            for i, k in enumerate(valid_keys):
                t1, t2 = BRACKET[k][0], BRACKET[k][1]
                
                current_val = clean_pick(st.session_state.temp_picks.get(k, "-"))

                left_selected = False
                right_selected = False
                num_games = 4

                if current_val != "-":
                    try:
                        parts = current_val.split("-")
                        left_selected = int(parts[0]) == 4
                        right_selected = int(parts[1]) == 4
                        num_games = sum(map(int, parts))
                    except:
                        current_val = "-"
                        left_selected = False
                        right_selected = False
                
                match_start_time = times_db.get(k, "2026-04-18 19:00")
                has_match_started = now_str >= match_start_time
                is_match_result_known = actual_res_db.get(k, "W toku") != "W toku"
                match_locked = has_match_started or is_match_result_known
                
                is_hot_str = str(st.session_state.temp_picks.get(f"hot_{k}", "False")).lower()
                is_hot = (is_hot_str == "true")
                hot_disabled = match_locked or current_val == "-" or (not is_hot and hot_takes_used >= 2)
                options_disabled = match_locked or current_val == "-"

                st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center; margin-bottom: 5px; color: #ddd;'>{t1} vs {t2}</h4>", unsafe_allow_html=True)
                
                st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.85em; margin-bottom: 15px;'>Mecz zamyka się: {match_start_time}</p>", unsafe_allow_html=True)
                
                st.markdown(f'''
                    <style>
                    #team-row-{k} + div[data-testid="stHorizontalBlock"] {{
                        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 8px !important;
                    }}
                    #team-row-{k} + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
                        width: 50% !important; min-width: 0 !important; flex: 1 1 50% !important;
                    }}
                    </style>
                    <div id="team-row-{k}"></div>
                ''', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                logo_t1, logo_t2 = LOGOS.get(t1, LOGOS["TBD"]), LOGOS.get(t2, LOGOS["TBD"])
                odd_t1 = clean_odd(odds_db.get(f"{k}_T1", "-"))
                odd_t2 = clean_odd(odds_db.get(f"{k}_T2", "-"))
                
                ud_badge_t1 = '<div style="margin-top: 6px;"><span style="background-color: #e67e22; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; font-weight: bold; letter-spacing: 0.5px;">💰 UNDERDOG</span></div>' if is_underdog(odd_t1) else ''
                ud_badge_t2 = '<div style="margin-top: 6px;"><span style="background-color: #e67e22; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; font-weight: bold; letter-spacing: 0.5px;">💰 UNDERDOG</span></div>' if is_underdog(odd_t2) else ''

                with c1:
                    css_class = "selected-blue" if left_selected else ("unselected" if right_selected else "")
                    st.markdown(f'<div class="team-box {css_class}"><img src="{logo_t1}"><span style="font-weight:bold; font-size:0.95em; line-height:1.2; margin-bottom:2px;">{t1}</span><span style="font-size:0.8em;color:#f39c12;">Kurs: {odd_t1}</span>{ud_badge_t1}</div>', unsafe_allow_html=True)
                    if st.button(f"Wybierz {t1}", key=f"bt1_{k}", disabled=match_locked, use_container_width=True):
                        st.session_state.temp_picks[k] = f"4-{num_games-4}"; st.rerun()

                with c2:
                    css_class = "selected-blue" if right_selected else ("unselected" if left_selected else "")
                    st.markdown(f'<div class="team-box {css_class}"><img src="{logo_t2}"><span style="font-weight:bold; font-size:0.95em; line-height:1.2; margin-bottom:2px;">{t2}</span><span style="font-size:0.8em;color:#f39c12;">Kurs: {odd_t2}</span>{ud_badge_t2}</div>', unsafe_allow_html=True)
                    if st.button(f"Wybierz {t2}", key=f"bt2_{k}", disabled=match_locked, use_container_width=True):
                        st.session_state.temp_picks[k] = f"{num_games-4}-4"; st.rerun()
                
                if current_val != "-":
                    st.markdown(f'<div class="hot-box {"hot-selected" if is_hot else ("unselected" if hot_disabled else "")}"><span style="font-size: 1.4em; font-weight: bold; color: {"white" if is_hot else "#aaa"};">🔥 UŻYJ HOT TAKE 🔥</span></div>', unsafe_allow_html=True)
                    if st.button(f"Hot_{k}", key=f"btn_hot_{k}", disabled=hot_disabled, use_container_width=True):
                        st.session_state.temp_picks[f"hot_{k}"] = "True" if not is_hot else "False"
                        if not is_hot: st.toast("🔥 HOT TAKE AKTYWOWANY! 🔥")
                        st.rerun()

                    st.markdown(f'<div style="text-align: center; font-size: 1.1em; font-weight: bold; margin-bottom: 10px; margin-top: 10px; color: #ccc;">Liczba meczów w serii:</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'''
                        <style>
                        #game-row-{k} + div[data-testid="stHorizontalBlock"] {{
                            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important;
                            justify-content: center !important; gap: 8px !important; width: 100% !important;
                        }}
                        #game-row-{k} + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
                            width: 25% !important; min-width: 0 !important; flex: 1 1 25% !important; display: flex; justify-content: center;
                        }}
                        </style>
                        <div id="game-row-{k}"></div>
                    ''', unsafe_allow_html=True)
                    
                    g_cols = st.columns(4)
                    for idx, g in enumerate([4, 5, 6, 7]):
                        with g_cols[idx]:
                            is_sel = (num_games == g)
                            css_btn = "game-btn-selected" if is_sel else "game-btn-unselected"
                            if options_disabled: css_btn += " game-btn-disabled"
                            
                            st.markdown(f'<div class="game-btn {css_btn}">{g}</div>', unsafe_allow_html=True)
                            if st.button(f"{g}", key=f"bg_{k}_{g}", disabled=options_disabled, use_container_width=True):
                                new_v = f"4-{g-4}" if left_selected else f"{g-4}-4"
                                if current_val != new_v: 
                                    st.session_state.temp_picks[k] = new_v
                                    st.rerun()

                mult = MULTIPLIERS[k]
                is_curr_ud = check_pick_underdog(current_val, odd_t1, odd_t2)
                pot_winner = (3 * mult) + (2 if is_hot else 0) + (1 if is_curr_ud else 0)
                pot_exact = (5 * mult) + (5 if is_hot else 0) + (3 if is_curr_ud else 0)
                
                pot_html = f'<div style="font-size: 0.85em; margin-top: 8px; color: #aaa;">Do zdobycia: <span style="color: #0099ff; font-weight: bold;">Zwycięzca {format_score(pot_winner)}</span> • <span style="color: #28a745; font-weight: bold;">Wynik {format_score(pot_exact)}</span></div>'

                colA, colB, colC = st.columns([2, 1, 1])
                with colA:
                    if current_val == "-": 
                        st.markdown(f'<div style="margin-top:20px; font-size: 1.2em;">Twój typ: <br><span style="color:#ff4b4b; font-weight:bold;">BRAK !!! 🚨</span><br>{pot_html}</div>', unsafe_allow_html=True)
                    else: 
                        parts = current_val.split("-")
                        if left_selected:
                            pick_text = f'<b style="font-size: 1.1em;">{t1}</b> <b style="font-size: 1.3em;">4</b>-{parts[1]} {t2}'
                        elif right_selected:
                            pick_text = f'{t1} {parts[0]}-<b style="font-size: 1.3em;">4</b> <b style="font-size: 1.1em;">{t2}</b>'
                        else:
                            pick_text = f'{t1} {current_val} {t2}'
                            
                        st.markdown(f'<div style="margin-top:20px; font-size: 1.0em; line-height: 1.4;">Twój typ: <br><span style="color:#0099ff;">{pick_text}{" 🔥" if is_hot else ""}</span><br>{pot_html}</div>', unsafe_allow_html=True)
                
                with colB:
                    st.markdown('<div class="save-btn-col">', unsafe_allow_html=True)
                    if st.button("💾 Zapisz", key=f"save_ind_{k}", disabled=match_locked or current_val == "-"):
                        fresh_db = load_data("wyniki.csv")
                        fresh_db[st.session_state.logged_user] = st.session_state.temp_picks
                        save_data(fresh_db, "wyniki.csv")
                        st.session_state.db = fresh_db
                        st.toast(f"Zapisano mecz {t1} vs {t2}!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                with colC:
                    st.markdown('<div class="clear-btn-col">', unsafe_allow_html=True)
                    if st.button("🗑️ Wyczyść", key=f"clear_{k}", disabled=match_locked or current_val == "-"):
                        st.session_state.temp_picks[k] = "-"
                        st.session_state.temp_picks[f"hot_{k}"] = "False"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if i < len(valid_keys) - 1: st.markdown("<hr style='margin: 30px 0; border-top: 1px solid #333;'>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("ZAPISZ WSZYSTKO", use_container_width=True):
            fresh_db = load_data("wyniki.csv")
            fresh_db[st.session_state.logged_user] = st.session_state.temp_picks
            save_data(fresh_db, "wyniki.csv")
            st.session_state.db = fresh_db
            st.balloons()
            st.success("Wszystko zapisane!")
            st.rerun()

# --- TYPY INNYCH ---
with tab2:
    st.subheader("👀 Typy pozostałych graczy")
    st.markdown("Typy są ukryte 🔒 do momentu wygaśnięcia czasu na typowanie danego meczu. **Twoje własne typy są dla Ciebie zawsze widoczne!**")
    
    summary_data = []
    for stage_name, keys in STAGE_GROUPS:
        valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
        for k in valid_keys:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            match_start_time = times_db.get(k, "2026-04-18 19:00")
            has_match_started = now_str >= match_start_time
            
            actual_res = actual_res_db.get(k, "W toku")
            is_match_finished = actual_res != "W toku" and actual_res != "-"
            
            odd_t1 = odds_db.get(f"{k}_T1", "-")
            odd_t2 = odds_db.get(f"{k}_T2", "-")
            
            row = {"Mecz": f"{t1} vs {t2}"}
            for p in PLAYERS:
                # Pokazujemy typ jeśli mecz wystartował ALBO to jest kolumna zalogowanego gracza
                if has_match_started or p == st.session_state.logged_user:
                    p_data = st.session_state.db.get(p, {})
                    pick = clean_pick(p_data.get(k, "-"))
                    is_hot = str(p_data.get(f"hot_{k}", "False")).lower() == "true"
                    
                    display_text = f"{pick} 🔥" if is_hot and pick != "-" else pick
                    
                    # Jeśli mecz zakończony i gracz miał oddany typ, dopisz zdobyte punkty w nawiasie
                    if is_match_finished and pick != "-":
                        is_ud = check_pick_underdog(pick, odd_t1, odd_t2)
                        pts, _, _ = get_points_logic(pick, actual_res, MULTIPLIERS[k], is_hot, is_ud)
                        pts_str = str(int(pts)) if pts % 1 == 0 else str(round(pts, 1))
                        display_text += f" ({pts_str} pkt)"
                        
                    row[p] = display_text
                else:
                    row[p] = "🔒"
            summary_data.append(row)
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data).set_index("Mecz")
        st.dataframe(df_summary, use_container_width=True)
    else:
        st.write("Brak dostępnych meczów do wyświetlenia.")

# --- RANKING ---
with tab3:
    st.subheader("Ranking")
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        pts = 0
        for k in ALL_KEYS:
            is_hot = str(p_data.get(f"hot_{k}","False")).lower()=="true"
            u_pick = clean_pick(p_data.get(k, "-"))
            odd_t1 = odds_db.get(f"{k}_T1", "-")
            odd_t2 = odds_db.get(f"{k}_T2", "-")
            is_ud = check_pick_underdog(u_pick, odd_t1, odd_t2)
            
            match_pts = get_points_logic(u_pick, actual_res_db.get(k, "W toku"), MULTIPLIERS[k], is_hot, is_ud)[0]
            pts += match_pts
            
        leaderboard.append({"Gracz": p, "Suma": int(pts) if pts % 1 == 0 else round(pts, 1)})
    st.table(pd.DataFrame(leaderboard).sort_values("Suma", ascending=False).set_index("Gracz"))

# --- DRABINKA ---
with tab4:
    def draw_bracket_card(k):
        t1, t2, s1, s2 = BRACKET[k]
        u_data = st.session_state.db.get(st.session_state.logged_user, {})
        u_pick = clean_pick(u_data.get(k, "-"))
        is_hot = str(u_data.get(f"hot_{k}","False")).lower()=="true"
        a_res = actual_res_db.get(k, "W toku")
        
        odd_t1 = odds_db.get(f"{k}_T1", "-")
        odd_t2 = odds_db.get(f"{k}_T2", "-")
        is_ud = check_pick_underdog(u_pick, odd_t1, odd_t2)
        
        pts, css_box, css_pts = get_points_logic(u_pick, a_res, MULTIPLIERS[k], is_hot, is_ud)
        st.markdown(f'<div class="match-box {css_box}"><div style="display:flex;align-items:center;"><div class="logo-bg"><img src="{LOGOS.get(t1, LOGOS["TBD"])}" width="30"></div> <b>({s1}) {t1}</b></div><div style="text-align:center;margin:5px 0;font-size:0.8em;color:#888;">{a_res if a_res != "W toku" else "W toku"} | Ty: {"BRAK" if u_pick=="-" else u_pick}{" 🔥" if is_hot and u_pick!="-" else ""} <span class="pts-badge {css_pts}">{format_score(pts)}</span></div><div style="display:flex;align-items:center;"><div class="logo-bg"><img src="{LOGOS.get(t2, LOGOS["TBD"])}" width="30"></div> <b>({s2}) {t2}</b></div></div>', unsafe_allow_html=True)

    for stage_name, keys in STAGE_GROUPS:
        valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
        if valid_keys:
            st.markdown(f'<div class="round-header">{stage_name} (x{MULTIPLIERS[keys[0]]})</div>', unsafe_allow_html=True)
            for k in valid_keys: draw_bracket_card(k)

# --- ADMIN ---
with tab5:
    admin_auth = st.text_input("Kod Administratora:", type="password")
    if admin_auth == ADMIN_PIN:
        new_results = {}
        new_odds = {}
        new_times = {}
        
        st.markdown("### Wprowadzanie Wyników, Kursów i Czasu")
        for k in ALL_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            curr_res = actual_res_db.get(k, "W toku")
            curr_odd_t1 = clean_odd(odds_db.get(f"{k}_T1", ""))
            curr_odd_t2 = clean_odd(odds_db.get(f"{k}_T2", ""))
            curr_time = times_db.get(k, "2026-04-18 19:00")
            
            if t1 == "TBD" or t2 == "TBD":
                new_results[k] = curr_res
                new_odds[f"{k}_T1"] = curr_odd_t1
                new_odds[f"{k}_T2"] = curr_odd_t2
                new_times[k] = curr_time
                continue
                
            st.markdown(f"**{t1} vs {t2}**")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                opts = ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"]
                new_results[k] = st.selectbox("Wynik", opts, index=opts.index(curr_res) if curr_res in opts else 0, key=f"adm_res_{k}")
            with c2:
                new_odds[f"{k}_T1"] = st.text_input(f"Kurs {t1}", value=curr_odd_t1 if curr_odd_t1 != "-" else "", key=f"adm_odd1_{k}", placeholder="Kurs")
            with c3:
                new_odds[f"{k}_T2"] = st.text_input(f"Kurs {t2}", value=curr_odd_t2 if curr_odd_t2 != "-" else "", key=f"adm_odd2_{k}", placeholder="Kurs")
            
            c4, c5 = st.columns(2)
            try:
                dt_obj = datetime.strptime(curr_time, "%Y-%m-%d %H:%M")
            except:
                dt_obj = datetime(2026, 4, 18, 19, 0)
                
            with c4:
                d = st.date_input("Data zamknięcia", value=dt_obj.date(), key=f"adm_d_{k}")
            with c5:
                t = st.time_input("Godzina zamknięcia", value=dt_obj.time(), key=f"adm_t_{k}")
                
            new_times[k] = f"{d.strftime('%Y-%m-%d')} {t.strftime('%H:%M')}"
            
            st.markdown("<hr style='margin: 10px 0; border-top: 1px solid #333;'>", unsafe_allow_html=True)
            
        if st.button("Zatwierdź Zmiany", use_container_width=True):
            fresh_res = load_data("oficjalne_wyniki.csv")
            fresh_res["OFFICIAL"] = new_results
            fresh_res["ODDS"] = new_odds
            fresh_res["START_TIMES"] = new_times
            save_data(fresh_res, "oficjalne_wyniki.csv")
            st.session_state.results = fresh_res
            st.success("Zapisano wszystkie zmiany!")
            st.rerun()
