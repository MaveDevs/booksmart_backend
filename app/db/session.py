from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

# Get the URL from .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Fail loudly if no URL is found
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)