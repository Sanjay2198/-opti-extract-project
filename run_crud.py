#!/usr/bin/env python3
r"""Simple runner for `app.crud` so you can invoke it directly from the project root.

Usage examples (from repo root):
    .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe run_crud.py list
    .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe run_crud.py create --original "in.pdf" --system "abc123.pdf" --size 12345
"""
import argparse
import sys
from typing import List

from app.crud import create_file_meta, list_files


def cmd_list() -> int:
    records: List = list_files()
    if not records:
        print("No records found.")
        return 0
    for r in records:
        print(f"{r.id}\t{r.original_filename}\t{r.system_filename}\t{r.file_size}\t{r.uploaded_at}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    meta = create_file_meta(
        original_filename=args.original,
        system_filename=args.system,
        file_size=args.size,
    )
    print(
        f"Created id={meta.id} original={meta.original_filename} system={meta.system_filename} size={meta.file_size}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="run_crud.py")
    sub = parser.add_subparsers(dest="cmd")
    sub.required = True

    sub.add_parser("list", help="List file metadata records")

    create_p = sub.add_parser("create", help="Create a file metadata record")
    create_p.add_argument("--original", required=True, help="Original filename")
    create_p.add_argument("--system", required=True, help="System filename")
    create_p.add_argument("--size", type=int, required=True, help="File size in bytes")

    # If no subcommand provided, show help and exit with success (avoids argparse error)
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()
    if args.cmd == "list":
        return cmd_list()
    if args.cmd == "create":
        return cmd_create(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

