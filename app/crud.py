from sqlalchemy.orm import Session
from app.models import FileMeta
from app.database import SessionLocal

def create_file_meta(original_filename: str, system_filename: str, file_size: int):
    db: Session = SessionLocal()
    try:
        meta = FileMeta(
            original_filename=original_filename,
            system_filename=system_filename,
            file_size=file_size,
        )
        db.add(meta)
        db.commit()
        db.refresh(meta)
        return meta
    finally:
        db.close()

def list_files():
    db: Session = SessionLocal()
    try:
        return db.query(FileMeta).order_by(FileMeta.uploaded_at.desc()).all()
    finally:
        db.close()
