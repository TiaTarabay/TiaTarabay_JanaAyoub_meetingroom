from fastapi import FastAPI
from .routers import router
from common.db.connection import Base, engine

app = FastAPI(title="Users Service")

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/users")
