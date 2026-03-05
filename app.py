# =============================================================
#  IoT Agricultural Monitoring System
#  Fichier : dashboard/app.py
#  Rôle    : Point d'entrée Streamlit + sidebar + navigation
# =============================================================

import streamlit as st
from queries import (
    get_total_active_fields,
    get_avg_soil_moisture,
    get_water_usage_today,
    get_active_alerts_count,
    get_active_devices_count,
)

# ─── CONFIG PAGE ──────────────────────────────────────────────
st.set_page_config(
    page_title="IoT Agri Monitor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS GLOBAL (style dashboard bleu marine + orange) ────────
st.markdown("""
<style>
/* ── Imports Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset global ── */
* { font-family: 'Inter', sans-serif; }

/* ── Fond principal gris clair ── */
.stApp {
    background-color: #f0f2f5;
}

/* ── Sidebar bleu marine ── */
[data-testid="stSidebar"] {
    background-color: #1a2d4a !important;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebarNav"] {
    display: none;
}

/* ── Titres ── */
h1 { color: #1a2d4a !important; font-weight: 700 !important; }
h2 { color: #1a2d4a !important; font-weight: 600 !important; }
h3 { color: #1a2d4a !important; font-weight: 600 !important; }

/* ── Cartes KPI ── */
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-top: 4px solid #1a2d4a;
    margin-bottom: 16px;
}
.kpi-card.orange { border-top-color: #f5a623; }
.kpi-card.green  { border-top-color: #22c55e; }
.kpi-card.red    { border-top-color: #ef4444; }

.kpi-label {
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #1a2d4a;
    line-height: 1;
}
.kpi-icon {
    font-size: 28px;
    float: right;
    margin-top: -4px;
}
.kpi-sub {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 6px;
}

/* ── Conteneur graphique ── */
.chart-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

/* ── Bouton navigation sidebar ── */
.nav-btn {
    display: block;
    width: 100%;
    padding: 10px 16px;
    margin: 4px 0;
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #cbd5e1;
    font-size: 14px;
    text-align: left;
    cursor: pointer;
    transition: background 0.2s;
}
.nav-btn:hover, .nav-btn.active {
    background: rgba(255,255,255,0.12);
    color: white;
}

/* ── Badge alerte ── */
.badge-critical { background:#fee2e2; color:#dc2626; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:600; }
.badge-high     { background:#ffedd5; color:#ea580c; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:600; }
.badge-medium   { background:#fef9c3; color:#ca8a04; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:600; }
.badge-low      { background:#dcfce7; color:#16a34a; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:600; }

/* ── Divider sidebar ── */
.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.12);
    margin: 12px 0;
}

/* ── Streamlit metric override ── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #1a2d4a !important; font-size: 28px !important; font-weight: 700 !important; }

/* ── Boutons Streamlit ── */
.stButton > button {
    background-color: #1a2d4a;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    transition: background 0.2s;
}
.stButton > button:hover {
    background-color: #f5a623;
    color: white;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-radius: 8px;
    border-color: #e5e7eb;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}

/* ── Header page ── */
.page-header {
    background: white;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.page-title {
    font-size: 22px;
    font-weight: 700;
    color: #1a2d4a;
}
.page-subtitle {
    font-size: 13px;
    color: #6b7280;
    margin-top: 2px;
}

/* ── Status dot ── */
.dot-active   { width:8px; height:8px; border-radius:50%; background:#22c55e; display:inline-block; margin-right:6px; }
.dot-inactive { width:8px; height:8px; border-radius:50%; background:#ef4444; display:inline-block; margin-right:6px; }
.dot-warning  { width:8px; height:8px; border-radius:50%; background:#f5a623; display:inline-block; margin-right:6px; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "overview"


# ─── LOGIN PAGE ───────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:32px;'>
            <div style='font-size:48px;'>🌿</div>
            <h2 style='color:#1a2d4a; margin:8px 0 4px;'>IoT Agri Monitor</h2>
            <p style='color:#6b7280; font-size:14px;'>Connectez-vous pour accéder au dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style='background:white; padding:32px; border-radius:16px;
                         '>
            """, unsafe_allow_html=True)

            email    = st.text_input("📧 Email",    placeholder="john.soh@agrifarm.com")
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••")

            # Utilisateurs de démonstration
            DEMO_USERS = {
                "john.soh@agrifarm.com":        {"name": "John Soh",       "role": "Farm Manager",        "id": 1,  "password": "admin123"},
                "maria.alamine@agrifarm.com":   {"name": "Alamine Lopez",  "role": "Agronomist",          "id": 2,  "password": "agro123"},
                "moussa.diallo@agrifarm.com":   {"name": "Moussa Diallo",  "role": "IoT Systems Manager", "id": 3,  "password": "iot123"},
                "fatou.ndiaye@agrifarm.com":    {"name": "Fatou Ndiaye",   "role": "Data Analyst",        "id": 4,  "password": "data123"},
            }

            if st.button("Se connecter", use_container_width=True):
                if email in DEMO_USERS and DEMO_USERS[email]["password"] == password:
                    user = DEMO_USERS[email]
                    st.session_state.logged_in = True
                    st.session_state.user_name = user["name"]
                    st.session_state.user_role = user["role"]
                    st.session_state.user_id   = user["id"]
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect.")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align:center; margin-top:20px; color:#9ca3af; font-size:12px;'>
            Comptes démo : john.soh@agrifarm.com / admin123
        </div>
        """, unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        # Logo + titre
        st.markdown("""
        <div style='text-align:center; padding: 20px 0 16px;'>
            <div style='font-size:40px;'>🌿</div>
            <div style='font-size:16px; font-weight:700; color:white; margin-top:6px;'>IoT Agri Monitor</div>
            <div style='font-size:11px; color:#94a3b8; margin-top:2px;'>Agricultural Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

        # Profil utilisateur
        st.markdown(f"""
        <div style='text-align:center; padding:12px 0;'>
            <div style='width:56px; height:56px; border-radius:50%;
                        background:rgba(245,166,35,0.2); border:2px solid #f5a623;
                        margin:0 auto 10px; display:flex; align-items:center;
                        justify-content:center; font-size:22px;'>
                👤
            </div>
            <div style='font-size:15px; font-weight:600; color:white;'>
                {st.session_state.user_name}
            </div>
            <div style='font-size:11px; color:#94a3b8; margin-top:3px;
                        background:rgba(245,166,35,0.15); border-radius:999px;
                        padding:2px 10px; display:inline-block;'>
                {st.session_state.user_role}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

        # Navigation
        nav_items = [
            ("overview",   "", "Overview"),
            ("moisture",   "", "Humidité Sol"),
            ("irrigation", "", "Irrigation"),
            ("alerts",     "", "Alertes"),
            ("cultures",   "", "Cycles Cultures"),
        ]

        for page_key, icon, label in nav_items:
            is_active = st.session_state.page == page_key
            style = "background:rgba(255,255,255,0.12); color:white;" if is_active else "color:#94a3b8;"
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
            ):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

        # KPIs rapides dans la sidebar
        try:
            alerts_count  = get_active_alerts_count()
            devices_count = get_active_devices_count()
            st.markdown(f"""
            <div style='padding:0 4px;'>
                <div style='font-size:10px; color:#64748b; letter-spacing:1px;
                            text-transform:uppercase; margin-bottom:10px;'>
                    Statut Rapide
                </div>
                <div style='display:flex; justify-content:space-between;
                            background:rgba(255,255,255,0.06); border-radius:8px;
                            padding:10px 14px; margin-bottom:8px;'>
                    <span style='font-size:12px; color:#94a3b8;'>🚨 Alertes ouvertes</span>
                    <span style='font-size:13px; font-weight:700;
                                 color:{"#ef4444" if alerts_count > 0 else "#22c55e"};'>
                        {alerts_count}
                    </span>
                </div>
                <div style='display:flex; justify-content:space-between;
                            background:rgba(255,255,255,0.06); border-radius:8px;
                            padding:10px 14px;'>
                    <span style='font-size:12px; color:#94a3b8;'>📡 Devices actifs</span>
                    <span style='font-size:13px; font-weight:700; color:#22c55e;'>
                        {devices_count}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.markdown("""
            <div style='background:rgba(239,68,68,0.1); border-radius:8px; padding:10px;
                        font-size:11px; color:#fca5a5; text-align:center;'>
                ⚠️ Connexion DB requise
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

        # Auto-refresh
        st.markdown("""
        <div style='font-size:11px; color:#64748b; text-align:center; margin-bottom:8px;'>
            🔄 Refresh automatique : 60s
        </div>
        """, unsafe_allow_html=True)

        # Déconnexion
        if st.button("🚪  Se déconnecter", use_container_width=True):
            for key in ["logged_in", "user_name", "user_role", "user_id", "page"]:
                del st.session_state[key]
            st.rerun()


# ─── ROUTING ──────────────────────────────────────────────────
def route():
    page = st.session_state.get("page", "overview")
    if page == "overview":
        from pages import overview
        overview.show()
    elif page == "moisture":
        from pages import moisture
        moisture.show()
    elif page == "irrigation":
        from pages import irrigation
        irrigation.show()
    elif page == "alerts":
        from pages import alerts
        alerts.show()
    elif page == "cultures":
        from pages import crop_cycles
        crop_cycles.show()


# ─── MAIN ─────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        show_sidebar()
        route()


if __name__ == "__main__":
    main()