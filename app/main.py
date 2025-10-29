import os
import sys
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# When this module is executed directly (python app/main.py) Python does not
# set the package context and `import app...` can fail. Ensure the project root
# is on sys.path so `import app` works in that case.
if __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI app
app = FastAPI(title="OptiExtract File Uploader & Tracker")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            system_filename TEXT NOT NULL UNIQUE,
            file_size INTEGER NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Create tables on startup
init_db()

# Set up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Generate unique system filename with original extension
    ext = os.path.splitext(file.filename or "")[1]
    system_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, system_name)

    # Save file
    with open(filepath, "wb") as f:
        f.write(contents)

    size_bytes = os.path.getsize(filepath)

    # Save metadata to SQLite
    try:
        conn = sqlite3.connect("files.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO files 
               (original_filename, system_filename, file_size, uploaded_at) 
               VALUES (?, ?, ?, ?)""",
            (file.filename, system_name, size_bytes, datetime.utcnow().isoformat())
        )
        file_id = cursor.lastrowid
        conn.commit()
    except sqlite3.Error as e:
        os.unlink(filepath)  # Clean up file if DB insert fails
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

    return JSONResponse({
        "message": "File uploaded successfully",
        "id": file_id,
        "original_filename": file.filename,
        "system_filename": system_name,
        "file_size": size_bytes,
    })


@app.get("/files")
def get_files() -> List[Dict[str, Any]]:
    try:
        conn = sqlite3.connect("files.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, original_filename, system_filename, file_size, uploaded_at 
               FROM files ORDER BY uploaded_at DESC"""
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "original_filename": row[1],
                "system_filename": row[2],
                "file_size": row[3],
                "uploaded_at": row[4]
            }
            for row in rows
        ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# @app.get("/download/{system_filename}")
# def download_file(system_filename: str):
#     filepath = os.path.join(UPLOAD_DIR, system_filename)
#     if not os.path.exists(filepath):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(filepath, filename=system_filename)


# @app.get("/")
# def root():
#     return RedirectResponse(url="/static/upload.html")


@app.get("/files/{file_id}")
def read_uploaded_file(file_id: int):
    try:
        # Get system_filename from database
        conn = sqlite3.connect("files.db")
        cursor = conn.cursor()
        cursor.execute("SELECT system_filename FROM files WHERE id = ?", (file_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="File not found in database")
        
        system_filename = result[0]
        filepath = os.path.join(UPLOAD_DIR, system_filename)
        
        # Ensure file is within uploads directory
        real_path = os.path.realpath(filepath)
        if not real_path.startswith(os.path.realpath(UPLOAD_DIR)):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found on disk")

        with open(filepath, "rb") as f:
            raw = f.read(4096)  # read first chunk for preview
        
        try:
            preview = raw.decode("utf-8", errors="replace")[:1000]
        except Exception:
            preview = "<binary content>"

        return {
            "file_id": file_id,
            "filename": system_filename,
            "preview": preview,
            "preview_size": len(preview),
            "is_truncated": len(raw) > 4096
        }

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    import os
    import sys

    # Ensure the project root is on sys.path so `import app` works when running
    # this file directly (python app/main.py).
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Try to start uvicorn for convenience; if uvicorn isn't available just
    # perform an import-check and print a confirmation.
    try:
        import uvicorn

        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception:
        try:
            # Import-check
            import app.main as _m  # type: ignore

            print("Imported app.main successfully (direct-run guard).")
        except Exception as exc:  # pragma: no cover - helpful runtime message
            print(f"Failed to import app as package even after adjusting sys.path: {exc}")
            raise
