import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from queries import (
    get_moisture_last_30_days,
    get_temperature_trend,
    get_fields_list,
    get_active_alerts_count, # Ajoute ces imports si dispo
    get_active_devices_count
)

# ─── COULEURS ─────────────────────────────────────────────────
NAVY   = "#1a2d4a"
BLUE   = "#3b82f6"
ORANGE = "#f5a623"
GREEN  = "#22c55e"
RED    = "#ef4444"
GRAY   = "#6b7280"

# Fonction pour convertir HEX en RGBA pour Plotly
def hex_to_rgba(hex_color, opacity=0.1):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    rgb = tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{opacity})'

# La fonction de carte harmonisée (la même que Page 1)
def kpi_card(title, value, unit, icon, color, subtext):
    return f"""
    <div style="background:white; border-radius:15px; box-shadow:0 4px 10px rgba(0,0,0,0.05); 
                height:160px; position:relative; display:flex; flex-direction:column; padding:15px; border:1px solid #f0f2f5;">
        <div style="position:absolute; top:0; left:0; right:0; height:6px; background-color:{color}; border-radius:15px 15px 0 0;"></div>
        <div style="height:40px; font-size:11px; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.8px; display:flex; align-items:center;">
            {title}
        </div>
        <div style="flex-grow:1; display:flex; align-items:center; justify-content:space-between;">
            <div style="font-size:30px; font-weight:800; color:#1a2d4a;">{value}<span style="font-size:16px;">{unit}</span></div>
            <div style="font-size:30px;">{icon}</div>
        </div>
        <div style="font-size:12px; color:#9ca3af; margin-top:5px;">{subtext}</div>
    </div>
    """

def show():
    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:20px 28px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:22px; font-weight:700; color:#1a2d4a;'> Humidité Sol & Température</div>
        <div style='font-size:13px; color:#6b7280; margin-top:2px;'>Analyse approfondie et tendances par secteur</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chargement des données ───────────────────────────────
    try:
        df_fields = get_fields_list()
        active_alerts = get_active_alerts_count()
        active_devices = get_active_devices_count()
    except:
        st.error("Erreur de base de données")
        return

    # ── Filtres ───────────────────────────────────────────────
    field_options = {"Tous les champs": None}
    for _, row in df_fields.iterrows():
        label = f"{row['field_name']} ({row['farm_name']})"
        field_options[label] = int(row["fieldid"])

    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        selected_field_label = st.selectbox("🌾 Filtrer par champ", options=list(field_options.keys()))
    with col_f2:
        days_options = {"30 jours": 30, "15 jours": 15, "7 jours": 7}
        selected_days = days_options[st.selectbox("📅 Période", options=list(days_options.keys()))]
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        show_optimal = st.checkbox("Zone optimale", value=True)

    selected_field_id = field_options[selected_field_label]
    
    # ── TOP KPIs (Même look que Page 1) ──────────────────────
    df_moist = get_moisture_last_30_days(field_id=selected_field_id)
    avg_moist_val = round(df_moist["avg_moisture"].mean(), 1) if not df_moist.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card("Humidité Moy.", f"{avg_moist_val}", "%", "💧", BLUE, "moyenne période"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Alertes", active_alerts, "", "🚨", RED if active_alerts > 0 else GREEN, "non résolues"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Capteurs", active_devices, "", "📡", NAVY, "en ligne"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Champs", len(df_fields), "", "🌾", ORANGE, "configurés"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("Système", "Auto", "", "🤖", GREEN, "Irrigation ON"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GRAPHIQUE HUMIDITÉ ────────────────────────────────────
    st.markdown("""<div style='background:white; border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:15px; font-weight:600; color:#1a2d4a;'> Évolution Humidité Sol (%)</div>""", unsafe_allow_html=True)

    if not df_moist.empty:
        fig = go.Figure()
        colors_list = [NAVY, BLUE, ORANGE, GREEN, "#6366f1"]
        
        for i, field in enumerate(df_moist["field_name"].unique()):
            df_f = df_moist[df_moist["field_name"] == field]
            c = colors_list[i % len(colors_list)]
            fig.add_trace(go.Scatter(
                x=df_f["date"], y=df_f["avg_moisture"], name=field,
                mode="lines", line=dict(color=c, width=3),
                fill="tozeroy", fillcolor=hex_to_rgba(c, 0.08) # ICI LA CORRECTION
            ))

        if show_optimal:
            fig.add_hrect(y0=20, y1=40, fillcolor=GREEN, opacity=0.05, line_width=0, annotation_text="ZONE OPTIMALE")
            
        fig.update_layout(plot_bgcolor="white", height=350, margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STATS PAR CHAMP (Harmonisées) ──────────────────────────
    if not df_moist.empty:
        st.markdown("<div style='font-weight:600; color:#1a2d4a; margin-bottom:15px;'> Statistiques Détaillées par Champ</div>", unsafe_allow_html=True)
        unique_fields = df_moist["field_name"].unique()
        cols = st.columns(len(unique_fields))
        
        for i, field in enumerate(unique_fields):
            df_f = df_moist[df_moist["field_name"] == field]
            f_avg = round(df_f["avg_moisture"].mean(), 1)
            f_min = round(df_f["avg_moisture"].min(), 1)
            f_max = round(df_f["avg_moisture"].max(), 1)
            
            with cols[i]:
                st.markdown(f"""
                <div style='background:white; border-radius:12px; padding:15px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border-top:4px solid {BLUE if f_avg > 20 else RED};'>
                    <div style='font-size:12px; font-weight:700; color:#1a2d4a; margin-bottom:10px;'>{field}</div>
                    <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                        <span style='color:#6b7280; font-size:11px;'>Moyenne</span>
                        <span style='font-weight:700; color:{BLUE};'>{f_avg}%</span>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#6b7280; font-size:11px;'>Min/Max</span>
                        <span style='font-size:11px;'>{f_min}% - {f_max}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TEMPÉRATURE ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style='background:white; border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:15px; font-weight:600; color:#1a2d4a;'> Tendance Température Air (°C)</div>""", unsafe_allow_html=True)
    
    df_temp = get_temperature_trend(days=selected_days)
    if not df_temp.empty:
        fig2 = px.line(df_temp, x="date", y="temp_avg", line_shape="spline")
        fig2.update_traces(line_color=NAVY, fill='tozeroy', fillcolor='rgba(26, 45, 74, 0.05)')
        fig2.update_layout(plot_bgcolor="white", height=250, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)