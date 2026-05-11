"""
database.py — Supabase bilan barcha operatsiyalar (to'liq async)
"""
import asyncio
from datetime import datetime
from supabase import acreate_client, AsyncClient
from bot.config import SUPABASE_URL, SUPABASE_KEY

_client: AsyncClient | None = None
_lock = asyncio.Lock()


async def get_client() -> AsyncClient:
    global _client
    if _client is None:
        async with _lock:
            if _client is None:
                _client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ── Mock testlar ─────────────────────────────────────────────

async def get_active_mocks() -> list[dict]:
    try:
        c = await get_client()
        res = (
            await c.table("mock_tests")
            .select("*")
            .eq("status", "active")
            .order("created_at", desc=False)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


async def get_all_mocks() -> list[dict]:
    try:
        c = await get_client()
        res = (
            await c.table("mock_tests")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


async def get_mock_by_id(mock_id: str) -> dict | None:
    try:
        c = await get_client()
        res = (
            await c.table("mock_tests")
            .select("*")
            .eq("id", mock_id)
            .single()
            .execute()
        )
        return res.data
    except Exception:
        return None


async def create_mock(data: dict) -> dict | None:
    try:
        c = await get_client()
        res = await c.table("mock_tests").insert(data).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


async def update_mock(mock_id: str, data: dict) -> bool:
    try:
        c = await get_client()
        await c.table("mock_tests").update(data).eq("id", mock_id).execute()
        return True
    except Exception:
        return False


async def archive_mock(mock_id: str) -> bool:
    return await update_mock(mock_id, {"status": "archived"})


async def delete_mock(mock_id: str) -> bool:
    try:
        c = await get_client()
        await c.table("mock_tests").delete().eq("id", mock_id).execute()
        return True
    except Exception:
        return False


# ── Supabase Storage — mock photo ────────────────────────────

async def upload_mock_photo(mock_id: str, image_bytes: bytes, content_type: str = "image/jpeg") -> str | None:
    try:
        c = await get_client()
        path = f"{mock_id}.jpg"
        await c.storage.from_("mock-photos").upload(
            path,
            image_bytes,
            {"content-type": content_type, "upsert": "true"},
        )
        return c.storage.from_("mock-photos").get_public_url(path)
    except Exception:
        return None


# ── Ro'yxatlar ───────────────────────────────────────────────

def gen_reg_id() -> str:
    return "REG" + datetime.now().strftime("%Y%m%d%H%M%S")


async def create_registration(data: dict) -> dict | None:
    try:
        c = await get_client()
        res = await c.table("registrations").insert(data).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


async def get_registration(reg_id: str) -> dict | None:
    try:
        c = await get_client()
        res = (
            await c.table("registrations")
            .select("*")
            .eq("id", reg_id)
            .single()
            .execute()
        )
        return res.data
    except Exception:
        return None


async def update_registration_status(reg_id: str, status: str, approved_by: str = "") -> bool:
    try:
        c = await get_client()
        await c.table("registrations").update({
            "status": status,
            "approved_by": approved_by,
        }).eq("id", reg_id).execute()
        return True
    except Exception:
        return False


async def get_registrations_by_mock(mock_id: str) -> list[dict]:
    try:
        c = await get_client()
        res = (
            await c.table("registrations")
            .select("*")
            .eq("mock_id", mock_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


async def get_recent_registrations(limit: int = 30) -> list[dict]:
    try:
        c = await get_client()
        res = (
            await c.table("registrations")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


async def get_stats() -> dict:
    try:
        c = await get_client()
        # 5 ta so'rov parallel — ketma-ket emas
        results = await asyncio.gather(
            c.table("registrations").select("id", count="exact").execute(),
            c.table("registrations").select("id", count="exact").eq("status", "approved").execute(),
            c.table("registrations").select("id", count="exact").eq("status", "pending").execute(),
            c.table("registrations").select("id", count="exact").eq("status", "rejected").execute(),
            c.table("mock_tests").select("id", count="exact").eq("status", "active").execute(),
        )
        return dict(
            total=results[0].count or 0,
            approved=results[1].count or 0,
            pending=results[2].count or 0,
            rejected=results[3].count or 0,
            active_mocks=results[4].count or 0,
        )
    except Exception:
        return {}
