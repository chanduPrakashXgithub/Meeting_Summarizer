# app/db/models.py
from sqlalchemy import Column, Integer, String, JSON
from app.db.database import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    transcript = Column(String, default="")
    summary_json = Column(JSON, default={})
