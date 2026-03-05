# =============================================================
#  IoT Agricultural Monitoring System
#  Fichier : dashboard/queries.py
#  Rôle    : Connexion PostgreSQL + toutes les requêtes SQL
# =============================================================

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# ─── CONNEXION ────────────────────────────────────────────────
def get_engine():
    """Crée et retourne le moteur SQLAlchemy."""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "iot_agri_db")
    DB_USER = os.getenv("DB_USER", "agri_user")
    DB_PASS = os.getenv("DB_PASSWORD", "tonmotdepasse")

    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_pre_ping=True)


def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """Exécute une requête SQL et retourne un DataFrame pandas."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


# =============================================================
#  KPIs — PAGE OVERVIEW
# =============================================================

def get_total_active_fields() -> int:
    """Nombre de champs ayant au moins un device actif."""
    sql = """
        SELECT COUNT(DISTINCT f.fieldId) AS total
        FROM   Fields f
        JOIN   IotDevices d ON d.fieldId = f.fieldId
        WHERE  d.deviceStatus = 'Active'
    """
    df = run_query(sql)
    return int(df["total"].iloc[0])


def get_avg_soil_moisture() -> float:
    """Humidité sol moyenne sur les dernières 24h (%)."""
    sql = """
        SELECT ROUND(AVG(sr.value)::NUMERIC, 1) AS avg_moisture
        FROM   SensorReadings sr
        WHERE  sr.metricType = 'soil_moisture'
          AND  sr.timestamp  >= NOW() - INTERVAL '24 hours'
    """
    df = run_query(sql)
    val = df["avg_moisture"].iloc[0]
    return float(val) if val is not None else 0.0


def get_water_usage_today() -> float:
    """Volume d'eau total utilisé aujourd'hui (m³)."""
    sql = """
        SELECT COALESCE(SUM(waterVolumeM3), 0) AS total_water
        FROM   IrrigationEvents
        WHERE  DATE(irrigStartTime) = CURRENT_DATE
    """
    df = run_query(sql)
    return float(df["total_water"].iloc[0])


def get_active_alerts_count() -> int:
    """Nombre d'alertes non résolues."""
    sql = """
        SELECT COUNT(*) AS total
        FROM   Alerts
        WHERE  resolved = FALSE
    """
    df = run_query(sql)
    return int(df["total"].iloc[0])


def get_yield_projection() -> float:
    """Projection de rendement : moyenne des cycles en cours (tons/ha estimés)."""
    sql = """
        SELECT ROUND(AVG(c.optimalMoistureMax * 0.8)::NUMERIC, 1) AS projection
        FROM   CropCycles cc
        JOIN   Crops c ON c.cropId = cc.cropId
        WHERE  cc.status = 'Growing'
    """
    df = run_query(sql)
    val = df["projection"].iloc[0]
    return float(val) if val is not None else 0.0


def get_active_devices_count() -> int:
    """Nombre de devices IoT actifs."""
    sql = """
        SELECT COUNT(*) AS total
        FROM   IotDevices
        WHERE  deviceStatus = 'Active'
    """
    df = run_query(sql)
    return int(df["total"].iloc[0])


# =============================================================
#  MOISTURE — PAGE 2
# =============================================================

def get_moisture_last_30_days(field_id: int = None) -> pd.DataFrame:
    """
    Humidité sol moyenne par jour sur les 30 derniers jours.
    Si field_id est fourni, filtre sur ce champ.
    """
    sql = """
        SELECT
            DATE(sr.timestamp)               AS date,
            f.name                           AS field_name,
            ROUND(AVG(sr.value)::NUMERIC, 2) AS avg_moisture
        FROM   SensorReadings sr
        JOIN   IotDevices d ON d.deviceId = sr.deviceId
        JOIN   Fields     f ON f.fieldId  = d.fieldId
        WHERE  sr.metricType = 'soil_moisture'
          AND  sr.timestamp  >= NOW() - INTERVAL '30 days'
          AND  (:field_id IS NULL OR f.fieldId = :field_id)
        GROUP  BY DATE(sr.timestamp), f.fieldId, f.name
        ORDER  BY date ASC
    """
    return run_query(sql, {"field_id": field_id})


def get_fields_list() -> pd.DataFrame:
    """Liste de tous les champs avec leur ferme."""
    sql = """
        SELECT f.fieldId, f.name AS field_name, fa.name AS farm_name
        FROM   Fields f
        JOIN   Farms  fa ON fa.farmId = f.farmId
        ORDER  BY fa.name, f.name
    """
    return run_query(sql)


# =============================================================
#  TEMPERATURE — PAGE 3 (dans 2_moisture.py)
# =============================================================

def get_temperature_trend(days: int = 30) -> pd.DataFrame:
    """
    Température air : min, moyenne, max par jour.
    """
    sql = """
        SELECT
            DATE(sr.timestamp)               AS date,
            ROUND(MIN(sr.value)::NUMERIC, 1) AS temp_min,
            ROUND(AVG(sr.value)::NUMERIC, 1) AS temp_avg,
            ROUND(MAX(sr.value)::NUMERIC, 1) AS temp_max
        FROM   SensorReadings sr
        WHERE  sr.metricType = 'air_temperature'
          AND  sr.timestamp  >= NOW() - INTERVAL :days
        GROUP  BY DATE(sr.timestamp)
        ORDER  BY date ASC
    """
    return run_query(sql, {"days": f"{days} days"})


# =============================================================
#  IRRIGATION — PAGE 3_irrigation.py
# =============================================================

def get_irrigation_events(field_id: int = None) -> pd.DataFrame:
    """
    Événements d'irrigation avec durée calculée.
    """
    sql = """
        SELECT
            ie.irrigId,
            f.name                                        AS field_name,
            fa.name                                       AS farm_name,
            ie.irrigStartTime                             AS start_time,
            ie.irrigEndTime                               AS end_time,
            ROUND(ie.waterVolumeM3::NUMERIC, 2)           AS volume_m3,
            ie.irrigAutomated,
            EXTRACT(EPOCH FROM (ie.irrigEndTime - ie.irrigStartTime))/3600
                                                          AS duration_hours
        FROM   IrrigationEvents ie
        JOIN   Fields f  ON f.fieldId  = ie.fieldId
        JOIN   Farms  fa ON fa.farmId  = f.farmId
        WHERE  (:field_id IS NULL OR ie.fieldId = :field_id)
        ORDER  BY ie.irrigStartTime DESC
        LIMIT  100
    """
    return run_query(sql, {"field_id": field_id})


def get_water_usage_by_field() -> pd.DataFrame:
    """Volume d'eau total par champ (tous les temps)."""
    sql = """
        SELECT
            f.name                                AS field_name,
            fa.name                               AS farm_name,
            ROUND(SUM(ie.waterVolumeM3)::NUMERIC, 2) AS total_volume_m3,
            COUNT(ie.irrigId)                     AS event_count
        FROM   IrrigationEvents ie
        JOIN   Fields f  ON f.fieldId = ie.fieldId
        JOIN   Farms  fa ON fa.farmId = f.farmId
        GROUP  BY f.fieldId, f.name, fa.name
        ORDER  BY total_volume_m3 DESC
    """
    return run_query(sql)


def get_irrigation_overlay(field_id: int = None) -> pd.DataFrame:
    """
    Données combinées humidité + irrigation par jour
    pour le graphique overlay.
    """
    sql = """
        SELECT
            dates.date,
            f.name                                       AS field_name,
            ROUND(AVG(sr.value)::NUMERIC, 2)             AS avg_moisture,
            COALESCE(SUM(ie.waterVolumeM3), 0)           AS water_volume
        FROM (
            SELECT DISTINCT DATE(timestamp) AS date
            FROM   SensorReadings
            WHERE  timestamp >= NOW() - INTERVAL '30 days'
        ) dates
        CROSS JOIN Fields f
        LEFT JOIN IotDevices  d  ON d.fieldId  = f.fieldId
        LEFT JOIN SensorReadings sr
               ON DATE(sr.timestamp) = dates.date
              AND sr.deviceId   = d.deviceId
              AND sr.metricType = 'soil_moisture'
        LEFT JOIN IrrigationEvents ie
               ON DATE(ie.irrigStartTime) = dates.date
              AND ie.fieldId = f.fieldId
        WHERE  (:field_id IS NULL OR f.fieldId = :field_id)
        GROUP  BY dates.date, f.fieldId, f.name
        ORDER  BY dates.date ASC
    """
    return run_query(sql, {"field_id": field_id})


# =============================================================
#  ALERTES — PAGE 4_alerts.py
# =============================================================

def get_open_alerts() -> pd.DataFrame:
    """Toutes les alertes non résolues, triées par sévérité."""
    sql = """
        SELECT
            a.alertId,
            f.name       AS field_name,
            fa.name      AS farm_name,
            a.alertType,
            a.severity,
            a.message,
            a.createdAt
        FROM   Alerts a
        JOIN   Fields f  ON f.fieldId = a.fieldId
        JOIN   Farms  fa ON fa.farmId = f.farmId
        WHERE  a.resolved = FALSE
        ORDER  BY
            CASE a.severity
                WHEN 'Critical' THEN 1
                WHEN 'High'     THEN 2
                WHEN 'Medium'   THEN 3
                WHEN 'Low'      THEN 4
            END,
            a.createdAt DESC
    """
    return run_query(sql)


def get_alerts_by_severity() -> pd.DataFrame:
    """Comptage des alertes ouvertes par sévérité (pour donut chart)."""
    sql = """
        SELECT severity, COUNT(*) AS count
        FROM   Alerts
        WHERE  resolved = FALSE
        GROUP  BY severity
        ORDER  BY
            CASE severity
                WHEN 'Critical' THEN 1
                WHEN 'High'     THEN 2
                WHEN 'Medium'   THEN 3
                WHEN 'Low'      THEN 4
            END
    """
    return run_query(sql)


def get_anomaly_frequency_by_field() -> pd.DataFrame:
    """Fréquence d'anomalies capteurs par champ (analyse DB)."""
    sql = """
        SELECT
            f.name        AS field_name,
            fa.name       AS farm_name,
            COUNT(*)      AS anomaly_count,
            MAX(sr.timestamp) AS last_anomaly
        FROM   SensorReadings sr
        JOIN   IotDevices d  ON d.deviceId = sr.deviceId
        JOIN   Fields     f  ON f.fieldId  = d.fieldId
        JOIN   Farms      fa ON fa.farmId  = f.farmId
        WHERE  sr.anomalyFlag = TRUE
        GROUP  BY f.fieldId, f.name, fa.name
        ORDER  BY anomaly_count DESC
    """
    return run_query(sql)


def resolve_alert(alert_id: int, user_id: int) -> None:
    """Marque une alerte comme résolue."""
    sql = """
        UPDATE Alerts
        SET    resolved   = TRUE,
               resolvedAt = NOW(),
               resolvedBy = :user_id
        WHERE  alertId = :alert_id
    """
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(sql), {"alert_id": alert_id, "user_id": user_id})
        conn.commit()


# =============================================================
#  CROP CYCLES — PAGE 5_crop_cycles.py
# =============================================================

def get_yield_per_crop() -> pd.DataFrame:
    """Rendement moyen par culture (tons/ha) — analyse DB."""
    sql = """
        SELECT
            c.cropName,
            COUNT(cc.cycleId)                              AS total_cycles,
            ROUND(AVG(cc.yieldTons)::NUMERIC, 2)           AS avg_yield_tons,
            ROUND(AVG(cc.yieldTons / f.areaHa)::NUMERIC, 2) AS avg_yield_per_ha
        FROM   CropCycles cc
        JOIN   Crops  c ON c.cropId  = cc.cropId
        JOIN   Fields f ON f.fieldId = cc.fieldId
        WHERE  cc.yieldTons IS NOT NULL
          AND  cc.status    = 'Completed'
        GROUP  BY c.cropName
        ORDER  BY avg_yield_per_ha DESC
    """
    return run_query(sql)


def get_crop_cycles_gantt() -> pd.DataFrame:
    """Données des cycles de cultures pour le diagramme Gantt."""
    sql = """
        SELECT
            cc.cycleId,
            f.name              AS field_name,
            fa.name             AS farm_name,
            c.cropName,
            cc.plantingDate     AS start_date,
            COALESCE(cc.actualHarvestDate, cc.expectedHarvestDate) AS end_date,
            cc.status,
            cc.yieldTons
        FROM   CropCycles cc
        JOIN   Fields f  ON f.fieldId = cc.fieldId
        JOIN   Farms  fa ON fa.farmId = f.farmId
        JOIN   Crops  c  ON c.cropId  = cc.cropId
        ORDER  BY cc.plantingDate DESC
    """
    return run_query(sql)


def get_active_crop_cycles() -> pd.DataFrame:
    """Cycles de cultures en cours."""
    sql = """
        SELECT
            f.name       AS field_name,
            c.cropName,
            cc.plantingDate,
            cc.expectedHarvestDate,
            cc.status
        FROM   CropCycles cc
        JOIN   Fields f ON f.fieldId = cc.fieldId
        JOIN   Crops  c ON c.cropId  = cc.cropId
        WHERE  cc.status = 'Growing'
        ORDER  BY cc.plantingDate
    """
    return run_query(sql)


# =============================================================
#  DEVICES — SIDEBAR / OVERVIEW
# =============================================================

def get_devices_status() -> pd.DataFrame:
    """Statut de tous les devices IoT."""
    sql = """
        SELECT
            d.deviceId,
            d.deviceType,
            d.deviceSerialNumber,
            d.firmwareVersion,
            d.deviceStatus,
            d.lastSeen,
            f.name  AS field_name,
            fa.name AS farm_name
        FROM   IotDevices d
        JOIN   Fields f  ON f.fieldId = d.fieldId
        JOIN   Farms  fa ON fa.farmId = f.farmId
        ORDER  BY d.deviceStatus, d.lastSeen DESC
    """
    return run_query(sql)