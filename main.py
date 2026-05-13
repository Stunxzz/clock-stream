from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from database import Base, engine
from routers import admin, stream
from routers.auth import router as auth_router, NotAuthenticatedException

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Часовници за производство")


@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse("/login", status_code=303)


app.include_router(auth_router)
app.include_router(admin.router)
app.include_router(stream.router)
