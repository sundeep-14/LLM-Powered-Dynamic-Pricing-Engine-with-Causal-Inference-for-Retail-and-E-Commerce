"""
session.py
----------
This file does 3 things:
1. Reads your DATABASE_URL from .env
2. Creates the engine (actual connection to MySQL)
3. Creates SessionLocal (factory to get DB sessions)
4. Creates Base (parent class all ORM models inherit from)
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Step 1: Load .env file so os.getenv can read it
load_dotenv()

# Step 2: Read the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Step 3: Create the engine
# Think of engine as the "phone line" between Python and MySQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # tests connection before using it
    pool_size=10,        # keep 10 connections open at all times
    max_overflow=20,     # allow 20 extra connections under heavy load
    echo=False,           # prints SQL queries in terminal (helpful for learning)
)

# Step 4: Create SessionLocal
# Think of a session as one "conversation" with the database
# Every time you want to read/write data you open a session, use it, then close it
SessionLocal = sessionmaker(
    autocommit=False,  # we manually control when to save (commit)
    autoflush=False,   # we manually control when to send queries
    bind=engine,       # use our MySQL engine
)

# Step 5: Create Base
# All your ORM models (User, Product, etc.) will inherit from this
# It keeps track of all your table definitions
Base = declarative_base()


def get_db():
    """
    This function gives a database session to whoever needs it.
    It automatically closes the session when done.
    
    Usage in FastAPI routes:
        def my_route(db: Session = Depends(get_db)):
    
    The 'yield' makes it a generator — it pauses here, gives the session
    to the caller, then resumes the finally block to close it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()