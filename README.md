# smart-waste-collection-system
A prototype system for digitizing door-to-door waste collection using a passive, GPS-based auto-logging backend (FastAPI) and a live monitoring dashboard (Streamlit).
# Smart Waste Collection System Prototype

This is a prototype system for digitizing door-to-door waste collection, built as a solution to the "Digitizing Door-to-Door Waste Collection in Mangaluru" problem statement.

It replaces a high-friction, manual QR-code system with a **passive, GPS-based auto-logging backend** and a **live monitoring dashboard**.
## System Architecture
The project consists of three main components that run simultaneously:
1.  **Backend API (`main.py`):** A FastAPI server that receives GPS pings, processes them using geofencing logic, and logs collections to a database.
2.  **Live Dashboard (`dashboard.py`):** A Streamlit web application that visualizes the status of collection zones in real-time by reading from the database.
3.  **Worker Simulator (`worker_app_simulator.py`):** A Python script that simulates a field worker's mobile app, sending test data to the backend.
---
## Technology Stack
-   **Backend:** Python, FastAPI, Uvicorn
-   **Frontend/Dashboard:** Streamlit, Folium, Pandas
-   **Database:** SQLite
-   **Core Logic:** SQLAlchemy (ORM), Shapely (Geospatial)
-   **Testing/Simulation:** Requests
---
## How to Run This Project
### 1. Prerequisites

Install all necessary Python libraries:
pip install "fastapi[all]" sqlalchemy shapely streamlit pandas folium streamlit-folium requests
---
You need to run the three components in three separate terminals from the project's root directory.
Terminal 1: Start the Backend API
uvicorn main:app --reload

Terminal 2: Start the Dashboard
streamlit run dashboard.py

Terminal 3: Start the Worker Simulator
python worker_app_simulator.py

After running the simulator, the dashboard (running in your browser) will update to show the collection zones being marked as "Serviced".
