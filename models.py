import atexit
import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PSWD = os.getenv("PG_PSWD")
PG_DB = os.getenv("PG_DB")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", 5431)

PG_DSN = f"postgresql://{PG_USER}:{PG_PSWD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(PG_DSN)
atexit.register(engine.dispose)

Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)


class Ad(Base):
    __tablename__ = "app_ads"

    id = Column(Integer, primary_key=True)
    headline = Column(String, nullable=False, unique=True, index=True)
    description = Column(String)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(Integer)


class User(Base):
    __tablename__ = "app_users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())


Base.metadata.create_all()
