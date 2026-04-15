import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURACJA ---
# Używamy daty z kontekstu: kwiecień 2026
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

# Rozbudowany CSS dla kolorów kafelków
st.markdown("""
    <style>
    .login-box { background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #555; margin-bottom: 25px; }
    
    /* Podstawowy styl kafelka (W toku / Domyślny) */
    .match-box { border: 1px solid #444; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: rgba(255, 255, 255, 0.05); transition: background-color 0.3s; }
    
    /* Kolory wynikowe */
    .res-exact { background-color: rgba(0, 200, 0, 0.2) !important; border-color: rgba(0, 255, 0, 0.5) !important; } /* Zielony: Idealny */
    .res-winner { background-color: rgba(0, 0, 200, 0.2) !important; border-color: rgba(0, 0, 255, 0.5) !important; } /* Niebieski: Tylko zwycięzca */
    .res-wrong { background-color: rgba(200, 0, 0, 0.2) !important; border-color: rgba(255, 0, 0, 0.5) !important; }  /* Czerwony: Błąd */

    .logo-bg { background-color: white; border-radius: 50%; padding: 5px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    
    /* Styl dla legendy */
    .legenda-item { display: inline-block; padding: 2px 10px; border-radius: 5px; margin-right: 10px; font-size: 0.8em; font-weight: bold; border: 1px solid #444; }
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
    """Zwraca liczbę punktów (0, 1, 2) oraz klasę CSS dla wyniku."""
    if actual_result == "W toku" or actual_result == "" or pd.isna(actual_result) or user_pick == "-":
        return 0, "" # Domyślny szary
    
    if user_pick == actual_result:
        return 2, "res-exact" # Zielony
    
    try:
        # Logika zwycięzcy: zakłada format "4-X" lub "X-4", gdzie X < 4.
        # Wygrywa ten, kto ma '4'.
        u_scores = user_pick.split("-")
        a_scores = actual_result.split("-")
        
        # Sprawdzamy czy format jest poprawny
        if len(u_scores) != 2 or len(a_scores) != 2: return 0, ""

        # Lewa drużyna wygrywa w typie użytkownika?
        u_left_wins = int(u_scores[0]) == 4
        # Lewa drużyna wygrywa w oficjalnym wyniku?
        a_left_wins = int(a_scores[0]) == 4
        
        if u_left_wins == a_left_wins:
            return 1, "res-winner" # Niebieski
    except Exception as e:
        print(f"Błąd punktacji dla typ:{user_pick} / wynik:{actual_result} - {e}")
        pass
        
    return 0, "res-wrong" # Czerwony

# Inicjalizacja baz
if 'db' not in st.session_state:
    st.session_state.db = load_data("wyniki.csv")
if 'results' not in st.session_state:
    st.session_state.results = load_data("oficjalne_wyniki.csv")
if 'logged_user' not in st.session_state:
    st.session_state.logged_user = None

st.title("🏀 NBA Playoff 2026")
now = datetime.now()
is_locked = now > START_TIME

tab1, tab2, tab3, tab4 = st.tabs(["🖋️ Twoje Typy", "🏆 Ranking", "📊 Drabinka Playoff", "⚙️ Admin"])

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
            save_data(st.session_state.db, "wyniki.csv")
            st.balloons()
            st.success("✅ Typy na NBA 2026 zapisane!")

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
            
            # Obliczamy punkty na potrzeby tabeli
            pts, _ = get_points_logic(u_pick, a_res)
            total_pts += pts
            
            # Widok typów (ukryty przed startem dla innych)
            if not is_locked and p != st.session_state.logged_user:
                player_row[match] = "🔒"
            else:
                player_row[match] = u_pick
        
        player_row["SUMA PKT"] = total_pts
        leaderboard.append(player_row)
    
    if leaderboard:
        df_leaderboard = pd.DataFrame(leaderboard).sort_values(by="SUMA PKT", ascending=False)
        st.dataframe(df_leaderboard, use_container_width=True)
    else:
        st.write("Brak danych do wyświetlenia rankingu.")

with tab3:
    st.subheader("📊 Drabinka Playoff NBA 2026")
    curr_user = st.session_state.logged_user
    actual_results_db = st.session_state.results.get("OFFICIAL", {})
    u_picks = st.session_state.db.get(curr_user, {}) if curr_user else {}
    
    if not curr_user:
        st.info("💡 Zaloguj się w zakładce 'Twoje Typy', aby zobaczyć podświetlenie swoich wyników w drabince.")

    # Legenda kolorów
    st.markdown("""
        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #444; border-radius: 5px;">
            <span style="font-weight: bold; margin-right: 15px;">Legenda (Twoje typy):</span>
            <span class="legenda-item res-exact">Idealny wynik (2 pkt)</span>
            <span class="legenda-item res-winner">Tylko zwycięzca (1 pkt)</span>
            <span class="legenda-item res-wrong">Błędny zwycięzca (0 pkt)</span>
            <span class="legenda-item match-box" style="display:inline; padding: 2px 10px;">W toku / Brak typu</span>
        </div>
    """, unsafe_allow_html=True)

    def bracket_card_dynamic(t1, seed1, t2, seed2):
        match_key = f"{t1} vs {t2}"
        my_pick = u_picks.get(match_key, "-")
        actual_res = actual_results_db.get(match_key, "W toku")
        
        # Logika podświetlenia: pobieramy tylko klasę CSS
        _, css_class = get_points_logic(my_pick, actual_res)
        
        # Przygotowanie tekstu oficjalnego wyniku
        status_text = f"Wynik: {actual_res}" if actual_res != "W toku" else "W toku"
        
        st.markdown(f"""
        <div class="match-box {css_class}">
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS[t1]}" width="35"></div><span style="margin-left: 10px; font-weight: bold;">({seed1}) {t1}</span></div>
            <div style="text-align: center; margin: 8px 0;">
                <span style="color: #bbb; font-size: 0.8em; background: rgba(0,0,0,0.5); padding: 2px 10px; border-radius: 10px; font-style: italic;">{status_text}</span>
                <br>
                <span style="color: #fff; font-size: 0.9em; font-weight: bold; background: #222; padding: 3px 12px; border-radius: 10px; display: inline-block; margin-top: 5px;">Twoje: {my_pick}</span>
            </div>
            <div style="display: flex; align-items: center;"><div class="logo-bg"><img src="{LOGOS[t2]}" width="35"></div><span style="margin-left: 10px; font-weight: bold;">({seed2}) {t2}</span></div>
        </div>
        """, unsafe_allow_html=True)

    c_e, _, c_w = st.columns([1, 0.1, 1])
    with c_e:
        st.markdown("#### 🔵 WSCHÓD")
        bracket_card_dynamic("Pistons", 1, "8 Seed", 8); bracket_card_dynamic("Cavaliers", 4, "Raptors", 5)
        st.markdown("<br>", unsafe_allow_html=True)
        bracket_card_dynamic("Knicks", 3, "Hawks", 6); bracket_card_dynamic("Celtics", 2, "7 Seed", 7)
    with c_w:
        st.markdown("#### 🔴 ZACHÓD")
        bracket_card_dynamic("Thunder", 1, "8 Seed", 8); bracket_card_dynamic("Lakers", 4, "Rockets", 5)
        st.markdown("<br>", unsafe_allow_html=True)
        bracket_card_dynamic("Nuggets", 3, "Timberwolves", 6); bracket_card_dynamic("Spurs", 2, "Trail Blazers", 7)

with tab4:
    st.subheader("⚙️ Panel Administratora")
    admin_auth = st.text_input("Kod:", type="password", key="admin_pwd")
    if admin_auth == ADMIN_PIN:
        st.success("Dostęp przyznany")
        
        st.markdown("### 🏆 Wpisz oficjalne wyniki meczów")
        st.info("Wybierz wynik, gdy seria się zakończy. 'W toku' nie przyznaje punktów i nie zmienia kolorów drabinki.")
        
        off_res = st.session_state.results.get("OFFICIAL", {})
        new_off_res = {}
        # Lista opcji: pierwsza drużyna musi mieć '4' lub druga musi mieć '4'.
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
            st.success("Wyniki zapisane! Punkty w tabeli i kolory w drabince zostały zaktualizowane.")
            st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Zarządzanie bazą")
        if st.session_state.db:
            df_admin = pd.DataFrame.from_dict(st.session_state.db, orient='index')
            st.dataframe(df_admin)
            csv_data = df_admin.to_csv().encode('utf-8')
            st.download_button(label="Pobierz backup typów (CSV)", data=csv_data, file_name="wyniki_nba_2026.csv", mime="text/csv")
