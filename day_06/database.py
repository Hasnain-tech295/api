# Everything SQLAlchemy needs to connect and create sessions.
# This file is the bridge between your app and PostgreSQL.

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import get_settings

settings = get_settings()

