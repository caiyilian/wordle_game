import asyncio
from pathlib import Path
import sqlite3
import subprocess
import sys

from database import Base, init_database


EXPECTED_TABLES = {"users", "rooms", "room_members", "game_records", "player_guesses"}


def test_metadata_contains_expected_tables() -> None:
    import models  # noqa: F401

    assert EXPECTED_TABLES.issubset(Base.metadata.tables)


def test_init_database_is_idempotent() -> None:
    asyncio.run(init_database())
    asyncio.run(init_database())

    db_path = Path(__file__).resolve().parents[1] / "wordle.db"
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("select name from sqlite_master where type = 'table'").fetchall()

    table_names = {row[0] for row in rows}
    assert EXPECTED_TABLES.issubset(table_names)


def test_init_db_script_is_idempotent() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "init_db.py"

    subprocess.run([sys.executable, str(script)], cwd=backend_dir, check=True)
    subprocess.run([sys.executable, str(script)], cwd=backend_dir, check=True)
