from sqlalchemy import create_engine, Column, Integer, String, JSON, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Palette(Base):
    __tablename__ = "palettes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String)
    colors_json = Column(Text)

class SessionCanvas(Base):
    __tablename__ = "session_canvases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    canvas_id = Column(String, index=True)
    canvas_json = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)
