import streamlit as st
import pandas as pd
from datetime import datetime
import os
from github import Github
import io

# --- 1. KONFIGURACJA ---
ADMIN_PIN = "1398"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")

now = pd.Timestamp.now('Europe/Warsaw')
now_str = now.strftime("%Y-%m-%d %H:%M")

DEFAULT_DEADLINE = "2026-08-01 00:00"

PLAYERS = ["Tymek", "Soból", "Maciek", "Kowal", "Paweł", "Mateusz", "Tomasz"]

PLAYER_PINS = {
    "Tymek": "4821",
    "Soból": "7390",
    "Maciek": "1564",
    "Kowal": "8203",
    "Paweł": "5912",
    "Mateusz": "3748",
    "Tomasz": "9156"
}

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
    "76ers": "https://loodibee.com/wp-content/uploads/nba-philadelphia-76ers-logo.png",
    "Suns": "https://loodibee.com/wp-content/uploads/nba-phoenix-suns-logo.png",
    "Magic": "https://loodibee.com/wp-content/uploads/nba-orlando-magic-logo.png",
    "TBD": "https://via.placeholder.com/150/333333/FFFFFF?text=?"
}

GENERIC_MATCH_NAMES = {
    "W_SF1": "SF WEST 1", "W_SF2": "SF WEST 2",
    "E_SF1": "SF EAST 1", "E_SF2": "SF EAST 2",
    "W_CF": "F WEST", "E_CF": "F EAST",
    "FINALS": "FINALS"
}

# --- 2. FUNKCJE ZAPISU DO GITHUB ---
def load_data(filename):
    if not GITHUB_TOKEN or not REPO_NAME:
        if os.path.exists(filename):
            try: return pd.read_csv(filename, index_col=0, dtype=str).to_dict('index')
            except: return {}
        return {}
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = repo.get_contents(filename)
        csv_data = file_content.decoded_content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data), index_col=0, dtype=str)
        return df.to_dict('index')
    except:
        return {}

def save_data(data, filename):
    if not GITHUB_TOKEN or not REPO_NAME:
        pd.DataFrame.from_dict(data, orient='index').to_csv(filename)
        return
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        df = pd.DataFrame.from_dict(data, orient='index')
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer)
        content = csv_buffer.getvalue()
        try:
            file = repo.get_contents(filename)
            repo.update_file(filename, f"Auto-update {filename}", content, file.sha)
        except:
            repo.create_file(filename, f"Create {filename}", content)
    except Exception as e:
        st.error(f"Błąd zapisu! {e}")

def auto_save():
    if st.session_state.logged_user:
        st.toast("⏳ Zapisywanie...")
        fresh_db = load_data("wyniki.csv")
        fresh_db[st.session_state.logged_user] = st.session_state.temp_picks
        save_data(fresh_db, "wyniki.csv")
        st.session_state.db = fresh_db
        st.toast("✅ Zapisano!")

def clean_pick(val):
    if pd.isna(val): return "-"
    val_str = str(val).strip()
    if val_str in ["nan", "NaN", "None", ""]: return "-"
    if "-" not in val_str: return "-"
    return val_str

def is_underdog(odd_str):
    try: return float(str(odd_str).replace(",", ".")) >= 2.1
    except: return False

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
        return 0, "res-normal", "pts-normal"
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
if 'confirm_clear' not in st.session_state: st.session_state.confirm_clear = False

actual_res_db = st.session_state.results.get("OFFICIAL", {})
odds_db = st.session_state.results.get("ODDS", {})
times_db = st.session_state.results.get("START_TIMES", {})

R1_MAP = {
    "W1": ["Thunder", "Suns", "1", "8"], "W2": ["Lakers", "Rockets", "4", "5"],
    "W3": ["Nuggets", "Timberwolves", "3", "6"], "W4": ["Spurs", "Trail Blazers", "2", "7"],
    "E1": ["Pistons", "Magic", "1", "8"], "E2": ["Cavaliers", "Raptors", "4", "5"],
    "E3": ["Knicks", "Hawks", "3", "6"], "E4": ["Celtics", "76ers", "2", "7"]
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
st.set_page_config(page_title="NBA Playoff Pick'Em 2026", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { background-color: transparent !important; z-index: 998; }
    div[data-testid="stTabs"] > div:first-of-type { 
        position: -webkit-sticky !important; position: sticky !important; top: 0px !important; 
        z-index: 99999 !important; background-color: #0e1117; padding: 10px 0 10px 0; border-bottom: 2px solid #333; 
    }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div { font-size: 20px !important; font-weight: bold !important; }
    button[data-baseweb="tab"] { padding-top: 15px !important; padding-bottom: 15px !important; }
    .match-card { margin-bottom: 20px; }
    .team-box { border-radius: 12px; padding: 10px 4px; text-align: center; border: 2px solid #444; background: rgba(255,255,255,0.02); transition: 0.3s; height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }
    .team-box img { margin-bottom: 8px; max-height: 80px; max-width: 100%; object-fit: contain; }
    div.element-container:has(.team-box) + div.element-container { margin-top: -180px; position: relative; z-index: 10; }
    div.element-container:has(.team-box) + div.element-container button { height: 180px; opacity: 0 !important; cursor: pointer; }
    .game-btn { border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; font-size: 1.3em; font-weight: bold; margin: 0 auto; border: 2px solid #444; transition: 0.3s; }
    .game-btn-selected { border-color: #0099ff; background-color: rgba(0, 153, 255, 0.2); color: #0099ff; box-shadow: 0 0 12px rgba(0, 153, 255, 0.4); }
    .game-btn-unselected { background-color: rgba(255,255,255,0.02); color: #aaa; }
    .game-btn-disabled { opacity: 0.3; border-color: #333; }
    div.element-container:has(.game-btn) + div.element-container { margin-top: -50px; position: relative; z-index: 10; display: flex; justify-content: center; }
    div.element-container:has(.game-btn) + div.element-container button { height: 50px; opacity: 0 !important; cursor: pointer; padding: 0 !important; margin: 0 auto !important; display: block !important; }
    .hot-box { border-radius: 10px; padding: 10px; text-align: center; border: 2px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); transition: 0.3s; height: 60px; margin: 15px 0; display: flex; align-items: center; justify-content: center; }
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
    .round-header { background-color: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; margin: 40px 0 30px 0; border-left: 5px solid #f82910; border-right: 5px solid #f82910; font-weight: bold; font-size: 1.4em; text-transform: uppercase; letter-spacing: 1px; }
    .pts-badge { font-weight: bold; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 8px; display: inline-block; }
    .pts-exact { background-color: #008000; color: white; }
    .pts-winner { background-color: #000080; color: white; }
    .pts-wrong { background-color: #800000; color: white; }
    .pts-normal { background-color: #444; color: #bbb; }
    .match-box { border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 2px solid #444; background-color: rgba(0, 0, 0, 0.2); }
    .res-exact { border-color: #008000 !important; background-color: rgba(0, 128, 0, 0.15) !important; }
    .res-winner { border-color: #000080 !important; background-color: rgba(0, 0, 128, 0.15) !important; }
    .res-wrong { border-color: #800000 !important; background-color: rgba(128, 0, 0, 0.15) !important; }
    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .custom-table-wrapper { overflow-x: auto; margin-bottom: 20px; border-radius: 10px; }
    .custom-table { width: 100%; border-collapse: collapse; color: #fff; font-size: 0.95em; }
    .custom-table th { background-color: #262730; padding: 15px; border: 1px solid #444; text-align: center !important; white-space: nowrap; }
    .custom-table td { padding: 12px 10px; border: 1px solid #444; text-align: center; vertical-align: middle; white-space: nowrap; min-width: 120px; line-height: 1.4;}
    .custom-table tr:nth-child(even) td { background-color: rgba(255, 255, 255, 0.05); }
    .rules-card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px; border: 1px solid #444; margin-bottom: 15px; }
    .rules-card h3 { margin-top: 0; color: #0099ff; }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🖋️ Twoje Typy", "👀 Typy Innych", "🏆 Ranking", "📊 Drabinka", "📜 Zasady", "⚙️ Admin"])

# --- TAB 1: TWOJE TYPY ---
with tab1:
    if st.session_state.logged_user is None:
        user = st.selectbox("Wybierz gracza:", [""] + PLAYERS)
        if user:
            pin_input = st.text_input("Podaj 4-cyfrowy PIN:", type="password", key=f"pin_{user}")
            if st.button("Wejdź", use_container_width=True):
                if pin_input == PLAYER_PINS.get(user):
                    st.session_state.logged_user = user
                    st.session_state.temp_picks = st.session_state.db.get(user, {}).copy()
                    st.rerun()
                else:
                    st.error("Błędny PIN!")
    else:
        st.subheader(f"Zalogowano: {st.session_state.logged_user}")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()

        for stage_name, keys in STAGE_GROUPS:
            valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
            if not valid_keys: continue
            st.markdown(f'<div class="round-header">{stage_name} (x{MULTIPLIERS[keys[0]]})</div>', unsafe_allow_html=True)
            
            for k in valid_keys:
                t1, t2 = BRACKET[k][0], BRACKET[k][1]
                current_val = clean_pick(st.session_state.temp_picks.get(k, "-"))
                left_selected, right_selected, num_games = False, False, 4

                if current_val != "-":
                    try:
                        parts = current_val.split("-")
                        left_selected, right_selected = int(parts[0]) == 4, int(parts[1]) == 4
                        num_games = sum(map(int, parts))
                    except: current_val = "-"
                
                match_start_time = times_db.get(k, DEFAULT_DEADLINE)
                match_locked = now_str >= match_start_time or actual_res_db.get(k, "W toku") != "W toku"
                is_hot = str(st.session_state.temp_picks.get(f"hot_{k}", "False")).lower() == "true"
                hot_disabled = match_locked or current_val == "-" or (not is_hot and sum(1 for x in ALL_KEYS if str(st.session_state.temp_picks.get(f"hot_{x}", "False")).lower() == "true") >= 2)

                st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center; margin-bottom: 5px; color: #ddd;'>{t1} vs {t2}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.85em; margin-bottom: 15px;'>Zamyka się: {match_start_time}</p>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                odd_t1, odd_t2 = clean_odd(odds_db.get(f"{k}_T1", "-")), clean_odd(odds_db.get(f"{k}_T2", "-"))
                with c1:
                    if st.button(f"Wybierz {t1}", key=f"bt1_{k}", disabled=match_locked, use_container_width=True):
                        st.session_state.temp_picks[k] = f"4-{num_games-4}"; auto_save(); st.rerun()
                with c2:
                    if st.button(f"Wybierz {t2}", key=f"bt2_{k}", disabled=match_locked, use_container_width=True):
                        st.session_state.temp_picks[k] = f"{num_games-4}-4"; auto_save(); st.rerun()
                
                if current_val != "-":
                    if st.button(f"Hot_{k}", key=f"btn_hot_{k}", disabled=hot_disabled, use_container_width=True):
                        st.session_state.temp_picks[f"hot_{k}"] = "True" if not is_hot else "False"; auto_save(); st.rerun()
                    
                    g_cols = st.columns(4)
                    for idx, g in enumerate([4, 5, 6, 7]):
                        if g_cols[idx].button(f"{g}", key=f"bg_{k}_{g}", disabled=match_locked, use_container_width=True):
                            st.session_state.temp_picks[k] = f"4-{g-4}" if left_selected else f"{g-4}-4"; auto_save(); st.rerun()

                if current_val != "-":
                    p = current_val.split("-")
                    pick_text = f"<b>{t1 if left_selected else t2}</b> w <b>{num_games}</b>"
                    st.markdown(f'<p style="text-align:center; color:#0099ff;">Twój typ: {pick_text} {"🔥" if is_hot else ""}</p>', unsafe_allow_html=True)
                    if st.button("🗑️ Wyczyść Typ", key=f"clr_{k}", disabled=match_locked):
                        st.session_state.temp_picks[k] = "-"; st.session_state.temp_picks[f"hot_{k}"] = "False"; auto_save(); st.rerun()

# --- TAB 2: TYPY INNYCH ---
with tab2:
    st.subheader("👀 Typy pozostałych graczy")
    ordered_players = PLAYERS.copy()
    if st.session_state.logged_user:
        ordered_players.remove(st.session_state.logged_user)
        ordered_players.insert(0, st.session_state.logged_user)
    
    html_table = '<div class="custom-table-wrapper"><table class="custom-table"><thead><tr><th>Mecz</th>'
    for p in ordered_players: html_table += f'<th>{p}</th>'
    html_table += '</tr></thead><tbody>'

    for stage_name, keys in STAGE_GROUPS:
        for k in keys:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            match_deadline = times_db.get(k, DEFAULT_DEADLINE)
            has_started = now_str >= match_deadline
            actual_res = actual_res_db.get(k, "W toku")
            
            match_label = f"<b>{t1} vs {t2}</b>"
            if actual_res != "W toku": match_label += f"<br><span style='font-size:0.8em; color:#888;'>Wynik: {actual_res}</span>"
            
            html_table += f'<tr><td>{match_label}</td>'
            for p in ordered_players:
                if has_started or p == st.session_state.logged_user:
                    p_data = st.session_state.db.get(p, {})
                    pick = clean_pick(p_data.get(k, "-"))
                    is_hot = str(p_data.get(f"hot_{k}", "False")).lower() == "true"
                    display = f"<b>{pick}</b>{' 🔥' if is_hot and pick != '-' else ''}"
                    if actual_res != "W toku" and pick != "-":
                        pts, _, _ = get_points_logic(pick, actual_res, MULTIPLIERS[k], is_hot, check_pick_underdog(pick, odds_db.get(f"{k}_T1", "-"), odds_db.get(f"{k}_T2", "-")))
                        display += f"<br><span style='font-size:0.8em; color:#aaa;'>({int(pts)} pkt)</span>"
                    html_table += f'<td>{display}</td>'
                else: html_table += '<td>🔒</td>'
            html_table += '</tr>'
    st.markdown(html_table + '</tbody></table></div>', unsafe_allow_html=True)

# --- TAB 3: RANKING ---
with tab3:
    st.subheader("🏆 Ranking")
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        pts = sum(get_points_logic(clean_pick(p_data.get(k, "-")), actual_res_db.get(k, "W toku"), MULTIPLIERS[k], str(p_data.get(f"hot_{k}","False")).lower()=="true", check_pick_underdog(clean_pick(p_data.get(k, "-")), odds_db.get(f"{k}_T1", "-"), odds_db.get(f"{k}_T2", "-")))[0] for k in ALL_KEYS)
        leaderboard.append({"Gracz": p, "Punkty": int(pts)})
    st.table(pd.DataFrame(leaderboard).sort_values("Punkty", ascending=False).set_index("Gracz"))

# --- TAB 4: DRABINKA ---
with tab4:
    for stage_name, keys in STAGE_GROUPS:
        v_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
        if v_keys:
            st.markdown(f'<div class="round-header">{stage_name}</div>', unsafe_allow_html=True)
            for k in v_keys:
                t1, t2, s1, s2 = BRACKET[k][0], BRACKET[k][1], BRACKET[k][2], BRACKET[k][3]
                u_pick = clean_pick(st.session_state.db.get(st.session_state.logged_user, {}).get(k, "-"))
                is_hot = str(st.session_state.db.get(st.session_state.logged_user, {}).get(f"hot_{k}","False")).lower()=="true"
                a_res = actual_res_db.get(k, "W toku")
                pts, css_box, css_pts = get_points_logic(u_pick, a_res, MULTIPLIERS[k], is_hot, check_pick_underdog(u_pick, odds_db.get(f"{k}_T1", "-"), odds_db.get(f"{k}_T2", "-")))
                st.markdown(f'<div class="match-box {css_box}"><div style="display:flex;align-items:center;"><div class="logo-bg"><img src="{LOGOS.get(t1, LOGOS["TBD"])}" width="30"></div> <b>({s1}) {t1}</b></div><div style="text-align:center;margin:5px 0;font-size:0.8em;color:#888;">{a_res} | Ty: {u_pick} <span class="pts-badge {css_pts}">{format_score(pts)}</span></div><div style="display:flex;align-items:center;"><div class="logo-bg"><img src="{LOGOS.get(t2, LOGOS["TBD"])}" width="30"></div> <b>({s2}) {t2}</b></div></div>', unsafe_allow_html=True)

# --- TAB 5: ZASADY ---
with tab5:
    st.subheader("📜 Zasady Gry")
    st.markdown("""<div class="rules-card"><h3>🎯 Punktacja</h3><ul><li>Zwycięzca: 3 pkt</li><li>Wynik: +2 pkt (łącznie 5)</li><li><b>Mnożniki:</b> R1 (1.0), R2 (1.3), Finał Konf. (1.6), Finał NBA (2.0)</li><li><b>Hot Take:</b> +2 pkt za zwycięzcę, +5 pkt za wynik (max 2 na grę)</li><li><b>Underdog (kurs >= 2.1):</b> +1 pkt za zwycięzcę, +2 pkt za wynik</li></ul></div>""", unsafe_allow_html=True)

# --- TAB 6: ADMIN ---
with tab6:
    if st.text_input("Kod:", type="password") == ADMIN_PIN:
        new_res, new_odds, new_times = {}, {}, {}
        for k in ALL_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            if t1 == "TBD" or t2 == "TBD": continue
            st.write(f"**{t1} vs {t2}**")
            c1, c2, c3 = st.columns(3)
            new_res[k] = c1.selectbox("Wynik", ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"], index=["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"].index(actual_res_db.get(k, "W toku")), key=f"r{k}")
            new_odds[f"{k}_T1"] = c2.text_input("Kurs T1", value=odds_db.get(f"{k}_T1", ""), key=f"o1{k}")
            new_odds[f"{k}_T2"] = c3.text_input("Kurs T2", value=odds_db.get(f"{k}_T2", ""), key=f"o2{k}")
            
            try: dt_obj = datetime.strptime(times_db.get(k, DEFAULT_DEADLINE), "%Y-%m-%d %H:%M")
            except: dt_obj = datetime(2026, 8, 1, 0, 0)
            
            c4, c5 = st.columns(2)
            d = c4.date_input("Data", value=dt_obj.date(), key=f"d{k}")
            t = c5.time_input("Czas", value=dt_obj.time(), key=f"t{k}")
            new_times[k] = f"{d.strftime('%Y-%m-%d')} {t.strftime('%H:%M')}"
            
        if st.button("Zapisz zmiany w chmurze"):
            res = load_data("oficjalne_wyniki.csv")
            res["OFFICIAL"], res["ODDS"], res["START_TIMES"] = new_res, new_odds, new_times
            save_data(res, "oficjalne_wyniki.csv"); st.rerun()
