#!/usr/bin/env python3
r"""Safe runner to import and optionally serve the FastAPI `app`.

This avoids running `app/main.py` directly (which causes
"attempted relative import with no known parent package").

Usage (from repo root):
  # import-check only (no server)
  .\.venv\Scripts\python.exe run_server.py

  # start uvicorn server
  .\.venv\Scripts\python.exe run_server.py --serve --host 127.0.0.1 --port 8000
"""
import argparse
import sys


def import_app() -> None:
    # Import as a package import so relative imports inside `app` work.
    try:
        import app.main as main_mod  # type: ignore
    except Exception as exc:  # pragma: no cover - runtime helper
        print(f"Failed to import app.main: {exc}")
        raise
    # Access the FastAPI app object if present
    app_obj = getattr(main_mod, "app", None)
    print(f"Imported app.main; app object found: {app_obj is not None}")


def serve(host: str, port: int) -> None:
    # Import uvicorn lazily so running import-check doesn't require it
    import uvicorn

    # Serve the app by module path so uvicorn handles imports correctly
    uvicorn.run("app.main:app", host=host, port=port, reload=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="run_server.py")
    parser.add_argument("--serve", action="store_true", help="Start uvicorn server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind when serving")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind when serving")
    args = parser.parse_args(argv)

    import_app()

    if args.serve:
        serve(args.host, args.port)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
