from pydantic import BaseModel
from typing import Optional

# CREATE 
class RoomCreate(BaseModel):
    name: str
    capacity: int
    equipment: str
    location: str
    available: bool = True

# UPDATE 
class RoomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[str] = None
    location: Optional[str] = None
    available: Optional[bool] = None

# READ
class RoomRead(BaseModel):
    id: int
    name: str
    capacity: int
    equipment: str
    location: str
    available: bool

    model_config = {
        "from_attributes": True
    }