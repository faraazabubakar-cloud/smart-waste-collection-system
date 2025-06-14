# File: dashboard.py (Final and Complete Version)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from sqlalchemy import create_engine, func, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import json
from datetime import datetime, time
import time as os_time

# --- Database Connection and Models ---
# This section makes the dashboard a self-contained application.
DATABASE_URL = "sqlite:///./waste_collection.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

# We define the table structures again so SQLAlchemy knows what it's reading from the DB.
class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    polygon_coords = Column(String)

class CollectionLog(Base):
    __tablename__ = "collection_logs"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    serviced_at = Column(DateTime)
    status = Column(String)

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Waste Collection Dashboard")
st.title("🚛 Live Waste Collection Dashboard")

# --- Data Loading Function ---
def load_data():
    """Loads all necessary data from the database for visualization."""
    db_session = Session()
    try:
        zones = db_session.query(Zone).all()
        
        # A reliable way to get all logs created between the start and end of today.
        today_start = datetime.combine(datetime.today(), time.min)
        today_end = datetime.combine(datetime.today(), time.max)
        today_logs = db_session.query(CollectionLog).filter(
            CollectionLog.serviced_at >= today_start,
            CollectionLog.serviced_at <= today_end
        ).all()
        
        serviced_zone_ids = {log.zone_id for log in today_logs}

        # Format the logs into a clean DataFrame for display.
        if today_logs:
            logs_df = pd.DataFrame([
                {"Zone ID": log.zone_id, "Serviced At": log.serviced_at.strftime("%Y-%m-%d %H:%M:%S"), "Status": log.status}
                for log in today_logs
            ])
        else:
            logs_df = pd.DataFrame()
    finally:
        db_session.close()
    
    return zones, serviced_zone_ids, logs_df

# --- Main Dashboard Layout ---
zones_data, serviced_ids, logs_df = load_data()
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Operations Map")
    map_center = [12.9141, 74.8560]
    m = folium.Map(location=map_center, zoom_start=13) # Zoomed out a bit to see bigger zones

    if not zones_data:
        st.info("No zones found. Please run the worker simulator script first.")
    else:
        for zone in zones_data:
            is_serviced = zone.id in serviced_ids
            color = "green" if is_serviced else "red"
            
            # This block correctly formats the coordinates for display on the map
            coords_from_db = json.loads(zone.polygon_coords)
            # Folium expects (lat, lon), but we stored as (lon, lat) for Shapely.
            # We swap them back here just for drawing the map.
            locations_for_map = [[lat, lon] for lon, lat in coords_from_db]
            
            folium.Polygon(
                locations=locations_for_map,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.4,
                tooltip=f"<b>{zone.name}</b><br>Status: {'Serviced' if is_serviced else 'Pending'}"
            ).add_to(m)
        
    st_folium(m, width='100%', height=600)

with col2:
    st.subheader("Daily Statistics")
    total_zones = len(zones_data)
    serviced_count = len(serviced_ids)
    
    if total_zones > 0:
        progress = serviced_count / total_zones
        st.metric(label="Zones Serviced Today", value=f"{serviced_count} / {total_zones}")
        st.progress(progress)
    else:
        st.metric(label="Zones Serviced Today", value="0 / 0")
        st.progress(0.0)

    st.subheader("Today's Collection Logs")
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No collections logged for today yet.")

# --- Auto-Refresh ---
os_time.sleep(10)
st.rerun()