import asyncio
import json
from datetime import datetime, timedelta, date, time as dtime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from database import SessionLocal
from models import Break

router = APIRouter()


def _in_range(current: dtime, start: dtime, end: dtime) -> bool:
    """Проверява дали current е в интервала [start, end).
    Работи и при нощни смени, когато end < start (минава полунощ)."""
    if start < end:
        return start <= current < end
    if start == end:
        return False
    # Пресича полунощ: current >= start ИЛИ current < end
    return current >= start or current < end


def get_color(breaks) -> str:
    now = datetime.now()
    current = now.time()

    for b in breaks:
        start   = dtime(*map(int, b.start_time.split(":")))
        end     = dtime(*map(int, b.end_time.split(":")))
        warning = (datetime.combine(date.today(), end) - timedelta(minutes=5)).time()

        if _in_range(current, start, end):
            return "yellow" if _in_range(current, warning, end) else "green"

    return "red"


@router.get("/stream/{location_id}")
async def clock_stream(location_id: int):
    async def generate():
        while True:
            db = SessionLocal()
            try:
                breaks = db.query(Break).filter(Break.location_id == location_id).all()
                now = datetime.now()
                payload = json.dumps({"time": now.strftime("%H:%M"), "color": get_color(breaks)})
                yield f"data: {payload}\n\n"
            finally:
                db.close()
            await asyncio.sleep(1)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
