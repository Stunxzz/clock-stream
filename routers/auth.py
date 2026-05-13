import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db, SessionLocal
from models import User
from translations import get_t, SUPPORTED_LANGS

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

# ── Crypto config ────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8
COOKIE_NAME = "access_token"


# ── Token helpers ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_initials(username: str) -> str:
    parts = username.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return username[:2].upper()


# ── Auth dependency ───────────────────────────────────────────────────────────

class NotAuthenticatedException(Exception):
    pass


def get_current_user(
    token: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise NotAuthenticatedException()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.get(User, int(payload["sub"]))
        if not user:
            raise NotAuthenticatedException()
        return user
    except (JWTError, Exception):
        raise NotAuthenticatedException()


def _lang_from_cookie(lang: str = Cookie(default="bg")) -> str:
    return lang if lang in SUPPORTED_LANGS else "bg"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, lang: str = Depends(_lang_from_cookie)):
    return templates.TemplateResponse("login.html", {"request": request, "t": get_t(lang), "lang": lang})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    lang: str = Depends(_lang_from_cookie),
    db: Session = Depends(get_db),
):
    t = get_t(lang)
    user = db.scalar(select(User).where(User.username == username.strip()))

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "t": t, "lang": lang, "error": t["auth_invalid_credentials"], "username": username},
            status_code=401,
        )

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(COOKIE_NAME, create_token(user.id), httponly=True, samesite="lax", max_age=TOKEN_EXPIRE_HOURS * 3600)
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, lang: str = Depends(_lang_from_cookie)):
    return templates.TemplateResponse("register.html", {"request": request, "t": get_t(lang), "lang": lang})


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    lang: str = Depends(_lang_from_cookie),
    db: Session = Depends(get_db),
):
    t = get_t(lang)

    def fail(error: str):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "t": t, "lang": lang, "error": error,
             "form": {"username": username, "email": email}},
            status_code=422,
        )

    if password != confirm_password:
        return fail(t["auth_passwords_mismatch"])
    if len(password) < 6:
        return fail(t["auth_password_too_short"])
    if db.scalar(select(User).where(User.username == username.strip())):
        return fail(t["auth_username_taken"])
    if db.scalar(select(User).where(User.email == email.strip().lower())):
        return fail(t["auth_email_taken"])

    user = User(username=username.strip(), email=email.strip().lower(), hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(COOKIE_NAME, create_token(user.id), httponly=True, samesite="lax", max_age=TOKEN_EXPIRE_HOURS * 3600)
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response
