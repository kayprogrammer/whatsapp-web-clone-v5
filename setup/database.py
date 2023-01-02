from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from . settings import *

SQLALCHAMY_DATABASE_URL = f"postgresql://{DATABASES['USER']}:{DATABASES['PASSWORD']}@{DATABASES['HOST']}:{DATABASES['PORT']}/{DATABASES['DB_NAME']}"

engine = create_engine(SQLALCHAMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
session = scoped_session(SessionLocal)
Base = declarative_base()

Base.query = session.query_property()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

