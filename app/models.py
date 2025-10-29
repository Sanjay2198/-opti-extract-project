from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class FileMeta(Base):
    __tablename__ = "file_meta"
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    system_filename = Column(String, nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
