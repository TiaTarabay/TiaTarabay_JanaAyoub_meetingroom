from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None