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
    "7 Seed": "https://via.placeholder.com/150/ffffff/000000?text=7+SEED"
}

SERIES = [
    "Thunder vs 8 Seed", "Lakers vs Rockets", "Nuggets vs Timberwolves", "Spurs vs Trail Blazers",
    "Pistons vs 8 Seed", "Cavaliers vs Raptors", "Knicks vs Hawks", "Celtics vs 7 Seed"
]

st.set_page_config(page_title="NBA Predictor 2026", page_icon="🏀", layout="wide")

st.markdown("""
    <style>
    .login-box { background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #555; margin-bottom: 25px; }
    
    .conf-container {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    
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
    
    h4 { text-align: center; margin-bottom: 20px !important; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

def load_data(filename="wyniki.csv"):
    if os.path.exists(filename):
        try: return pd.read_csv(filename, index_col=0, dtype=str).to_dict('index')
        except: return {}
    return {}

def save_data(data, filename="wyniki.csv"):
    pd.DataFrame.from_dict(data, orient='index').to_csv(filename)

def get_points_logic(user_pick, actual_result):
    if actual_result == "W toku" or actual_result == "" or pd.isna(actual_result) or user_pick == "-":
        return 0, "", "pts-normal"
    if user_pick == actual_result:
        return 5, "res-exact", "pts-exact"
    try:
        u_scores = user_pick.split("-")
        a_scores = actual_result.split("-")
        u_left_wins = int(u_scores[0]) == 4
        a_left_wins = int(a_scores[0]) == 4
        if u_left_wins == a_left_wins:
            return 3, "res-winner", "pts-winner"
    except: pass
    return 0, "res-wrong", "pts-wrong"

if 'db' not in st.session_state: st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state: st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state: st.session_state.logged_user = None

st.title("🏀 NBA Playoff 2026")
now = datetime.now()
is_locked = now > START_TIME

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

# --- TAB 1: TYPY ---
with tab1:
    if st.session_state.logged_user is None:
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("🔐 Zaloguj się")
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
                        if st.button("Zapisz i wejdź"):
                            if len(new_pwd) >= 3:
                                user_data["PIN"] = str(new_pwd)
                                st.session_state.db[user] = user_data
                                save_data(st.session_state.db, "wyniki.csv")
                                st.session_state.logged_user = user
                                st.rerun()
                    else:
                        pwd_input = st.text_input("Hasło:", type="password", key=f"login_{user}")
                        if st.button("Zaloguj"):
                            if pwd_input == saved_pwd:
                                st.session_state.logged_user = user
                                st.rerun()
                            else: st.error("Błędne hasło!")
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
            save_data(st.session_state.db, "wyniki.csv")
            st.balloons()
            st.success("✅ Typy zapisane!")

# --- TAB 2: RANKING ---
with tab2:
    st.subheader("Tabela Wyników NBA 2026")
    actual_results = st.session_state.results.get("OFFICIAL", {})
    leaderboard = []
    for p in PLAYERS:
        p_data = st.session_state.db.get(p, {})
        total_pts = 0
        player_row = {"Gracz": p}
        for match in SERIES:
            u_pick = p_data.get(match, "-")
            a_res = actual_results.get(match, "W toku")
            pts, _ , _ = get_points_logic(u_pick, a_res)
            total_pts += pts
            player_row[match] = "🔒" if (not is_locked and p != st.session_state.logged_user) else u_pick
        player_row["SUMA PKT"] = total_pts
        leaderboard.append(player_row)
    if leaderboard:
        df_leaderboard = pd.DataFrame(leaderboard).sort_values(by="SUMA PKT", ascending=False)
        st.dataframe(df_leaderboard, use_container_width=True)

# --- TAB 3: DRABINKA (Z WYBOREM KONFERENCJI) ---
with tab3:
    st.subheader("📊 Drabinka Playoff NBA 2026")
    
    # Przełącznik konferencji
    view_mode = st.radio("Wybierz widok:", ["Wszystko", "Wschód 🔵", "Zachód 🔴"], horizontal=True)
    
    curr_user = st.session_state.logged_user
    actual_results_db = st.session_state.results.get("OFFICIAL", {})
    u_picks = st.session_state.db.get(curr_user, {}) if curr_user else {}

    def render_bracket_card(t1, seed1, t2, seed2):
        match_key = f"{t1} vs {t2}"
        my_pick = u_picks.get(match_key, "-")
        actual_res = actual_results_db.get(match_key, "W toku")
        pts, css_box, css_pts = get_points_logic(my_pick, actual_res)
        status_display = "W toku" if actual_res == "W toku" else f"Wynik: {actual_res}"
        
        return f"""
        <div class="match-box {css_box}">
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS[t1]}" width="35"></div><span style="margin-left: 10px; font-weight: bold;">({seed1}) {t1}</span></div>
            <div style="text-align: center; margin: 8px 0;">
                <span style="color: #bbb; font-size: 0.8em; background: rgba(0,0,0,0.5); padding: 2px 10px; border-radius: 10px; font-style: italic;">{status_display}</span><br>
                <div style="margin-top: 5px;">
                    <span style="color: #fff; font-size: 0.9em; font-weight: bold; background: #222; padding: 3px 12px; border-radius: 10px; display: inline-block;">Twoje: {my_pick}</span>
                    <span class="pts-badge {css_pts}">+{pts} pkt</span>
                </div>
            </div>
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS[t2]}" width="35"></div><span style="margin-left: 10px; font-weight: bold;">({seed2}) {t2}</span></div>
        </div>
        """

    # Logika wyświetlania kolumn w zależności od wyboru
    if view_mode == "Wszystko":
        col_east, col_west = st.columns(2)
    elif view_mode == "Wschód 🔵":
        col_east, col_west = st.columns([1, 0.01]) # Schowaj zachód
    else:
        col_east, col_west = st.columns([0.01, 1]) # Schowaj wschód

    if view_mode != "Zachód 🔴":
        with col_east:
            st.markdown('<div class="conf-container"><h4>🔵 WSCHÓD</h4>', unsafe_allow_html=True)
            st.markdown(render_bracket_card("Pistons", 1, "8 Seed", 8), unsafe_allow_html=True)
            st.markdown(render_bracket_card("Cavaliers", 4, "Raptors", 5), unsafe_allow_html=True)
            st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
            st.markdown(render_bracket_card("Knicks", 3, "Hawks", 6), unsafe_allow_html=True)
            st.markdown(render_bracket_card("Celtics", 2, "7 Seed", 7), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if view_mode != "Wschód 🔵":
        with col_west:
            st.markdown('<div class="conf-container"><h4>🔴 ZACHÓD</h4>', unsafe_allow_html=True)
            st.markdown(render_bracket_card("Thunder", 1, "8 Seed", 8), unsafe_allow_html=True)
            st.markdown(render_bracket_card("Lakers", 4, "Rockets", 5), unsafe_allow_html=True)
            st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
            st.markdown(render_bracket_card("Nuggets", 3, "Timberwolves", 6), unsafe_allow_html=True)
            st.markdown(render_bracket_card("Spurs", 2, "Trail Blazers", 7), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: ADMIN ---
with tab4:
    st.subheader("⚙️ Panel Administratora")
    admin_auth = st.text_input("Kod:", type="password", key="admin_pwd")
    if admin_auth == ADMIN_PIN:
        st.success("Dostęp przyznany")
        off_res = st.session_state.results.get("OFFICIAL", {})
        new_off_res = {}
        options_off = ["W toku", "4-0", "4-1", "4-2", "4-3", "3-4", "2-4", "1-4", "0-4"]
        cols_off = st.columns(2)
        for i, match in enumerate(SERIES):
            current_off = off_res.get(match, "W toku")
            idx_off = options_off.index(current_off) if current_off in options_off else 0
            new_val = cols_off[i % 2].selectbox(f"Wynik: {match}", options_off, index=idx_off, key=f"off_{match}")
            new_off_res[match] = new_val
        if st.button("Zatwierdź oficjalne wyniki"):
            st.session_state.results["OFFICIAL"] = new_off_res
            save_data(st.session_state.results, "oficjalne_wyniki.csv")
            st.rerun()
