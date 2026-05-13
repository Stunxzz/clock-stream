import re
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pathlib import Path

from database import get_db
from models import Location, Break
from translations import get_t, SUPPORTED_LANGS

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

_TIME_RE = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')


def _lang(lang: str = Cookie(default="bg")) -> str:
    return lang if lang in SUPPORTED_LANGS else "bg"


# ── Language switcher ────────────────────────────────────────────────────────

@router.get("/lang/{code}")
def set_lang(code: str, request: Request):
    target = code if code in SUPPORTED_LANGS else "bg"
    response = RedirectResponse(request.headers.get("referer", "/"), status_code=303)
    response.set_cookie("lang", target, max_age=31_536_000, httponly=True, samesite="lax")
    return response


# ── Admin pages ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
def admin_index(request: Request, db: Session = Depends(get_db), lang: str = Depends(_lang)):
    locations = db.scalars(
        select(Location).options(selectinload(Location.breaks))
    ).all()
    return templates.TemplateResponse("index.html", {
        "request": request, "locations": locations, "t": get_t(lang), "lang": lang,
    })


@router.post("/locations")
def create_location(name: str = Form(...), db: Session = Depends(get_db), lang: str = Depends(_lang)):
    db.add(Location(name=name.strip()))
    db.commit()
    return RedirectResponse("/", status_code=303)


@router.post("/locations/{location_id}/delete")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.get(Location, location_id)
    if location:
        db.delete(location)
        db.commit()
    return RedirectResponse("/", status_code=303)


@router.get("/locations/{location_id}", response_class=HTMLResponse)
def location_detail(location_id: int, request: Request, db: Session = Depends(get_db), lang: str = Depends(_lang)):
    location = db.scalar(
        select(Location).where(Location.id == location_id).options(selectinload(Location.breaks))
    )
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return templates.TemplateResponse("location.html", {
        "request": request, "location": location, "t": get_t(lang), "lang": lang,
    })


@router.post("/locations/{location_id}/breaks")
def add_break(
    location_id: int,
    request: Request,
    name: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    db: Session = Depends(get_db),
    lang: str = Depends(_lang),
):
    location = db.scalar(
        select(Location).where(Location.id == location_id).options(selectinload(Location.breaks))
    )
    if not location:
        raise HTTPException(status_code=404)

    t = get_t(lang)
    error = None
    if not _TIME_RE.match(start_time) or not _TIME_RE.match(end_time):
        error = t["form_time_invalid_format"]
    elif start_time == end_time:
        error = t["form_time_equal_error"]
    elif start_time > end_time:
        error = t["form_time_order_error"]

    if error:
        return templates.TemplateResponse(
            "location.html",
            {
                "request": request,
                "location": location,
                "t": t,
                "lang": lang,
                "break_error": error,
                "break_form": {"name": name, "start_time": start_time, "end_time": end_time},
            },
            status_code=422,
        )

    db.add(Break(name=name.strip(), start_time=start_time, end_time=end_time, location_id=location_id))
    db.commit()
    return RedirectResponse(f"/locations/{location_id}", status_code=303)


@router.post("/breaks/{break_id}/delete")
def delete_break(break_id: int, db: Session = Depends(get_db)):
    b = db.get(Break, break_id)
    if not b:
        raise HTTPException(status_code=404)
    location_id = b.location_id
    db.delete(b)
    db.commit()
    return RedirectResponse(f"/locations/{location_id}", status_code=303)


@router.get("/clock/{location_id}", response_class=HTMLResponse)
def clock_view(location_id: int, request: Request, db: Session = Depends(get_db), lang: str = Depends(_lang)):
    location = db.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("clock.html", {
        "request": request, "location": location, "t": get_t(lang), "lang": lang,
    })
