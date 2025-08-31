# src/config.py
from pathlib import Path

ROOT = Path(__file__).resolve().parent        # .../job_hunter/src
DB_PATH = ROOT.parent / "db.sqlite"           # .../job_hunter/db.sqlite
# If you prefer a data folder, use:
# DB_PATH = ROOT.parent / "data" / "db.sqlite"
