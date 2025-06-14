# File: worker_app_simulator.py

import requests
import time
import json

# The URL of our running FastAPI backend API
API_URL = "http://127.0.0.1:8000"

def setup_test_zones():
    """This function calls our API to create some zones for our worker to drive through."""
    print("--- Setting up test zones ---")
    
    # Define the zones we want to create
    zones_to_create = [
        {"name": "Zone-A1", "coordinates": [[12.914, 74.856], [12.915, 74.856], [12.915, 74.857], [12.914, 74.857]]},
        {"name": "Zone-A2", "coordinates": [[12.915, 74.857], [12.916, 74.857], [12.916, 74.858], [12.915, 74.858]]},
        {"name": "Zone-B1", "coordinates": [[12.914, 74.858], [12.915, 74.858], [12.915, 74.859], [12.914, 74.859]]}
    ]

    for zone in zones_to_create:
        try:
            # Send a POST request to the /api/zones endpoint we created in main.py
            response = requests.post(f"{API_URL}/api/zones", json=zone)
            if response.status_code == 201: # 201 means "Created"
                print(f"Successfully created zone: {zone['name']}")
            elif response.status_code == 400: # 400 means "Bad Request" (e.g., zone already exists)
                print(f"Zone {zone['name']} already exists.")
            else:
                print(f"Error creating zone {zone['name']}: {response.text}")
        except requests.exceptions.ConnectionError:
            print("\n🚨 ERROR: Could not connect to the API. Is the backend (uvicorn) running?")
            return False
    return True


def run_simulation(worker_id: int):
    """Simulates a worker moving along a path and sending GPS pings."""
    print(f"\n--- Starting simulation for Worker {worker_id} ---")
    
    # This path is designed to test our logic:
    # 1. Stays in Zone A1 for 3 pings (15 seconds) -> Should be logged.
    # 2. Stays in Zone A2 for 3 pings (15 seconds) -> Should be logged.
    # 3. Passes through Zone B1 for only 1 ping (5 seconds) -> Should NOT be logged.
    path = [
        # Dwell in Zone A1
        {"lat": 12.9145, "lon": 74.8565}, # Ping 1 in A1
        {"lat": 12.9146, "lon": 74.8566}, # Ping 2 in A1
        {"lat": 12.9147, "lon": 74.8567}, # Ping 3 in A1 (Now we've been here > 10s)
        # Move to Zone A2 and dwell
        {"lat": 12.9155, "lon": 74.8575}, # Ping 1 in A2
        {"lat": 12.9156, "lon": 74.8576}, # Ping 2 in A2
        {"lat": 12.9157, "lon": 74.8577}, # Ping 3 in A2 (Now we've been here > 10s)
        # Pass through Zone B1 quickly
        {"lat": 12.9145, "lon": 74.8585}, # Only 1 ping in B1
        # Move out of all zones to end the simulation
        {"lat": 12.9130, "lon": 74.8600},
    ]

    for point in path:
        payload = {
            "worker_id": worker_id,
            "latitude": point["lat"],
            "longitude": point["lon"]
        }
        try:
            # Send a POST request to the /api/pings endpoint
            requests.post(f"{API_URL}/api/pings", json=payload)
            print(f"📍 Ping sent: Worker {worker_id} at ({point['lat']:.4f}, {point['lon']:.4f})")
        except requests.exceptions.ConnectionError:
            print("\n🚨 ERROR: Could not connect to the API. Is the backend (uvicorn) running?")
            break
        
        # Wait for 5 seconds before sending the next ping
        time.sleep(5)

if __name__ == "__main__":
    if setup_test_zones():
        run_simulation(worker_id=1)
        print("\n--- Simulation complete ---")