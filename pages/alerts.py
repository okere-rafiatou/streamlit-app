# =============================================================
#  IoT Agricultural Monitoring System
#  Fichier : dashboard/pages/alerts.py
#  Rôle    : Page 4 — Gestion alertes + anomalies capteurs
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from queries import (
    get_open_alerts,
    get_alerts_by_severity,
    get_anomaly_frequency_by_field,
    resolve_alert,
)

# ─── COULEURS ─────────────────────────────────────────────────
NAVY   = "#1a2d4a"
ORANGE = "#f5a623"
GREEN  = "#22c55e"
RED    = "#ef4444"
GRAY   = "#6b7280"

SEVERITY_COLORS = {
    "Critical": {"bg": "#fee2e2", "text": "#dc2626", "border": "#fca5a5"},
    "High":     {"bg": "#ffedd5", "text": "#ea580c", "border": "#fdba74"},
    "Medium":   {"bg": "#fef9c3", "text": "#ca8a04", "border": "#fde047"},
    "Low":      {"bg": "#dcfce7", "text": "#16a34a", "border": "#86efac"},
}

SEVERITY_ICONS = {
    "Critical": "🔴",
    "High":     "🟠",
    "Medium":   "🟡",
    "Low":      "🟢",
}


def show():

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:20px 28px;
                margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:22px; font-weight:700; color:#1a2d4a;'>
            🚨 Gestion des Alertes
        </div>
        <div style='font-size:13px; color:#6b7280; margin-top:2px;'>
            Alertes actives, historique et fréquence d'anomalies par champ
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chargement données ────────────────────────────────────
    try:
        df_alerts   = get_open_alerts()
        df_severity = get_alerts_by_severity()
        df_anomaly  = get_anomaly_frequency_by_field()
    except Exception as e:
        st.error(f"❌ Erreur connexion base de données : {e}")
        return

    # ── KPIs alertes ──────────────────────────────────────────
    total      = len(df_alerts)
    n_critical = len(df_alerts[df_alerts["severity"] == "Critical"]) if not df_alerts.empty else 0
    n_high     = len(df_alerts[df_alerts["severity"] == "High"])     if not df_alerts.empty else 0
    n_medium   = len(df_alerts[df_alerts["severity"] == "Medium"])   if not df_alerts.empty else 0
    n_low      = len(df_alerts[df_alerts["severity"] == "Low"])      if not df_alerts.empty else 0

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid {NAVY};'>
            <div style='font-size:10px; color:#6b7280; text-transform:uppercase;
                        letter-spacing:1px;'>Total Actives</div>
            <div style='font-size:34px; font-weight:700; color:{NAVY};
                        margin-top:6px;'>{total}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div style='background:#fee2e2; border-radius:12px; padding:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid #dc2626;'>
            <div style='font-size:10px; color:#dc2626; text-transform:uppercase;
                        letter-spacing:1px;'>🔴 Critical</div>
            <div style='font-size:34px; font-weight:700; color:#dc2626;
                        margin-top:6px;'>{n_critical}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div style='background:#ffedd5; border-radius:12px; padding:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid #ea580c;'>
            <div style='font-size:10px; color:#ea580c; text-transform:uppercase;
                        letter-spacing:1px;'>🟠 High</div>
            <div style='font-size:34px; font-weight:700; color:#ea580c;
                        margin-top:6px;'>{n_high}</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div style='background:#fef9c3; border-radius:12px; padding:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid #ca8a04;'>
            <div style='font-size:10px; color:#ca8a04; text-transform:uppercase;
                        letter-spacing:1px;'>🟡 Medium</div>
            <div style='font-size:34px; font-weight:700; color:#ca8a04;
                        margin-top:6px;'>{n_medium}</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div style='background:#dcfce7; border-radius:12px; padding:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-top:4px solid #16a34a;'>
            <div style='font-size:10px; color:#16a34a; text-transform:uppercase;
                        letter-spacing:1px;'>🟢 Low</div>
            <div style='font-size:34px; font-weight:700; color:#16a34a;
                        margin-top:6px;'>{n_low}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2 : Liste alertes + Donut ─────────────────────────
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:24px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px; font-weight:600; color:#1a2d4a;
                        margin-bottom:16px;'>
                📋 Alertes Actives
            </div>
        """, unsafe_allow_html=True)

        # Filtre sévérité
        col_fil1, col_fil2 = st.columns([1, 2])
        with col_fil1:
            filter_sev = st.selectbox(
                "Filtrer par sévérité",
                ["Toutes", "Critical", "High", "Medium", "Low"],
                label_visibility="collapsed",
            )

        if not df_alerts.empty:
            df_show = df_alerts.copy()
            if filter_sev != "Toutes":
                df_show = df_show[df_show["severity"] == filter_sev]

            if df_show.empty:
                st.markdown("""
                <div style='text-align:center; padding:40px; color:#22c55e;'>
                    <div style='font-size:36px;'>✅</div>
                    <div style='font-size:14px; margin-top:8px;'>
                        Aucune alerte pour ce filtre
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Affichage carte par alerte
                for _, row in df_show.iterrows():
                    sev    = row["severity"]
                    colors = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["Low"])
                    icon   = SEVERITY_ICONS.get(sev, "⚪")
                    date_str = pd.to_datetime(row["createdat"]).strftime("%d/%m/%Y %H:%M")

                    col_card, col_btn = st.columns([5, 1])
                    with col_card:
                        st.markdown(f"""
                        <div style='background:{colors["bg"]}; border-radius:10px;
                                    padding:14px 16px; margin-bottom:8px;
                                    border-left:4px solid {colors["border"]};'>
                            <div style='display:flex; align-items:center;
                                        justify-content:space-between;'>
                                <div>
                                    <span style='font-size:13px; font-weight:600;
                                                 color:{colors["text"]};'>
                                        {icon} {row["alerttype"]}
                                    </span>
                                    <span style='font-size:11px; color:#6b7280;
                                                 margin-left:10px;'>
                                        {row["field_name"]} · {row["farm_name"]}
                                    </span>
                                </div>
                                <span style='font-size:10px; color:#9ca3af;'>
                                    {date_str}
                                </span>
                            </div>
                            <div style='font-size:12px; color:#374151;
                                        margin-top:6px;'>
                                {row["message"]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_btn:
                        # Seul Farm Manager peut résoudre
                        if st.session_state.get("user_role") in ["Farm Manager", "Agronomist"]:
                            if st.button("✅", key=f"resolve_{row['alertid']}", help="Marquer comme résolu"):
                                try:
                                    resolve_alert(
                                        alert_id=int(row["alertid"]),
                                        user_id=int(st.session_state.get("user_id", 1))
                                    )
                                    st.success("Alerte résolue !")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erreur : {e}")
        else:
            st.markdown("""
            <div style='text-align:center; padding:60px 0; color:#22c55e;'>
                <div style='font-size:48px;'>✅</div>
                <div style='font-size:16px; font-weight:600; margin-top:12px;
                             color:#1a2d4a;'>
                    Aucune alerte active
                </div>
                <div style='font-size:13px; color:#6b7280; margin-top:4px;'>
                    Tous les systèmes fonctionnent normalement
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_side:
        # Donut sévérité
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:24px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:16px;'>
            <div style='font-size:14px; font-weight:600; color:#1a2d4a;
                        margin-bottom:12px;'>
                Répartition par Sévérité
            </div>
        """, unsafe_allow_html=True)

        if not df_severity.empty:
            colors_donut = {
                "Critical": "#dc2626",
                "High":     "#f5a623",
                "Medium":   "#eab308",
                "Low":      "#22c55e",
            }
            fig_donut = go.Figure(data=[go.Pie(
                labels=df_severity["severity"],
                values=df_severity["count"],
                hole=0.55,
                marker=dict(colors=[colors_donut.get(s, GRAY) for s in df_severity["severity"]]),
                textinfo="label+percent",
                textfont=dict(size=11),
            )])
            fig_donut.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=0, r=0, t=0, b=0),
                height=220,
                showlegend=False,
                annotations=[dict(
                    text=f"<b>{total}</b>",
                    x=0.5, y=0.5,
                    font=dict(size=18, color=NAVY),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("""
            <div style='text-align:center; padding:40px 0; color:#22c55e;'>
                <div style='font-size:32px;'>✅</div>
                <div style='font-size:13px; margin-top:8px;'>Aucune alerte</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Types d'alertes
        if not df_alerts.empty:
            st.markdown("""
            <div style='background:white; border-radius:12px; padding:20px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
                <div style='font-size:14px; font-weight:600; color:#1a2d4a;
                            margin-bottom:12px;'>
                    Types d'Alertes
                </div>
            """, unsafe_allow_html=True)

            type_counts = df_alerts.groupby("alerttype").size().reset_index(name="count")
            type_counts = type_counts.sort_values("count", ascending=False)

            for _, row in type_counts.iterrows():
                pct = int(100 * row["count"] / total) if total > 0 else 0
                st.markdown(f"""
                <div style='margin-bottom:10px;'>
                    <div style='display:flex; justify-content:space-between;
                                margin-bottom:4px;'>
                        <span style='font-size:11px; color:#374151;'>{row["alerttype"]}</span>
                        <span style='font-size:11px; font-weight:600;
                                     color:{NAVY};'>{row["count"]}</span>
                    </div>
                    <div style='background:#f3f4f6; border-radius:999px; height:6px;'>
                        <div style='background:{ORANGE}; border-radius:999px;
                                    height:6px; width:{pct}%;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ANOMALIES PAR CHAMP ───────────────────────────────────
    st.markdown("""
    <div style='background:white; border-radius:12px; padding:24px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <div style='font-size:15px; font-weight:600; color:#1a2d4a; margin-bottom:4px;'>
            ⚠️ Fréquence d'Anomalies Capteurs par Champ
        </div>
        <div style='font-size:12px; color:#9ca3af; margin-bottom:16px;'>
            Analyse DB — Quels champs ont la plus haute fréquence d'anomalies ?
        </div>
    """, unsafe_allow_html=True)

    if not df_anomaly.empty:
        col_chart, col_table = st.columns([3, 2])

        with col_chart:
            fig_ano = px.bar(
                df_anomaly,
                x="field_name",
                y="anomaly_count",
                color="anomaly_count",
                color_continuous_scale=[[0, "#fef9c3"], [0.5, ORANGE], [1, RED]],
                labels={"anomaly_count": "Anomalies", "field_name": "Champ"},
                text="anomaly_count",
            )
            fig_ano.update_traces(texttemplate="%{text}", textposition="outside")
            fig_ano.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=280,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                coloraxis_showscale=False,
                xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#f3f4f6",
                    tickfont=dict(size=11),
                ),
            )
            st.plotly_chart(fig_ano, use_container_width=True, config={"displayModeBar": False})

        with col_table:
            df_ano_display = df_anomaly[["field_name", "farm_name", "anomaly_count", "last_anomaly"]].copy()
            df_ano_display.columns = ["Champ", "Ferme", "Anomalies", "Dernière"]
            df_ano_display["Dernière"] = pd.to_datetime(
                df_ano_display["Dernière"]
            ).dt.strftime("%d/%m %H:%M")

            st.dataframe(
                df_ano_display,
                use_container_width=True,
                hide_index=True,
                height=280,
            )
    else:
        st.markdown("""
        <div style='text-align:center; padding:40px 0; color:#22c55e;'>
            <div style='font-size:36px;'>✅</div>
            <div style='font-size:14px; margin-top:8px;'>Aucune anomalie détectée</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)