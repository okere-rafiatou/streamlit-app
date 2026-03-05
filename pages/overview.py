# =============================================================
#  IoT Agricultural Monitoring System
#  Fichier : dashboard/pages/overview.py
# =============================================================

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from queries import (
    get_total_active_fields,
    get_avg_soil_moisture,
    get_water_usage_today,
    get_active_alerts_count,
    get_yield_projection,
    get_active_devices_count,
    get_alerts_by_severity,
    get_moisture_last_30_days,
    get_anomaly_frequency_by_field,
    get_water_usage_by_field,
)

NAVY   = "#1a2d4a"
ORANGE = "#f5a623"
GREEN  = "#22c55e"
RED    = "#ef4444"
GRAY   = "#6b7280"


def kpi_card(title, value, unit, icon, color):
    title_upper = title.upper()
    if "CHAMPS" in title_upper:
        sub = "sur 6 champs"
    elif "HUMIDITE" in title_upper or "HUMIDIT" in title_upper:
        sub = "moyenne 24h"
    elif "EAU" in title_upper:
        sub = "m3 aujourd'hui"
    elif "ALERTES" in title_upper:
        sub = "non resolues"
    else:
        sub = "operationnels"
    html = "<div style='background:white;border-radius:15px;"
    html += "box-shadow:0 4px 10px rgba(0,0,0,0.05);height:180px;"
    html += "position:relative;overflow:hidden;display:flex;"
    html += "flex-direction:column;padding:15px;border:1px solid #f0f2f5;'>"
    html += "<div style='position:absolute;top:0;left:0;right:0;height:6px;"
    html += "background-color:" + str(color) + ";border-radius:15px 15px 0 0;'></div>"
    html += "<div style='height:40px;font-size:11px;font-weight:700;color:#6b7280;"
    html += "text-transform:uppercase;letter-spacing:0.8px;display:flex;"
    html += "align-items:center;margin-top:5px;'>" + str(title) + "</div>"
    html += "<div style='flex-grow:1;display:flex;align-items:center;"
    html += "justify-content:space-between;'>"
    html += "<div style='font-size:32px;font-weight:800;color:#1a2d4a;'>"
    html += str(value)
    html += "<span style='font-size:16px;margin-left:2px;'>" + str(unit) + "</span></div>"
    html += "<div style='font-size:32px;'>" + str(icon) + "</div></div>"
    html += "<div style='font-size:12px;color:#9ca3af;margin-top:5px;'>" + sub + "</div>"
    html += "</div>"
    return html


def show():
    st.markdown("""
    <div style='background:white;border-radius:12px;padding:20px 28px;
                margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);
                display:flex;align-items:center;justify-content:space-between;'>
        <div>
            <div style='font-size:22px;font-weight:700;color:#1a2d4a;'>
                 Dashboard Overview
            </div>
            <div style='font-size:13px;color:#6b7280;margin-top:2px;'>
                Vue globale du système de monitoring agricole
            </div>
        </div>
        <div style='font-size:12px;color:#9ca3af;'>🕐 Mis à jour toutes les 60s</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        active_fields  = get_total_active_fields()
        avg_moisture   = get_avg_soil_moisture()
        water_today    = get_water_usage_today()
        active_alerts  = get_active_alerts_count()
        yield_proj     = get_yield_projection()
        active_devices = get_active_devices_count()
    except Exception as e:
        st.error("Erreur DB : " + str(e))
        st.exception(e)
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi_card("Champs Actifs", active_fields, "", "🌾", "#1a2d4a"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Humidite Moyenne", str(avg_moisture), "%", "💧", "#3b82f6"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Eau Utilisee", str(int(water_today)), "m3", "📋", "#f5a623"), unsafe_allow_html=True)
    with c4:
        ac = "#ef4444" if active_alerts > 0 else "#22c55e"
        st.markdown(kpi_card("Alertes Actives", active_alerts, "", "🚨", ac), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("Devices Actifs", active_devices, "", "📡", "#22c55e"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("""
        <div style='background:white;border-radius:12px;padding:20px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:16px;'>
            <div style='font-size:15px;font-weight:600;color:#1a2d4a;margin-bottom:16px;'>
                📈 Humidité Sol 30 derniers jours
            </div>
        """, unsafe_allow_html=True)
        try:
            df_moisture = get_moisture_last_30_days()
            if not df_moisture.empty:
                fig = px.line(df_moisture, x="date", y="avg_moisture", color="field_name",
                    labels={"date":"Date","avg_moisture":"Humidite (%)","field_name":"Champ"},
                    color_discrete_sequence=[NAVY, ORANGE, GREEN, "#6366f1", "#ec4899", "#14b8a6"])
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=0,r=0,t=0,b=0), height=260,
                    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=11)),
                    xaxis=dict(showgrid=False,tickfont=dict(size=11,color=GRAY)),
                    yaxis=dict(showgrid=True,gridcolor="#f3f4f6",tickfont=dict(size=11,color=GRAY),ticksuffix="%"))
                fig.add_hrect(y0=20,y1=40,fillcolor=GREEN,opacity=0.05,line_width=0,
                    annotation_text="Zone optimale",annotation_position="top left",
                    annotation_font=dict(size=10,color=GREEN))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Aucune donnee d'humidite disponible.")
        except Exception as e:
            st.error("Erreur humidite : " + str(e))
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style='background:white;border-radius:12px;padding:20px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:16px;'>
            <div style='font-size:15px;font-weight:600;color:#1a2d4a;margin-bottom:16px;'>
                🚨 Alertes par Sévérité
            </div>
        """, unsafe_allow_html=True)
        try:
            df_alerts = get_alerts_by_severity()
            if not df_alerts.empty:
                cmap = {"Critical":"#dc2626","High":"#f5a623","Medium":"#eab308","Low":"#22c55e"}
                colors = [cmap.get(s, GRAY) for s in df_alerts["severity"]]
                total_alerts = int(df_alerts["count"].sum())
                fig2 = go.Figure(data=[go.Pie(
                    labels=df_alerts["severity"], values=df_alerts["count"],
                    hole=0.6, marker=dict(colors=colors),
                    textinfo="label+value", textfont=dict(size=11))])
                fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=0,r=0,t=0,b=0), height=260, showlegend=False,
                    annotations=[dict(text="<b>"+str(total_alerts)+"</b><br>alertes",
                        x=0.5,y=0.5,font=dict(size=14,color=NAVY),showarrow=False)])
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown("<div style='text-align:center;padding:60px 0;color:#22c55e;'><div style='font-size:40px;'>✅</div><div style='font-size:14px;margin-top:8px;'>Aucune alerte active</div></div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("Erreur alertes : " + str(e))
        st.markdown("</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div style='background:white;border-radius:12px;padding:20px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px;font-weight:600;color:#1a2d4a;margin-bottom:16px;'>
                 Consommation Eau par Champ (m³)
            </div>
        """, unsafe_allow_html=True)
        try:
            df_water = get_water_usage_by_field()
            if not df_water.empty:
                fig3 = px.bar(df_water, x="total_volume_m3", y="field_name", orientation="h",
                    color="total_volume_m3", color_continuous_scale=[[0,"#dbeafe"],[1,NAVY]],
                    labels={"total_volume_m3":"Volume (m3)","field_name":"Champ"}, text="total_volume_m3")
                fig3.update_traces(texttemplate="%{text:.0f} m3", textposition="outside")
                fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=0,r=40,t=0,b=0), height=250, showlegend=False,
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=True,gridcolor="#f3f4f6",tickfont=dict(size=11)),
                    yaxis=dict(tickfont=dict(size=11)))
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Aucune donnee d'irrigation disponible.")
        except Exception as e:
            st.error("Erreur eau : " + str(e))
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div style='background:white;border-radius:12px;padding:20px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:15px;font-weight:600;color:#1a2d4a;margin-bottom:16px;'>
                Fréquence Anomalies par Champ
            </div>
        """, unsafe_allow_html=True)
        try:
            df_anomaly = get_anomaly_frequency_by_field()
            if not df_anomaly.empty:
                fig4 = px.bar(df_anomaly, x="field_name", y="anomaly_count", color="anomaly_count",
                    color_continuous_scale=[[0,"#fef9c3"],[0.5,ORANGE],[1,RED]],
                    labels={"anomaly_count":"Anomalies","field_name":"Champ"}, text="anomaly_count")
                fig4.update_traces(texttemplate="%{text}", textposition="outside")
                fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=0,r=0,t=0,b=0), height=250, showlegend=False,
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=False,tickfont=dict(size=11)),
                    yaxis=dict(showgrid=True,gridcolor="#f3f4f6",tickfont=dict(size=11)))
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown("<div style='text-align:center;padding:60px 0;color:#22c55e;'><div style='font-size:40px;'>✅</div><div style='font-size:14px;margin-top:8px;'>Aucune anomalie detectee</div></div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("Erreur anomalies : " + str(e))
        st.markdown("</div>", unsafe_allow_html=True)