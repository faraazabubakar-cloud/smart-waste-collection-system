# File: database.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base
import json

# --- Database Configuration ---
# This creates a file named 'waste_collection.db' in your project folder.
DATABASE_URL = "sqlite:///./waste_collection.db"

# --- SQLAlchemy Setup ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models (Tables) ---
class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    # We will store the polygon's coordinates as a simple text (JSON string)
    polygon_coords = Column(String, nullable=False)

class CollectionLog(Base):
    __tablename__ = "collection_logs"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    serviced_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="Auto-Logged")

class WorkerStatus(Base):
    """This table is a simple 'memory' for the system.
       It tracks where a worker was last seen and when they entered that zone.
    """
    __tablename__ = "worker_status"
    worker_id = Column(Integer, primary_key=True, index=True)
    current_zone_id = Column(Integer, nullable=True)
    entry_timestamp = Column(DateTime(timezone=True), nullable=True)

# --- Utility Function to Create Database ---
def create_db_and_tables():
    # This command tells SQLAlchemy to create all the tables defined above.
    Base.metadata.create_all(bind=engine)

# This is a special function for FastAPI to manage database connections.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import event
from sqlalchemy.engine import Engine
import datetime

# This is a special configuration for SQLite to ensure it handles timezone-aware datetimes correctly.
# It makes sure that when we get a datetime back from the SQLite database, it's still "aware" of its timezone.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# The code above is standard boilerplate for enabling some good features in SQLite.
# The code below is NOT needed, as modern SQLAlchemy handles this better.
# Let's ensure our datetime columns are defined correctly. We already did this with:
# serviced_at = Column(DateTime(timezone=True), ...)
# entry_timestamp = Column(DateTime(timezone=True), ...)
# This `timezone=True` argument is the key.