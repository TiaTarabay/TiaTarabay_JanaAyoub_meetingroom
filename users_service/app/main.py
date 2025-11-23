from fastapi import FastAPI
from .routes import router
from .db import Base, engine

app = FastAPI(title="Users Service")

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/users")
