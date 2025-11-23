from pydantic import BaseModel
from typing import Optional



# Base info
class UserBase(BaseModel):
    username: str
    email: str


# Login schema
class UserLogin(BaseModel):
    username: str
    password: str



# Public Registration (NO role)
class UserCreate(UserBase):
    password: str


# Admin Create User (CAN SET ROLE)
class AdminCreateUser(UserBase):
    password: str
    role: str


# Update user (self or admin)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None



# Role update (admin)
class RoleUpdate(BaseModel):
    role: str


# READ OUTPUT SCHEMA
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


