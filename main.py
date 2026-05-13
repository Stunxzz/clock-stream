from fastapi import FastAPI
from database import Base, engine
from routers import admin, stream

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Часовници за производство")

app.include_router(admin.router)
app.include_router(stream.router)
