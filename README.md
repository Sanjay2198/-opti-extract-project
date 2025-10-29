# OptiExtract Take-Home Assignment — File Uploader & Tracker

### 🚀 How to Run
1. Create virtual environment  
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # (Windows)
   ```
2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```
3. Run FastAPI  
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open  
   - Upload page → [http://127.0.0.1:8000/static/upload.html](http://127.0.0.1:8000/static/upload.html)  
   - History page → [http://127.0.0.1:8000/static/history.html](http://127.0.0.1:8000/static/history.html)

Notes — running modules and relative imports
-------------------------------------------

If you ran a file directly (for example `python app/crud.py` or `python app/main.py`) you may see errors like:

```
ImportError: attempted relative import with no known parent package
```

That's because relative imports (e.g. `from .models import FileMeta`) only work when a module is executed as part of a package. There are two simple options:

- Run the module as a package from the project root:

   ```powershell
   # using the project's venv on Windows PowerShell
   .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe -m app.crud
   .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe -m app.main
   ```

- Or run the FastAPI app with uvicorn (recommended for serving the API):

   ```powershell
   .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

Adding `app/__init__.py` (present in this repo) makes `app` a proper package so the `-m` approach works.
