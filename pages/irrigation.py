# =============================================================
#  IoT Agricultural Monitoring System
#  Fichier : dashboard/pages/irrigation.py
#  Rôle    : Page 3 — Événements irrigation + overlay humidité
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from queries import (
    get_irrigation_events,
    get_water_usage_by_field,
    get_irrigation_overlay,
    get_fields_list,
)

# ─── COULEURS ─────────────────────────────────────────────────
NAVY   = "#1a2d4a"
ORANGE = "#f5a623"
GREEN  = "#22c55e"
RED    = "#ef4444"
BLUE   = "#60a5fa"
GRAY   = "#6b7280"


def show():

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:20px 28px;
                margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:22px; font-weight:700; color:#1a2d4a;'>
            Irrigation & Consommation Eau
        </div>
        <div style='font-size:13px; color:#6b7280; margin-top:2px;'>
            Suivi des événements d'irrigation et corrélation avec l'humidité sol
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filtres ───────────────────────────────────────────────
    try:
        df_fields = get_fields_list()
        field_options = {"Tous les champs": None}
        for _, row in df_fields.iterrows():
            label = f"{row['field_name']} ({row['farm_name']})"
            field_options[label] = int(row["fieldid"])
    except Exception as e:
        st.error(f"❌ Erreur chargement champs : {e}")
        return

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        selected_label = st.selectbox("🌾 Filtrer par champ", options=list(field_options.keys()))
    with col_f2:
        filter_auto = st.selectbox("⚙️ Type d'irrigation", ["Tous", "Automatique", "Manuel"])

    selected_field_id = field_options[selected_label]

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPIs IRRIGATION ───────────────────────────────────────
    try:
        df_events = get_irrigation_events(field_id=selected_field_id)

        # Filtre automatique/manuel
        if filter_auto == "Automatique":
            df_events = df_events[df_events["irrigautomated"] == True]
        elif filter_auto == "Manuel":
            df_events = df_events[df_events["irrigautomated"] == False]

        total_volume    = df_events["volume_m3"].sum() if not df_events.empty else 0
        total_events    = len(df_events)
        avg_volume      = round(df_events["volume_m3"].mean(), 1) if not df_events.empty else 0
        auto_pct        = round(
            100 * df_events["irrigautomated"].sum() / total_events, 0
        ) if total_events > 0 else 0

    except Exception as e:
        st.error(f"Erreur chargement irrigation : {e}")
        return

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {NAVY};'>
            <div style='font-size:11px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>Volume Total</div>
            <div style='display:flex; align-items:center;
                        justify-content:space-between; margin-top:8px;'>
                <div style='font-size:30px; font-weight:700; color:{NAVY};'>
                    {total_volume:.0f}
                </div>
                <div style='font-size:24px;'>💧</div>
            </div>
            <div style='font-size:11px; color:#9ca3af; margin-top:4px;'>m³ consommés</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {ORANGE};'>
            <div style='font-size:11px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>Événements</div>
            <div style='display:flex; align-items:center;
                        justify-content:space-between; margin-top:8px;'>
                <div style='font-size:30px; font-weight:700; color:{NAVY};'>
                    {total_events}
                </div>
                <div style='font-size:24px;'>📋</div>
            </div>
            <div style='font-size:11px; color:#9ca3af; margin-top:4px;'>irrigations enregistrées</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {BLUE};'>
            <div style='font-size:11px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>Volume Moyen</div>
            <div style='display:flex; align-items:center;
                        justify-content:space-between; margin-top:8px;'>
                <div style='font-size:30px; font-weight:700; color:{NAVY};'>
                    {avg_volume}
                </div>
                <div style='font-size:24px;'>📊</div>
            </div>
            <div style='font-size:11px; color:#9ca3af; margin-top:4px;'>m³ par événement</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {GREEN};'>
            <div style='font-size:11px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>Automatisé</div>
            <div style='display:flex; align-items:center;
                        justify-content:space-between; margin-top:8px;'>
                <div style='font-size:30px; font-weight:700; color:{NAVY};'>
                    {auto_pct:.0f}%
                </div>
                <div style='font-size:24px;'>🤖</div>
            </div>
            <div style='font-size:11px; color:#9ca3af; margin-top:4px;'>irrigations automatiques</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── OVERLAY HUMIDITÉ + IRRIGATION ─────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:24px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:20px;'>
        <div style='font-size:15px; font-weight:600; color:#1a2d4a; margin-bottom:4px;'>
             Humidité Sol + Événements Irrigation (Overlay)
        </div>
        <div style='font-size:12px; color:#9ca3af; margin-bottom:16px;'>
            Corrélation entre arrosage et évolution de l'humidité — 30 jours
        </div>
    """, unsafe_allow_html=True)

    try:
        df_overlay = get_irrigation_overlay(field_id=selected_field_id)

        if not df_overlay.empty:
            df_overlay["date"] = pd.to_datetime(df_overlay["date"])

            # Agréger si plusieurs champs
            df_agg = df_overlay.groupby("date").agg(
                avg_moisture=("avg_moisture", "mean"),
                water_volume=("water_volume", "sum"),
            ).reset_index()

            fig = go.Figure()

            # Barres irrigation (axe secondaire)
            fig.add_trace(go.Bar(
                x=df_agg["date"],
                y=df_agg["water_volume"],
                name="Volume irrigation (m³)",
                marker_color=BLUE,
                opacity=0.5,
                yaxis="y2",
            ))

            # Courbe humidité (axe principal)
            fig.add_trace(go.Scatter(
                x=df_agg["date"],
                y=df_agg["avg_moisture"],
                name="Humidité sol (%)",
                mode="lines+markers",
                line=dict(color=NAVY, width=2.5),
                marker=dict(size=5),
                fill="tozeroy",
                fillcolor="rgba(26,45,74,0.06)",
            ))

            # Zone optimale
            fig.add_hrect(
                y0=20, y1=40,
                fillcolor=GREEN, opacity=0.06,
                line_width=1, line_color=GREEN,
                annotation_text="Zone optimale",
                annotation_position="top left",
                annotation_font=dict(size=10, color=GREEN),
            )

            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=340,
                margin=dict(l=0, r=60, t=10, b=0),
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(size=11),
                ),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11, color=GRAY),
                    title=None,
                ),
                yaxis=dict(
    showgrid=True,
    gridcolor="#f3f4f6",
    tickfont=dict(size=11, color=GRAY),
    ticksuffix="%",
    title=dict(text="Humidité (%)", font=dict(size=11, color=NAVY)),
    range=[0, 70],
    side="left",
),
yaxis2=dict(
    tickfont=dict(size=11, color=BLUE),
    ticksuffix=" m³",
    title=dict(text="Volume irrigation (m³)", font=dict(size=11, color=BLUE)),
    overlaying="y",
    side="right",
    showgrid=False,
    range=[0, df_agg["water_volume"].max() * 4 if df_agg["water_volume"].max() > 0 else 100],
),
                hovermode="x unified",
                barmode="overlay",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Aucune donnée d'overlay disponible.")

    except Exception as e:
        st.error(f"Erreur overlay : {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── WATER USAGE PAR CHAMP ─────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:24px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px; font-weight:600; color:#1a2d4a; margin-bottom:16px;'>
                🌾 Volume Eau par Champ (m³)
            </div>
        """, unsafe_allow_html=True)

        try:
            df_usage = get_water_usage_by_field()
            if not df_usage.empty:
                fig2 = px.bar(
                    df_usage,
                    x="field_name",
                    y="total_volume_m3",
                    color="farm_name",
                    color_discrete_sequence=[NAVY, ORANGE],
                    labels={
                        "total_volume_m3": "Volume (m³)",
                        "field_name": "Champ",
                        "farm_name": "Ferme",
                    },
                    text="total_volume_m3",
                )
                fig2.update_traces(texttemplate="%{text:.0f}", textposition="outside")
                fig2.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    height=280,
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(font=dict(size=11)),
                    xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="#f3f4f6",
                        tickfont=dict(size=11),
                        ticksuffix=" m³",
                    ),
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        except Exception as e:
            st.error(f"Erreur : {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:24px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px; font-weight:600; color:#1a2d4a; margin-bottom:16px;'>
                 Derniers Événements d'Irrigation
            </div>
        """, unsafe_allow_html=True)

        try:
            if not df_events.empty:
                df_display = df_events[[
                    "field_name", "start_time", "volume_m3", "duration_hours", "irrigautomated"
                ]].copy()
                df_display.columns = ["Champ", "Début", "Volume (m³)", "Durée (h)", "Auto"]
                df_display["Début"]     = pd.to_datetime(df_display["Début"]).dt.strftime("%d/%m %H:%M")
                df_display["Durée (h)"] = pd.to_numeric(df_display["Durée (h)"], errors="coerce").round(1).fillna(0)
                df_display["Volume (m³)"] = pd.to_numeric(df_display["Volume (m³)"], errors="coerce").round(1).fillna(0)
                df_display["Auto"]      = df_display["Auto"].map({True: "✅", False: "👤"})
                df_display = df_display.head(10)

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    height=280,
                )
            else:
                st.info("Aucun événement d'irrigation enregistré.")
        except Exception as e:
            st.error(f"Erreur : {e}")

        st.markdown("</div>", unsafe_allow_html=True)