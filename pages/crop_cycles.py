# =============================================================
#  IoT Agricultural Monitoring System
#  Fichier : dashboard/pages/crop_cycles.py
#  Rôle    : Page 5 — Cycles cultures + rendement par culture
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from queries import (
    get_yield_per_crop,
    get_crop_cycles_gantt,
    get_active_crop_cycles,
)

# ─── COULEURS ─────────────────────────────────────────────────
NAVY   = "#1a2d4a"
ORANGE = "#f5a623"
GREEN  = "#22c55e"
RED    = "#ef4444"
GRAY   = "#6b7280"
BLUE   = "#60a5fa"

STATUS_COLORS = {
    "Growing":   {"bg": "#dcfce7", "text": "#16a34a", "border": "#86efac"},
    "Completed": {"bg": "#dbeafe", "text": "#1d4ed8", "border": "#93c5fd"},
    "Failed":    {"bg": "#fee2e2", "text": "#dc2626", "border": "#fca5a5"},
    "Planned":   {"bg": "#f3f4f6", "text": "#6b7280", "border": "#d1d5db"},
}

STATUS_ICONS = {
    "Growing":   "🌱",
    "Completed": "✅",
    "Failed":    "❌",
    "Planned":   "📅",
}


def show():

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:20px 28px;
                margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:22px; font-weight:700; color:#1a2d4a;'>
             Cycles de Cultures & Rendements
        </div>
        <div style='font-size:13px; color:#6b7280; margin-top:2px;'>
            Suivi des cycles, planning et analyse des rendements par culture
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chargement données ────────────────────────────────────
    try:
        df_yield   = get_yield_per_crop()
        df_gantt   = get_crop_cycles_gantt()
        df_active  = get_active_crop_cycles()
    except Exception as e:
        st.error(f"❌ Erreur connexion base de données : {e}")
        return

    # ── KPIs cultures ─────────────────────────────────────────
    n_growing   = len(df_gantt[df_gantt["status"] == "Growing"])   if not df_gantt.empty else 0
    n_completed = len(df_gantt[df_gantt["status"] == "Completed"]) if not df_gantt.empty else 0
    n_failed    = len(df_gantt[df_gantt["status"] == "Failed"])    if not df_gantt.empty else 0
    best_yield  = df_yield["avg_yield_per_ha"].max() if not df_yield.empty else 0
    best_crop   = df_yield.iloc[0]["cropname"] if not df_yield.empty else "—"

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {GREEN};'>
            <div style='font-size:10px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>🌱 En Cours</div>
            <div style='font-size:34px; font-weight:700; color:{NAVY};
                        margin-top:6px;'>{n_growing}</div>
            <div style='font-size:11px; color:#9ca3af; margin-top:2px;'>
                cycles actifs
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {BLUE};'>
            <div style='font-size:10px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>✅ Complétés</div>
            <div style='font-size:34px; font-weight:700; color:{NAVY};
                        margin-top:6px;'>{n_completed}</div>
            <div style='font-size:11px; color:#9ca3af; margin-top:2px;'>
                récoltes effectuées
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {RED};'>
            <div style='font-size:10px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>❌ Échoués</div>
            <div style='font-size:34px; font-weight:700; color:{NAVY};
                        margin-top:6px;'>{n_failed}</div>
            <div style='font-size:11px; color:#9ca3af; margin-top:2px;'>
                cycles non complétés
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {ORANGE};'>
            <div style='font-size:10px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>🏆 Meilleur Rendement</div>
            <div style='font-size:26px; font-weight:700; color:{NAVY};
                        margin-top:6px;'>{best_yield} t/ha</div>
            <div style='font-size:11px; color:{ORANGE}; margin-top:2px;
                        font-weight:600;'>
                {best_crop}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2 : Rendement par culture + Cycles actifs ─────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:24px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px; font-weight:600; color:#1a2d4a;
                        margin-bottom:4px;'>
                🏆 Rendement Moyen par Culture (tons/ha)
            </div>
            <div style='font-size:12px; color:#9ca3af; margin-bottom:16px;'>
                Analyse DB — cultures les plus productives sur toutes les saisons
            </div>
        """, unsafe_allow_html=True)

        if not df_yield.empty:
            fig_yield = go.Figure()

            # Barres rendement moyen
            fig_yield.add_trace(go.Bar(
                x=df_yield["cropname"],
                y=df_yield["avg_yield_per_ha"],
                name="Rendement moy. (t/ha)",
                marker=dict(
                    color=df_yield["avg_yield_per_ha"],
                    colorscale=[[0, "#dbeafe"], [0.5, NAVY], [1, ORANGE]],
                    showscale=False,
                ),
                text=df_yield["avg_yield_per_ha"],
                texttemplate="%{text:.1f} t/ha",
                textposition="outside",
            ))

            # Barres rendement total moyen
            fig_yield.add_trace(go.Bar(
                x=df_yield["cropname"],
                y=df_yield["avg_yield_tons"],
                name="Rendement moy. total (t)",
                marker_color=ORANGE,
                opacity=0.4,
                text=df_yield["avg_yield_tons"],
                texttemplate="%{text:.0f} t",
                textposition="outside",
            ))

            fig_yield.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                barmode="group",
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(size=11),
                ),
                xaxis=dict(showgrid=False, tickfont=dict(size=12)),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#f3f4f6",
                    tickfont=dict(size=11),
                ),
                hovermode="x unified",
            )
            st.plotly_chart(fig_yield, use_container_width=True, config={"displayModeBar": False})

            # Tableau détaillé
            df_yield_display = df_yield.copy()
            df_yield_display.columns = ["Culture", "Cycles", "Rend. moy. (t)", "Rend. moy. (t/ha)"]
            st.dataframe(df_yield_display, use_container_width=True, hide_index=True)

        else:
            st.info("Aucune donnée de rendement disponible.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:24px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px; font-weight:600; color:#1a2d4a;
                        margin-bottom:16px;'>
                🌱 Cycles en Cours
            </div>
        """, unsafe_allow_html=True)

        if not df_active.empty:
            for _, row in df_active.iterrows():
                planting  = pd.to_datetime(row["plantingdate"])
                expected  = pd.to_datetime(row["expectedharvestdate"])
                today     = pd.Timestamp.now()
                total_days = (expected - planting).days
                elapsed    = (today - planting).days
                progress   = min(100, max(0, int(100 * elapsed / total_days))) if total_days > 0 else 0
                days_left  = max(0, (expected - today).days)

                st.markdown(f"""
                <div style='background:#f8fafc; border-radius:10px; padding:14px;
                            margin-bottom:10px;
                            border-left:4px solid {GREEN};'>
                    <div style='display:flex; justify-content:space-between;
                                align-items:center; margin-bottom:8px;'>
                        <div>
                            <span style='font-size:13px; font-weight:600;
                                         color:{NAVY};'>
                                🌾 {row["field_name"]}
                            </span>
                            <span style='font-size:11px; color:{ORANGE};
                                         font-weight:600; margin-left:8px;'>
                                {row["cropname"]}
                            </span>
                        </div>
                        <span style='font-size:11px; color:#6b7280;'>
                            J-{days_left}
                        </span>
                    </div>
                    <div style='background:#e5e7eb; border-radius:999px; height:8px;
                                margin-bottom:6px;'>
                        <div style='background:{GREEN}; border-radius:999px;
                                    height:8px; width:{progress}%;
                                    transition: width 0.3s;'></div>
                    </div>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='font-size:10px; color:#9ca3af;'>
                            Semis : {planting.strftime("%d/%m/%Y")}
                        </span>
                        <span style='font-size:10px; color:#9ca3af;'>
                            {progress}% · Récolte : {expected.strftime("%d/%m/%Y")}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align:center; padding:40px 0; color:#6b7280;'>
                <div style='font-size:36px;'>🌾</div>
                <div style='font-size:14px; margin-top:8px;'>
                    Aucun cycle en cours
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GANTT PLANNING ────────────────────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:24px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:15px; font-weight:600; color:#1a2d4a;
                    margin-bottom:4px;'>
             Planning Cultures — Diagramme de Gantt
        </div>
        <div style='font-size:12px; color:#9ca3af; margin-bottom:16px;'>
            Semis → Récolte par champ et par culture
        </div>
    """, unsafe_allow_html=True)

    if not df_gantt.empty:
        df_gantt["start_date"] = pd.to_datetime(df_gantt["start_date"])
        df_gantt["end_date"]   = pd.to_datetime(df_gantt["end_date"])

        # Couleur par statut
        color_map = {
            "Growing":   GREEN,
            "Completed": BLUE,
            "Failed":    RED,
            "Planned":   GRAY,
        }

        fig_gantt = px.timeline(
            df_gantt,
            x_start="start_date",
            x_end="end_date",
            y="field_name",
            color="status",
            color_discrete_map=color_map,
            hover_data=["cropname", "yieldtons", "farm_name"],
            labels={
                "field_name": "Champ",
                "status":     "Statut",
                "cropname":   "Culture",
                "yieldtons":  "Rendement (t)",
            },
            text="cropname",
        )

        fig_gantt.update_traces(textposition="inside", insidetextanchor="middle")
        fig_gantt.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                font=dict(size=11),
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="#f3f4f6",
                tickfont=dict(size=11),
                title=None,
            ),
            yaxis=dict(
                tickfont=dict(size=11),
                title=None,
                autorange="reversed",
            ),
        )
        st.plotly_chart(fig_gantt, use_container_width=True, config={"displayModeBar": False})

        # Légende statuts
        leg_cols = st.columns(4)
        for i, (status, colors) in enumerate(STATUS_COLORS.items()):
            with leg_cols[i]:
                st.markdown(f"""
                <div style='background:{colors["bg"]}; border-radius:8px;
                            padding:8px 12px; text-align:center;
                            border:1px solid {colors["border"]};'>
                    <span style='font-size:13px;'>{STATUS_ICONS[status]}</span>
                    <span style='font-size:11px; font-weight:600;
                                 color:{colors["text"]}; margin-left:6px;'>
                        {status}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucun cycle de culture enregistré.")

    st.markdown("</div>", unsafe_allow_html=True)