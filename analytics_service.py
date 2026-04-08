"""Basic analytics for admin dashboard."""
import aiosqlite
from config import DB_PATH


async def get_analytics() -> dict:
    conn = await aiosqlite.connect(DB_PATH)
    try:
        cur = await conn.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        cur = await conn.execute("SELECT COUNT(*) FROM crop_data")
        crop_records = (await cur.fetchone())[0]
        cur = await conn.execute(
            "SELECT crop_name, COUNT(*) as c FROM crop_data WHERE suitable = 'Y' GROUP BY crop_name ORDER BY c DESC LIMIT 10"
        )
        top_crops = [{"crop": r[0], "count": r[1]} for r in await cur.fetchall()]
        cur = await conn.execute(
            "SELECT state, COUNT(DISTINCT district) as d FROM crop_data GROUP BY state"
        )
        districts = [{"state": r[0], "districts": r[1]} for r in await cur.fetchall()]
        return {
            "total_users": users,
            "crop_records": crop_records,
            "top_suitable_crops": top_crops,
            "states_covered": len(districts),
            "districts_by_state": districts[:10],
        }
    finally:
        await conn.close()
