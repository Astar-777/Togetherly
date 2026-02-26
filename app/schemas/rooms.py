from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str


class RoomJoin(BaseModel):
    join_code: str


class RoomResponse(BaseModel):
    id: int
    name: str
    join_code: str
    owner_id: int

    class Config:
        from_attributes = True
