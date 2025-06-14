# File: logic.py (Complete code with the final fix)

from sqlalchemy.orm import Session
from shapely.geometry import Point, Polygon
import json
from datetime import datetime, timezone
from sqlalchemy import func
import database as db

MIN_SECONDS_IN_ZONE = 10

def process_gps_ping(worker_id: int, location: Point, db_session: Session):
    print("\n--- Processing new ping ---")
    
    # 1. Get worker status
    worker_status = db_session.query(db.WorkerStatus).filter(db.WorkerStatus.worker_id == worker_id).first()
    if not worker_status:
        worker_status = db.WorkerStatus(worker_id=worker_id)
        db_session.add(worker_status)
        db_session.commit()
        print(f"DEBUG: Created new status for worker {worker_id}")

    previous_zone_id = worker_status.current_zone_id
    print(f"DEBUG: Worker's previous zone was: {previous_zone_id}")

    # 2. Check current location
    zones = db_session.query(db.Zone).all()
    current_zone_id = None
    for zone in zones:
        poly = Polygon(json.loads(zone.polygon_coords))
        if poly.contains(location):
            current_zone_id = zone.id
            break
    print(f"DEBUG: Worker is currently in zone: {current_zone_id}")

    # 3. Core Logic Check
    if current_zone_id != previous_zone_id:
        print("DEBUG: Zone has changed! Evaluating time spent.")
        
        # Check if they just left a valid zone
        if previous_zone_id is not None and worker_status.entry_timestamp is not None:
            now = datetime.now(timezone.utc)
            
            # --- THIS IS THE FIX for the TypeError ---
            # When we retrieve the timestamp from SQLite, it becomes "naive".
            # We must make it "aware" of the UTC timezone again before we can do math with it.
            entry_time_aware = worker_status.entry_timestamp.replace(tzinfo=timezone.utc)
            
            time_spent = (now - entry_time_aware).total_seconds()
            # --- END OF FIX ---
            
            print(f"DEBUG: Time spent in previous zone {previous_zone_id} was {time_spent:.2f} seconds.")

            is_already_logged_today = db_session.query(db.CollectionLog).filter(
                db.CollectionLog.zone_id == previous_zone_id,
                func.date(db.CollectionLog.serviced_at) == func.date(now)
            ).first()

            if time_spent >= MIN_SECONDS_IN_ZONE and not is_already_logged_today:
                log_entry = db.CollectionLog(zone_id=previous_zone_id)
                db_session.add(log_entry)
                print(f"✅✅✅ SUCCESS: LOGGED COLLECTION FOR ZONE {previous_zone_id} ✅✅✅")
            else:
                print(f"INFO: Did not log for zone {previous_zone_id}. Time spent was too short or already logged.")

        # Update status to the new zone
        worker_status.current_zone_id = current_zone_id
        worker_status.entry_timestamp = datetime.now(timezone.utc) if current_zone_id is not None else None
        
    else:
        print("DEBUG: Worker is still in the same zone. No change.")

    db_session.commit()
    print("--- Ping processing complete ---")