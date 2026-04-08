import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "crop.db")

async def get_db():
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
    finally:
        await conn.close()

async def init_db(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            mobile TEXT,
            name TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur = await conn.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in await cur.fetchall()]
    if "name" not in cols:
        await conn.execute("ALTER TABLE users ADD COLUMN name TEXT")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS crop_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            district TEXT,
            crop_name TEXT,
            season TEXT,
            min_temp REAL,
            max_temp REAL,
            rainfall REAL,
            humidity REAL,
            wind_speed REAL,
            soil_type TEXT,
            soil_ph REAL,
            irrigation_type TEXT,
            suitable TEXT
        )
    """)
    await conn.commit()
