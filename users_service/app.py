from fastapi import FastAPI
from users_service.routers import router
from common.db.connection import Base, engine
from common.utils.exceptions import add_exception_handlers
from users_service.circuitbreaker_router import circuit_router

# 1) Create app first
app = FastAPI(title="Users Service")

# 2) Add exception handlers
add_exception_handlers(app)

# 3) Create database tables
Base.metadata.create_all(bind=engine)

# 4) API Versioning + Routers
app.include_router(router, prefix="/v1/users")
app.include_router(circuit_router, prefix="/v1/users")

# Optional legacy path
app.include_router(router, prefix="/users")
