# File: main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from shapely.geometry import Point
import json

# Import the modules we just created
import database as db
import logic

# This command runs the function from our database.py file
# to create the 'waste_collection.db' file and all the tables inside it.
db.create_db_and_tables()

app = FastAPI(title="Smart Waste Collection API")

# --- Pydantic Models: These define the expected structure of incoming data ---
class PingPayload(BaseModel):
    worker_id: int
    latitude: float
    longitude: float

class ZonePayload(BaseModel):
    name: str
    coordinates: list[list[float]] # e.g., [[12.91, 74.85], [12.92, 74.85], ...]


# --- API Endpoints ---

@app.get("/")
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"message": "Welcome to the Smart Waste Collection API"}

@app.post("/api/pings")
def receive_ping(payload: PingPayload, db_session: Session = Depends(db.get_db)):
    """This is the main endpoint that will receive GPS pings from the worker's app."""
    # Convert latitude/longitude into a Point object for our logic module
    location = Point(payload.longitude, payload.latitude) # Shapely uses (lon, lat) order
    
    # Call the 'brain' function from our logic.py file
    logic.process_gps_ping(
        worker_id=payload.worker_id,
        location=location,
        db_session=db_session
    )
    return {"status": "Ping processed successfully"}

# --- Find this function in main.py ---
@app.post("/api/zones", status_code=201)
def create_zone(payload: ZonePayload, db_session: Session = Depends(db.get_db)):
    """A helper endpoint to easily add new zones to our system for testing."""
    existing_zone = db_session.query(db.Zone).filter(db.Zone.name == payload.name).first()
    if existing_zone:
        raise HTTPException(status_code=400, detail="Zone with this name already exists")
    
    # --- THIS IS THE FIX ---
    # The Shapely library expects (longitude, latitude) order.
    # The payload gives us (latitude, longitude). We need to swap them.
    swapped_coords = [[lon, lat] for lat, lon in payload.coordinates]
    
    # Store the CORRECTLY ORDERED coordinates as a JSON string
    coords_json = json.dumps(swapped_coords)
    # --- END OF FIX ---
    
    new_zone = db.Zone(name=payload.name, polygon_coords=coords_json)
    db_session.add(new_zone)
    db_session.commit()
    return {"name": new_zone.name, "id": new_zone.id}