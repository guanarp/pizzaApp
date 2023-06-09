#imports
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, Session, declarative_base

#We'll use a SQLite db
SQLALCHEMY_DATABASE_URL = "sqlite:///./pizza_database.db"

#With the database url we'll create the SQL Alchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}) #check same thread is for SQLite

#Each instance of SessionLlocal will be a db session
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind = engine)

#We'll inherit from Base to create db models/classes
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency function to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

