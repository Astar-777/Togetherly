from pydantic import BaseModel


class QueueItemCreate(BaseModel):
    title: str


class QueueItemResponse(BaseModel):
    id: int
    title: str
    position: int
    added_by: int

    class Config:
        from_attributes = True


class MoveItemRequest(BaseModel):
    new_position: int
