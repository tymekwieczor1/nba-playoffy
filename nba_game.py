import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. KONFIGURACJA ---
START_TIME = datetime(2026, 4, 18, 19, 0)
ADMIN_PIN = "1398"
now = datetime.now()

PLAYERS = ["Tymek", "Soból", "Maciek", "Kowal", "Paweł", "Mateusz", "Tomasz"]

PLAYER_PINS = {
    "Tymek": "839201",
    "Soból": "471029",
    "Maciek": "593812",
    "Kowal": "104857",
    "Paweł": "629403",
    "Mateusz": "385192",
    "Tomasz": "740285"
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

def get_points_logic(user_pick, actual_result, multiplier=1.0, is_hot_take=False):
    if pd.isna(actual_result) or actual_result == "W toku" or pd.isna(user_pick) or user_pick == "-": 
        return 0, "", "pts-normal"
    pts = 0
    try:
        u_left_wins = int(str(user_pick).split("-")[0]) == 4
        a_left_wins = int(str(actual_result).split("-")[0]) == 4
        if str(user_pick) == str(actual_result): 
            pts = 5 * multiplier
            if is_hot_take: pts += 5  
            return pts, "res-exact", "pts-exact"
        elif u_left_wins == a_left_wins: 
            pts = 3 * multiplier
            if is_hot_take: pts += 2  
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

# --- 4. CSS ---
st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    div[data-testid="stTabs"] > div:first-child {
        position: sticky; top: 40px; z-index: 999;
        background-color: #0e1117; padding: 10px 0 15px 0; border-bottom: 2px solid #333;
    }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] div { font-size: 26px !important; font-weight: bold !important; }
    button[data-baseweb="tab"] { padding-top: 15px !important; padding-bottom: 15px !important; }
    .match-card { margin-bottom: 20px; }
    
    .team-box {
        border-radius: 15px; padding: 15px; text-align: center; border: 2px solid #444;
        background: rgba(255,255,255,0.02); transition: 0.3s; height: 160px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .team-box img { margin-bottom: 10px; max-height: 60px; object-fit: contain; }
    div.element-container:has(.team-box) + div.element-container { margin-top: -160px; position: relative; z-index: 10; }
    div.element-container:has(.team-box) + div.element-container button { height: 160px; opacity: 0 !important; cursor: pointer; }

    .hot-box {
        border-radius: 10px; padding: 10px; text-align: center; border: 2px solid #ff4b4b;
        background: rgba(255, 75, 75, 0.05); transition: 0.3s; height: 60px;
        display: flex; align-items: center; justify-content: center; margin-top: 15px; margin-bottom: 15px;
    }
    .hot-selected { background: rgba(255, 75, 75, 0.2) !important; box-shadow: 0 0 15px rgba(255, 75, 75, 0.5); border: 3px solid #ff4b4b !important; }
    div.element-container:has(.hot-box) + div.element-container { margin-top: -90px; position: relative; z-index: 10; }
    div.element-container:has(.hot-box) + div.element-container button { height: 60px; opacity: 0 !important; cursor: pointer; }

    .selected-blue { border: 3px solid #0099ff !important; background: rgba(0, 153, 255, 0.1) !important; box-shadow: 0 0 10px rgba(0, 153, 255, 0.3); }
    .unselected { opacity: 0.5; filter: grayscale(50%); }
    
    .stButton > button { width: 100%; background-color: transparent !important; border: 1px solid #555 !important; color: white !important; }
    .stButton > button:hover { border-color: #0099ff !important; color: #0099ff !important; }

    .clear-btn-col .stButton > button { border-color: #ff4b4b !important; color: #ff4b4b !important; }
    .save-btn-col .stButton > button { border-color: #0099ff !important; color: #0099ff !important; }

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

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka", "⚙️ Admin"])

# --- TYPY ---
with tab1:
    if st.session_state.logged_user is None:
        user = st.selectbox("Wybierz gracza:", [""] + PLAYERS)
        if user:
            pwd = st.text_input("Hasło (6 cyfr):", type="password", key=f"login_{user}")
            if st.button("Wejdź"):
                if pwd == PLAYER_PINS.get(user):
                    st.session_state.logged_user = user
                    user_data = st.session_state.db.get(user, {})
                    st.session_state.temp_picks = user_data.copy()
                    st.rerun()
                else: st.error("Błędne hasło!")
    else:
        st.subheader(f"Zalogowano: {st.session_state.logged_user}")
        if st.button("Wyloguj"):
            st.session_state.logged_user = None
            st.rerun()
        
        is_global_locked = now > START_TIME

        # Statystyki zapisanych typów
        user_saved_data = st.session_state.db.get(st.session_state.logged_user, {})
        placed_picks = sum(1 for k in ALL_KEYS if user_saved_data.get(k, "-") != "-")
        hot_takes_used = sum(1 for k in ALL_KEYS if str(st.session_state.temp_picks.get(f"hot_{k}", "False")).lower() == "true")
        
        st.markdown(f"""
        <div style="background-color: rgba(0, 153, 255, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #0099ff; text-align: center; margin-top: 20px; margin-bottom: 10px;">
            <span style="font-size: 1.1em; font-weight: bold; color: #0099ff;">✅ Zapisane typy: {placed_picks} / {len(ALL_KEYS)}</span>
        </div>
        <div style="background-color: rgba(255, 75, 75, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; text-align: center; margin-bottom: 20px;">
            <span style="font-size: 1.1em; font-weight: bold; color: #ff4b4b;">🔥 Wykorzystane Hot Take'i: {hot_takes_used} / 2</span>
        </div>
        """, unsafe_allow_html=True)

        STAGE_GROUPS = [
            ("PIERWSZA RUNDA - ZACHÓD", ["W1", "W2", "W3", "W4"]),
            ("PIERWSZA RUNDA - WSCHÓD", ["E1", "E2", "E3", "E4"]),
            ("PÓŁFINAŁY KONFERENCJI", ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]),
            ("FINAŁY KONFERENCJI", ["W_CF", "E_CF"]),
            ("FINAŁ NBA", ["FINALS"])
        ]

        for stage_name, keys in STAGE_GROUPS:
            valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
            if not valid_keys: continue

            st.markdown(f'<div class="round-header">{stage_name} (x{MULTIPLIERS[keys[0]]})</div>', unsafe_allow_html=True)
            
            for i, k in enumerate(valid_keys):
                t1, t2 = BRACKET[k][0], BRACKET[k][1]
                current_val = st.session_state.temp_picks.get(k, "-")
                left_selected = False
                right_selected = False
                num_games = 4

                if current_val != "-" and "-" in str(current_val):
                    try:
                        parts = str(current_val).split("-")
                        left_selected = int(parts[0]) == 4
                        right_selected = int(parts[1]) == 4
                        num_games = sum(map(int, parts))
                    except: current_val = "-"
                
                is_match_result_known = actual_res_db.get(k, "W toku") != "W toku"
                match_locked = is_global_locked or is_match_result_known
                is_hot_str = str(st.session_state.temp_picks.get(f"hot_{k}", "False")).lower()
                is_hot = (is_hot_str == "true")
                hot_disabled = match_locked or current_val == "-" or (not is_hot and hot_takes_used >= 2)

                st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center; margin-bottom: 15px; color: #ddd;'>{t1} vs {t2}</h4>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                logo_t1, logo_t2 = LOGOS.get(t1, LOGOS["TBD"]), LOGOS.get(t2, LOGOS["TBD"])
                
                with c1:
                    css_class = "selected-blue" if left_selected else ("unselected" if right_selected else "")
                    st.markdown(f'<div class="team-box {css_class}"><img src="{logo_t1}"><span style="font-weight:bold;">{t1}</span><span style="font-size:0.8em;color:#f39c12;">Kurs: {ODDS.get(t1,"-")}</span></div>', unsafe_allow_html=True)
                    if st.button(f"Wybierz {t1}", key=f"bt1_{k}", disabled=match_locked):
                        st.session_state.temp_picks[k] = f"4-{num_games-4}"; st.rerun()

                with c2:
                    css_class = "selected-blue" if right_selected else ("unselected" if left_selected else "")
                    st.markdown(f'<div class="team-box {css_class}"><img src="{logo_t2}"><span style="font-weight:bold;">{t2}</span><span style="font-size:0.8em;color:#f39c12;">Kurs: {ODDS.get(t2,"-")}</span></div>', unsafe_allow_html=True)
                    if st.button(f"Wybierz {t2}", key=f"bt2_{k}", disabled=match_locked):
                        st.session_state.temp_picks[k] = f"{num_games-4}-4"; st.rerun()
                
                if current_val != "-":
                    st.markdown(f'<div class="hot-box {"hot-selected" if is_hot else ("unselected" if hot_disabled else "")}"><span style="font-size: 1.4em; font-weight: bold; color: {"white" if is_hot else "#aaa"};">🔥 UŻYJ HOT TAKE 🔥</span></div>', unsafe_allow_html=True)
                    if st.button(f"Hot_{k}", key=f"btn_hot_{k}", disabled=hot_disabled):
                        st.session_state.temp_picks[f"hot_{k}"] = "True" if not is_hot else "False"
                        if not is_hot: st.toast("🔥 HOT TAKE AKTYWOWANY! 🔥")
                        st.rerun()

                    st.markdown(f'<div style="font-weight:bold;margin-bottom:5px;color:#ccc;">Liczba meczów serii:</div>', unsafe_allow_html=True)
                    selected_games = st.selectbox(f"L_{k}", [4, 5, 6, 7], index=[4, 5, 6, 7].index(num_games) if num_games in [4, 5, 6, 7] else 0, key=f"sl_{k}", disabled=match_locked, label_visibility="collapsed")
                    
                    new_val = f"4-{selected_games-4}" if left_selected else f"{selected_games-4}-4"
                    if current_val != new_val: st.session_state.temp_picks[k] = new_val; st.rerun()

                colA, colB, colC = st.columns([2, 1, 1])
                with colA:
                    if current_val == "-": st.markdown(f'<p style="margin-top:15px; font-size: 1.2em; color:#ff4b4b;"><b>BRAK !!! 🚨</b></p>', unsafe_allow_html=True)
                    else: st.markdown(f'<p style="margin-top:15px; font-size: 1.2em; color:#0099ff;"><b>{current_val}{" 🔥" if is_hot else ""}</b></p>', unsafe_allow_html=True)
                
                with colB:
                    st.markdown('<div class="save-btn-col">', unsafe_allow_html=True)
                    if st.button("💾 Zapisz", key=f"save_ind_{k}", disabled=match_locked or current_val == "-"):
                        st.session_state.db[st.session_state.logged_user] = st.session_state.temp_picks
                        save_data(st.session_state.db, "wyniki.csv")
                        st.toast(f"Zapisano mecz {t1} vs {t2}!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                with colC:
                    st.markdown('<div class="clear-btn-col">', unsafe_allow_html=True)
                    if st.button("🗑️ Usuń", key=f"clear_{k}", disabled=match_locked or current_val == "-"):
                        st.session_state.temp_picks[k] = "-"; st.session_state.temp_picks[f"hot_{k}"] = "False"
                        if f"sl_{k}" in st.session_state: del st.session_state[f"sl_{k}"]
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if i < len(valid_keys) - 1: st.markdown("<hr style='margin: 30px 0; border-top: 1px solid #333;'>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("ZAPISZ WSZYSTKO", use_container_width=True, disabled=is_global_locked):
            st.session_state.db[st.session_state.logged_user] = st.session_state.temp_picks
            save_data(st.session_state.db, "wyniki.csv"); st.balloons(); st.success("Wszystko zapisane!"); st.rerun()

# --- RANKING ---
with tab2:
    st.subheader("Ranking")
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        pts = sum(get_points_logic(p_data.get(k, "-"), actual_res_db.get(k, "W toku"), MULTIPLIERS[k], str(p_data.get(f"hot_{k}","False")).lower()=="true")[0] for k in ALL_KEYS)
        leaderboard.append({"Gracz": p, "Suma": int(pts) if pts % 1 == 0 else round(pts, 1)})
    st.table(pd.DataFrame(leaderboard).sort_values("Suma", ascending=False).set_index("Gracz"))

# --- DRABINKA ---
with tab3:
    def draw_bracket_card(k):
        t1, t2, s1, s2 = BRACKET[k]
        u_data = st.session_state.db.get(st.session_state.logged_user, {})
        u_pick = u_data.get(k, "-")
        is_hot = str(u_data.get(f"hot_{k}","False")).lower()=="true"
        a_res = actual_res_db.get(k, "W toku")
        pts, css_box, css_pts = get_points_logic(u_pick, a_res, MULTIPLIERS[k], is_hot)
        st.markdown(f'<div class="match-box {css_box}"><div style="display:flex;align-items:center;"><div class="logo-bg"><img src="{LOGOS.get(t1, LOGOS["TBD"])}" width="30"></div> <b>({s1}) {t1}</b></div><div style="text-align:center;margin:5px 0;font-size:0.8em;color:#888;">{a_res if a_res != "W toku" else "W toku"} | Ty: {"BRAK" if u_pick=="-" else u_pick}{" 🔥" if is_hot else ""} <span class="pts-badge {css_pts}">{format_score(pts)}</span></div><div style="display:flex;align-items:center;"><div class="logo-bg"><img src="{LOGOS.get(t2, LOGOS["TBD"])}" width="30"></div> <b>({s2}) {t2}</b></div></div>', unsafe_allow_html=True)

    STAGE_GROUPS_BRACKET = [("ZACHÓD", ["W1", "W2", "W3", "W4"]), ("WSCHÓD", ["E1", "E2", "E3", "E4"]), ("PÓŁFINAŁY KONFERENCJI", ["W_SF1", "W_SF2", "E_SF1", "E_SF2"]), ("FINAŁY KONFERENCJI", ["W_CF", "E_CF"]), ("FINAŁ NBA", ["FINALS"])]
    for stage_name, keys in STAGE_GROUPS_BRACKET:
        valid_keys = [k for k in keys if BRACKET[k][0] != "TBD" and BRACKET[k][1] != "TBD"]
        if valid_keys:
            st.markdown(f'<div class="round-header">{stage_name} (x{MULTIPLIERS[keys[0]]})</div>', unsafe_allow_html=True)
            for k in valid_keys: draw_bracket_card(k)

# --- ADMIN ---
with tab4:
    admin_auth = st.text_input("Kod Administratora:", type="password")
    if admin_auth == ADMIN_PIN:
        new_results = {}
        for k in ALL_KEYS:
            t1, t2 = BRACKET[k][0], BRACKET[k][1]
            curr = actual_res_db.get(k, "W toku")
            if t1 == "TBD" or t2 == "TBD": new_results[k] = curr; continue
            opts = ["W toku","4-0","4-1","4-2","4-3","3-4","2-4","1-4","0-4"]
            new_results[k] = st.selectbox(f"Wynik {t1}-{t2}", opts, index=opts.index(curr) if curr in opts else 0, key=f"adm_{k}")
        if st.button("Zatwierdź Wyniki"):
            st.session_state.results["OFFICIAL"] = new_results
            save_data(st.session_state.results, "oficjalne_wyniki.csv"); st.rerun()
