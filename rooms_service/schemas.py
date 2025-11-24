from pydantic import BaseModel

class RoomBase(BaseModel):
    name: str | None = None
    capacity: int | None = None
    equipment: str | None = None
    location: str | None = None   # <-- add this

class RoomCreate(RoomBase):
    name: str
    capacity: int
    equipment: str
    location: str

class RoomUpdate(RoomBase):
    pass

class RoomRead(RoomBase):
    id: int

    class Config:
        orm_mode = True
